from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any
import json
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

    Translation-at-the-edge (ADR-0019/0020): provider adapters stay OpenAI-compatible.
    - `tools` -> OpenAI function tools
    - assistant `tool_use` blocks -> OpenAI `tool_calls`
    - user `tool_result` blocks -> OpenAI `tool` role messages
    - `thinking` accepted and passed through in the raw body (not mapped; ADR-0020)
    """
    openai_messages: list[dict[str, object]] = []

    system = request.body.get("system")
    if system:
        openai_messages.append({"role": "system", "content": _system_text(system)})

    for message in request.messages:
        openai_messages.extend(_message_to_openai(message))

    openai_body = dict(request.body)
    openai_body["model"] = request.model
    openai_body["messages"] = openai_messages
    openai_body["stream"] = request.stream

    tools = request.body.get("tools")
    if tools is not None:
        openai_body["tools"] = _tools_to_openai(tools)

    return openai_body


def _message_to_openai(message: dict[str, object]) -> list[dict[str, object]]:
    role = message["role"]
    content = message["content"]

    if isinstance(content, str):
        return [{"role": role, "content": content}]

    if not isinstance(content, list):
        raise BadRequestError("message content must be a string or a list of blocks")

    if role == "assistant":
        return _assistant_blocks_to_openai(content)
    if role == "user":
        return _user_blocks_to_openai(content)
    raise BadRequestError(f"unsupported Anthropic message role: {role}")


def _assistant_blocks_to_openai(blocks: list[object]) -> list[dict[str, object]]:
    text_parts: list[str] = []
    tool_calls: list[dict[str, object]] = []
    for block in blocks:
        if not isinstance(block, dict):
            raise BadRequestError("content blocks must be objects")
        block_type = block.get("type")
        if block_type == "text":
            text_parts.append(str(block.get("text", "")))
        elif block_type == "tool_use":
            tool_id = block.get("id")
            name = block.get("name")
            if not isinstance(tool_id, str) or not isinstance(name, str):
                raise BadRequestError("tool_use block requires string id and name")
            tool_calls.append(
                {
                    "id": tool_id,
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": json.dumps(block.get("input") or {}),
                    },
                }
            )
        else:
            raise BadRequestError(
                f"unsupported Anthropic content block type '{block_type}' in assistant message"
            )

    if not tool_calls:
        return [{"role": "assistant", "content": "\n".join(text_parts)}]
    return [{"role": "assistant", "content": "\n".join(text_parts) or None, "tool_calls": tool_calls}]


def _user_blocks_to_openai(blocks: list[object]) -> list[dict[str, object]]:
    text_parts: list[str] = []
    tool_results: list[dict[str, object]] = []
    for block in blocks:
        if not isinstance(block, dict):
            raise BadRequestError("content blocks must be objects")
        block_type = block.get("type")
        if block_type == "text":
            text_parts.append(str(block.get("text", "")))
        elif block_type == "tool_result":
            tool_call_id = block.get("tool_use_id")
            if not isinstance(tool_call_id, str):
                raise BadRequestError("tool_result block requires a string tool_use_id")
            tool_results.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": _tool_result_text(block.get("content")),
                }
            )
        else:
            raise BadRequestError(
                f"unsupported Anthropic content block type '{block_type}' in user message"
            )

    messages: list[dict[str, object]] = []
    if text_parts:
        messages.append({"role": "user", "content": "\n".join(text_parts)})
    messages.extend(tool_results)
    return messages


def _tool_result_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                parts.append(str(part.get("text", "")))
        return "\n".join(parts)
    raise BadRequestError("tool_result content must be a string or a list of text parts")


def _tools_to_openai(tools: object) -> list[dict[str, object]]:
    if not isinstance(tools, list):
        raise BadRequestError("tools must be a list")
    converted: list[dict[str, object]] = []
    for tool in tools:
        if not isinstance(tool, dict):
            raise BadRequestError("each tool must be an object")
        name = tool.get("name")
        if not isinstance(name, str):
            raise BadRequestError("each tool requires a string name")
        converted.append(
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool.get("description") or "",
                    "parameters": tool.get("input_schema") or {"type": "object", "properties": {}},
                },
            }
        )
    return converted


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

    content_blocks: list[dict[str, object]] = []
    if content:
        content_blocks.append({"type": "text", "text": content})

    tool_calls = message.get("tool_calls")
    if isinstance(tool_calls, list):
        for call in tool_calls:
            if not isinstance(call, dict):
                raise UpstreamProviderError("provider returned invalid tool call")
            call_id = call.get("id")
            fn = call.get("function")
            if not isinstance(call_id, str) or not isinstance(fn, dict):
                raise UpstreamProviderError("provider returned invalid tool call shape")
            name = fn.get("name")
            arguments = fn.get("arguments")
            if not isinstance(name, str) or not isinstance(arguments, str):
                raise UpstreamProviderError("provider returned invalid tool call function")
            try:
                parsed_input = json.loads(arguments) if arguments else {}
            except json.JSONDecodeError:
                parsed_input = {}
            content_blocks.append(
                {
                    "type": "tool_use",
                    "id": call_id,
                    "name": name,
                    "input": parsed_input,
                }
            )

    return {
        "id": f"msg_{uuid.uuid4().hex[:24]}",
        "type": "message",
        "role": "assistant",
        "content": content_blocks,
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
    message_start -> content_block_start* -> content_block_delta* ->
    content_block_stop* -> message_delta -> message_stop.

    Text deltas and tool-call input_json deltas are emitted per block
    (text block index 0 when present; tool-use blocks follow at index 1+).
    """
    message_id = f"msg_{uuid.uuid4().hex[:24]}"
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

    text_block_started = False
    tool_blocks: dict[int, dict[str, object]] = {}  # index -> {"id", "name"}

    def ensure_text_block() -> bool:
        nonlocal text_block_started
        if text_block_started:
            return False
        text_block_started = True
        return True

    for chunk in stream:
        choices = chunk.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise UpstreamProviderError("provider returned invalid stream chunk")
        first = choices[0]
        delta = first.get("delta")
        if isinstance(delta, dict):
            piece = delta.get("content")
            if isinstance(piece, str) and piece:
                if ensure_text_block():
                    yield "content_block_start", {
                        "type": "content_block_start",
                        "index": 0,
                        "content_block": {"type": "text", "text": ""},
                    }
                text_parts.append(piece)
                yield "content_block_delta", {
                    "type": "content_block_delta",
                    "index": 0,
                    "delta": {"type": "text_delta", "text": piece},
                }

            tool_calls = delta.get("tool_calls")
            if isinstance(tool_calls, list):
                for call in tool_calls:
                    if not isinstance(call, dict):
                        raise UpstreamProviderError("provider returned invalid stream tool call")
                    index = call.get("index")
                    if not isinstance(index, int):
                        raise UpstreamProviderError("provider returned invalid stream tool call index")
                    fn = call.get("function")
                    if isinstance(fn, dict):
                        name = fn.get("name")
                        if isinstance(name, str) and name:
                            if index not in tool_blocks:
                                tool_blocks[index] = {"id": f"toolu_{uuid.uuid4().hex[:24]}", "name": name}
                                block_index = _block_index(index)
                                yield "content_block_start", {
                                    "type": "content_block_start",
                                    "index": block_index,
                                    "content_block": {
                                        "type": "tool_use",
                                        "id": tool_blocks[index]["id"],
                                        "name": name,
                                        "input": {},
                                    },
                                }
                        arguments = fn.get("arguments")
                        if isinstance(arguments, str) and arguments:
                            if index not in tool_blocks:
                                tool_blocks[index] = {"id": f"toolu_{uuid.uuid4().hex[:24]}", "name": ""}
                            block_index = _block_index(index)
                            yield "content_block_delta", {
                                "type": "content_block_delta",
                                "index": block_index,
                                "delta": {"type": "input_json_delta", "partial_json": arguments},
                            }

        finish = first.get("finish_reason")
        if isinstance(finish, str) and finish:
            stop_reason = _stop_reason(first)

    # close blocks: text first, then tool blocks (index 0 text, 1+ tools)
    if text_block_started:
        yield "content_block_stop", {"type": "content_block_stop", "index": 0}
    for index in sorted(tool_blocks):
        block_index = _block_index(index)
        yield "content_block_stop", {"type": "content_block_stop", "index": block_index}

    yield "message_delta", {
        "type": "message_delta",
        "delta": {"stop_reason": stop_reason or "end_turn", "stop_sequence": None},
        "usage": {"output_tokens": max(1, len("".join(text_parts).split()))},
    }
    yield "message_stop", {"type": "message_stop"}


def _block_index(tool_index: int) -> int:
    # text block occupies index 0 when present; tool blocks start at 1
    return tool_index + 1


def _system_text(system: object) -> str:
    if isinstance(system, str):
        return system
    blocks: list[str] = []
    for block in system:  # type: ignore[union-attr]
        if not isinstance(block, dict) or block.get("type") != "text":
            raise BadRequestError("system blocks must be text blocks")
        blocks.append(str(block.get("text", "")))
    return "\n".join(blocks)


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
    if finish == "tool_calls":
        return "tool_use"
    return "end_turn"
