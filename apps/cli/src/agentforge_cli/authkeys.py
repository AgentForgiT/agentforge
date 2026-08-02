from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys

if "apps/gateway/src" not in " ".join(sys.path):
    _gateway_src = Path(__file__).resolve().parents[2] / "gateway" / "src"
    if _gateway_src.is_dir() and str(_gateway_src) not in sys.path:
        sys.path.insert(0, str(_gateway_src))

from agentforge_gateway.keystore import (  # type: ignore[import-not-found]
    NamedKey,
    generate_key,
    load_key_store,
    load_passphrase_from_env,
    write_encrypted_key_store,
    write_key_store,
)


@dataclass(frozen=True)
class AuthKeyResult:
    errors: tuple[str, ...] = ()
    new_key: str | None = None

    @property
    def ok(self) -> bool:
        return not self.errors


def add_key(
    store_path: Path,
    name: str,
    rate_limit_rpm: int | None = None,
    encrypt: bool = False,
    passphrase_env: str | None = None,
) -> AuthKeyResult:
    if not name.strip():
        return AuthKeyResult(errors=("key name must be non-empty",))
    try:
        keys = load_key_store(store_path) if store_path.is_file() else []
    except ValueError as exc:
        return AuthKeyResult(errors=(str(exc),))
    if any(k.name == name for k in keys):
        return AuthKeyResult(errors=(f"key '{name}' already exists",))
    key = generate_key()
    keys.append(NamedKey(name=name.strip(), key=key, rate_limit_rpm=rate_limit_rpm))
    try:
        if encrypt:
            passphrase = load_passphrase_from_env(passphrase_env or "AGENTFORGE_AUTH_KEYS_PASSPHRASE")
            if not passphrase:
                return AuthKeyResult(errors=("--encrypt requires the passphrase env to be set",))
            write_encrypted_key_store(store_path, keys, passphrase)
        else:
            write_key_store(store_path, keys)
    except OSError as exc:
        return AuthKeyResult(errors=(f"could not write key store: {exc}",))
    return AuthKeyResult(new_key=key)


def list_keys(store_path: Path) -> AuthKeyResult:
    if not store_path.is_file():
        return AuthKeyResult(errors=(f"key store not found: {store_path}",))
    try:
        keys = load_key_store(store_path)
    except ValueError as exc:
        return AuthKeyResult(errors=(str(exc),))
    for key in sorted(keys, key=lambda k: k.name):
        rpm = key.rate_limit_rpm if key.rate_limit_rpm is not None else "unlimited"
        print(f"{key.name}\t{rpm}")
    return AuthKeyResult()


def revoke_key(store_path: Path, name: str) -> AuthKeyResult:
    if not store_path.is_file():
        return AuthKeyResult(errors=(f"key store not found: {store_path}",))
    try:
        keys = load_key_store(store_path)
    except ValueError as exc:
        return AuthKeyResult(errors=(str(exc),))
    remaining = [k for k in keys if k.name != name]
    if len(remaining) == len(keys):
        return AuthKeyResult(errors=(f"key '{name}' not found",))
    if not remaining:
        return AuthKeyResult(errors=("refusing to revoke the last key (store must stay non-empty)",))
    try:
        write_key_store(store_path, remaining)
    except OSError as exc:
        return AuthKeyResult(errors=(f"could not write key store: {exc}",))
    return AuthKeyResult()
