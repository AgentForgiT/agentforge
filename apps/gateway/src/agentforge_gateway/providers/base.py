from __future__ import annotations

from typing import Any, Protocol

from ..config import ModelConfig


class ChatProvider(Protocol):
    def chat_completion(self, model: ModelConfig, body: dict[str, Any]) -> dict[str, object]:
        ...
