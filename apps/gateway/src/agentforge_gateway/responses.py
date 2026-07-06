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

    if not isinstance(message.get("content"), str):
        raise UpstreamProviderError("provider returned invalid chat completion message content")
