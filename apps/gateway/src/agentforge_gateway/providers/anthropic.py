from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import ModelConfig, ProviderConfig
from ..errors import ProviderConfigurationError, UpstreamProviderError
from .http import http_error_message, sse_data

ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MAX_TOKENS = 4096


class AnthropicProvider:
    default_base_url = "https://api.anthropic.com"
    default_api_key_env = "ANTHROPIC_API_KEY"

    def __init__(
        self,
        config: ProviderConfig,
        urlopen_fn: Callable[..., object] = urlopen,
    ) -> None:
        self.config = config
        self._urlopen = urlopen_fn

    def chat_completion(self, model: ModelConfig, body: dict[str, Any]) -> dict[str, object]:
        api_key = self._require_api_key()
        payload = self._to_anthropic_payload(model, body, stream=False)
        request = Request(
            self._messages_url(),
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(api_key),
            method="POST",
        )

        try:
            with self._urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw_response = response.read().decode("utf-8")
        except HTTPError as exc:
            raise UpstreamProviderError(http_error_message(self.config.name, exc)) from exc
        except URLError as exc:
            raise UpstreamProviderError(f"provider '{self.config.name}' request failed: {exc.reason}") from exc

        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise UpstreamProviderError(f"provider '{self.config.name}' returned invalid JSON") from exc
        if not isinstance(parsed, dict):
            raise UpstreamProviderError(f"provider '{self.config.name}' returned a non-object response")

        return _to_openai_response(model, parsed)

    def chat_completion_stream(self, model: ModelConfig, body: dict[str, Any]) -> Iterator[dict[str, object]]:
        api_key = self._require_api_key()
        payload = self._to_anthropic_payload(model, body, stream=True)
        request = Request(
            self._messages_url(),
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(api_key),
            method="POST",
        )

        try:
            response = self._urlopen(request, timeout=self.config.timeout_seconds)
        except HTTPError as exc:
            raise UpstreamProviderError(http_error_message(self.config.name, exc)) from exc
        except URLError as exc:
            raise UpstreamProviderError(f"provider '{self.config.name}' request failed: {exc.reason}") from exc

        try:
            with response:
                for _event_type, event in _iter_anthropic_events(response):
                    yield from _translate_stream_event(model, event)
        except URLError as exc:
            raise UpstreamProviderError(f"provider '{self.config.name}' stream failed: {exc.reason}") from exc
        except OSError as exc:
            raise UpstreamProviderError(f"provider '{self.config.name}' stream failed: {exc}") from exc

    # --- outbound request translation: OpenAI body -> Anthropic Messages ---

    def _to_anthropic_payload(self, model: ModelConfig, body: dict[str, Any], *, stream: bool) -> dict[str, Any]:
        messages = body.get("messages", [])
        system_parts: list[str] = []
        anthropic_messages: list[dict[str, Any]] = []

        for message in messages:
            if not isinstance(message, dict):
                continue
            role = message.get("role")
            content = message.get("content")
            if role == "system":
                system_parts.append(str(content or ""))
            elif role == "user":
                anthropic_messages.append(_user_message_to_anthropic(message))
            elif role == "assistant":
                anthropic_messages.append(_assistant_message_to_anthropic(message))
            elif role == "tool":
                anthropic_messages.append(_tool_message_to_anthropic(message))

        payload: dict[str, Any] = {
            "model": model.provider_model,
            "max_tokens": body.get("max_tokens", DEFAULT_MAX_TOKENS),
            "messages": anthropic_messages,
        }
        if system_parts:
            payload["system"] = "\n".join(system_parts)

        tools = body.get("tools")
        if isinstance(tools, list) and tools:
            payload["tools"] = _tools_to_anthropic(tools)

        if stream:
            payload["stream"] = True
        return payload

    def _require_api_key(self) -> str:
        api_key_env = self.config.api_key_env or self.default_api_key_env
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise ProviderConfigurationError(f"provider '{self.config.name}' requires ${api_key_env}")
        return api_key

    def _messages_url(self) -> str:
        return f"{(self.config.base_url or self.default_base_url).rstrip('/')}/v1/messages"

    def _headers(self, api_key: str) -> dict[str, str]:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        }
        headers.update(self.config.headers or {})
        return headers


# --- outbound request translation helpers ---


def _user_message_to_anthropic(message: dict[str, Any]) -> dict[str, Any]:
    content = message.get("content")
    if isinstance(content, str):
        return {"role": "user", "content": content}
    if isinstance(content, list):
        blocks: list[dict[str, Any]] = []
        for item in content:
            if not isinstance(item, dict):
                continue
            tool_call_id = item.get("tool_call_id")
            if item.get("role") == "tool" and tool_call_id:
                blocks.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_call_id,
                        "content": item.get("content") or "",
                    }
                )
            else:
                blocks.append({"type": "text", "text": str(item.get("content", ""))})
        return {"role": "user", "content": blocks}
    return {"role": "user", "content": str(content or "")}


def _assistant_message_to_anthropic(message: dict[str, Any]) -> dict[str, Any]:
    content: list[dict[str, Any]] = []
    text = message.get("content")
    if isinstance(text, str) and text:
        content.append({"type": "text", "text": text})
    tool_calls = message.get("tool_calls")
    if isinstance(tool_calls, list):
        for call in tool_calls:
            if not isinstance(call, dict):
                continue
            function = call.get("function")
            if not isinstance(function, dict):
                continue
            arguments = function.get("arguments")
            try:
                parsed_input = json.loads(arguments) if isinstance(arguments, str) and arguments else {}
            except json.JSONDecodeError:
                parsed_input = {}
            content.append(
                {
                    "type": "tool_use",
                    "id": call.get("id") or f"toolu_{_short_uuid()}",
                    "name": function.get("name") or "",
                    "input": parsed_input,
                }
            )
    return {"role": "assistant", "content": content}


def _tool_message_to_anthropic(message: dict[str, Any]) -> dict[str, Any]:
    return {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": message.get("tool_call_id") or "",
                "content": message.get("content") or "",
            }
        ],
    }


def _tools_to_anthropic(tools: list[Any]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for tool in tools:
        if not isinstance(tool, dict):
            continue
        function = tool.get("function") if tool.get("type") == "function" else tool
        if not isinstance(function, dict):
            continue
        name = function.get("name")
        if not name:
            continue
        converted.append(
            {
                "name": name,
                "description": function.get("description") or "",
                "input_schema": function.get("parameters") or {"type": "object", "properties": {}},
            }
        )
    return converted


# --- outbound response translation: Anthropic message -> OpenAI chat.completion ---


def _to_openai_response(model: ModelConfig, message: dict[str, Any]) -> dict[str, object]:
    text_parts: list[str] = []
    tool_calls: list[dict[str, object]] = []

    content = message.get("content")
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = block.get("type")
            if block_type == "text":
                text_parts.append(str(block.get("text", "")))
            elif block_type == "tool_use":
                tool_calls.append(
                    {
                        "id": block.get("id") or f"call_{_short_uuid()}",
                        "type": "function",
                        "function": {
                            "name": block.get("name") or "",
                            "arguments": json.dumps(block.get("input") or {}),
                        },
                    }
                )

    usage = message.get("usage") if isinstance(message.get("usage"), dict) else {}
    prompt_tokens = usage.get("input_tokens") or 0
    completion_tokens = usage.get("output_tokens") or 0

    choice: dict[str, object] = {
        "index": 0,
        "message": {
            "role": "assistant",
            "content": "".join(text_parts) or None,
        },
        "finish_reason": _finish_reason(message.get("stop_reason")),
    }
    if tool_calls:
        choice["message"] = {  # type: ignore[index]
            "role": "assistant",
            "content": "".join(text_parts) or None,
            "tool_calls": tool_calls,
        }

    return {
        "id": message.get("id") or f"chatcmpl-{_short_uuid()}",
        "object": "chat.completion",
        "created": int(message.get("created") or 0),
        "model": model.name,
        "choices": [choice],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


# --- outbound streaming translation: Anthropic SSE events -> OpenAI chunks ---


def _iter_anthropic_events(response: object) -> Iterator[tuple[str, dict[str, Any]]]:
    for line in response:  # type: ignore[union-attr]
        data = sse_data(line)
        if data is None:
            continue
        try:
            event = json.loads(data)
        except json.JSONDecodeError as exc:
            raise UpstreamProviderError("provider 'anthropic' returned invalid stream JSON") from exc
        if not isinstance(event, dict):
            raise UpstreamProviderError("provider 'anthropic' returned a non-object stream event")
        yield event.get("type", ""), event


def _translate_stream_event(model: ModelConfig, event: dict[str, Any]) -> Iterator[dict[str, object]]:
    """Translate a single Anthropic stream event into zero or more OpenAI chunks."""
    event_type = event.get("type")

    if event_type == "message_start":
        message = event.get("message")
        message_id = message.get("id") if isinstance(message, dict) else None
        yield _chunk(model, {"role": "assistant"}, finish_reason=None, chunk_id=message_id)

    elif event_type == "content_block_delta":
        delta = event.get("delta")
        if not isinstance(delta, dict):
            return
        delta_type = delta.get("type")
        if delta_type == "text_delta":
            text = delta.get("text")
            if isinstance(text, str) and text:
                yield _chunk(model, {"content": text}, finish_reason=None)
        elif delta_type == "input_json_delta":
            partial = delta.get("partial_json")
            if isinstance(partial, str) and partial:
                yield _chunk(
                    model,
                    {"tool_calls": [{"index": 0, "function": {"arguments": partial}}]},
                    finish_reason=None,
                )

    elif event_type == "message_delta":
        delta = event.get("delta")
        stop_reason = delta.get("stop_reason") if isinstance(delta, dict) else None
        if stop_reason:
            yield _chunk(model, {}, finish_reason=_finish_reason(stop_reason))


def _chunk(
    model: ModelConfig,
    delta: dict[str, object],
    *,
    finish_reason: str | None,
    chunk_id: str | None = None,
) -> dict[str, object]:
    return {
        "id": chunk_id or f"chatcmpl-{_short_uuid()}",
        "object": "chat.completion.chunk",
        "created": 0,
        "model": model.name,
        "choices": [{"index": 0, "delta": delta, "finish_reason": finish_reason}],
    }


def _finish_reason(stop_reason: Any) -> str:
    if stop_reason == "max_tokens":
        return "length"
    if stop_reason == "tool_use":
        return "tool_calls"
    return "stop"


def _short_uuid() -> str:
    import uuid

    return uuid.uuid4().hex[:24]
