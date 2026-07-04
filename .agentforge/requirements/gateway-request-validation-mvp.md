# Gateway Request Validation MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 12
- Related issues: #50, #52, #54, #51, #53
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0009, ADR-0010
- Related policy: `docs/release-policy.md`
- Last updated: 2026-07-05

## Purpose

Define the requirements for separating gateway chat-completion request validation from gateway routing and provider orchestration.

This document exists so Sprint 12 strengthens the gateway application boundary before adding streaming, more providers, or broader request schema support.

## Scope

In scope:

- internal chat-completion request validation module inside `apps/gateway`
- focused validation tests for current request requirements
- preservation of provider payload forwarding
- preservation of current error messages for model, messages, stream, and message-shape validation
- documentation of the request validation boundary
- local and CI validation evidence

Out of scope:

- streaming support
- new OpenAI-compatible request parameters
- external schema dependencies
- changing the public HTTP API surface
- changing provider adapters
- changing gateway configuration format
- extracting shared packages
- publishing gateway packages

## Background

The Genesis gateway already exposes an OpenAI-compatible `/v1/chat/completions` endpoint and validates the minimum request shape before calling provider adapters.

Before Sprint 12, request validation lived inline in `GatewayApp.chat_completions`. That is acceptable for the first MVP, but it mixes request validation with model lookup and provider dispatch.

Sprints 10 and 11 hardened the provider boundary and provider contract tests. Sprint 12 should apply the same discipline to request validation while preserving runtime behavior.

## User Workflows

The MVP must support these workflows:

- A contributor can locate chat-completion request validation without reading gateway routing code.
- A maintainer can add future request parameters without touching provider adapter logic.
- CI can validate request boundary behavior offline.
- Gateway users can continue using existing request bodies unchanged.
- Streaming requests continue to receive a clear unsupported error during Genesis.

## Boundary Requirements

The gateway must expose an internal request validation boundary inside `apps/gateway`.

The request validation boundary must:

- validate the required `model` field
- validate non-empty `messages`
- reject unsupported streaming requests
- validate that each message has `role` and `content`
- return a small typed result for app orchestration
- preserve the original request body passed to providers

Gateway routing must continue to own HTTP paths and JSON body reading.

Provider adapters must not own gateway request validation.

## Compatibility Requirements

Sprint 12 must preserve:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- current mock provider behavior
- current OpenRouter payload forwarding
- current error messages for invalid chat-completion requests
- current behavior of forwarding optional provider parameters such as `temperature`
- current config examples
- default offline test behavior

## Testing and CI Requirements

Tests must cover:

- valid chat-completion request validation
- missing or empty model rejection
- missing, non-list, or empty messages rejection
- unsupported streaming rejection
- malformed message rejection
- preservation of extra provider payload fields
- regression coverage for existing gateway endpoint behavior

CI must not require network access, provider credentials, or live upstream providers.

## Documentation Requirements

Documentation must explain:

- the internal request validation boundary
- why streaming remains unsupported during Genesis
- how request validation relates to provider dispatch
- how to run the gateway tests locally
- current Sprint 12 limitations

## Acceptance Criteria

Issue #50 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references ADR-0010
- it defines Sprint 12 request validation scope before implementation begins

The Sprint 12 request validation milestone is complete when:

- issue #52 records ADR-0010
- issue #54 implements the internal request validation module
- issue #51 validates request boundary behavior locally and in CI
- issue #53 documents the boundary and prepares `Genesis-0.0.12`

## Examples

Expected internal dependency direction:

```text
GatewayApp.chat_completions -> validate_chat_completion_request -> provider dispatch
```

Expected validation command:

```bash
python -m unittest discover -s apps/gateway/tests
```

## Best Practices

- Keep HTTP routing separate from request validation.
- Keep provider adapters separate from gateway request validation.
- Preserve provider payload forwarding for optional request fields.
- Avoid schema libraries until the API surface justifies them.
- Keep streaming rejection explicit until streaming is intentionally designed.

## Risks

- Over-validating too early could reject OpenAI-compatible request shapes the gateway should later support.
- Under-validating can let malformed requests reach providers.
- Adding a schema dependency during Genesis would increase ceremony before need.
- Implementing streaming without an RFC would blur the release scope.

## References

- `.agentforge/adrs/0002-gateway-module-placement.md`
- `.agentforge/adrs/0008-gateway-provider-boundary.md`
- `.agentforge/adrs/0009-gateway-provider-contract-testing.md`
- `.agentforge/adrs/0010-gateway-request-validation-boundary.md`
- `.agentforge/requirements/gateway-reconciliation.md`
- `apps/gateway/README.md`
- `docs/gateway.md`

## Revision History

- 2026-07-05: Initial requirements draft for Genesis Sprint 12.
