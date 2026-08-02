from __future__ import annotations

import json
import os
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.app import GatewayApp, create_handler
from agentforge_gateway.config import DEFAULT_CONFIG, GatewayConfig, parse_config
from agentforge_gateway.errors import unauthorized_response, rate_limited_response
from agentforge_gateway.ratelimit import TokenBucketRateLimiter


def authed_config(api_key_env: str = "AGENTFORGE_API_KEY", rate_limit_rpm: int | None = None) -> GatewayConfig:
    return GatewayConfig(
        host="127.0.0.1",
        port=8080,
        api_key_env=api_key_env,
        rate_limit_rpm=rate_limit_rpm,
        models=DEFAULT_CONFIG.models,
        providers=DEFAULT_CONFIG.providers,
    )


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

    def post(self, path: str, body: dict[str, object], headers: dict[str, str] | None = None) -> tuple[int, dict[str, object]]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", **(headers or {})},
            method="POST",
        )
        try:
            with urlopen(request) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            return exc.code, json.loads(exc.read().decode("utf-8"))

    def get(self, path: str, headers: dict[str, str] | None = None) -> tuple[int, dict[str, object] | None]:
        request = Request(f"{self.base_url}{path}", headers=headers or {})
        try:
            with urlopen(request) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read()
            return exc.code, json.loads(body.decode("utf-8")) if body else None


class AuthConfigTests(unittest.TestCase):
    def test_api_key_env_defaults_to_none(self) -> None:
        config = parse_config({"models": {"mock-coder": {"provider": "mock", "provider_model": "v1"}}})
        self.assertIsNone(config.api_key_env)
        self.assertIsNone(config.rate_limit_rpm)

    def test_api_key_env_parses(self) -> None:
        config = parse_config(
            {"server": {"api_key_env": "MY_KEY"}, "models": {"mock-coder": {"provider": "mock", "provider_model": "v1"}}}
        )
        self.assertEqual(config.api_key_env, "MY_KEY")

    def test_api_key_env_rejects_empty(self) -> None:
        with self.assertRaises(ValueError):
            parse_config({"server": {"api_key_env": "  "}, "models": {}})

    def test_rate_limit_rpm_parses(self) -> None:
        config = parse_config(
            {"server": {"rate_limit_rpm": 60}, "models": {"mock-coder": {"provider": "mock", "provider_model": "v1"}}}
        )
        self.assertEqual(config.rate_limit_rpm, 60)

    def test_rate_limit_rpm_rejects_non_positive(self) -> None:
        with self.assertRaises(ValueError):
            parse_config({"server": {"rate_limit_rpm": 0}, "models": {}})

    def test_missing_env_key_raises_at_startup(self) -> None:
        os.environ.pop("AGENTFORGE_API_KEY_TEST", None)
        with self.assertRaises(RuntimeError):
            GatewayApp(authed_config(api_key_env="AGENTFORGE_API_KEY_TEST"))


class AuthHttpTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["AGENTFORGE_API_KEY"] = "sekrit-123"
        self.server = LocalServer(GatewayApp(authed_config()))
        self.addCleanup(self.server.close)

    def tearDown(self) -> None:
        os.environ.pop("AGENTFORGE_API_KEY", None)

    def test_missing_key_returns_401(self) -> None:
        status, body = self.server.post("/v1/chat/completions", {"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]})
        self.assertEqual(status, 401)
        self.assertEqual(body["error"]["type"], "unauthorized")

    def test_wrong_key_returns_401(self) -> None:
        status, _ = self.server.post(
            "/v1/chat/completions",
            {"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]},
            headers={"Authorization": "Bearer wrong"},
        )
        self.assertEqual(status, 401)

    def test_bearer_key_succeeds(self) -> None:
        status, body = self.server.post(
            "/v1/chat/completions",
            {"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]},
            headers={"Authorization": "Bearer sekrit-123"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["model"], "mock-coder")

    def test_x_api_key_header_succeeds(self) -> None:
        status, body = self.server.post(
            "/v1/chat/completions",
            {"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]},
            headers={"x-api-key": "sekrit-123"},
        )
        self.assertEqual(status, 200)

    def test_anthropic_surface_requires_auth(self) -> None:
        status, body = self.server.post(
            "/v1/messages",
            {"model": "mock-coder", "max_tokens": 10, "messages": [{"role": "user", "content": "Hi"}]},
        )
        self.assertEqual(status, 401)
        self.assertEqual(body["type"], "error")

    def test_health_exempt_from_auth(self) -> None:
        status, body = self.server.get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_models_requires_auth(self) -> None:
        status, _ = self.server.get("/v1/models")
        self.assertEqual(status, 401)


class AuthCorsTests(unittest.TestCase):
    def test_401_carries_cors_headers(self) -> None:
        os.environ["AGENTFORGE_API_KEY"] = "k"
        config = GatewayConfig(
            host="127.0.0.1", port=8080, api_key_env="AGENTFORGE_API_KEY",
            cors_origin="https://example.com",
            models=DEFAULT_CONFIG.models, providers=DEFAULT_CONFIG.providers,
        )
        server = LocalServer(GatewayApp(config))
        try:
            request = Request(
                f"{server.base_url}/v1/chat/completions",
                data=json.dumps({"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as ctx:
                urlopen(request)
            self.assertEqual(ctx.exception.code, 401)
            self.assertEqual(ctx.exception.headers.get("Access-Control-Allow-Origin"), "https://example.com")
        finally:
            server.close()
            os.environ.pop("AGENTFORGE_API_KEY", None)


class RateLimitTests(unittest.TestCase):
    def test_bucket_blocks_after_capacity(self) -> None:
        limiter = TokenBucketRateLimiter(requests_per_minute=2)
        self.assertTrue(limiter.allow("a"))
        self.assertTrue(limiter.allow("a"))
        self.assertFalse(limiter.allow("a"))
        # different key unaffected
        self.assertTrue(limiter.allow("b"))

    def test_bucket_refills_with_time(self) -> None:
        now = [0.0]

        def fake_now() -> float:
            return now[0]

        limiter = TokenBucketRateLimiter(requests_per_minute=60, now_fn=fake_now)
        for _ in range(60):
            self.assertTrue(limiter.allow("a"))
        self.assertFalse(limiter.allow("a"))
        now[0] += 1.0  # one second -> 1 token
        self.assertTrue(limiter.allow("a"))

    def test_http_429_after_limit(self) -> None:
        server = LocalServer(GatewayApp(authed_config(api_key_env=None, rate_limit_rpm=2)))
        try:
            body = {"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]}
            status1, _ = server.post("/v1/chat/completions", body)
            status2, _ = server.post("/v1/chat/completions", body)
            status3, body3 = server.post("/v1/chat/completions", body)
            self.assertEqual(status1, 200)
            self.assertEqual(status2, 200)
            self.assertEqual(status3, 429)
            self.assertEqual(body3["error"]["type"], "rate_limited")
        finally:
            server.close()

    def test_429_has_retry_after(self) -> None:
        server = LocalServer(GatewayApp(authed_config(api_key_env=None, rate_limit_rpm=1)))
        try:
            body = {"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]}
            server.post("/v1/chat/completions", body)
            request = Request(
                f"{server.base_url}/v1/chat/completions",
                data=json.dumps(body).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as ctx:
                urlopen(request)
            self.assertEqual(ctx.exception.code, 429)
            self.assertEqual(ctx.exception.headers.get("Retry-After"), "60")
        finally:
            server.close()

    def test_health_exempt_from_rate_limit(self) -> None:
        server = LocalServer(GatewayApp(authed_config(api_key_env=None, rate_limit_rpm=1)))
        try:
            body = {"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]}
            server.post("/v1/chat/completions", body)
            for _ in range(5):
                status, _ = server.get("/health")
                self.assertEqual(status, 200)
        finally:
            server.close()

    def test_keyed_by_key_when_auth_on(self) -> None:
        os.environ["AGENTFORGE_API_KEY"] = "k"
        server = LocalServer(GatewayApp(authed_config(rate_limit_rpm=2)))
        try:
            body = {"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]}
            # key A exhausts its own bucket
            server.post("/v1/chat/completions", body, headers={"x-api-key": "k"})
            server.post("/v1/chat/completions", body, headers={"x-api-key": "k"})
            status, _ = server.post("/v1/chat/completions", body, headers={"x-api-key": "k"})
            self.assertEqual(status, 429)
        finally:
            server.close()
            os.environ.pop("AGENTFORGE_API_KEY", None)


class RateLimitResponseShapeTests(unittest.TestCase):
    def test_error_shapes(self) -> None:
        self.assertEqual(unauthorized_response()["error"]["type"], "unauthorized")
        self.assertEqual(rate_limited_response()["error"]["type"], "rate_limited")


if __name__ == "__main__":
    unittest.main()
