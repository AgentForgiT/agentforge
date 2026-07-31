# ADR-0015: Add Structured Access Logging with Configurable Log Level

Metadata:

- Status: Accepted
- Date: 2026-07-31
- Deciders: AgentForge maintainers
- Related issues: #80, #81, #82, #83, #84
- Related decisions: ADR-0001, ADR-0002, ADR-0010, ADR-0011, ADR-0013
- Related requirements: `.agentforge/requirements/gateway-logging-observability-mvp.md`

## Context

The gateway currently suppresses HTTP access logging by overriding `log_message` with a no-op.

Operators and contributors have no structured way to observe gateway request traffic: which endpoints are requested, with what status, and how long requests take.

Logging touches three existing surfaces at once:

- HTTP handling must record status, timing, and request context
- configuration parsing must accept and validate a log level
- tests must assert on log records without depending on wall-clock text

The decision must answer:

- who owns logging
- what the access record looks like
- how the log level is configured and validated
- what is explicitly excluded from logs
- what observability remains deferred

## Decision

Add structured access logging to `apps/gateway` during Genesis Sprint 18 using the Python standard library `logging` module.

The gateway will own a logger namespace and emit one access record per HTTP request with method, path, status code, and elapsed time in milliseconds.

The gateway will emit a chat-completion context record after successful request validation with the requested model and stream flag.

The log level will be configurable through `server.log_level` with strict validation consistent with ADR-0013, defaulting to `INFO`.

Request bodies, response bodies, headers, and credentials will never be logged.

Provider adapters will not emit gateway logs during Genesis; provider-side logging remains deferred.

## Logging Boundary

HTTP handling owns:

- per-request timing
- status capture
- access record emission
- unexpected error records

Configuration parsing owns:

- `server.log_level` acceptance
- strict level validation
- default level behavior

The gateway logger namespace owns:

- structured record shape
- level filtering
- deterministic test capture

Provider adapters own:

- no logging during Genesis (deferred)
- provider-specific diagnostics only in later sprints

## Access Record

Access records are emitted at `INFO` with structured fields:

```text
method=POST path=/v1/chat/completions status=200 duration_ms=3
```

Chat-completion context records are emitted at `INFO` after successful validation:

```text
chat_completion model=mock-coder stream=false
```

Unexpected handler errors are emitted at `ERROR` with the access fields and status `500`.

## Configuration

`server.log_level` accepts `DEBUG`, `INFO`, `WARNING`, and `ERROR` with a case-insensitive match.

The default is `INFO` when `server.log_level` is omitted.

An invalid value is rejected at configuration parse time.

## Privacy Rules

The gateway must never log:

- request bodies
- response bodies
- headers
- credentials or API keys

Body and credential exclusion is explicit and covered by tests.

## Consequences

Benefits:

- operators can observe gateway traffic and status
- log verbosity is configurable without code changes
- logging stays dependency-free and deterministic in tests
- the ADR-0013 config boundary extends cleanly to the log level
- no new HTTP or provider contract surface

Trade-offs:

- access records do not yet include request IDs or trace IDs
- provider-level diagnostics are not logged
- metrics endpoints and structured telemetry remain future work
- streaming requests log at response initiation (time to first byte)

## Alternatives Considered

Keep logging suppressed:
Rejected because operators cannot observe gateway behavior, which is the stated purpose of the observability sprint.

Log raw `BaseHTTPRequestHandler` default lines:
Rejected because default format is not structured, not level-filtered, and cannot carry chat-completion context.

Log request bodies for debugging:
Rejected because request bodies contain user prompts; privacy rules must be explicit.

Let provider adapters log through the gateway logger:
Deferred because provider logging needs its own boundary decision; the MVP keeps provider logging out of scope.

Adopt a structured logging library:
Rejected because the Genesis gateway intentionally remains dependency-free and stdlib `logging` covers the MVP.

Add metrics endpoints or request IDs now:
Deferred because they expand the HTTP surface and need requirements of their own; the access record is the Sprint 18 observability baseline.

## Follow-Up Work

- Consider request IDs and trace IDs for correlating gateway and provider activity.
- Consider provider latency and error logging behind a provider-side boundary decision.
- Consider a metrics endpoint once logging proves its value.
- Keep log level validation aligned with future configuration surface.

## Revision History

- 2026-07-31: Accepted for Genesis Sprint 18.
