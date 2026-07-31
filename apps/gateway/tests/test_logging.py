from __future__ import annotations

from http.server import ThreadingHTTPServer
import json
import logging
from pathlib import Path
import sys
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.app import GatewayApp, create_handler
from agentforge_gateway.config import DEFAULT_CONFIG, ModelConfig
from agentforge_gateway.errors import UpstreamProviderError
from agentforge_gateway.logger import GATEWAY_LOGGER_NAME, get_logger


class GatewayLoggingTests(unittest.TestCase):
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

    def test_access_record_for_health_endpoint(self) -> None:
        with self.assertLogs(GATEWAY_LOGGER_NAME, level="INFO") as captured:
            self.get("/health")

        self.assertTrue(any("method=GET path=/health status=200 duration_ms=" in record for record in captured.output))

    def test_access_record_for_chat_completions(self) -> None:
        with self.assertLogs(GATEWAY_LOGGER_NAME, level="INFO") as captured:
            self.post(
                "/v1/chat/completions",
                {"model": "mock-coder", "messages": [{"role": "user", "content": "Hello"}]},
            )

        self.assertTrue(
            any(
                "method=POST path=/v1/chat/completions status=200 duration_ms=" in record
                for record in captured.output
            )
        )

    def test_access_record_for_unknown_route(self) -> None:
        with self.assertLogs(GATEWAY_LOGGER_NAME, level="INFO") as captured:
            with self.assertRaises(HTTPError):
                self.get("/missing")

        self.assertTrue(any("method=GET path=/missing status=404 duration_ms=" in record for record in captured.output))

    def test_chat_completion_context_record_non_streaming(self) -> None:
        with self.assertLogs(GATEWAY_LOGGER_NAME, level="INFO") as captured:
            self.post(
                "/v1/chat/completions",
                {"model": "mock-coder", "messages": [{"role": "user", "content": "Hello"}]},
            )

        self.assertTrue(any("chat_completion model=mock-coder stream=false" in record for record in captured.output))

    def test_chat_completion_context_record_streaming(self) -> None:
        with self.assertLogs(GATEWAY_LOGGER_NAME, level="INFO") as captured:
            self.post(
                "/v1/chat/completions",
                {"model": "mock-coder", "stream": True, "messages": [{"role": "user", "content": "Hello"}]},
            )

        self.assertTrue(any("chat_completion model=mock-coder stream=true" in record for record in captured.output))

    def test_invalid_requests_do_not_log_chat_context(self) -> None:
        with self.assertLogs(GATEWAY_LOGGER_NAME, level="INFO") as captured:
            with self.assertRaises(HTTPError):
                self.post("/v1/chat/completions", {"model": "mock-coder"})

        self.assertFalse(any("chat_completion" in record for record in captured.output))

    def test_no_request_body_or_credentials_in_logs(self) -> None:
        secret_prompt = "super-secret-prompt-xyz"
        secret_key = "super-secret-key-abc"
        request = Request(
            f"{self.base_url}/v1/chat/completions",
            data=json.dumps(
                {"model": "mock-coder", "messages": [{"role": "user", "content": secret_prompt}]}
            ).encode("utf-8"),
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {secret_key}"},
            method="POST",
        )

        with self.assertLogs(GATEWAY_LOGGER_NAME, level="INFO") as captured:
            with urlopen(request) as response:
                response.read()

        for record in captured.output:
            self.assertNotIn(secret_prompt, record)
            self.assertNotIn(secret_key, record)

    def test_access_record_for_upstream_error_status(self) -> None:
        app = GatewayApp(DEFAULT_CONFIG, providers={"mock": RaisingProvider(UpstreamProviderError("upstream down"))})
        server = LocalServer(app)
        try:
            with self.assertLogs(GATEWAY_LOGGER_NAME, level="INFO") as captured:
                with self.assertRaises(HTTPError):
                    server.post(
                        "/v1/chat/completions",
                        {"model": "mock-coder", "messages": [{"role": "user", "content": "Hello"}]},
                    )
        finally:
            server.close()

        self.assertTrue(
            any(
                "method=POST path=/v1/chat/completions status=502 duration_ms=" in record
                for record in captured.output
            )
        )

    def test_unexpected_handler_error_logs_500_at_error_level(self) -> None:
        app = GatewayApp(DEFAULT_CONFIG, providers={"mock": RaisingProvider(RuntimeError("boom"))})
        server = LocalServer(app)
        try:
            with self.assertLogs(GATEWAY_LOGGER_NAME, level="ERROR") as captured:
                with self.assertRaises(Exception):
                    server.post(
                        "/v1/chat/completions",
                        {"model": "mock-coder", "messages": [{"role": "user", "content": "Hello"}]},
                    )
        finally:
            server.close()

        self.assertTrue(
            any(
                "method=POST path=/v1/chat/completions status=500 duration_ms=" in record
                for record in captured.output
            )
        )

    def test_log_level_filtering_suppresses_info_records(self) -> None:
        records: list[logging.LogRecord] = []
        handler = logging.Handler()
        handler.emit = records.append  # type: ignore[method-assign]
        logger = get_logger()
        previous_level = logger.level
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        try:
            self.get("/health")
        finally:
            logger.setLevel(previous_level)
            logger.removeHandler(handler)

        self.assertEqual(records, [])

    def get(self, path: str) -> None:
        with urlopen(f"{self.base_url}{path}") as response:
            response.read()

    def post(self, path: str, body: dict[str, object]) -> None:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            response.read()


class RaisingProvider:
    def __init__(self, error: Exception) -> None:
        self.error = error

    def chat_completion(self, model: ModelConfig, body: dict[str, object]) -> dict[str, object]:
        raise self.error


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

    def post(self, path: str, body: dict[str, object]) -> None:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request) as response:
            response.read()


if __name__ == "__main__":
    unittest.main()
