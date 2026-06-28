from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ModelConfig:
    name: str
    provider: str
    provider_model: str


@dataclass(frozen=True)
class ProviderConfig:
    name: str
    type: str
    base_url: str | None = None
    api_key_env: str | None = None
    timeout_seconds: float = 30.0
    headers: dict[str, str] | None = None


@dataclass(frozen=True)
class GatewayConfig:
    host: str
    port: int
    models: dict[str, ModelConfig]
    providers: dict[str, ProviderConfig]


DEFAULT_CONFIG = GatewayConfig(
    host="127.0.0.1",
    port=8080,
    models={
        "mock-coder": ModelConfig(
            name="mock-coder",
            provider="mock",
            provider_model="mock-coder-v1",
        )
    },
    providers={
        "mock": ProviderConfig(
            name="mock",
            type="mock",
        )
    },
)


def load_config(path: str | Path | None = None) -> GatewayConfig:
    if path is None:
        return DEFAULT_CONFIG

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return parse_config(raw)


def parse_config(raw: dict[str, Any]) -> GatewayConfig:
    server = raw.get("server", {})
    models = raw.get("models", {})
    providers = raw.get("providers", {})

    if not isinstance(models, dict) or not models:
        raise ValueError("config must define at least one model")

    parsed_providers = _parse_providers(providers)
    parsed_models: dict[str, ModelConfig] = {}
    for name, model in models.items():
        if not isinstance(model, dict):
            raise ValueError(f"model '{name}' must be an object")
        provider = model.get("provider")
        provider_model = model.get("provider_model")
        if not provider or not provider_model:
            raise ValueError(f"model '{name}' requires provider and provider_model")
        parsed_models[name] = ModelConfig(
            name=name,
            provider=str(provider),
            provider_model=str(provider_model),
        )

    for name, model in parsed_models.items():
        if model.provider not in parsed_providers:
            raise ValueError(f"model '{name}' references unknown provider '{model.provider}'")

    return GatewayConfig(
        host=str(server.get("host", "127.0.0.1")),
        port=int(server.get("port", 8080)),
        models=parsed_models,
        providers=parsed_providers,
    )


def _parse_providers(providers: Any) -> dict[str, ProviderConfig]:
    if providers is None:
        providers = {}
    if not isinstance(providers, dict):
        raise ValueError("providers must be an object")
    if not providers:
        return {
            "mock": ProviderConfig(
                name="mock",
                type="mock",
            )
        }

    parsed: dict[str, ProviderConfig] = {}
    for name, provider in providers.items():
        if not isinstance(provider, dict):
            raise ValueError(f"provider '{name}' must be an object")
        provider_type = str(provider.get("type", name))
        headers = provider.get("headers")
        if headers is not None and not isinstance(headers, dict):
            raise ValueError(f"provider '{name}' headers must be an object")

        parsed[name] = ProviderConfig(
            name=name,
            type=provider_type,
            base_url=_optional_str(provider.get("base_url")),
            api_key_env=_optional_str(provider.get("api_key_env")),
            timeout_seconds=float(provider.get("timeout_seconds", 30.0)),
            headers={str(key): str(value) for key, value in (headers or {}).items()},
        )

    return parsed


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)
