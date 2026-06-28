from __future__ import annotations

import json
import os
import time
from typing import Any, Callable, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import uuid

from .config import ModelConfig, ProviderConfig
from .errors import ProviderConfigurationError, UpstreamProviderError


class ChatProvider(Protocol):
    def chat_completion(self, model: ModelConfig, body: dict[str, Any]) -> dict[str, object]:
        ...


class MockProvider:
    def chat_completion(self, model: ModelConfig, body: dict[str, Any]) -> dict[str, object]:
        messages = body["messages"]
        user_text = _last_user_text(messages)
        content = f"Mock response from {model.name}: {user_text}"

        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:24]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model.name,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content,
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": _estimate_tokens(messages),
                "completion_tokens": _estimate_text_tokens(content),
                "total_tokens": _estimate_tokens(messages) + _estimate_text_tokens(content),
            },
        }


class OpenRouterProvider:
    default_base_url = "https://openrouter.ai/api/v1"
    default_api_key_env = "OPENROUTER_API_KEY"

    def __init__(
        self,
        config: ProviderConfig,
        urlopen_fn: Callable[..., object] = urlopen,
    ) -> None:
        self.config = config
        self._urlopen = urlopen_fn

    def chat_completion(self, model: ModelConfig, body: dict[str, Any]) -> dict[str, object]:
        api_key_env = self.config.api_key_env or self.default_api_key_env
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise ProviderConfigurationError(f"provider '{self.config.name}' requires ${api_key_env}")

        payload = dict(body)
        payload["model"] = model.provider_model
        url = f"{(self.config.base_url or self.default_base_url).rstrip('/')}/chat/completions"
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(api_key),
            method="POST",
        )

        try:
            with self._urlopen(request, timeout=self.config.timeout_seconds) as response:
                raw_response = response.read().decode("utf-8")
        except HTTPError as exc:
            raise UpstreamProviderError(_http_error_message(self.config.name, exc)) from exc
        except URLError as exc:
            raise UpstreamProviderError(f"provider '{self.config.name}' request failed: {exc.reason}") from exc

        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise UpstreamProviderError(f"provider '{self.config.name}' returned invalid JSON") from exc
        if not isinstance(parsed, dict):
            raise UpstreamProviderError(f"provider '{self.config.name}' returned a non-object response")
        parsed["model"] = model.name
        return parsed

    def _headers(self, api_key: str) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self.config.headers or {})
        return headers


def build_provider(config: ProviderConfig) -> ChatProvider:
    if config.type == "mock":
        return MockProvider()
    if config.type == "openrouter":
        return OpenRouterProvider(config)
    raise ProviderConfigurationError(f"unsupported provider type: {config.type}")


def _http_error_message(provider_name: str, exc: HTTPError) -> str:
    raw = exc.read().decode("utf-8", errors="replace")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {}

    message = raw.strip()
    if isinstance(parsed, dict):
        error = parsed.get("error")
        if isinstance(error, dict) and error.get("message"):
            message = str(error["message"])
        elif parsed.get("message"):
            message = str(parsed["message"])

    return f"provider '{provider_name}' request failed with status {exc.code}: {message}"


def _last_user_text(messages: list[dict[str, object]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            content = message.get("content", "")
            return str(content)
    return "No user message provided."


def _estimate_tokens(messages: list[dict[str, object]]) -> int:
    return sum(_estimate_text_tokens(str(message.get("content", ""))) for message in messages)


def _estimate_text_tokens(text: str) -> int:
    return max(1, len(text.split()))
