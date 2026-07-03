from __future__ import annotations

from typing import Any
import time
import uuid

from ..config import ModelConfig


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
