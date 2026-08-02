from __future__ import annotations

import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "cli" / "src"))
sys.path.insert(0, str(ROOT / "apps" / "gateway" / "src"))

from agentforge_cli.scaffolding import init_context
from agentforge_cli.twin import build_twin
from agentforge_cli.twin_service import (
    GeneratorConfig,
    ask_twin,
    generate,
    make_handler,
    resolve_generator_config,
)


class FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


def fake_generator(answer: str = "The twin says: use the gateway."):
    def urlopen_fn(request, timeout: float) -> FakeResponse:
        payload = {
            "choices": [{"message": {"role": "assistant", "content": answer}}],
        }
        return FakeResponse(json.dumps(payload).encode("utf-8"))

    return urlopen_fn


def failing_generator():
    def urlopen_fn(request, timeout: float):
        raise OSError("connection refused")

    return urlopen_fn


# hold TemporaryDirectory references so they are not GC'd mid-test
_LIVE_TMP: list[object] = []


def make_project() -> Path:
    tmp = tempfile.TemporaryDirectory()
    _LIVE_TMP.append(tmp)  # keep alive until process exit
    project = Path(tmp.name) / "qa-project"
    init_context(project)
    adr = project / ".agentforge" / "adrs" / "0001-use-aics.md"
    adr.write_text("# Use the AICS Context Standard\n\nContext\nDecision\nConsequences\n", encoding="utf-8")
    build_twin(project)
    return project


class AskTwinTests(unittest.TestCase):
    def test_generated_answer(self) -> None:
        project = make_project()
        try:
            result = ask_twin(project, "AICS", GeneratorConfig(), urlopen_fn=fake_generator("answer here"))
            self.assertEqual(result["source"], "generated")
            self.assertEqual(result["answer"], "answer here")
            self.assertTrue(result["excerpts"])
        finally:
            import shutil

            shutil.rmtree(project.parent, ignore_errors=True)

    def test_extractive_fallback_on_generator_failure(self) -> None:
        project = make_project()
        try:
            result = ask_twin(project, "AICS", GeneratorConfig(), urlopen_fn=failing_generator())
            self.assertEqual(result["source"], "extractive")
            self.assertIn("extractive answer", result["answer"])
            self.assertIn("[", result["answer"])  # excerpt ids quoted
            self.assertTrue(result["excerpts"])
        finally:
            import shutil

            shutil.rmtree(project.parent, ignore_errors=True)

    def test_empty_retrieval_returns_empty_source(self) -> None:
        project = make_project()
        try:
            result = ask_twin(project, "zzzznothingmatches", GeneratorConfig(), urlopen_fn=fake_generator())
            self.assertEqual(result["source"], "empty")
            self.assertEqual(result["excerpts"], [])
        finally:
            import shutil

            shutil.rmtree(project.parent, ignore_errors=True)

    def test_excerpts_include_id_title_and_excerpt(self) -> None:
        project = make_project()
        try:
            result = ask_twin(project, "AICS", GeneratorConfig(), urlopen_fn=fake_generator())
            for e in result["excerpts"]:
                self.assertIn("id", e)
                self.assertIn("title", e)
                self.assertIn("excerpt", e)
                self.assertTrue(e["excerpt"])
        finally:
            import shutil

            shutil.rmtree(project.parent, ignore_errors=True)


class GenerateTests(unittest.TestCase):
    def test_generate_builds_prompt_and_parses_answer(self) -> None:
        captured: dict[str, object] = {}

        def urlopen_fn(request, timeout: float):
            captured["url"] = request.full_url
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(
                json.dumps({"choices": [{"message": {"role": "assistant", "content": "use the gateway"}}]}).encode()
            )

        answer = generate("question", [{"id": "ADR-0001", "title": "t", "excerpt": "e"}], GeneratorConfig(), urlopen_fn)
        self.assertEqual(answer, "use the gateway")
        self.assertEqual(captured["body"]["model"], "mock-coder")
        system = captured["body"]["messages"][0]["content"]
        self.assertIn("ONLY the provided excerpts", system)

    def test_generate_raises_on_bad_shape(self) -> None:
        def urlopen_fn(request, timeout: float):
            return FakeResponse(b'{"choices": []}')

        with self.assertRaises(ValueError):
            generate("q", [{"id": "a", "title": "t", "excerpt": "e"}], GeneratorConfig(), urlopen_fn)


class ResolveGeneratorTests(unittest.TestCase):
    def test_flags_beat_defaults(self) -> None:
        config = resolve_generator_config("http://x/v1/chat/completions", "my-model", "k")
        self.assertEqual(config.url, "http://x/v1/chat/completions")
        self.assertEqual(config.model, "my-model")
        self.assertEqual(config.api_key, "k")

    def test_defaults_to_local_gateway(self) -> None:
        config = resolve_generator_config()
        self.assertEqual(config.url, "http://127.0.0.1:8080/v1/chat/completions")
        self.assertEqual(config.model, "mock-coder")


class AskHttpTests(unittest.TestCase):
    def test_ask_endpoint_extractive_fallback(self) -> None:
        from http.server import ThreadingHTTPServer
        import threading
        from urllib.request import urlopen

        project = make_project()
        try:
            handler = make_handler(project, generator=GeneratorConfig(url="http://127.0.0.1:1", model="mock-coder"))
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://{server.server_address[0]}:{server.server_address[1]}"
            try:
                with urlopen(f"{base}/ask?q=AICS") as response:
                    body = json.loads(response.read().decode("utf-8"))
                self.assertEqual(body["source"], "extractive")
                self.assertTrue(body["excerpts"])
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)
        finally:
            import shutil

            shutil.rmtree(project.parent, ignore_errors=True)

    def test_ask_endpoint_empty_q_400(self) -> None:
        from http.server import ThreadingHTTPServer
        from urllib.error import HTTPError
        import threading
        from urllib.request import urlopen

        project = make_project()
        try:
            handler = make_handler(project)
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            base = f"http://{server.server_address[0]}:{server.server_address[1]}"
            try:
                with self.assertRaises(HTTPError) as ctx:
                    urlopen(f"{base}/ask")
                self.assertEqual(ctx.exception.code, 400)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)
        finally:
            import shutil

            shutil.rmtree(project.parent, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
