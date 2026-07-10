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
from agentforge_gateway.config import DEFAULT_CONFIG, ModelConfig, ProviderConfig
from agentforge_gateway.errors import ProviderConfigurationError, UpstreamProviderError
from agentforge_gateway.providers import MockProvider, OpenRouterProvider, build_provider, supported_provider_types


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

    def test_chat_completion_preserves_request_body_for_provider(self) -> None:
        provider = RecordingProvider()
        app = GatewayApp(DEFAULT_CONFIG, providers={"mock": provider})
        body = {
            "model": "mock-coder",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.2,
        }

        app.chat_completions(body)

        self.assertIs(provider.calls[0], body)
        self.assertEqual(provider.calls[0]["temperature"], 0.2)

    def test_chat_completion_normalizes_provider_model_alias(self) -> None:
        provider = UpstreamModelProvider()
        app = GatewayApp(DEFAULT_CONFIG, providers={"mock": provider})

        response = app.chat_completions(
            {
                "model": "mock-coder",
                "messages": [{"role": "user", "content": "Hello"}],
            }
        )

        self.assertEqual(response["model"], "mock-coder")

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


class ProviderFactoryTests(unittest.TestCase):
    def test_build_provider_returns_mock_provider(self) -> None:
        provider = build_provider(ProviderConfig(name="mock", type="mock"))

        self.assertIsInstance(provider, MockProvider)

    def test_build_provider_returns_openrouter_provider(self) -> None:
        provider = build_provider(ProviderConfig(name="openrouter", type="openrouter"))

        self.assertIsInstance(provider, OpenRouterProvider)

    def test_build_provider_rejects_unsupported_provider_type(self) -> None:
        with self.assertRaises(ProviderConfigurationError) as ctx:
            build_provider(ProviderConfig(name="custom", type="custom"))

        self.assertIn("unsupported provider type: custom", str(ctx.exception))

    def test_supported_provider_types_are_explicit(self) -> None:
        self.assertEqual(supported_provider_types(), ("mock", "openrouter"))


class MockProviderTests(unittest.TestCase):
    def test_chat_completion_returns_openai_compatible_shape(self) -> None:
        provider = MockProvider()

        response = provider.chat_completion(
            ModelConfig(
                name="mock-coder",
                provider="mock",
                provider_model="mock-coder-v1",
            ),
            {"messages": [{"role": "user", "content": "Hello"}]},
        )

        self.assertEqual(response["object"], "chat.completion")
        self.assertEqual(response["model"], "mock-coder")
        self.assertIn("usage", response)
        self.assertIn("Mock response from mock-coder: Hello", response["choices"][0]["message"]["content"])


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


class RecordingProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def chat_completion(self, model: ModelConfig, body: dict[str, object]) -> dict[str, object]:
        self.calls.append(body)
        return {
            "id": "chatcmpl-recording",
            "object": "chat.completion",
            "created": 123,
            "model": model.name,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Recorded"},
                    "finish_reason": "stop",
                }
            ],
        }


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
        body = self.error_json(ctx.exception)
        self.assertEqual(body["error"]["type"], "model_not_found")
        self.assertIn("unknown model", body["error"]["message"])

    def test_unknown_route_returns_error_envelope(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self.get_json("/missing")

        self.assertEqual(ctx.exception.code, 404)
        body = self.error_json(ctx.exception)
        self.assertEqual(body["error"], {"message": "not found", "type": "not_found"})

    def test_invalid_json_returns_error_envelope(self) -> None:
        request = Request(
            f"{self.base_url}/v1/chat/completions",
            data=b"{",
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self.assertRaises(HTTPError) as ctx:
            urlopen(request)

        self.assertEqual(ctx.exception.code, 400)
        body = self.error_json(ctx.exception)
        self.assertEqual(body["error"], {"message": "invalid JSON body", "type": "bad_request"})

    def test_non_object_body_returns_error_envelope(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self.post_raw("/v1/chat/completions", [])

        self.assertEqual(ctx.exception.code, 400)
        body = self.error_json(ctx.exception)
        self.assertEqual(body["error"]["type"], "bad_request")
        self.assertIn("JSON object", body["error"]["message"])

    def test_request_validation_error_returns_error_envelope(self) -> None:
        with self.assertRaises(HTTPError) as ctx:
            self.post_json("/v1/chat/completions", {"model": "mock-coder"})

        self.assertEqual(ctx.exception.code, 400)
        body = self.error_json(ctx.exception)
        self.assertEqual(body["error"]["type"], "bad_request")
        self.assertIn("messages", body["error"]["message"])

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

    def post_raw(self, path: str, body: object) -> dict[str, object]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))

    def error_json(self, error: HTTPError) -> dict[str, object]:
        return json.loads(error.read().decode("utf-8"))


class ProviderErrorHttpTests(unittest.TestCase):
    def test_provider_configuration_error_returns_error_envelope(self) -> None:
        app = GatewayApp(DEFAULT_CONFIG, providers={"mock": RaisingProvider(ProviderConfigurationError("missing key"))})
        server = LocalServer(app)
        try:
            with self.assertRaises(HTTPError) as ctx:
                server.post_json(
                    "/v1/chat/completions",
                    {"model": "mock-coder", "messages": [{"role": "user", "content": "Hello"}]},
                )
        finally:
            server.close()

        self.assertEqual(ctx.exception.code, 500)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertEqual(body["error"], {"message": "missing key", "type": "provider_configuration_error"})

    def test_upstream_provider_error_returns_error_envelope(self) -> None:
        app = GatewayApp(DEFAULT_CONFIG, providers={"mock": RaisingProvider(UpstreamProviderError("upstream down"))})
        server = LocalServer(app)
        try:
            with self.assertRaises(HTTPError) as ctx:
                server.post_json(
                    "/v1/chat/completions",
                    {"model": "mock-coder", "messages": [{"role": "user", "content": "Hello"}]},
                )
        finally:
            server.close()

        self.assertEqual(ctx.exception.code, 502)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertEqual(body["error"], {"message": "upstream down", "type": "upstream_provider_error"})

    def test_malformed_provider_success_returns_upstream_error_envelope(self) -> None:
        app = GatewayApp(DEFAULT_CONFIG, providers={"mock": MalformedSuccessProvider()})
        server = LocalServer(app)
        try:
            with self.assertRaises(HTTPError) as ctx:
                server.post_json(
                    "/v1/chat/completions",
                    {"model": "mock-coder", "messages": [{"role": "user", "content": "Hello"}]},
                )
        finally:
            server.close()

        self.assertEqual(ctx.exception.code, 502)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertEqual(body["error"]["type"], "upstream_provider_error")
        self.assertIn("choices", body["error"]["message"])


class RaisingProvider:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def chat_completion(self, model: ModelConfig, body: dict[str, object]) -> dict[str, object]:
        raise self.error


class UpstreamModelProvider:
    def chat_completion(self, model: ModelConfig, body: dict[str, object]) -> dict[str, object]:
        return {
            "id": "chatcmpl-upstream",
            "object": "chat.completion",
            "created": 123,
            "model": "upstream-model",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Normalized"},
                    "finish_reason": "stop",
                }
            ],
        }


class MalformedSuccessProvider:
    def chat_completion(self, model: ModelConfig, body: dict[str, object]) -> dict[str, object]:
        return {
            "id": "chatcmpl-malformed",
            "object": "chat.completion",
            "model": model.name,
            "choices": [],
        }


class LocalServer:
    def __init__(self, app: GatewayApp) -> None:
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(app))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        host, port = self.server.server_address
        self.base_url = f"http://{host}:{port}"

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

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
