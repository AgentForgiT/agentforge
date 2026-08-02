# Per-User Auth: Named Key Store

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 39 |
| Issues | #170, #171, #172, #173, #174 |
| Related | ADR-0023 (auth/rate-limit base), ADR-0031, DEC-0006 (semver) |

## Purpose

ADR-0023 shipped a single shared API key (`server.api_key_env`) and deferred per-user keys. This sprint adds the production story: a **named key store** where each key belongs to a user/workload with its own rate limit, managed by a CLI command — while keeping the shared-key path fully backward compatible.

## Requirements

R1. **Key store** (`server.auth_keys_file`): a JSON file with named keys:
   ```json
   {
     "keys": [
       {"name": "alice", "key": "af-k-...", "rate_limit_rpm": 60},
       {"name": "ci-bot", "key": "af-k-...", "rate_limit_rpm": 300}
     ]
   }
   ```
   Schema-validated on load; malformed file → configuration error at startup (fail fast).
R2. **Gateway auth**: when the store is configured, `Authorization: Bearer <key>` / `x-api-key: <key>` authenticates against the store. The shared `api_key_env` key also still works when set (both paths valid). Unknown key → 401.
R3. **Per-key rate limiting**: each named key gets its own token bucket at its own `rate_limit_rpm` (ADR-0023's limiter, keyed per name). A key without `rate_limit_rpm` uses the global `server.rate_limit_rpm` if set, else unlimited. 429 on exceed.
R4. **CLI management** (`agentforge auth-key`):
   - `auth-key add --name <n> [--rate-limit <rpm>] [--file <path>]` — generates a key (`af-k-<random>`), writes it to the store, prints the name + key **once**, then never again.
   - `auth-key list --file <path>` — prints names + rate limits (never keys).
   - `auth-key revoke --name <n> --file <path>` — removes a key.
   - Store created if absent; never logged, never printed except the one-time add output.
R5. Keys use a random hex suffix (stdlib `secrets`); store file permissions guidance documented (0600 on POSIX).
R6. All tests offline; the shared-key tests from ADR-0023 remain green.

## Acceptance Criteria

- [ ] Gateway authenticates against the store; unknown key → 401
- [ ] Per-key rate limits enforced (key A limited at 60, key B at 300)
- [ ] `api_key_env` shared key still works alongside the store
- [ ] `auth-key add/list/revoke` manage the store; keys never re-printed
- [ ] Malformed store → startup configuration error
- [ ] Full suite passes offline; CI green
