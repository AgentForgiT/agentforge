from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any
import time
import uuid

from .config import ModelConfig
from .errors import BadRequestError, UpstreamProviderError
from .responses import normalize_chat_completion_response, normalize_stream_chunk


@dataclass(frozen=True)
class AnthropicMessagesRequest:
    model: str
    messages: list[dict[str, object]]
    body: dict[str, Any]
    stream: bool = False


def validate_anthropic_messages_request(body: dict[str, Any]) -> AnthropicMessagesRequest:
    model = body.get("model")
    messages = body.get("messages")

    if not isinstance(model, str) or not model:
        raise BadRequestError("request requires a model")
    if not isinstance(messages, list) or not messages:
        raise BadRequestError("request requires non-empty messages")

    stream = body.get("stream", False)
    if not isinstance(stream, bool):
        raise BadRequestError("stream must be a boolean")

    validated: list[dict[str, object]] = []
    for message in messages:
        if not isinstance(message, dict) or "role" not in message or "content" not in message:
            raise BadRequestError("each message requires role and content")
        role = message["role"]
        if role not in ("user", "assistant"):
            raise BadRequestError(f"unsupported Anthropic message role: {role}")
        validated.append(message)

    system = body.get("system")
    if system is not None and not isinstance(system, (str, list)):
        raise BadRequestError("system must be a string or a list of text blocks")

    max_tokens = body.get("max_tokens")
    if max_tokens is not None and (not isinstance(max_tokens, int) or max_tokens <= 0):
        raise BadRequestError("max_tokens must be a positive integer")

    return AnthropicMessagesRequest(
        model=model,
        messages=validated,
        body=body,
        stream=stream,
    )


def to_openai_body(request: AnthropicMessagesRequest) -> dict[str, Any]:
    """Translate an Anthropic Messages request into the internal OpenAI-compatible body.

    Translation-at-the-edge (ADR-0019): provider adapters stay OpenAI-compatible.
    Text blocks concatenate; tool_result blocks surface as text; image, tool_use,
    and thinking blocks are rejected (deferred).
    """
    openai_messages: list[dict[str, object]] = []

    system = request.body.get("system")
    if system:
        openai_messages.append({"role": "system", "content": _system_text(system)})

    for message in request.messages:
        openai_messages.append(
            {
                "role": message["role"],
                "content": _content_text(message["content"]),
            }
        )

    openai_body = dict(request.body)
    openai_body["model"] = request.model
    openai_body["messages"] = openai_messages
    openai_body["stream"] = request.stream
    return openai_body


def normalize_anthropic_response(
    model: ModelConfig,
    response: object,
) -> dict[str, object]:
    """Translate a normalized OpenAI chat completion into the Anthropic Messages shape."""
    if not isinstance(response, dict):
        raise UpstreamProviderError("provider returned non-object chat completion response")

    choices = response.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise UpstreamProviderError("provider returned invalid chat completion choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise UpstreamProviderError("provider returned invalid chat completion message")

    content = message.get("content")
    if content is not None and not isinstance(content, str):
        raise UpstreamProviderError("provider returned invalid chat completion message content")

    usage = response.get("usage")
    input_tokens = _usage_tokens(usage, "prompt_tokens")
    output_tokens = _usage_tokens(usage, "completion_tokens")

    return {
        "id": f"msg_{uuid.uuid4().hex[:24]}",
        "type": "message",
        "role": "assistant",
        "content": [{"type": "text", "text": content or ""}],
        "model": model.name,
        "stop_reason": _stop_reason(choices[0]),
        "stop_sequence": None,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        },
    }


def anthropic_sse_events(
    model: ModelConfig,
    stream: Iterator[dict[str, object]],
) -> Iterator[tuple[str, dict[str, object]]]:
    """Translate normalized OpenAI stream chunks into Anthropic SSE events.

    Yields (event_name, data) pairs in Anthropic's event order:
    message_start -> content_block_start -> content_block_delta* ->
    content_block_stop -> message_delta -> message_stop.
    """
    message_id = f"msg_{uuid.uuid4().hex[:24]}"
    created = int(time.time())
    text_parts: list[str] = []
    stop_reason: str | None = None

    yield "message_start", {
        "type": "message_start",
        "message": {
            "id": message_id,
            "type": "message",
            "role": "assistant",
            "content": [],
            "model": model.name,
            "stop_reason": None,
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        },
    }
    yield "content_block_start", {
        "type": "content_block_start",
        "index": 0,
        "content_block": {"type": "text", "text": ""},
    }

    for chunk in stream:
        choices = chunk.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise UpstreamProviderError("provider returned invalid stream chunk")
        first = choices[0]
        delta = first.get("delta")
        if isinstance(delta, dict):
            piece = delta.get("content")
            if isinstance(piece, str) and piece:
                text_parts.append(piece)
                yield "content_block_delta", {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": piece},
                }
        finish = first.get("finish_reason")
        if isinstance(finish, str) and finish:
            stop_reason = _stop_reason(first)

    yield "content_block_stop", {"type": "content_block_stop", "index": 0}
    yield "message_delta", {
        "type": "message_delta",
        "delta": {"stop_reason": stop_reason or "end_turn", "stop_sequence": None},
        "usage": {"output_tokens": max(1, len("".join(text_parts).split()))},
    }
    yield "message_stop", {"type": "message_stop"}


def _system_text(system: object) -> str:
    if isinstance(system, str):
        return system
    blocks: list[str] = []
    for block in system:  # type: ignore[union-attr]
        if not isinstance(block, dict) or block.get("type") != "text":
            raise BadRequestError("system blocks must be text blocks")
        blocks.append(str(block.get("text", "")))
    return "\n".join(blocks)


def _content_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        raise BadRequestError("message content must be a string or a list of blocks")
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            raise BadRequestError("content blocks must be objects")
        block_type = block.get("type")
        if block_type == "text":
            parts.append(str(block.get("text", "")))
        elif block_type == "tool_result":
            tool_content = block.get("content", "")
            if isinstance(tool_content, list):
                tool_text = "".join(
                    str(b.get("text", "")) for b in tool_content if isinstance(b, dict) and b.get("type") == "text"
                )
                parts.append(tool_text)
            else:
                parts.append(str(tool_content))
        else:
            raise BadRequestError(
                f"unsupported Anthropic content block type '{block_type}' (deferred in ADR-0019)"
            )
    return "\n".join(parts)


def _usage_tokens(usage: object, key: str) -> int:
    if isinstance(usage, dict):
        value = usage.get(key)
        if isinstance(value, int):
            return value
    return 0


def _stop_reason(choice: dict[str, object]) -> str:
    finish = choice.get("finish_reason")
    if finish == "length":
        return "max_tokens"
    if finish == "content_filter":
        return "refusal"
    return "end_turn"
