from __future__ import annotations

from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import time
from typing import Any

from .config import GatewayConfig, load_config
from .anthropic import (
    anthropic_sse_events,
    normalize_anthropic_response,
    to_openai_body,
    validate_anthropic_messages_request,
)
from .errors import (
    BadRequestError,
    GatewayError,
    internal_error_response,
    invalid_json_response,
    not_found_response,
    unauthorized_response,
    rate_limited_response,
)
from .logger import configure_logging, get_logger
from .mcp import McpServer
from .keystore import load_key_store
from .models import ModelRegistry
from .providers import ChatProvider, build_provider
from .ratelimit import TokenBucketRateLimiter
from .requests import validate_chat_completion_request
from .responses import normalize_chat_completion_response, normalize_stream_chunk
import os


class GatewayApp:
    def __init__(self, config: GatewayConfig, providers: dict[str, ChatProvider] | None = None) -> None:
        self.config = config
        self.registry = ModelRegistry(config)
        self.providers = providers or {
            name: build_provider(provider)
            for name, provider in config.providers.items()
        }
        self.api_key = self._resolve_api_key()
        self.rate_limiter = (
            TokenBucketRateLimiter(config.rate_limit_rpm) if config.rate_limit_rpm else None
        )
        self.named_keys = self._resolve_named_keys()
        self.mcp = McpServer(self)

    def _resolve_api_key(self) -> str | None:
        if not self.config.api_key_env:
            return None
        key = os.environ.get(self.config.api_key_env)
        if not key:
            raise RuntimeError(f"server.api_key_env names ${self.config.api_key_env} but it is not set")
        return key

    def _resolve_named_keys(self) -> dict[str, object] | None:
        """Startup validation of the named key store (fail-fast)."""
        if not self.config.auth_keys_file:
            return None
        from pathlib import Path

        self._named_limiters: dict[str, TokenBucketRateLimiter] = {}
        # strict load at startup: malformed store fails fast
        load_key_store(Path(self.config.auth_keys_file).resolve())
        return self._named_keys_live() or None

    def _named_keys_live(self) -> dict[str, object]:
        """Reload the key store per request (ADR-0031).

        Auth-key add/revoke take effect immediately, no restart. The
        store is a small local file; per-request reads are cheap.
        Per-key token buckets persist across requests (keyed by name)
        so rate limits accumulate; revoked names drop their bucket.
        Startup validation (self.named_keys) still fail-fasts on a
        malformed file; live reads tolerate a transiently missing file
        by returning an empty store (all requests 401 until restored).
        """
        if not self.config.auth_keys_file:
            return {}
        from pathlib import Path

        try:
            keys = load_key_store(Path(self.config.auth_keys_file).resolve())
        except ValueError:
            return {}

        live_names = {named.name for named in keys}
        # drop buckets for revoked names
        for name in list(getattr(self, "_named_limiters", {})):
            if name not in live_names:
                del self._named_limiters[name]

        store: dict[str, object] = {}
        for named in keys:
            limiter = None
            if named.rate_limit_rpm:
                if named.name not in self._named_limiters:
                    self._named_limiters[named.name] = TokenBucketRateLimiter(named.rate_limit_rpm)
                limiter = self._named_limiters[named.name]
            store[named.name] = {"key": named.key, "limiter": limiter}
        return store

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

    def anthropic_messages(self, body: dict[str, Any]) -> dict[str, object]:
        request = validate_anthropic_messages_request(body)
        get_logger().info("anthropic_message model=%s stream=false", request.model)
        model = self.registry.get(request.model)
        provider = self.providers[model.provider]
        openai_body = to_openai_body(request)
        response = provider.chat_completion(model, openai_body)
        normalized = normalize_chat_completion_response(model, response)
        return normalize_anthropic_response(model, normalized)

    def anthropic_messages_stream(self, body: dict[str, Any]) -> Iterator[tuple[str, dict[str, object]]]:
        request = validate_anthropic_messages_request(body)
        get_logger().info("anthropic_message model=%s stream=true", request.model)
        model = self.registry.get(request.model)
        provider = self.providers[model.provider]
        openai_body = to_openai_body(request)
        stream = provider.chat_completion_stream(model, openai_body)
        for event in anthropic_sse_events(model, stream):
            yield event


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

        def _bearer_key(self) -> str | None:
            header = self.headers.get("Authorization", "")
            if header.startswith("Bearer "):
                return header[7:].strip()
            return None

        def _authenticated(self) -> bool:
            if app.api_key is None and app.named_keys is None:
                return True
            key = self._bearer_key() or self.headers.get("x-api-key", "")
            if not key:
                return False
            if app.api_key is not None and key == app.api_key:
                return True
            if app.named_keys is not None:
                return any(entry["key"] == key for entry in app._named_keys_live().values())
            return False

        def _rate_limit_key(self) -> str:
            if app.api_key is not None:
                header = self.headers.get("Authorization", "")
                if header.startswith("Bearer "):
                    return "key:" + header[7:].strip()
                return "key:" + self.headers.get("x-api-key", "")
            return "ip:" + (self.client_address[0] if self.client_address else "unknown")

        def _rate_limited(self) -> bool:
            # per-key limiter when a named key matched (ADR-0031)
            if app.named_keys is not None:
                key = self._bearer_key() or self.headers.get("x-api-key", "")
                for name, entry in app._named_keys_live().items():
                    limiter = entry.get("limiter")
                    if entry["key"] == key and limiter is not None:
                        return not limiter.allow(name)
            if app.rate_limiter is None:
                return False
            return not app.rate_limiter.allow(self._rate_limit_key())

        def _guard(self, anthropic: bool = False) -> bool:
            """Returns False (and writes the error response) when the request
            must be rejected for auth or rate limiting. Health and OPTIONS
            are exempt (probes/preflight)."""
            if not self._authenticated():
                if anthropic:
                    self._send_json(401, GatewayError("unauthorized: valid API key required", status_code=401).to_anthropic_response())
                else:
                    self._send_json(401, unauthorized_response())
                return False
            if self._rate_limited():
                self.send_response(429)
                self.send_header("Content-Type", "application/json")
                self.send_header("Retry-After", "60")
                for name, value in self._cors_headers().items():
                    self.send_header(name, value)
                payload = json.dumps(rate_limited_response()).encode("utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
                return False
            return True

        def do_OPTIONS(self) -> None:
            self._request_started = time.monotonic()
            if app.config.cors_origin is None:
                self._send_json(404, not_found_response())
                return
            self.send_response(204)
            for name, value in self._cors_headers().items():
                self.send_header(name, value)
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, x-api-key")
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
                    if not self._guard():
                        return
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
            is_anthropic = self.path == "/v1/messages"
            try:
                if self.path == "/v1/chat/completions":
                    if not self._guard():
                        return
                    body = self._read_json()
                    if body.get("stream") is True:
                        self._handle_stream(body)
                    else:
                        self._send_json(200, app.chat_completions(body))
                    return
                if is_anthropic:
                    if not self._guard(anthropic=True):
                        return
                    body = self._read_json()
                    if body.get("stream") is True:
                        self._handle_anthropic_stream(body)
                    else:
                        self._send_json(200, app.anthropic_messages(body))
                    return
                if self.path == "/mcp":
                    if not self._guard():
                        return
                    raw = self.rfile.read(int(self.headers.get("Content-Length", "0"))).decode("utf-8")
                    response = app.mcp.handle(raw)
                    self._send_json(200, response)
                    return
                self._send_json(404, not_found_response())
            except GatewayError as exc:
                self._send_json(exc.status_code, exc.to_anthropic_response() if is_anthropic else exc.to_response())
            except json.JSONDecodeError:
                if is_anthropic:
                    self._send_json(400, BadRequestError("invalid JSON body").to_anthropic_response())
                else:
                    self._send_json(400, invalid_json_response())
            except Exception:
                get_logger().error("unhandled gateway error", exc_info=True)
                if is_anthropic:
                    self._send_json(500, GatewayError("internal server error").to_anthropic_response())
                else:
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

        def _handle_anthropic_stream(self, body: dict[str, Any]) -> None:
            try:
                events = app.anthropic_messages_stream(body)
                first_event = next(events)
            except GatewayError as exc:
                self._send_json(exc.status_code, exc.to_anthropic_response())
                return
            except Exception:
                get_logger().error("unhandled gateway error", exc_info=True)
                self._send_json(500, GatewayError("internal server error").to_anthropic_response())
                return

            self._send_stream_headers()
            try:
                self._send_anthropic_sse_event(first_event)
                for event in events:
                    self._send_anthropic_sse_event(event)
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

        def _send_anthropic_sse_event(self, event: tuple[str, dict[str, object]]) -> None:
            name, data = event
            payload = (
                b"event: "
                + name.encode("utf-8")
                + b"\ndata: "
                + json.dumps(data).encode("utf-8")
                + b"\n\n"
            )
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
