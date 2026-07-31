from __future__ import annotations

from collections.abc import Iterator
from typing import Any, Protocol

from ..config import ModelConfig


class ChatProvider(Protocol):
    def chat_completion(self, model: ModelConfig, body: dict[str, Any]) -> dict[str, object]:
        ...

    def chat_completion_stream(self, model: ModelConfig, body: dict[str, Any]) -> Iterator[dict[str, object]]:
        ...
