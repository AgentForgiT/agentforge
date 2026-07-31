from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any
import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import ModelConfig, ProviderConfig
from ..errors import ProviderConfigurationError, UpstreamProviderError


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
        api_key = self._require_api_key()
        payload = dict(body)
        payload["model"] = model.provider_model
        url = self._chat_completions_url()
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

    def chat_completion_stream(self, model: ModelConfig, body: dict[str, Any]) -> Iterator[dict[str, object]]:
        api_key = self._require_api_key()
        payload = dict(body)
        payload["model"] = model.provider_model
        payload["stream"] = True
        url = self._chat_completions_url()
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(api_key),
            method="POST",
        )

        try:
            response = self._urlopen(request, timeout=self.config.timeout_seconds)
        except HTTPError as exc:
            raise UpstreamProviderError(_http_error_message(self.config.name, exc)) from exc
        except URLError as exc:
            raise UpstreamProviderError(f"provider '{self.config.name}' request failed: {exc.reason}") from exc

        try:
            with response:
                for line in response:
                    data = _sse_data(line)
                    if data is None:
                        continue
                    if data == "[DONE]":
                        return
                    try:
                        chunk = json.loads(data)
                    except json.JSONDecodeError as exc:
                        raise UpstreamProviderError(
                            f"provider '{self.config.name}' returned invalid stream JSON"
                        ) from exc
                    if not isinstance(chunk, dict):
                        raise UpstreamProviderError(
                            f"provider '{self.config.name}' returned a non-object stream chunk"
                        )
                    yield chunk
        except URLError as exc:
            raise UpstreamProviderError(f"provider '{self.config.name}' stream failed: {exc.reason}") from exc
        except OSError as exc:
            raise UpstreamProviderError(f"provider '{self.config.name}' stream failed: {exc}") from exc

    def _require_api_key(self) -> str:
        api_key_env = self.config.api_key_env or self.default_api_key_env
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise ProviderConfigurationError(f"provider '{self.config.name}' requires ${api_key_env}")
        return api_key

    def _chat_completions_url(self) -> str:
        return f"{(self.config.base_url or self.default_base_url).rstrip('/')}/chat/completions"

    def _headers(self, api_key: str) -> dict[str, str]:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self.config.headers or {})
        return headers


def _sse_data(line: bytes | str) -> str | None:
    text = line.decode("utf-8").strip() if isinstance(line, bytes) else str(line).strip()
    if not text or not text.startswith("data:"):
        return None
    return text[len("data:") :].strip()


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
