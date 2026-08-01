from __future__ import annotations

from collections.abc import Iterator
from io import BytesIO
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.config import ModelConfig, ProviderConfig
from agentforge_gateway.errors import UpstreamProviderError
from agentforge_gateway.providers import MockProvider, OllamaProvider, OpenRouterProvider


class ChatCompletionContract:
    def assert_chat_completion_contract(
        self,
        response: dict[str, object],
        *,
        expected_model: str,
    ) -> None:
        self.assertEqual(response["object"], "chat.completion")
        self.assertEqual(response["model"], expected_model)

        choices = response["choices"]
        self.assertIsInstance(choices, list)
        self.assertGreaterEqual(len(choices), 1)

        for choice in choices:
            self.assertIsInstance(choice, dict)
            self.assertIn("finish_reason", choice)

        message = choices[0]["message"]
        self.assertIsInstance(message, dict)
        self.assertEqual(message["role"], "assistant")
        self.assertIsInstance(message["content"], str)


class MockProviderContractTests(ChatCompletionContract, unittest.TestCase):
    def test_mock_provider_satisfies_chat_completion_contract(self) -> None:
        provider = MockProvider()

        response = provider.chat_completion(
            ModelConfig(name="mock-coder", provider="mock", provider_model="mock-coder-v1"),
            {"model": "mock-coder", "messages": [{"role": "user", "content": "Write a unit test."}]},
        )

        self.assert_chat_completion_contract(response, expected_model="mock-coder")
        self.assertIn("Write a unit test.", response["choices"][0]["message"]["content"])
        usage = response["usage"]
        self.assertIsInstance(usage, dict)
        self.assertGreaterEqual(usage["total_tokens"], usage["prompt_tokens"])


class OpenRouterProviderContractTests(ChatCompletionContract, unittest.TestCase):
    def test_openrouter_provider_satisfies_chat_completion_contract_with_injected_transport(self) -> None:
        calls: list[tuple[Request, float]] = []

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            calls.append((request, timeout))
            return FakeResponse(
                {
                    "id": "chatcmpl-contract",
                    "object": "chat.completion",
                    "created": 123,
                    "model": "qwen/qwen3-coder:free",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "Contract satisfied."},
                            "finish_reason": "stop",
                        }
                    ],
                }
            )

        provider = OpenRouterProvider(
            ProviderConfig(
                name="openrouter",
                type="openrouter",
                base_url="https://example.test/api/v1",
                api_key_env="OPENROUTER_API_KEY",
                timeout_seconds=7,
            ),
            urlopen_fn=fake_urlopen,
        )

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "contract-key"}):
            response = provider.chat_completion(
                ModelConfig(
                    name="openrouter-coder",
                    provider="openrouter",
                    provider_model="qwen/qwen3-coder:free",
                ),
                {
                    "model": "openrouter-coder",
                    "messages": [{"role": "user", "content": "Check the contract."}],
                },
            )

        self.assert_chat_completion_contract(response, expected_model="openrouter-coder")
        request, timeout = calls[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "https://example.test/api/v1/chat/completions")
        self.assertEqual(payload["model"], "qwen/qwen3-coder:free")
        self.assertEqual(timeout, 7)

    def test_openrouter_provider_translates_upstream_http_errors(self) -> None:
        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            raise HTTPError(
                url=request.full_url,
                code=429,
                msg="Too Many Requests",
                hdrs={},
                fp=BytesIO(b'{"error":{"message":"rate limited"}}'),
            )

        provider = OpenRouterProvider(
            ProviderConfig(
                name="openrouter",
                type="openrouter",
                base_url="https://example.test/api/v1",
                api_key_env="OPENROUTER_API_KEY",
            ),
            urlopen_fn=fake_urlopen,
        )

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "contract-key"}):
            with self.assertRaises(UpstreamProviderError) as ctx:
                provider.chat_completion(
                    ModelConfig(
                        name="openrouter-coder",
                        provider="openrouter",
                        provider_model="qwen/qwen3-coder:free",
                    ),
                    {"model": "openrouter-coder", "messages": [{"role": "user", "content": "Hi"}]},
                )

        self.assertIn("status 429", str(ctx.exception))
        self.assertIn("rate limited", str(ctx.exception))


class OllamaProviderContractTests(ChatCompletionContract, unittest.TestCase):
    def test_ollama_provider_satisfies_chat_completion_contract_with_injected_transport(self) -> None:
        calls: list[tuple[Request, float]] = []

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            calls.append((request, timeout))
            return FakeResponse(
                {
                    "id": "chatcmpl-contract",
                    "object": "chat.completion",
                    "created": 123,
                    "model": "llama3.2",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "Contract satisfied locally."},
                            "finish_reason": "stop",
                        }
                    ],
                    "usage": {"prompt_tokens": 5, "completion_tokens": 3, "total_tokens": 8},
                }
            )

        provider = OllamaProvider(
            ProviderConfig(
                name="ollama",
                type="ollama",
                base_url="http://127.0.0.1:11434/v1",
                timeout_seconds=7,
            ),
            urlopen_fn=fake_urlopen,
        )

        response = provider.chat_completion(
            ModelConfig(name="local-llama3", provider="ollama", provider_model="llama3.2"),
            {"model": "local-llama3", "messages": [{"role": "user", "content": "Check the contract."}]},
        )

        self.assert_chat_completion_contract(response, expected_model="local-llama3")
        request, timeout = calls[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/v1/chat/completions")
        self.assertEqual(payload["model"], "llama3.2")
        self.assertEqual(timeout, 7)

    def test_ollama_provider_sends_no_authorization_header(self) -> None:
        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            self.assertNotIn("Authorization", {k.lower(): v for k, v in request.header_items()})
            return FakeResponse(
                {
                    "id": "chatcmpl-local",
                    "object": "chat.completion",
                    "created": 123,
                    "model": "llama3.2",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "Keyless."},
                            "finish_reason": "stop",
                        }
                    ],
                }
            )

        provider = OllamaProvider(
            ProviderConfig(name="ollama", type="ollama"),
            urlopen_fn=fake_urlopen,
        )
        provider.chat_completion(
            ModelConfig(name="local-llama3", provider="ollama", provider_model="llama3.2"),
            {"model": "local-llama3", "messages": [{"role": "user", "content": "Hi"}]},
        )

    def test_ollama_provider_streams_chunks_and_stops_at_done(self) -> None:
        def fake_urlopen(request: Request, timeout: float) -> StreamingFakeResponse:
            self.assertEqual(json.loads(request.data.decode("utf-8"))["stream"], True)
            return StreamingFakeResponse(
                [
                    {"id": "chatcmpl-local", "object": "chat.completion.chunk", "created": 123, "model": "llama3.2", "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}]},
                    {"id": "chatcmpl-local", "object": "chat.completion.chunk", "created": 123, "model": "llama3.2", "choices": [{"index": 0, "delta": {"content": "Hello"}, "finish_reason": None}]},
                    {"id": "chatcmpl-local", "object": "chat.completion.chunk", "created": 123, "model": "llama3.2", "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]},
                ]
            )

        provider = OllamaProvider(
            ProviderConfig(name="ollama", type="ollama"),
            urlopen_fn=fake_urlopen,
        )
        chunks = list(
            provider.chat_completion_stream(
                ModelConfig(name="local-llama3", provider="ollama", provider_model="llama3.2"),
                {"model": "local-llama3", "messages": [{"role": "user", "content": "Say hello."}]},
            )
        )

        self.assertEqual(len(chunks), 3)
        self.assertEqual(chunks[1]["choices"][0]["delta"]["content"], "Hello")
        self.assertEqual(chunks[-1]["choices"][0]["finish_reason"], "stop")

    def test_ollama_provider_translates_upstream_http_errors(self) -> None:
        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            raise HTTPError(
                url=request.full_url,
                code=404,
                msg="Not Found",
                hdrs={},
                fp=BytesIO(b'{"error":{"message":"model not found"}}'),
            )

        provider = OllamaProvider(
            ProviderConfig(name="ollama", type="ollama"),
            urlopen_fn=fake_urlopen,
        )

        with self.assertRaises(UpstreamProviderError) as ctx:
            provider.chat_completion(
                ModelConfig(name="local-llama3", provider="ollama", provider_model="llama3.2"),
                {"model": "local-llama3", "messages": [{"role": "user", "content": "Hi"}]},
            )

        self.assertIn("status 404", str(ctx.exception))
        self.assertIn("model not found", str(ctx.exception))

    def test_ollama_provider_translates_connection_refused(self) -> None:
        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            raise URLError(ConnectionRefusedError(111, "Connection refused"))

        provider = OllamaProvider(
            ProviderConfig(name="ollama", type="ollama"),
            urlopen_fn=fake_urlopen,
        )

        with self.assertRaises(UpstreamProviderError) as ctx:
            provider.chat_completion(
                ModelConfig(name="local-llama3", provider="ollama", provider_model="llama3.2"),
                {"model": "local-llama3", "messages": [{"role": "user", "content": "Hi"}]},
            )

        self.assertIn("provider 'ollama'", str(ctx.exception))
        self.assertIn("Connection refused", str(ctx.exception))


class FakeResponse:
    def __init__(self, body: dict[str, object]) -> None:
        self.body = body

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.body).encode("utf-8")


class StreamingFakeResponse:
    def __init__(self, chunks: list[dict[str, object]]) -> None:
        self._chunks = chunks

    def __enter__(self) -> StreamingFakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def __iter__(self) -> Iterator[bytes]:
        for chunk in self._chunks:
            yield f"data: {json.dumps(chunk)}\n\n".encode("utf-8")
        yield b"data: [DONE]\n\n"

    def read(self) -> bytes:
        return b""


if __name__ == "__main__":
    unittest.main()
