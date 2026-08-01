from __future__ import annotations

from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import time
from typing import Any

from .config import GatewayConfig, load_config
from .errors import (
    BadRequestError,
    GatewayError,
    internal_error_response,
    invalid_json_response,
    not_found_response,
)
from .logger import configure_logging, get_logger
from .models import ModelRegistry
from .providers import ChatProvider, build_provider
from .requests import validate_chat_completion_request
from .responses import normalize_chat_completion_response, normalize_stream_chunk


class GatewayApp:
    def __init__(self, config: GatewayConfig, providers: dict[str, ChatProvider] | None = None) -> None:
        self.config = config
        self.registry = ModelRegistry(config)
        self.providers = providers or {
            name: build_provider(provider)
            for name, provider in config.providers.items()
        }

    def health(self) -> dict[str, object]:
        return {
            "status": "ok",
            "service": "agentforge-gateway",
        }

    def models(self) -> dict[str, object]:
        return self.registry.list_models()

    def chat_completions(self, body: dict[str, Any]) -> dict[str, object]:
        request = validate_chat_completion_request(body)
        get_logger().info("chat_completion model=%s stream=false", request.model)
        model = self.registry.get(request.model)
        provider = self.providers[model.provider]
        return normalize_chat_completion_response(model, provider.chat_completion(model, request.body))

    def chat_completion_stream(self, body: dict[str, Any]) -> Iterator[dict[str, object]]:
        request = validate_chat_completion_request(body)
        get_logger().info("chat_completion model=%s stream=true", request.model)
        model = self.registry.get(request.model)
        provider = self.providers[model.provider]
        for chunk in provider.chat_completion_stream(model, request.body):
            yield normalize_stream_chunk(model, chunk)


def create_handler(app: GatewayApp) -> type[BaseHTTPRequestHandler]:
    class GatewayHandler(BaseHTTPRequestHandler):
        server_version = "AgentForgeGateway/0.1"
        protocol_version = "HTTP/1.1"

        def log_message(self, format: str, *args: object) -> None:
            return

        def log_request(self, code: int | str = "-", size: int | str = "-") -> None:
            started = getattr(self, "_request_started", None)
            duration_ms = int((time.monotonic() - started) * 1000) if started is not None else 0
            record = "method=%s path=%s status=%s duration_ms=%d"
            values: tuple[object, ...] = (self.command, self.path, code, duration_ms)
            if str(code).isdigit() and int(code) >= 500:
                get_logger().error(record, *values)
            else:
                get_logger().info(record, *values)

        def _cors_headers(self) -> dict[str, str]:
            origin = app.config.cors_origin
            if origin is None:
                return {}
            return {"Access-Control-Allow-Origin": origin}

        def do_OPTIONS(self) -> None:
            self._request_started = time.monotonic()
            if app.config.cors_origin is None:
                self._send_json(404, not_found_response())
                return
            self.send_response(204)
            for name, value in self._cors_headers().items():
                self.send_header(name, value)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Max-Age", "86400")
            self.send_header("Content-Length", "0")
            self.end_headers()
            self.wfile.flush()

        def do_GET(self) -> None:
            self._request_started = time.monotonic()
            try:
                if self.path == "/health":
                    self._send_json(200, app.health())
                    return
                if self.path == "/v1/models":
                    self._send_json(200, app.models())
                    return
                self._send_json(404, not_found_response())
            except GatewayError as exc:
                self._send_json(exc.status_code, exc.to_response())
            except Exception:
                get_logger().error("unhandled gateway error", exc_info=True)
                self._send_json(500, internal_error_response())

        def do_POST(self) -> None:
            self._request_started = time.monotonic()
            try:
                if self.path == "/v1/chat/completions":
                    body = self._read_json()
                    if body.get("stream") is True:
                        self._handle_stream(body)
                    else:
                        self._send_json(200, app.chat_completions(body))
                    return
                self._send_json(404, not_found_response())
            except GatewayError as exc:
                self._send_json(exc.status_code, exc.to_response())
            except json.JSONDecodeError:
                self._send_json(400, invalid_json_response())
            except Exception:
                get_logger().error("unhandled gateway error", exc_info=True)
                self._send_json(500, internal_error_response())

        def _handle_stream(self, body: dict[str, Any]) -> None:
            try:
                stream = app.chat_completion_stream(body)
                first_chunk = next(stream)
            except GatewayError as exc:
                self._send_json(exc.status_code, exc.to_response())
                return
            except Exception:
                get_logger().error("unhandled gateway error", exc_info=True)
                self._send_json(500, internal_error_response())
                return

            self._send_stream_headers()
            try:
                self._send_sse_event(first_chunk)
                for chunk in stream:
                    self._send_sse_event(chunk)
                self._send_sse_event(None)
            except GatewayError:
                return
            except OSError:
                return
            except Exception:
                get_logger().error("unhandled gateway error", exc_info=True)
                return

        def _read_json(self) -> dict[str, Any]:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length)
            body = json.loads(raw.decode("utf-8"))
            if not isinstance(body, dict):
                raise BadRequestError("request body must be a JSON object")
            return body

        def _send_stream_headers(self) -> None:
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            for name, value in self._cors_headers().items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.flush()

        def _send_sse_event(self, chunk: dict[str, object] | None) -> None:
            if chunk is None:
                payload = b"data: [DONE]\n\n"
            else:
                payload = b"data: " + json.dumps(chunk).encode("utf-8") + b"\n\n"
            self.wfile.write(payload)
            self.wfile.flush()

        def _send_json(self, status_code: int, body: dict[str, object]) -> None:
            payload = json.dumps(body).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            for name, value in self._cors_headers().items():
                self.send_header(name, value)
            self.end_headers()
            self.wfile.write(payload)

    return GatewayHandler


def create_server(config_path: str | None = None) -> ThreadingHTTPServer:
    config = load_config(config_path)
    configure_logging(config.log_level)
    app = GatewayApp(config)
    return ThreadingHTTPServer((config.host, config.port), create_handler(app))
