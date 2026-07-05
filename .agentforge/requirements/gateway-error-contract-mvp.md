# Gateway Error Contract MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 13
- Related issues: #57, #59, #55, #58, #56
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0009, ADR-0010, ADR-0011
- Related policy: `docs/release-policy.md`
- Last updated: 2026-07-05

## Purpose

Define the requirements for a predictable JSON error contract in the AgentForge Gateway.

This document exists so Sprint 13 makes gateway error responses explicit before the gateway adds streaming, more providers, or broader OpenAI-compatible request support.

## Scope

In scope:

- standard JSON error envelope construction
- HTTP status mapping for known gateway errors
- unknown route error responses
- invalid JSON request body responses
- non-object JSON request body responses
- request validation error responses
- unknown model error responses
- provider configuration and upstream error responses
- offline tests and documentation

Out of scope:

- changing success response shapes
- adding streaming support
- adding new provider integrations
- adding exception middleware frameworks
- changing provider adapter behavior
- adding runtime dependencies
- publishing gateway packages

## Background

The gateway already returns JSON errors through `GatewayError.to_response()` and a few inline HTTP-handler dictionaries.

That is enough for the MVP, but the error contract is split across exception classes and route handling. Sprint 13 should centralize the response envelope helper and add focused endpoint tests so future gateway work does not accidentally drift.

## User Workflows

The MVP must support these workflows:

- A client receives a predictable JSON error envelope for known gateway failures.
- A contributor can find the error response helper without reading route handlers.
- A maintainer can add future gateway errors without inventing a new response shape.
- CI can validate error behavior without network access or provider credentials.
- Success-path gateway behavior remains unchanged.

## Error Contract Requirements

Gateway error responses must use this shape:

```json
{
  "error": {
    "message": "human-readable message",
    "type": "machine_readable_type"
  }
}
```

The gateway must preserve current status mappings:

- bad request: `400`
- unknown model: `404`
- provider configuration error: `500`
- upstream provider error: `502`
- unknown route: `404`

## Compatibility Requirements

Sprint 13 must preserve:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- current request validation messages
- current provider configuration and upstream error classes
- current success response bodies
- current config examples
- default offline test behavior

## Testing and CI Requirements

Tests must cover:

- error envelope helper behavior
- invalid JSON request body response
- non-object JSON request body response
- unknown route response
- request validation error response
- unknown model response
- provider configuration error response
- upstream provider error response
- regression coverage for existing success endpoints

CI must not require network access, provider credentials, or live upstream providers.

## Documentation Requirements

Documentation must explain:

- the standard gateway error envelope
- status mapping for known gateway errors
- how error responses relate to request validation and providers
- how to run the gateway tests locally
- current Sprint 13 limitations

## Acceptance Criteria

Issue #57 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references ADR-0011
- it defines Sprint 13 error contract scope before implementation begins

The Sprint 13 error contract milestone is complete when:

- issue #59 records ADR-0011
- issue #55 implements the error response helper boundary
- issue #58 validates error contract behavior locally and in CI
- issue #56 documents the contract and prepares `Genesis-0.0.13`

## Examples

Expected not-found response:

```json
{
  "error": {
    "message": "not found",
    "type": "not_found"
  }
}
```

Expected validation command:

```bash
python -m unittest discover -s apps/gateway/tests
```

## Best Practices

- Keep error envelope construction centralized.
- Keep HTTP status mapping explicit.
- Keep provider-specific error translation inside provider adapters.
- Do not expose provider secrets or raw stack traces in JSON errors.
- Keep default error tests offline and deterministic.

## Risks

- Over-specifying the error contract too early could make later OpenAI compatibility changes harder.
- Under-testing error paths can let client-facing behavior drift silently.
- Adding middleware frameworks during Genesis would add avoidable complexity.

## References

- `.agentforge/adrs/0002-gateway-module-placement.md`
- `.agentforge/adrs/0010-gateway-request-validation-boundary.md`
- `.agentforge/adrs/0011-gateway-error-response-boundary.md`
- `.agentforge/requirements/gateway-reconciliation.md`
- `apps/gateway/README.md`
- `docs/gateway.md`

## Revision History

- 2026-07-05: Initial requirements draft for Genesis Sprint 13.
