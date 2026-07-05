# ADR-0011: Centralize Gateway JSON Error Responses

Metadata:

- Status: Accepted
- Date: 2026-07-05
- Deciders: AgentForge maintainers
- Related issues: #57, #59, #55, #58, #56
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0009, ADR-0010
- Related requirements: `.agentforge/requirements/gateway-error-contract-mvp.md`

## Context

The gateway has established internal boundaries for provider adapters, provider contract tests, and chat-completion request validation.

The HTTP handler still constructs some error envelopes inline while `GatewayError` classes construct others through `to_response()`.

The current behavior works, but a scattered error contract makes it easier for future endpoint work to return inconsistent JSON shapes or status mappings.

Sprint 13 needs a small error response boundary that keeps the gateway dependency-free and preserves the existing public API behavior.

## Decision

Centralize gateway JSON error envelope construction in `agentforge_gateway.errors`.

The error boundary will provide helpers for:

- standard error envelope creation
- unknown route errors
- invalid JSON body errors

`GatewayError.to_response()` will use the same helper as HTTP handler code.

The HTTP handler will continue to own status codes and response delivery, while exception classes and helper functions own the JSON body shape.

No middleware framework or runtime dependency will be introduced during Sprint 13.

## Boundary Rules

Error response helpers own:

- standard error body shape
- error type strings for helper-created responses
- human-readable helper messages

Gateway errors own:

- typed gateway exception classes
- status codes for known gateway failures
- conversion to standard error bodies

HTTP handling owns:

- path routing
- exception catching
- HTTP status delivery
- content headers and body bytes

Provider adapters own:

- translating provider-specific failures into gateway error classes

## Compatibility

Sprint 13 must preserve existing behavior for:

- gateway success responses
- request validation errors
- unknown model errors
- provider configuration errors
- upstream provider errors
- unknown route errors
- invalid JSON errors
- offline CI validation

The refactor may update internal helper calls, but it must not require clients to change successful request bodies or configuration.

## Consequences

Benefits:

- makes the JSON error contract easier to find and review
- reduces duplicated inline error dictionaries
- gives future endpoints a reusable error response pattern
- supports endpoint-level regression tests for client-facing failures
- keeps Genesis dependency-free

Trade-offs:

- adds a small amount of helper surface area
- keeps the error contract intentionally minimal during Genesis
- does not yet attempt full OpenAI error compatibility

## Alternatives Considered

Keep inline dictionaries in the HTTP handler:
Rejected because request and provider boundaries have already been clarified, and error responses are the next client-facing contract that should not drift.

Adopt a web framework or middleware layer:
Rejected because the Genesis gateway intentionally remains dependency-free and small.

Define full OpenAI error compatibility now:
Rejected because the current gateway surface is still small. Sprint 13 should preserve the existing envelope and status mapping before broadening compatibility.

Move error construction into provider adapters:
Rejected because provider adapters should translate provider failures into gateway errors, not own HTTP response bodies.

## Follow-Up Work

- Revisit error compatibility when the gateway broadens OpenAI-compatible endpoint coverage.
- Keep future endpoint errors on the standard envelope unless a later ADR supersedes it.
- Consider request IDs or trace metadata only after logging and observability requirements exist.
- Keep provider failures translated into gateway error classes.

## Revision History

- 2026-07-05: Accepted for Genesis Sprint 13.
