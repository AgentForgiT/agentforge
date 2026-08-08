from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any

from .logger import SUPPORTED_LOG_LEVELS


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
class McpServerConfig:
    """A remote MCP server the gateway can call (MCP client mode, ADR-0039).

    Keyless by default (local trust boundary, mirroring ADR-0017); an
    optional auth header env name enables token auth without storing secrets
    in the config file.
    """

    name: str
    url: str
    auth_header_env: str | None = None
    timeout_seconds: float = 10.0


@dataclass(frozen=True)
class GatewayConfig:
    host: str
    port: int
    models: dict[str, ModelConfig]
    providers: dict[str, ProviderConfig]
    log_level: str = "INFO"
    cors_origin: str | None = None
    api_key_env: str | None = None
    auth_keys_file: str | None = None
    rate_limit_rpm: int | None = None
    mcp_servers: dict[str, McpServerConfig] = field(default_factory=dict)


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


def parse_config(raw: object) -> GatewayConfig:
    if not isinstance(raw, dict):
        raise ValueError("config must be a JSON object")

    server = _object_field(raw.get("server", {}), "server")
    models = raw.get("models", {})
    providers = raw.get("providers", {})

    if not isinstance(models, dict) or not models:
        raise ValueError("config must define at least one model")

    parsed_providers = _parse_providers(providers)
    parsed_models: dict[str, ModelConfig] = {}
    for name, model in models.items():
        if not isinstance(model, dict):
            raise ValueError(f"model '{name}' must be an object")
        provider = _required_str(model.get("provider"), f"model '{name}'.provider")
        provider_model = _required_str(model.get("provider_model"), f"model '{name}'.provider_model")
        parsed_models[name] = ModelConfig(
            name=name,
            provider=provider,
            provider_model=provider_model,
        )

    for name, model in parsed_models.items():
        if model.provider not in parsed_providers:
            raise ValueError(f"model '{name}' references unknown provider '{model.provider}'")

    return GatewayConfig(
        host=_server_host(server),
        port=_port(server.get("port", 8080), "server.port"),
        log_level=_log_level(server.get("log_level", "INFO"), "server.log_level"),
        cors_origin=_cors_origin(server.get("cors_origin")),
        api_key_env=_optional_env_name(server.get("api_key_env"), "server.api_key_env"),
        auth_keys_file=_optional_str(server.get("auth_keys_file"), "server.auth_keys_file"),
        rate_limit_rpm=_positive_int(server.get("rate_limit_rpm"), "server.rate_limit_rpm"),
        mcp_servers=_parse_mcp_servers(server.get("mcp_servers")),
        models=parsed_models,
        providers=parsed_providers,
    )


def _optional_env_name(value: Any, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string naming an environment variable")
    return value.strip()


def _positive_int(value: Any, label: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{label} must be a positive integer")
    return value


def _cors_origin(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("server.cors_origin must be a string")
    origin = value.strip()
    if not origin:
        return None
    if origin == "*":
        return origin
    if any(char.isspace() for char in origin):
        raise ValueError("server.cors_origin must not contain whitespace")
    if not (origin.startswith("https://") or origin.startswith("http://")):
        raise ValueError("server.cors_origin must be '*' or an http(s) origin")
    return origin


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
        provider_type = _optional_str(provider.get("type", name), f"provider '{name}'.type")
        if provider_type is None:
            raise ValueError(f"provider '{name}'.type must be a non-empty string")

        parsed[name] = ProviderConfig(
            name=name,
            type=provider_type,
            base_url=_optional_str(provider.get("base_url"), f"provider '{name}'.base_url"),
            api_key_env=_optional_str(provider.get("api_key_env"), f"provider '{name}'.api_key_env"),
            timeout_seconds=_positive_number(provider.get("timeout_seconds", 30.0), f"provider '{name}'.timeout_seconds"),
            headers=_headers(provider["headers"] if "headers" in provider else {}, f"provider '{name}'.headers"),
        )

    return parsed


def _parse_mcp_servers(value: Any) -> dict[str, McpServerConfig]:
    """Parse the optional `server.mcp_servers` block (MCP client mode).

    Each entry: `{name, url, auth_header_env?, timeout_seconds?}`.
    Keyless by default (ADR-0039, mirroring ADR-0017's local trust boundary).
    """
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("server.mcp_servers must be an object")
    if not value:
        return {}

    parsed: dict[str, McpServerConfig] = {}
    for name, entry in value.items():
        if not isinstance(entry, dict):
            raise ValueError(f"server.mcp_servers '{name}' must be an object")
        url = _required_str(entry.get("url"), f"server.mcp_servers '{name}'.url")
        parsed[name] = McpServerConfig(
            name=name,
            url=url,
            auth_header_env=_optional_env_name(
                entry.get("auth_header_env"), f"server.mcp_servers '{name}'.auth_header_env"
            ),
            timeout_seconds=_positive_number(
                entry.get("timeout_seconds", 10.0), f"server.mcp_servers '{name}'.timeout_seconds"
            ),
        )
    return parsed


def _server_host(server: dict[str, Any]) -> str:
    if "host" not in server:
        return "127.0.0.1"
    return _required_str(server["host"], "server.host")


def _object_field(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    return value


def _required_str(value: Any, field_name: str) -> str:
    parsed = _optional_str(value, field_name)
    if parsed is None:
        raise ValueError(f"{field_name} must be a non-empty string")
    return parsed


def _optional_str(value: Any, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")
    return value


def _port(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{field_name} must be an integer from 1 to 65535")
    if value < 1 or value > 65535:
        raise ValueError(f"{field_name} must be an integer from 1 to 65535")
    return value


def _log_level(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be one of {', '.join(SUPPORTED_LOG_LEVELS)}")
    normalized = value.strip().upper()
    if normalized not in SUPPORTED_LOG_LEVELS:
        raise ValueError(f"{field_name} must be one of {', '.join(SUPPORTED_LOG_LEVELS)}")
    return normalized


def _positive_number(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be a positive number")
    parsed = float(value)
    if parsed <= 0:
        raise ValueError(f"{field_name} must be a positive number")
    return parsed


def _headers(value: Any, field_name: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object")
    headers: dict[str, str] = {}
    for key, header_value in value.items():
        if not isinstance(key, str) or not isinstance(header_value, str):
            raise ValueError(f"{field_name} keys and values must be strings")
        headers[key] = header_value
    return headers
