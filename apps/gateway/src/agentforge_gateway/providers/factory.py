from __future__ import annotations

from collections.abc import Callable

from ..config import ProviderConfig
from ..errors import ProviderConfigurationError
from .base import ChatProvider
from .mock import MockProvider
from .ollama import OllamaProvider
from .openrouter import OpenRouterProvider


ProviderBuilder = Callable[[ProviderConfig], ChatProvider]


def _build_mock_provider(config: ProviderConfig) -> ChatProvider:
    return MockProvider()


PROVIDER_BUILDERS: dict[str, ProviderBuilder] = {
    "mock": _build_mock_provider,
    "ollama": OllamaProvider,
    "openrouter": OpenRouterProvider,
}


def build_provider(config: ProviderConfig) -> ChatProvider:
    builder = PROVIDER_BUILDERS.get(config.type)
    if builder is None:
        raise ProviderConfigurationError(f"unsupported provider type: {config.type}")
    return builder(config)


def supported_provider_types() -> tuple[str, ...]:
    return tuple(sorted(PROVIDER_BUILDERS))
