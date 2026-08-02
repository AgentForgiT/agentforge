from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import secrets


@dataclass(frozen=True)
class NamedKey:
    name: str
    key: str
    rate_limit_rpm: int | None = None


def load_key_store(path: Path) -> list[NamedKey]:
    """Load and validate the named key store (ADR-0031).

    Raises ValueError on malformed content (fail-fast at startup).
    """
    if not path.is_file():
        raise ValueError(f"auth key store not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"auth key store is not valid JSON: {path}: {exc}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("keys"), list):
        raise ValueError("auth key store must be an object with a 'keys' list")

    keys: list[NamedKey] = []
    seen_names: set[str] = set()
    for entry in data["keys"]:
        if not isinstance(entry, dict):
            raise ValueError("each key entry must be an object")
        name = entry.get("name")
        key = entry.get("key")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("each key entry requires a non-empty 'name'")
        if not isinstance(key, str) or not key.strip():
            raise ValueError(f"key entry '{name}' requires a non-empty 'key'")
        if name in seen_names:
            raise ValueError(f"duplicate key name: {name}")
        seen_names.add(name)
        rpm = entry.get("rate_limit_rpm")
        if rpm is not None and (not isinstance(rpm, int) or isinstance(rpm, bool) or rpm <= 0):
            raise ValueError(f"key entry '{name}' has an invalid rate_limit_rpm")
        keys.append(NamedKey(name=name, key=key, rate_limit_rpm=rpm))

    if not keys:
        raise ValueError("auth key store must contain at least one key")
    return keys


def generate_key() -> str:
    return "af-k-" + secrets.token_hex(16)


def write_key_store(path: Path, keys: list[NamedKey]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "keys": [
            {"name": k.name, "key": k.key, **({"rate_limit_rpm": k.rate_limit_rpm} if k.rate_limit_rpm else {})}
            for k in keys
        ]
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
