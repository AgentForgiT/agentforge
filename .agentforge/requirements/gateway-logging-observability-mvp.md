# Gateway Logging and Observability MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 18
- Related issues: #80, #81, #82, #83, #84
- Related decisions: ADR-0001, ADR-0002, ADR-0010, ADR-0011, ADR-0013
- Related policy: `docs/release-policy.md`
- Last updated: 2026-07-31

## Purpose

Define the requirements for structured gateway logging in the AgentForge Gateway.

This document exists so gateway request logging can be implemented after requirements and architecture coverage, without expanding the HTTP surface, configuration surface, or provider contract in an undocumented way.

## Scope

In scope:

- structured access logging for gateway HTTP requests
- per-request status, method, path, and duration capture
- chat-completion context logging with model and stream flag
- configurable log level through `server.log_level`
- strict log level validation consistent with ADR-0013
- logging tests and CI validation
- documentation of the logging contract and release limitations

Out of scope:

- request body or response body logging
- credential or header logging
- provider adapter logging
- metrics endpoints
- request IDs and trace IDs
- distributed tracing
- log file rotation, shipping, or aggregation
- changing the gateway HTTP contract
- adding runtime dependencies

## Background

The gateway currently suppresses HTTP access logging by overriding `log_message` with a no-op.

Sprint 18 introduces structured, level-filtered access logging while keeping the gateway dependency-free and its default tests deterministic.

Logging touches three existing surfaces at once:

- HTTP handling must record status, timing, and request context
- configuration parsing must accept and validate a log level
- tests must assert on log records without depending on wall-clock text

The MVP should introduce logging without weakening the ADR-0011 error contract, the ADR-0010 request validation boundary, or the ADR-0013 configuration validation boundary.

## User Workflows

The MVP must support these workflows:

- A gateway operator can observe which endpoints are requested and with what status.
- A gateway operator can raise or lower log verbosity through configuration without code changes.
- A contributor can reason about gateway request traffic from structured log records.
- CI can validate logging behavior without network access or provider credentials.
- Existing gateway behavior remains unchanged for clients.

## Logging Requirements

The gateway must log one access record per HTTP request handled.

Access records must include:

- HTTP method
- request path
- response status code
- elapsed time in milliseconds

The gateway must log chat-completion context after successful request validation, including:

- the requested model
- the stream flag

Request and response bodies must never be logged.

Headers and credentials must never be logged.

Unexpected handler exceptions must produce a `500` access record through the standard handler error path.

## Log Level Requirements

The gateway must support log levels `DEBUG`, `INFO`, `WARNING`, and `ERROR`.

The default log level must be `INFO` when configuration omits `server.log_level`.

`server.log_level` must be validated against the supported levels with a case-insensitive match.

An invalid `server.log_level` value must be rejected with a configuration error.

Access records must be emitted at `INFO` level.

Chat-completion context records must be emitted at `INFO` level.

Unexpected handler errors must be emitted at `ERROR` level.

## Implementation Requirements

Logging must use the Python standard library `logging` module.

The gateway must own a logger namespace distinct from third-party loggers.

Log output must remain deterministic for tests: tests must assert on structured log records, not on formatted timestamps.

The access record must remain available even when the handler is embedded in a custom server.

## Compatibility Requirements

Sprint 18 must preserve:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions` non-streaming and streaming behavior
- current JSON error envelopes and status mappings
- current configuration examples
- default offline test behavior
- the default mock provider behavior

Clients must observe no change in HTTP behavior.

## Testing and CI Requirements

Tests must cover:

- access records for known routes with method, path, and status
- access records for unknown routes
- chat-completion context records with model and stream flag
- streaming requests producing stream context records
- level filtering (records suppressed below the configured level)
- invalid `server.log_level` rejection
- default log level behavior
- no request body or credential content in log records
- unexpected handler errors producing `500` records

CI must continue to require no network access, provider credentials, or live upstream providers.

## Documentation Requirements

Documentation must explain:

- the structured access record shape
- the log level configuration option and default
- the explicit exclusion of bodies and credentials
- the current Sprint 18 limitations (no metrics, no request IDs, no provider logging)

## Acceptance Criteria

Issue #80 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references ADR-0010, ADR-0011, and ADR-0013
- it defines the Sprint 18 logging scope before implementation begins

The Sprint 18 logging milestone is complete when:

- issue #81 records ADR-0015
- issue #82 implements logging in `apps/gateway`
- issue #83 adds logging tests and CI validation
- issue #84 documents logging and prepares `Genesis-0.0.18`

## Examples

Configuration with explicit log level:

```json
{
  "server": {
    "host": "127.0.0.1",
    "port": 8080,
    "log_level": "INFO"
  },
  "providers": {
    "mock": { "type": "mock" }
  },
  "models": {
    "mock-coder": { "provider": "mock", "provider_model": "mock-coder-v1" }
  }
}
```

Expected access record fields:

```text
method=POST path=/v1/chat/completions status=200 duration_ms=3
chat_completion model=mock-coder stream=false
```

## Best Practices

- Keep access records structured and greppable.
- Never log bodies, headers, or credentials.
- Validate log level at configuration parse time.
- Emit access records at `INFO` and unexpected errors at `ERROR`.
- Keep tests deterministic by asserting on log records, not formatted output.

## Risks

- Logging could accidentally include sensitive fields; body and credential exclusion must be explicit and tested.
- Over-verbose logging could obscure signal; the default `INFO` level keeps access records visible without debug noise.
- A malformed log level should fail configuration, not default silently.

## References

- `.agentforge/adrs/0002-gateway-module-placement.md`
- `.agentforge/adrs/0010-gateway-request-validation-boundary.md`
- `.agentforge/adrs/0011-gateway-error-response-boundary.md`
- `.agentforge/adrs/0013-gateway-configuration-validation-boundary.md`
- `apps/gateway/README.md`
- `docs/gateway.md`

## Revision History

- 2026-07-31: Initial requirements draft for Genesis Sprint 18.
