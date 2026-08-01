# Gateway CORS Support

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 21 |
| Issues | #95, #96, #97, #98, #99 |
| Related ADRs | ADR-0008 (provider boundary), ADR-0014 (streaming boundary), ADR-0015 (logging boundary) |

## Context

The web playground (docs site quick-wins) needs browsers to call a locally running gateway from an https page. Browsers enforce the Same-Origin Policy, so cross-origin fetch/SSE from `https://agentforgit.github.io/agentforge-docs-site/` to `http://127.0.0.1:8080` is blocked unless the gateway answers CORS preflights and sends `Access-Control-Allow-*` response headers.

The gateway is a local, developer-run service. CORS must be strictly opt-in — never enabled by default — so existing non-browser clients and security posture are unchanged.

## Requirements

### R1: Opt-in CORS via configuration

The gateway must expose a `server.cors_origin` config option (string). When absent or empty, the gateway MUST NOT emit any CORS headers. When set, the gateway MUST emit CORS headers on every response.

**Acceptance criteria:**
- `server.cors_origin` absent → no `Access-Control-Allow-*` headers on any response.
- `server.cors_origin: "*"` → `Access-Control-Allow-Origin: *` on all responses.
- `server.cors_origin: "https://example.com"` → `Access-Control-Allow-Origin: https://example.com` (echoed, not wildcard).
- Invalid values (non-http(s) origins, embedded whitespace) are rejected at config load with a clear error.

### R2: Preflight handling

The gateway must answer `OPTIONS` requests with HTTP 204 and CORS headers when CORS is enabled, and 404 (or 405) when disabled.

**Acceptance criteria:**
- `OPTIONS /v1/chat/completions` with CORS enabled returns 204 with `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods` (GET, POST, OPTIONS), `Access-Control-Allow-Headers` (Content-Type), and `Access-Control-Max-Age`.
- With CORS disabled, `OPTIONS` returns 404 and no CORS headers.

### R3: Headers on all response types

CORS headers must appear on JSON responses (health, models, errors, completions) and on SSE streams.

**Acceptance criteria:**
- `GET /health` includes `Access-Control-Allow-Origin` when enabled.
- `POST /v1/chat/completions` (non-streaming) includes it.
- `POST /v1/chat/completions` (streaming) includes it in the SSE headers.
- Error responses (400/404/500) include it.

### R4: No body or credential leakage

CORS support must not change logging or error behavior. No request bodies, origins beyond the configured value, or credentials are logged (per ADR-0015).

**Acceptance criteria:**
- Log lines keep the existing shape (`method`, `path`, `status`, `duration_ms`).
- The configured origin is not echoed in logs.

### R5: Test coverage

The gateway suite must cover config parsing (valid/invalid), preflight behavior (enabled/disabled), header presence on JSON and SSE responses, and the disabled default.

**Acceptance criteria:**
- All CORS tests run offline with no live server.
- Suite stays green (122 existing + new CORS tests).

## Non-Goals

- No credentials-based CORS (`Access-Control-Allow-Credentials`); the gateway has no cookie/session auth.
- No CORS origin allow-list beyond a single configured origin (or `*`).
- No changes to provider adapters.

## Deliverables

- ADR-0018 recording the CORS browser boundary.
- `server.cors_origin` config + validation.
- `OPTIONS` preflight handler and CORS headers on JSON/SSE responses.
- Config example updated with a commented `cors_origin` entry.
- Tests + full doc updates (CHANGELOG, gateway docs, README, roadmap, milestones, backlog, decisions).
- Genesis-0.0.21 release.
