from __future__ import annotations

from http.server import ThreadingHTTPServer
import json
import os
import sys
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.app import GatewayApp, create_handler
from agentforge_gateway.config import DEFAULT_CONFIG, ModelConfig, ProviderConfig, parse_config
from agentforge_gateway.errors import ProviderConfigurationError
from agentforge_gateway.providers import OpenRouterProvider


class GatewayAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = GatewayApp(DEFAULT_CONFIG)

    def test_health(self) -> None:
        self.assertEqual(self.app.health()["status"], "ok")

    def test_models(self) -> None:
        models = self.app.models()
        self.assertEqual(models["object"], "list")
        self.assertEqual(models["data"][0]["id"], "mock-coder")

    def test_chat_completion(self) -> None:
        response = self.app.chat_completions(
            {
                "model": "mock-coder",
                "messages": [{"role": "user", "content": "Hello"}],
            }
        )

        self.assertEqual(response["object"], "chat.completion")
        self.assertEqual(response["model"], "mock-coder")
        self.assertIn("Mock response", response["choices"][0]["message"]["content"])

    def test_unknown_model(self) -> None:
        with self.assertRaises(Exception) as ctx:
            self.app.chat_completions(
                {
                    "model": "missing",
                    "messages": [{"role": "user", "content": "Hello"}],
                }
            )

        self.assertIn("unknown model", str(ctx.exception))

    def test_malformed_request(self) -> None:
        with self.assertRaises(Exception) as ctx:
            self.app.chat_completions({"model": "mock-coder"})

        self.assertIn("messages", str(ctx.exception))

    def test_streaming_is_rejected_until_supported(self) -> None:
        with self.assertRaises(Exception) as ctx:
            self.app.chat_completions(
                {
                    "model": "mock-coder",
                    "stream": True,
                    "messages": [{"role": "user", "content": "Hello"}],
                }
            )

        self.assertIn("streaming", str(ctx.exception))


class ConfigTests(unittest.TestCase):
    def test_parse_openrouter_provider_config(self) -> None:
        config = parse_config(
            {
                "models": {
                    "openrouter-coder": {
                        "provider": "openrouter",
                        "provider_model": "qwen/qwen3-coder:free",
                    }
                },
                "providers": {
                    "openrouter": {
                        "type": "openrouter",
                        "base_url": "https://openrouter.ai/api/v1",
                        "api_key_env": "OPENROUTER_API_KEY",
                        "timeout_seconds": 10,
                    }
                },
            }
        )

        self.assertEqual(config.models["openrouter-coder"].provider, "openrouter")
        self.assertEqual(config.providers["openrouter"].type, "openrouter")
        self.assertEqual(config.providers["openrouter"].timeout_seconds, 10)

    def test_parse_config_rejects_unknown_provider_reference(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            parse_config(
                {
                    "models": {
                        "openrouter-coder": {
                            "provider": "openrouter",
                            "provider_model": "qwen/qwen3-coder:free",
                        }
                    }
                }
            )

        self.assertIn("unknown provider", str(ctx.exception))


class OpenRouterProviderTests(unittest.TestCase):
    def test_chat_completion_posts_openai_compatible_payload(self) -> None:
        calls: list[tuple[Request, float]] = []

        def fake_urlopen(request: Request, timeout: float) -> FakeResponse:
            calls.append((request, timeout))
            return FakeResponse(
                {
                    "id": "chatcmpl-test",
                    "object": "chat.completion",
                    "created": 123,
                    "model": "qwen/qwen3-coder:free",
                    "choices": [
                        {
                            "index": 0,
                            "message": {"role": "assistant", "content": "Done"},
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
                timeout_seconds=12,
                headers={"HTTP-Referer": "https://github.com/AgentForgiT/agentforge"},
            ),
            urlopen_fn=fake_urlopen,
        )

        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key"}):
            response = provider.chat_completion(
                ModelConfig(
                    name="openrouter-coder",
                    provider="openrouter",
                    provider_model="qwen/qwen3-coder:free",
                ),
                {
                    "model": "openrouter-coder",
                    "messages": [{"role": "user", "content": "Write a test."}],
                    "temperature": 0.2,
                },
            )

        request, timeout = calls[0]
        payload = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request.full_url, "https://example.test/api/v1/chat/completions")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(request.get_header("Content-type"), "application/json")
        self.assertEqual(request.get_header("Http-referer"), "https://github.com/AgentForgiT/agentforge")
        self.assertEqual(payload["model"], "qwen/qwen3-coder:free")
        self.assertEqual(payload["temperature"], 0.2)
        self.assertEqual(timeout, 12)
        self.assertEqual(response["model"], "openrouter-coder")

    def test_chat_completion_requires_api_key(self) -> None:
        provider = OpenRouterProvider(ProviderConfig(name="openrouter", type="openrouter"))

        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ProviderConfigurationError) as ctx:
                provider.chat_completion(
                    ModelConfig(
                        name="openrouter-coder",
                        provider="openrouter",
                        provider_model="qwen/qwen3-coder:free",
                    ),
                    {"model": "openrouter-coder", "messages": [{"role": "user", "content": "Hi"}]},
                )

        self.assertIn("OPENROUTER_API_KEY", str(ctx.exception))


class FakeResponse:
    def __init__(self, body: dict[str, object]) -> None:
        self.body = body

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.body).encode("utf-8")


class GatewayHttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        app = GatewayApp(DEFAULT_CONFIG)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(app))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        host, port = cls.server.server_address
        cls.base_url = f"http://{host}:{port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def test_health_endpoint(self) -> None:
        body = self.get_json("/health")
        self.assertEqual(body["status"], "ok")

    def test_models_endpoint(self) -> None:
        body = self.get_json("/v1/models")
        self.assertEqual(body["data"][0]["id"], "mock-coder")

    def test_chat_completions_endpoint(self) -> None:
        body = self.post_json(
            "/v1/chat/completions",
            {
                "model": "mock-coder",
                "messages": [{"role": "user", "content": "Write a test."}],
            },
        )
        self.assertEqual(body["choices"][0]["message"]["role"], "assistant")

    def test_unknown_model_endpoint(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self.post_json(
                "/v1/chat/completions",
                {
                    "model": "missing",
                    "messages": [{"role": "user", "content": "Hello"}],
                },
            )

        self.assertEqual(ctx.exception.code, 404)

    def get_json(self, path: str) -> dict[str, object]:
        with urlopen(f"{self.base_url}{path}") as response:
            return json.loads(response.read().decode("utf-8"))

    def post_json(self, path: str, body: dict[str, object]) -> dict[str, object]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
