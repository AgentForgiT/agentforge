from __future__ import annotations

from .config import ModelConfig
from .errors import UpstreamProviderError


def normalize_chat_completion_response(
    model: ModelConfig,
    response: object,
) -> dict[str, object]:
    if not isinstance(response, dict):
        raise UpstreamProviderError("provider returned non-object chat completion response")

    _validate_chat_completion_response(response)
    normalized = dict(response)
    normalized["model"] = model.name
    return normalized


def normalize_stream_chunk(model: ModelConfig, chunk: object) -> dict[str, object]:
    if not isinstance(chunk, dict):
        raise UpstreamProviderError("provider returned non-object stream chunk")

    _validate_stream_chunk(chunk)
    normalized = dict(chunk)
    normalized["model"] = model.name
    return normalized


def _validate_chat_completion_response(response: dict[str, object]) -> None:
    if response.get("object") != "chat.completion":
        raise UpstreamProviderError("provider returned invalid chat completion object")

    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise UpstreamProviderError("provider returned invalid chat completion choices")

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise UpstreamProviderError("provider returned invalid chat completion choice")

    message = first_choice.get("message")
    if not isinstance(message, dict):
        raise UpstreamProviderError("provider returned invalid chat completion message")

    if message.get("role") != "assistant":
        raise UpstreamProviderError("provider returned invalid chat completion message role")

    content = message.get("content")
    # OpenAI-compatible spec: content may be null for reasoning models that
    # emit their output in `reasoning` fields (e.g. OpenAI o-series, DeepSeek
    # R1-style, OpenRouter reasoning models). Pass null through untouched.
    if content is not None and not isinstance(content, str):
        raise UpstreamProviderError("provider returned invalid chat completion message content")


def _validate_stream_chunk(chunk: dict[str, object]) -> None:
    if chunk.get("object") != "chat.completion.chunk":
        raise UpstreamProviderError("provider returned invalid stream chunk object")

    choices = chunk.get("choices")
    if not isinstance(choices, list) or not choices:
        raise UpstreamProviderError("provider returned invalid stream chunk choices")

    first_choice = choices[0]
    if not isinstance(first_choice, dict):
        raise UpstreamProviderError("provider returned invalid stream chunk choice")

    delta = first_choice.get("delta")
    if not isinstance(delta, dict):
        raise UpstreamProviderError("provider returned invalid stream chunk delta")

    finish_reason = first_choice.get("finish_reason")
    if finish_reason is not None and not isinstance(finish_reason, str):
        raise UpstreamProviderError("provider returned invalid stream chunk finish reason")
