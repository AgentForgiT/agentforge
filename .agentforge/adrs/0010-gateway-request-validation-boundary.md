# ADR-0010: Separate Gateway Chat Completion Request Validation

Metadata:

- Status: Accepted
- Date: 2026-07-05
- Deciders: AgentForge maintainers
- Related issues: #50, #52, #54, #51, #53
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0009
- Related requirements: `.agentforge/requirements/gateway-request-validation-mvp.md`

## Context

The gateway now has explicit provider adapter modules and offline provider contract tests.

Request validation for `/v1/chat/completions` still lives inside `GatewayApp.chat_completions` with model lookup and provider dispatch.

That shape works for the Genesis MVP, but it will become harder to maintain when the gateway later adds more OpenAI-compatible request fields, streaming behavior, or richer validation rules.

Sprint 12 needs a small internal boundary improvement that does not change the public HTTP API or introduce schema dependencies.

## Decision

Create an internal request validation module inside `apps/gateway`.

The module will validate the current chat-completion request requirements and return a small typed result that `GatewayApp` can use for model lookup and provider dispatch.

The request validation module will preserve the original request body so provider adapters continue receiving optional request fields unchanged.

The gateway will keep streaming unsupported during Genesis. Streaming support requires later design work because it affects HTTP response behavior, provider contracts, tests, and documentation.

No external schema validation dependency will be introduced during Sprint 12.

## Boundary Rules

Request validation owns:

- required `model` field validation
- required non-empty `messages` validation
- unsupported streaming rejection
- per-message `role` and `content` presence validation
- typed validation result construction

Gateway app orchestration owns:

- model registry lookup
- selected provider lookup
- provider dispatch

HTTP handling owns:

- path routing
- JSON body decoding
- HTTP status and response delivery

Provider adapters own:

- provider-specific payload mapping
- provider-specific authentication
- provider-specific upstream error translation
- provider-specific response normalization

## Compatibility

Sprint 12 must preserve existing behavior for:

- gateway HTTP endpoints
- mock provider request handling
- OpenRouter payload forwarding
- current invalid request error messages
- existing configuration examples
- offline CI validation

The refactor may update internal imports, but it must not require users to change request bodies or configuration.

## Consequences

Benefits:

- makes request validation easier to find and test
- keeps `GatewayApp` focused on orchestration
- preserves optional provider payload fields
- creates a safer place for future request-field support
- keeps Genesis dependency-free

Trade-offs:

- adds a small internal module during Genesis
- keeps validation intentionally minimal
- defers streaming design and richer request schemas

## Alternatives Considered

Keep validation inline in `GatewayApp`:
Rejected because provider and contract boundaries have matured, and request validation is now the next mixed responsibility in the gateway app.

Adopt a schema validation library:
Rejected because the current request surface does not justify a runtime dependency during Genesis.

Implement streaming support now:
Rejected because streaming changes response semantics, provider contracts, and test strategy. It needs its own requirements and ADR.

Move validation into provider adapters:
Rejected because request validation is gateway API behavior, while providers own provider-specific mapping and upstream behavior.

## Follow-Up Work

- Revisit validation when streaming support is designed.
- Add richer OpenAI-compatible request field handling only through explicit requirements.
- Consider schema tooling only when the request surface becomes too broad for simple validation.
- Keep provider payload forwarding covered by tests.

## Revision History

- 2026-07-05: Accepted for Genesis Sprint 12.
