from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from ..config import ModelConfig, ProviderConfig
from ..errors import UpstreamProviderError
from .http import http_error_message, sse_data


class OllamaProvider:
    default_base_url = "http://127.0.0.1:11434/v1"

    def __init__(
        self,
        config: ProviderConfig,
        urlopen_fn: Callable[..., object] = urlopen,
    ) -> None:
        self.config = config
        self._urlopen = urlopen_fn

    def chat_completion(self, model: ModelConfig, body: dict[str, Any]) -> dict[str, object]:
        payload = dict(body)
        payload["model"] = model.provider_model
        url = self._chat_completions_url()
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
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
        parsed["model"] = model.name
        return parsed

    def chat_completion_stream(self, model: ModelConfig, body: dict[str, Any]) -> Iterator[dict[str, object]]:
        payload = dict(body)
        payload["model"] = model.provider_model
        payload["stream"] = True
        url = self._chat_completions_url()
        request = Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=self._headers(),
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
                for line in response:
                    data = sse_data(line)
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

    def _chat_completions_url(self) -> str:
        return f"{(self.config.base_url or self.default_base_url).rstrip('/')}/chat/completions"

    def _headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
        }
        headers.update(self.config.headers or {})
        return headers
