from __future__ import annotations

import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "apps" / "cli" / "src"))

from agentforge_cli.scaffolding import init_context
from agentforge_cli.twin import build_twin
from agentforge_cli.twin_service import make_handler, search_twin, serve_twin


def start_server(root: Path, port: int):
    from http.server import ThreadingHTTPServer
    import threading

    handler = make_handler(root)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{port}"


class SearchTwinTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "twin-search"
        init_context(self.project)
        # add a real ADR so ADR-title search has corpus
        adr = self.project / ".agentforge" / "adrs" / "0001-use-aics.md"
        adr.write_text("# Use the AICS Context Standard\n\nContext\nDecision\nConsequences\n", encoding="utf-8")
        build_twin(self.project)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_search_finds_adr_by_title_term(self) -> None:
        results = search_twin(self.project, "AICS")
        self.assertTrue(results, "expected hits for 'AICS'")
        types = {r["type"] for r in results}
        self.assertIn("adr", types)

    def test_search_finds_decision_by_title(self) -> None:
        # scaffold decision register has ADR-0001 "Adopt AICS context"
        results = search_twin(self.project, "context")
        self.assertTrue(results)
        self.assertIn("score", results[0])

    def test_search_ranks_higher_term_overlap_first(self) -> None:
        results = search_twin(self.project, "AICS context")
        self.assertTrue(results)
        scores = [r["score"] for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_empty_query_returns_empty(self) -> None:
        self.assertEqual(search_twin(self.project, ""), [])


class ServeTwinHttpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.project = Path(self.tmp.name) / "twin-http"
        init_context(self.project)
        build_twin(self.project)
        self.server, self.base = start_server(self.project, 18737)

    def tearDown(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def test_twin_json_endpoint(self) -> None:
        with urlopen(f"{self.base}/twin.json") as response:
            body = json.loads(response.read().decode("utf-8"))
        self.assertEqual(body["schema_version"], "0.1")
        self.assertEqual(body["profile"]["aics_level"], 3)

    def test_search_endpoint(self) -> None:
        with urlopen(f"{self.base}/search?q=AICS") as response:
            body = json.loads(response.read().decode("utf-8"))
        self.assertEqual(body["query"], "AICS")
        self.assertTrue(body["results"])

    def test_search_empty_query_400(self) -> None:
        from urllib.error import HTTPError

        with self.assertRaises(HTTPError) as ctx:
            urlopen(f"{self.base}/search")
        self.assertEqual(ctx.exception.code, 400)

    def test_index_html(self) -> None:
        with urlopen(f"{self.base}/") as response:
            html = response.read().decode("utf-8")
        self.assertIn("AgentForge Twin", html)
        self.assertIn("twin.json", html)

    def test_unknown_path_404(self) -> None:
        from urllib.error import HTTPError

        with self.assertRaises(HTTPError) as ctx:
            urlopen(f"{self.base}/nope")
        self.assertEqual(ctx.exception.code, 404)


class ServeTwinMissingProfileTests(unittest.TestCase):
    def test_twin_json_404_hints_build_twin(self) -> None:
        from urllib.error import HTTPError

        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "no-twin"
            init_context(project)  # no build_twin
            server, base = start_server(project, 18738)
            try:
                with self.assertRaises(HTTPError) as ctx:
                    urlopen(f"{base}/twin.json")
                body = json.loads(ctx.exception.read().decode("utf-8"))
                self.assertIn("build-twin", body["error"])
            finally:
                server.shutdown()
                server.server_close()


class ServeTwinReadOnlyTests(unittest.TestCase):
    def test_aics_files_untouched_after_serving(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "ro"
            init_context(project)
            build_twin(project)
            before = (project / ".agentforge" / "constitution.md").read_bytes()
            server, base = start_server(project, 18739)
            try:
                urlopen(f"{base}/twin.json").read()
                urlopen(f"{base}/search?q=AICS").read()
                urlopen(f"{base}/").read()
            finally:
                server.shutdown()
                server.server_close()
            after = (project / ".agentforge" / "constitution.md").read_bytes()
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
