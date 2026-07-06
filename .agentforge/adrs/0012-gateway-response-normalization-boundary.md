# ADR-0012: Normalize Gateway Chat Completion Responses

Metadata:

- Status: Accepted
- Date: 2026-07-06
- Deciders: AgentForge maintainers
- Related issues: #60, #63, #61, #64, #62
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0009, ADR-0010, ADR-0011
- Related requirements: `.agentforge/requirements/gateway-response-normalization-mvp.md`

## Context

The gateway has established internal boundaries for provider adapters, provider contract tests, chat-completion request validation, and JSON error responses.

Successful provider responses are still normalized implicitly. The OpenRouter adapter rewrites upstream response model names to the public gateway alias, while the mock provider already emits the public alias directly.

That behavior is acceptable for the current MVP, but the success response boundary should not live accidentally inside individual adapters. Future providers should not be able to leak upstream model identifiers or malformed success bodies through the public gateway API.

Sprint 14 needs a small response normalization boundary that keeps the gateway dependency-free and preserves the existing public API behavior.

## Decision

Add a gateway-owned chat-completion response normalization helper.

The response boundary will live in `agentforge_gateway.responses` and will:

- validate the minimal successful chat-completion response shape expected by the gateway
- copy provider response dictionaries before normalizing them
- set the public gateway model alias on successful chat-completion responses
- raise `UpstreamProviderError` when a provider returns a malformed success response

`GatewayApp.chat_completions()` will call the normalizer after provider dispatch.

Provider adapters will continue to own provider-specific request mapping, authentication, upstream HTTP behavior, and upstream error translation.

No schema validation framework or runtime dependency will be introduced during Sprint 14.

## Boundary Rules

Response normalization owns:

- minimal success response shape checks
- public gateway model alias normalization
- malformed provider success response translation to upstream provider errors
- preserving provider-supplied fields that are not explicitly normalized

Provider adapters own:

- provider-specific payload construction
- provider-specific authentication
- provider-specific upstream error translation
- provider-specific transport behavior
- parsing upstream JSON into response dictionaries

Request validation owns:

- incoming client request shape
- unsupported streaming rejection
- preserving request bodies passed to providers

Error handling owns:

- standard JSON error envelopes
- HTTP status mapping for gateway errors
- route-level response delivery

Provider contract tests own:

- adapter conformance to the minimal provider response contract
- offline provider behavior checks

## Compatibility

Sprint 14 must preserve existing behavior for:

- gateway success endpoint availability
- request validation behavior
- provider contract tests
- error envelopes and status mappings
- public model alias behavior
- offline CI validation

The normalizer may reject malformed provider success responses that previously could pass through as `200` responses. That is an intentional hardening of the provider boundary.

## Consequences

Benefits:

- makes successful response normalization easy to find and review
- gives future provider adapters a reusable gateway-level response boundary
- prevents upstream model identifiers from leaking through the public gateway model field
- converts malformed provider success bodies into explicit upstream provider failures
- keeps Genesis dependency-free

Trade-offs:

- adds a small internal helper module
- keeps response validation intentionally minimal during Genesis
- does not yet attempt full OpenAI response schema compatibility
- does not implement streaming response behavior

## Alternatives Considered

Keep response normalization inside provider adapters:
Rejected because provider adapters should own provider-specific mapping and transport behavior, while the gateway should own its public response contract.

Trust provider contract tests without runtime normalization:
Rejected because tests reduce drift but do not protect clients from malformed provider success responses at runtime.

Adopt a full schema validation library:
Rejected because the Genesis gateway intentionally remains dependency-free and the current response surface is small.

Define full OpenAI response compatibility now:
Rejected because broader response compatibility should follow explicit requirements after the current gateway boundary is stable.

Implement streaming support now:
Rejected because streaming changes HTTP response behavior, provider contracts, request validation, and test strategy. It needs its own requirements and ADR.

## Follow-Up Work

- Revisit the response contract when streaming support is designed.
- Add richer OpenAI-compatible response handling only through explicit requirements.
- Keep future provider adapters routed through the response normalizer.
- Consider response metadata such as request IDs only after logging and observability requirements exist.

## Revision History

- 2026-07-06: Accepted for Genesis Sprint 14.
