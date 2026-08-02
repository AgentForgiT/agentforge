# Gateway: API-Key Auth and Rate Limiting

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 27 |
| Issues | #120, #121, #122, #123, #124 |
| Related ADRs | ADR-0015 (logging — never log keys), ADR-0017 (keyless local trust — this is the opt-in credentialed extension), ADR-0018 (CORS — 401/429 must carry CORS headers) |

## Background

The gateway is keyless by design (ADR-0017): a local trust-boundary device with no credentials. The Compatibility Matrix and provider work (Sprint 19–25) grew its reach — the gateway now fronts cloud providers (OpenRouter, Anthropic) that hold real keys, and exposes a CORS-enabled web surface. A team sharing a gateway on a LAN, or exposing one behind a reverse proxy, needs opt-in auth and abuse protection.

This sprint adds **opt-in static API-key auth** and **token-bucket rate limiting** while preserving the keyless default — no existing workflow changes when unconfigured.

## Requirements

R1. **Opt-in API-key auth**: `server.api_key_env` names an environment variable (e.g. `AGENTFORGE_API_KEY`) whose value gates access. When set:
   - `Authorization: Bearer <key>` or `x-api-key: <key>` accepted on `/v1/chat/completions` and `/v1/messages`.
   - Missing/wrong key → 401 with the standard error envelope (OpenAI surface) or Anthropic envelope (Messages surface).
   - `GET /health` stays unauthenticated (liveness probes); `GET /v1/models` and `OPTIONS` (preflight) follow the configured surface rules — preflight must succeed without auth for browser clients (CORS).
   - The key is read from the environment at startup, never logged (ADR-0015), never committed.
R2. **Opt-in rate limiting**: `server.rate_limit_rpm` (requests per minute) applies a token bucket per client:
   - bucket keyed by API key when auth is on, else by client IP.
   - Exceeding the limit → 429 with error envelope + `Retry-After` header.
   - `GET /health` exempt (probes must never be throttled).
R3. **Defaults unchanged**: with `api_key_env` and `rate_limit_rpm` unset, behavior is byte-for-byte the keyless, unthrottled gateway of Genesis 0.0.25. All existing tests pass unchanged.
R4. **CORS integration**: 401 and 429 responses carry `Access-Control-Allow-Origin` when CORS is enabled (ADR-0018).
R5. **Config validation**: `server.api_key_env` must be a non-empty string naming an env var; `server.rate_limit_rpm` must be a positive integer when present.
R6. All tests offline and deterministic (injected clock and transport); no new dependencies (stdlib `time` bucket).

## Acceptance Criteria

- [ ] Auth on: 401 for missing/wrong key; 200 with correct key; health unauthenticated
- [ ] Rate limit on: 429 after N requests in a window; `Retry-After` present; health exempt
- [ ] Both off: identical to Genesis 0.0.25 behavior (existing suite green)
- [ ] 401/429 carry CORS headers when CORS configured
- [ ] Config validation rejects bad `api_key_env`/`rate_limit_rpm`
- [ ] Key never logged; full suite passes offline
