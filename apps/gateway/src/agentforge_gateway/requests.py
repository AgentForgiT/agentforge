from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .errors import BadRequestError


@dataclass(frozen=True)
class ChatCompletionRequest:
    model: str
    messages: list[dict[str, object]]
    body: dict[str, Any]
    stream: bool = False


def validate_chat_completion_request(body: dict[str, Any]) -> ChatCompletionRequest:
    model = body.get("model")
    messages = body.get("messages")

    if not isinstance(model, str) or not model:
        raise BadRequestError("request requires a model")
    if not isinstance(messages, list) or not messages:
        raise BadRequestError("request requires non-empty messages")

    stream = body.get("stream", False)
    if not isinstance(stream, bool):
        raise BadRequestError("stream must be a boolean")

    validated_messages: list[dict[str, object]] = []
    for message in messages:
        if not isinstance(message, dict) or "role" not in message or "content" not in message:
            raise BadRequestError("each message requires role and content")
        validated_messages.append(message)

    return ChatCompletionRequest(
        model=model,
        messages=validated_messages,
        body=body,
        stream=stream,
    )
