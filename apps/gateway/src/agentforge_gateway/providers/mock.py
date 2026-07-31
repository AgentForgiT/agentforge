from __future__ import annotations

from collections.abc import Iterator
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

    def chat_completion_stream(self, model: ModelConfig, body: dict[str, Any]) -> Iterator[dict[str, object]]:
        messages = body["messages"]
        user_text = _last_user_text(messages)
        content = f"Mock response from {model.name}: {user_text}"

        completion_id = f"chatcmpl-{uuid.uuid4().hex[:24]}"
        created = int(time.time())
        words = content.split(" ") if content else []

        yield _chunk(
            completion_id=completion_id,
            created=created,
            model_name=model.name,
            delta={"role": "assistant"},
            finish_reason=None,
        )

        for word in words:
            yield _chunk(
                completion_id=completion_id,
                created=created,
                model_name=model.name,
                delta={"content": word + " "},
                finish_reason=None,
            )

        yield _chunk(
            completion_id=completion_id,
            created=created,
            model_name=model.name,
            delta={},
            finish_reason="stop",
        )


def _chunk(
    *,
    completion_id: str,
    created: int,
    model_name: str,
    delta: dict[str, object],
    finish_reason: str | None,
) -> dict[str, object]:
    return {
        "id": completion_id,
        "object": "chat.completion.chunk",
        "created": created,
        "model": model_name,
        "choices": [
            {
                "index": 0,
                "delta": delta,
                "finish_reason": finish_reason,
            }
        ],
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
