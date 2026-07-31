from __future__ import annotations

from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from typing import Any

from .config import GatewayConfig, load_config
from .errors import BadRequestError, GatewayError, invalid_json_response, not_found_response
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
        model = self.registry.get(request.model)
        provider = self.providers[model.provider]
        return normalize_chat_completion_response(model, provider.chat_completion(model, request.body))

    def chat_completion_stream(self, body: dict[str, Any]) -> Iterator[dict[str, object]]:
        request = validate_chat_completion_request(body)
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

        def do_GET(self) -> None:
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

        def do_POST(self) -> None:
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

        def _handle_stream(self, body: dict[str, Any]) -> None:
            stream = app.chat_completion_stream(body)
            try:
                first_chunk = next(stream)
            except GatewayError as exc:
                self._send_json(exc.status_code, exc.to_response())
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
            self.end_headers()
            self.wfile.write(payload)

    return GatewayHandler


def create_server(config_path: str | None = None) -> ThreadingHTTPServer:
    config = load_config(config_path)
    app = GatewayApp(config)
    return ThreadingHTTPServer((config.host, config.port), create_handler(app))
