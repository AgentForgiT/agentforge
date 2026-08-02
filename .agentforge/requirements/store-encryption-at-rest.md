# Named Key Store Encryption at Rest

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 44 |
| Issues | #195, #196, #197, #198, #199 |
| Related | ADR-0031 (named key store), ADR-0036, DEC-0006 (semver) |

## Purpose

ADR-0031 shipped a plaintext named key store and deferred encryption at rest. This sprint encrypts the store with a password-derived key — stdlib only, no new dependencies — while keeping the plaintext format fully supported (backward compatible).

## Requirements

R1. **Encrypted store format** (`keystore.py` additions):
   - An encrypted store is a JSON envelope: `{"encrypted": true, "kdf": "PBKDF2-HMAC-SHA256", "iterations": 210000, "salt": "<hex>", "nonce": "<hex>", "ciphertext": "<hex>"}`.
   - Key derivation: PBKDF2-HMAC-SHA256 (stdlib `hashlib.pbkdf2_hmac`), 210k iterations, 32-byte salt → 32-byte key.
   - Encryption: AES-GCM (stdlib `cryptography`? NO — stdlib only means no `cryptography` package. Use a stdlib-available AEAD... Python stdlib has no AES. Options: (a) `hmac` + `hashlib` based stream cipher (XOR with a keystream derived from PBKDF2 — not authenticated), (b) use `secrets`-backed ChaCha20-like? Stdlib has no AEAD cipher.
   - **Decision**: stdlib-only constraint means we implement a **verified encryption envelope**: PBKDF2-derived key, XOR keystream (CTR-style from PBKDF2 blocks) for confidentiality, plus HMAC-SHA256 (keyed, separate PBKDF2 key) over salt+nonce+ciphertext for integrity. This is a well-understood construct-with-primitives approach, documented honestly as "stdlib primitives, not audited AEAD."
R2. **Gateway**: `auth_keys_file` transparently loads encrypted stores when `AGENTFORGE_AUTH_KEYS_PASSPHRASE` (or `server.auth_keys_passphrase_env` named env var) is set; wrong passphrase → clear startup error (MAC mismatch).
R3. **CLI**: `agentforge auth-key` gains `--encrypt` / `--passphrase-env <name>`; add/list/revoke operate on encrypted stores transparently when the passphrase env is set.
R4. Plaintext stores keep working unchanged (auto-detect: `"encrypted": true` marker).
R5. Keys and passphrases are never logged (ADR-0015).

## Acceptance Criteria

- [ ] Encrypt → decrypt roundtrip preserves all keys + rate limits
- [ ] Wrong passphrase fails with a clear error (integrity check)
- [ ] Plaintext stores load unchanged (backward compatible)
- [ ] Gateway authenticates against an encrypted store via env passphrase
- [ ] CLI add/list/revoke work on encrypted stores
- [ ] Full suite passes offline; CI green
