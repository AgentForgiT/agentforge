from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import hashlib
import hmac
import json
import secrets


@dataclass(frozen=True)
class NamedKey:
    name: str
    key: str
    rate_limit_rpm: int | None = None


PBKDF2_ITERATIONS = 210_000


def load_key_store(path: Path) -> list[NamedKey]:
    """Load the named key store (ADR-0031 / ADR-0036).

    Auto-detects the encrypted format ("encrypted": true) and requires
    the passphrase from the AGENTFORGE_AUTH_KEYS_PASSPHRASE env var.
    Raises ValueError on malformed content (fail-fast at startup).
    """
    if not path.is_file():
        raise ValueError(f"auth key store not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"auth key store is not valid JSON: {path}: {exc}") from exc

    if isinstance(data, dict) and data.get("encrypted") is True:
        data = decrypt_store(data, _passphrase())

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


def _passphrase() -> str:
    import os

    passphrase = os.environ.get("AGENTFORGE_AUTH_KEYS_PASSPHRASE")
    if not passphrase:
        raise ValueError(
            "encrypted key store requires AGENTFORGE_AUTH_KEYS_PASSPHRASE to be set"
        )
    return passphrase


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


def write_encrypted_key_store(path: Path, keys: list[NamedKey], passphrase: str) -> None:
    """Write the store as an encrypted envelope (ADR-0036)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "keys": [
            {"name": k.name, "key": k.key, **({"rate_limit_rpm": k.rate_limit_rpm} if k.rate_limit_rpm else {})}
            for k in keys
        ]
    }
    envelope = encrypt_store(payload, passphrase)
    path.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")


def load_passphrase_from_env(env_name: str = "AGENTFORGE_AUTH_KEYS_PASSPHRASE") -> str | None:
    import os

    return os.environ.get(env_name)


def encrypt_store(payload: dict[str, Any], passphrase: str) -> dict[str, Any]:
    """Encrypt the store payload (ADR-0036).

    Construct-with-primitives, stdlib only (no AES in the stdlib):
    - PBKDF2-HMAC-SHA256 (210k iterations) derives an encryption key
      and a MAC key from the passphrase + random salt.
    - Confidentiality: XOR keystream (PBKDF2 counter mode, a stream
      cipher construct).
    - Integrity: HMAC-SHA256 over salt+nonce+ciphertext (encrypt-then-
      MAC) with the separate MAC key.
    Documented honestly: stdlib primitives, not an audited AEAD.
    """
    plaintext = json.dumps(payload).encode("utf-8")
    salt = secrets.token_bytes(32)
    nonce = secrets.token_bytes(16)
    enc_key, mac_key = _derive_keys(passphrase, salt)
    ciphertext = _xor_keystream(enc_key, nonce, plaintext)
    mac = hmac.new(mac_key, salt + nonce + ciphertext, hashlib.sha256).digest()
    return {
        "encrypted": True,
        "kdf": "PBKDF2-HMAC-SHA256",
        "iterations": PBKDF2_ITERATIONS,
        "salt": salt.hex(),
        "nonce": nonce.hex(),
        "mac": mac.hex(),
        "ciphertext": ciphertext.hex(),
    }


def decrypt_store(envelope: dict[str, Any], passphrase: str) -> dict[str, Any]:
    """Decrypt an encrypted store envelope (ADR-0036).

    Raises ValueError on wrong passphrase or tampered data (MAC check).
    """
    try:
        iterations = int(envelope.get("iterations", PBKDF2_ITERATIONS))
        salt = bytes.fromhex(envelope["salt"])
        nonce = bytes.fromhex(envelope["nonce"])
        mac = bytes.fromhex(envelope["mac"])
        ciphertext = bytes.fromhex(envelope["ciphertext"])
    except (KeyError, ValueError) as exc:
        raise ValueError("encrypted key store is malformed") from exc

    enc_key, mac_key = _derive_keys(passphrase, salt, iterations)
    expected = hmac.new(mac_key, salt + nonce + ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, expected):
        raise ValueError("key store decryption failed: wrong passphrase or tampered data")

    plaintext = _xor_keystream(enc_key, nonce, ciphertext)
    try:
        payload = json.loads(plaintext.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("key store decryption failed: invalid payload") from exc
    if not isinstance(payload, dict):
        raise ValueError("key store decryption failed: non-object payload")
    return payload


def _derive_keys(passphrase: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> tuple[bytes, bytes]:
    material = hashlib.pbkdf2_hmac("sha256", passphrase.encode("utf-8"), salt, iterations, dklen=64)
    return material[:32], material[32:]


def _xor_keystream(key: bytes, nonce: bytes, data: bytes) -> bytes:
    """XOR data with a keystream: PBKDF2(key, nonce || counter) blocks.

    CTR-style stream cipher construct using PBKDF2 as the PRF.
    """
    out = bytearray()
    counter = 0
    for offset in range(0, len(data), 32):
        block = hashlib.pbkdf2_hmac("sha256", key, nonce + counter.to_bytes(4, "big"), 1, dklen=32)
        out.extend(bytes(a ^ b for a, b in zip(block, data[offset : offset + 32])))
        counter += 1
    return bytes(out)
