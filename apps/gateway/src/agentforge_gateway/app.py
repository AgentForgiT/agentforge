from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from typing import Any

from .config import GatewayConfig, load_config
from .errors import BadRequestError, GatewayError
from .models import ModelRegistry
from .providers import ChatProvider, build_provider


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
        model_name = body.get("model")
        messages = body.get("messages")

        if not isinstance(model_name, str) or not model_name:
            raise BadRequestError("request requires a model")
        if not isinstance(messages, list) or not messages:
            raise BadRequestError("request requires non-empty messages")
        if body.get("stream") is True:
            raise BadRequestError("streaming responses are not supported yet")
        for message in messages:
            if not isinstance(message, dict) or "role" not in message or "content" not in message:
                raise BadRequestError("each message requires role and content")

        model = self.registry.get(model_name)
        provider = self.providers[model.provider]
        return provider.chat_completion(model, body)


def create_handler(app: GatewayApp) -> type[BaseHTTPRequestHandler]:
    class GatewayHandler(BaseHTTPRequestHandler):
        server_version = "AgentForgeGateway/0.1"

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
                self._send_json(404, {"error": {"message": "not found", "type": "not_found"}})
            except GatewayError as exc:
                self._send_json(exc.status_code, exc.to_response())

        def do_POST(self) -> None:
            try:
                if self.path == "/v1/chat/completions":
                    self._send_json(200, app.chat_completions(self._read_json()))
                    return
                self._send_json(404, {"error": {"message": "not found", "type": "not_found"}})
            except GatewayError as exc:
                self._send_json(exc.status_code, exc.to_response())
            except json.JSONDecodeError:
                self._send_json(400, {"error": {"message": "invalid JSON body", "type": "bad_request"}})

        def _read_json(self) -> dict[str, Any]:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length)
            body = json.loads(raw.decode("utf-8"))
            if not isinstance(body, dict):
                raise BadRequestError("request body must be a JSON object")
            return body

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
