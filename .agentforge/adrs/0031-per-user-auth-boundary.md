# ADR-0031: Per-User Auth Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #170, #171, #172, #173, #174
- Related: ADR-0023 (API-key auth + rate limiting), DEC-0006 (semver)

## Context

ADR-0023 shipped a single shared static key (`server.api_key_env`) and deferred per-user keys. Teams sharing a gateway need to distinguish who is calling (audit, per-user limits, revocation) without a full identity service. The gateway has no user model, no database, and a stdlib-only ethos — a user registry is out of scope, but a **file-based named key store** is exactly the right size.

## Decision

Add a **named key store**:

- `server.auth_keys_file` points to a JSON store: `{"keys": [{"name", "key", "rate_limit_rpm"}]}`, schema-validated at load; malformed → startup configuration error (fail fast).
- Gateway auth checks the store first; the existing `api_key_env` shared key remains valid alongside (both paths work) — fully backward compatible.
- **Per-key token buckets**: each named key gets its own bucket at its own `rate_limit_rpm` (reusing ADR-0023's limiter, keyed by name). Missing per-key limit falls back to the global `server.rate_limit_rpm`, else unlimited.
- **CLI management** (`agentforge auth-key add|list|revoke`): generates keys with `secrets` (stdlib), writes the store, prints a new key exactly once at `add` time, never re-prints or logs keys.
- Keys never logged (ADR-0015); file permission guidance documented (0600 POSIX).

## Consequences

- Teams get per-user/per-workload identities with independent limits and revocation — the production auth story ADR-0023 deferred.
- The store is a plain JSON file: inspectable, versionable, no database.
- The shared-key path keeps working, so existing single-key deployments upgrade with a config line, not a migration.
- Security is bounded: the store holds plaintext keys (like the env var did); this is a local-trust tool, not an internet service.

## Alternatives Considered

- **Real user registry + DB** — rejected: the gateway has no database and should not gain one for Genesis-era scale; the file store covers teams.
- **Hashed keys in the store** — rejected: hashing breaks the CLI's one-time-print contract and adds complexity without a server-side secret; plaintext in a 0600 file matches the local-trust model.
- **JWT per user** — rejected: needs an issuer; overkill for named keys.

## Deferred

- Key rotation scheduling (revoke + add covers it manually).
- Store encryption at rest.
- Distributed/Redis rate limiting (single-process buckets remain).
- Trusted-proxy `X-Forwarded-For` handling.
