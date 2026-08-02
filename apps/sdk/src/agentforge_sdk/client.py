from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

__all__ = ["AgentForgeClient", "AgentForgeError"]

UrlOpenFn = Callable[..., object]


class AgentForgeError(Exception):
    def __init__(self, status: int, body: dict[str, Any]) -> None:
        super().__init__(f"gateway error {status}: {json.dumps(body)}")
        self.status = status
        self.body = body


class AgentForgeClient:
    """Thin, dependency-free client for the AgentForge gateway (ADR-0025).

    Covers both inbound surfaces: OpenAI Chat Completions and Anthropic
    Messages. The gateway owns validation, normalization, and protocol
    translation; this client only speaks HTTP.
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        urlopen_fn: UrlOpenFn = urlopen,
        timeout: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._urlopen = urlopen_fn
        self._timeout = timeout

    # --- public API ---

    def health(self) -> dict[str, Any]:
        return self._get("/health")

    def models(self) -> dict[str, Any]:
        return self._get("/v1/models")

    def chat_completions(
        self,
        model: str,
        messages: list[dict[str, Any]],
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any] | Iterator[dict[str, Any]]:
        payload: dict[str, Any] = {"model": model, "messages": messages, "stream": stream}
        payload.update(kwargs)
        if stream:
            return self._stream_post("/v1/chat/completions", payload, sse_mode="openai")
        return self._post("/v1/chat/completions", payload)

    def anthropic_messages(
        self,
        model: str,
        messages: list[dict[str, Any]],
        max_tokens: int = 4096,
        stream: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any] | Iterator[tuple[str, dict[str, Any]]]:
        payload: dict[str, Any] = {"model": model, "messages": messages, "max_tokens": max_tokens, "stream": stream}
        payload.update(kwargs)
        if stream:
            return self._stream_post("/v1/messages", payload, sse_mode="anthropic")
        return self._post("/v1/messages", payload)

    # --- HTTP internals ---

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _get(self, path: str) -> dict[str, Any]:
        request = Request(f"{self.base_url}{path}", headers=self._headers())
        return self._open(request)

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        return self._open(request)

    def _open(self, request: Request) -> dict[str, Any]:
        try:
            with self._urlopen(request, timeout=self._timeout) as response:  # type: ignore[operator]
                raw = response.read().decode("utf-8")
        except HTTPError as exc:
            body = _parse_error_body(exc)
            raise AgentForgeError(exc.code, body) from exc
        except URLError as exc:
            raise AgentForgeError(0, {"error": {"message": f"connection failed: {exc.reason}", "type": "connection_error"}}) from exc
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise AgentForgeError(200, {"error": {"message": "non-object response", "type": "bad_response"}})
        return parsed

    def _stream_post(
        self,
        path: str,
        payload: dict[str, Any],
        *,
        sse_mode: str,
    ) -> Iterator[dict[str, Any]] | Iterator[tuple[str, dict[str, Any]]]:
        request = Request(
            f"{self.base_url}{path}",
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            response = self._urlopen(request, timeout=self._timeout)  # type: ignore[operator]
        except HTTPError as exc:
            raise AgentForgeError(exc.code, _parse_error_body(exc)) from exc
        except URLError as exc:
            raise AgentForgeError(0, {"error": {"message": f"connection failed: {exc.reason}", "type": "connection_error"}}) from exc

        def generate() -> Iterator[dict[str, Any] | tuple[str, dict[str, Any]]]:
            try:
                with response:  # type: ignore[attr-defined]
                    for line in response:  # type: ignore[attr-defined]
                        if sse_mode == "openai":
                            chunk = _openai_sse_line(line)
                            if chunk is not None:
                                yield chunk
                        else:
                            event = _anthropic_sse_line(line)
                            if event is not None:
                                yield event
            except URLError as exc:
                raise AgentForgeError(0, {"error": {"message": f"stream failed: {exc.reason}", "type": "connection_error"}}) from exc
            except OSError as exc:
                raise AgentForgeError(0, {"error": {"message": f"stream failed: {exc}", "type": "connection_error"}}) from exc

        return generate()


def _openai_sse_line(line: bytes) -> dict[str, Any] | None:
    text = line.decode("utf-8", errors="replace").strip()
    if not text.startswith("data:"):
        return None
    data = text[5:].strip()
    if data == "[DONE]":
        return None
    parsed = json.loads(data)
    return parsed if isinstance(parsed, dict) else None


def _anthropic_sse_line(line: bytes) -> tuple[str, dict[str, Any]] | None:
    text = line.decode("utf-8", errors="replace").rstrip("\r\n")
    if text.startswith("event: "):
        return None  # event name handled on the following data: line
    if text.startswith("data: "):
        data = json.loads(text[6:].strip())
        if isinstance(data, dict) and "type" in data:
            return data["type"], data
    return None


def _parse_error_body(exc: HTTPError) -> dict[str, Any]:
    try:
        raw = exc.read().decode("utf-8")
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except (ValueError, OSError):
        pass
    return {"error": {"message": f"HTTP {exc.code}", "type": "http_error"}}
