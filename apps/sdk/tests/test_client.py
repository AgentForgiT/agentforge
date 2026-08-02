from __future__ import annotations

import io
import json
import sys
import unittest
from pathlib import Path
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_sdk import AgentForgeClient, AgentForgeError


class FakeResponse:
    def __init__(self, payload: bytes, status: int = 200) -> None:
        self._payload = payload
        self.status = status

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


class FakeStreamResponse:
    def __init__(self, lines: list[str], status: int = 200) -> None:
        self._buffer = io.BytesIO("".join(lines).encode("utf-8"))
        self.status = status

    def __iter__(self):
        return self

    def __next__(self) -> bytes:
        line = self._buffer.readline()
        if not line:
            raise StopIteration
        return line

    def __enter__(self) -> "FakeStreamResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


def fake_openai_response() -> bytes:
    return json.dumps(
        {
            "id": "chatcmpl-1",
            "object": "chat.completion",
            "model": "mock-coder",
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "Hello"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
        }
    ).encode()


def fake_anthropic_response() -> bytes:
    return json.dumps(
        {
            "id": "msg_1",
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": "Bonjour"}],
            "model": "claude-sonnet-4-5",
            "stop_reason": "end_turn",
            "usage": {"input_tokens": 2, "output_tokens": 1},
        }
    ).encode()


class ClientHttpTests(unittest.TestCase):
    def test_health_hits_correct_path(self) -> None:
        captured: dict[str, object] = {}

        def fake(request, timeout: float) -> FakeResponse:
            captured["url"] = request.full_url
            return FakeResponse(b'{"status": "ok"}')

        client = AgentForgeClient("http://127.0.0.1:8080", urlopen_fn=fake)
        result = client.health()
        self.assertEqual(result["status"], "ok")
        self.assertEqual(captured["url"], "http://127.0.0.1:8080/health")

    def test_models(self) -> None:
        def fake(request, timeout: float) -> FakeResponse:
            return FakeResponse(b'{"object": "list", "data": [{"id": "mock-coder"}]}')

        client = AgentForgeClient("http://x", urlopen_fn=fake)
        self.assertEqual(client.models()["data"][0]["id"], "mock-coder")

    def test_chat_completions_payload_and_path(self) -> None:
        captured: dict[str, object] = {}

        def fake(request, timeout: float) -> FakeResponse:
            captured["url"] = request.full_url
            captured["body"] = json.loads(request.data.decode("utf-8"))
            captured["headers"] = dict(request.headers)
            return FakeResponse(fake_openai_response())

        client = AgentForgeClient("http://127.0.0.1:8080", urlopen_fn=fake)
        result = client.chat_completions("mock-coder", [{"role": "user", "content": "Hi"}])

        self.assertEqual(captured["url"], "http://127.0.0.1:8080/v1/chat/completions")
        self.assertEqual(captured["body"]["model"], "mock-coder")
        self.assertEqual(captured["body"]["stream"], False)
        self.assertEqual(result["choices"][0]["message"]["content"], "Hello")

    def test_anthropic_messages_payload_and_path(self) -> None:
        captured: dict[str, object] = {}

        def fake(request, timeout: float) -> FakeResponse:
            captured["url"] = request.full_url
            captured["body"] = json.loads(request.data.decode("utf-8"))
            return FakeResponse(fake_anthropic_response())

        client = AgentForgeClient("http://127.0.0.1:8080", urlopen_fn=fake)
        result = client.anthropic_messages("claude-sonnet-4-5", [{"role": "user", "content": "Hi"}])

        self.assertEqual(captured["url"], "http://127.0.0.1:8080/v1/messages")
        self.assertEqual(captured["body"]["max_tokens"], 4096)
        self.assertEqual(result["type"], "message")
        self.assertEqual(result["content"][0]["text"], "Bonjour")

    def test_api_key_sends_bearer_header(self) -> None:
        captured: dict[str, object] = {}

        def fake(request, timeout: float) -> FakeResponse:
            captured["headers"] = {k.lower(): v for k, v in request.headers.items()}
            return FakeResponse(fake_openai_response())

        client = AgentForgeClient("http://x", api_key="sekrit", urlopen_fn=fake)
        client.health()
        self.assertEqual(captured["headers"]["authorization"], "Bearer sekrit")

    def test_no_api_key_no_auth_header(self) -> None:
        captured: dict[str, object] = {}

        def fake(request, timeout: float) -> FakeResponse:
            captured["headers"] = {k.lower(): v for k, v in request.headers.items()}
            return FakeResponse(fake_openai_response())

        client = AgentForgeClient("http://x", urlopen_fn=fake)
        client.health()
        self.assertNotIn("authorization", captured["headers"])

    def test_error_envelope_raises(self) -> None:
        def fake(request, timeout: float) -> FakeResponse:
            raise HTTPError(
                "http://x/v1/chat/completions",
                401,
                "Unauthorized",
                None,
                io.BytesIO(b'{"error": {"message": "unauthorized", "type": "unauthorized"}}'),
            )

        client = AgentForgeClient("http://x", urlopen_fn=fake)
        with self.assertRaises(AgentForgeError) as ctx:
            client.chat_completions("mock-coder", [{"role": "user", "content": "Hi"}])
        self.assertEqual(ctx.exception.status, 401)
        self.assertEqual(ctx.exception.body["error"]["type"], "unauthorized")


class ClientStreamTests(unittest.TestCase):
    def test_openai_stream_parses_chunks(self) -> None:
        lines = [
            'data: {"id":"1","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}\n\n',
            'data: {"id":"1","object":"chat.completion.chunk","choices":[{"index":0,"delta":{"content":"Hello"},"finish_reason":null}]}\n\n',
            "data: [DONE]\n\n",
        ]

        def fake(request, timeout: float) -> FakeStreamResponse:
            return FakeStreamResponse(lines)

        client = AgentForgeClient("http://x", urlopen_fn=fake)
        chunks = list(client.chat_completions("mock-coder", [{"role": "user", "content": "Hi"}], stream=True))
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[1]["choices"][0]["delta"]["content"], "Hello")

    def test_anthropic_stream_parses_events(self) -> None:
        lines = [
            'event: message_start\ndata: {"type":"message_start","message":{"id":"m1"}}\n\n',
            'event: content_block_delta\ndata: {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":"Hi"}}\n\n',
            'event: message_stop\ndata: {"type":"message_stop"}\n\n',
        ]

        def fake(request, timeout: float) -> FakeStreamResponse:
            return FakeStreamResponse(lines)

        client = AgentForgeClient("http://x", urlopen_fn=fake)
        events = list(client.anthropic_messages("claude-sonnet-4-5", [{"role": "user", "content": "Hi"}], stream=True))
        names = [name for name, _ in events]
        self.assertEqual(names, ["message_start", "content_block_delta", "message_stop"])
        delta = [data for name, data in events if name == "content_block_delta"][0]
        self.assertEqual(delta["delta"]["text"], "Hi")


if __name__ == "__main__":
    unittest.main()
