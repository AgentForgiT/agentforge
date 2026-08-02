# ADR-0023: API-Key Auth and Rate-Limiting Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #120, #121, #122, #123, #124
- Related ADRs: ADR-0015 (logging boundary — never log credentials), ADR-0017 (keyless local trust — the default this extends), ADR-0018 (CORS — errors carry headers)

## Context

The gateway is keyless by design (ADR-0017): a local trust-boundary device. It now fronts credentialed cloud providers and a CORS-enabled web surface; a shared LAN gateway or a reverse-proxy-exposed instance needs opt-in auth and abuse protection. The keyless default must survive: local single-user workflows change nothing.

## Decision

Add two opt-in server controls, both disabled by default:

1. **Static shared API key** — `server.api_key_env` names an environment variable (e.g. `AGENTFORGE_API_KEY`). When set, `/v1/chat/completions` and `/v1/messages` require `Authorization: Bearer <key>` or `x-api-key: <key>`; missing/wrong key → 401. `GET /health` stays unauthenticated (probes). `OPTIONS` preflight succeeds without auth (browser CORS). The key is read from the environment at startup and never logged (ADR-0015).

2. **Token-bucket rate limiting** — `server.rate_limit_rpm` sets requests-per-minute per client (bucket keyed by API key when auth is on, else by client IP). Exceeding → 429 with `Retry-After`. `GET /health` is exempt.

Rationale for static shared key over per-user keys: the gateway has no user model, no store, and no enrollment flow; a shared key mirrors the trust boundary (one device, one secret) and is the minimum that makes LAN/reverse-proxy exposure defensible. Per-user keys belong with the deferred auth story (see Deferred).

## Consequences

- Default behavior is byte-for-byte unchanged: unset controls mean keyless, unthrottled (Genesis 0.0.25 semantics); the existing suite passes untouched.
- Auth errors and 429s carry CORS headers when CORS is enabled, so browser clients see the right status, not a CORS failure.
- The bucket is in-memory (stdlib `time`); restart resets limits — acceptable for a local gateway.
- Rate limiting without auth keys by IP; behind a proxy, `X-Forwarded-For` is not trusted by default (documented) — the operator should configure the proxy to set it or use auth-keyed buckets.

## Alternatives Considered

- **Per-user API keys with a store** — rejected: needs persistence, enrollment, and rotation UX; deferred until a real multi-user story exists.
- **JWT/OAuth** — rejected: no identity provider; overkill for a local gateway.
- **Reverse-proxy-only enforcement** — rejected: pushes a core safety control out of the product; the gateway should own its boundary.

## Deferred

- Per-user keys, rotation, and a key store.
- Distributed/Redis rate limiting (single-process bucket is fine for Genesis).
- Trusted-proxy `X-Forwarded-For` handling.
- Admin endpoints (key management, bucket stats).
