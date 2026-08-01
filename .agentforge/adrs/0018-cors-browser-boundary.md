# ADR-0018: Gateway CORS Browser Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #95, #96, #97, #98, #99
- Related ADRs: ADR-0014 (streaming boundary), ADR-0015 (logging boundary)

## Context

The public docs site (https://agentforgit.github.io/agentforge-docs-site/) will host a live gateway playground. Browsers enforce the Same-Origin Policy, and cross-origin requests from that https page to a locally running gateway (`http://127.0.0.1:8080`) fail without CORS cooperation from the gateway.

The gateway is a developer-local service. Its default posture is closed: no authentication, bound to localhost, used by curl/CLI clients. Any CORS behavior must therefore be opt-in so that enabling the playground never weakens the default configuration, and never changes behavior for existing non-browser clients.

## Decision

Add an opt-in `server.cors_origin` string option to the gateway configuration:

- Absent or empty → CORS disabled: the gateway emits no `Access-Control-Allow-*` headers, and `OPTIONS` requests are not specially handled (they fall through to the normal 404 path).
- `"*"` → `Access-Control-Allow-Origin: *` on every response (health, models, chat completions, SSE streams, and all error responses).
- A single `https://` or `http://` origin → that exact origin is echoed in `Access-Control-Allow-Origin` on every response.
- Any other value (non-http(s) scheme, embedded whitespace) → configuration load error.

When CORS is enabled, the gateway:

- Answers `OPTIONS` with HTTP 204 and headers:
  - `Access-Control-Allow-Origin` (as configured),
  - `Access-Control-Allow-Methods: GET, POST, OPTIONS`,
  - `Access-Control-Allow-Headers: Content-Type`,
  - `Access-Control-Max-Age: 86400`.
- Emits `Access-Control-Allow-Origin` on all JSON responses (200/400/404/500) and in the SSE header block of streaming responses.

No `Access-Control-Allow-Credentials` is ever emitted: the gateway has no cookie/session auth, and credentials-based CORS would broaden the trust surface without benefit.

## Consequences

- The web playground can call a local gateway from the public docs site with CORS enabled in the user's local config.
- Default behavior is unchanged for existing clients (no headers emitted, no OPTIONS handling, 404 for unknown paths).
- The `cors_origin` value is configuration, never logged (ADR-0015 privacy rules apply).
- One configured origin (or `*`) is supported; a multi-origin allow-list is deferred and not needed for the playground.
- Streaming SSE responses carry the CORS header in the initial header block, so EventSource/fetch streams work cross-origin.

## Alternatives Considered

- **Always-on `Access-Control-Allow-Origin: *`** — rejected: silently changes the security posture of a local service and would surprise non-browser users.
- **Proxy the playground through a hosted gateway** — rejected: requires public infrastructure, an API-key story, and auth; contradicts the local-first design and the "run on AgentForge" demo goal.
- **Multi-origin allow-list** — deferred: single origin (or `*`) satisfies the docs-site playground; a list can be added later without breaking this ADR's contract.

## Deferred

- Multi-origin allow-list.
- CORS for WebSocket upgrade requests (not currently exposed by the gateway).
