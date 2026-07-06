# Gateway Response Normalization MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 14
- Related issues: #60, #63, #61, #64, #62
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0009, ADR-0010, ADR-0011, ADR-0012
- Related policy: `docs/release-policy.md`
- Last updated: 2026-07-06

## Purpose

Define the requirements for normalizing successful chat-completion responses in the AgentForge Gateway.

This document exists so Sprint 14 makes the gateway success response boundary explicit before adding streaming, more providers, or broader OpenAI-compatible response support.

## Scope

In scope:

- successful `/v1/chat/completions` response normalization after provider calls
- public gateway model alias preservation
- minimal chat-completion response shape validation
- malformed provider success response handling
- offline tests and documentation

Out of scope:

- adding streaming support
- changing request validation behavior
- changing the gateway error envelope
- adding new provider integrations
- implementing full OpenAI response schema validation
- adding runtime dependencies
- publishing gateway packages

## Background

The gateway already validates chat-completion requests, isolates provider adapters, tests provider contracts offline, and returns errors through a standard JSON envelope.

Successful provider responses still pass through the gateway with only adapter-local behavior. The OpenRouter adapter currently rewrites the response `model` field to the public gateway alias, while the mock provider already returns that alias directly.

That behavior works for the current MVP, but the boundary is implicit. Sprint 14 should centralize minimal success response normalization so future providers cannot accidentally leak upstream model names or malformed response shapes through the public gateway API.

## Architecture

Sprint 14 introduces an internal `agentforge_gateway.responses` module.

`GatewayApp.chat_completions()` remains responsible for request validation, model lookup, provider selection, and provider dispatch. After provider dispatch, it passes the provider response and selected public model configuration to the response normalizer.

Provider adapters continue to produce provider-specific chat-completion response dictionaries. The normalizer provides a gateway-owned final guard for the public success response contract.

## User Workflows

The MVP must support these workflows:

- A client receives a successful chat-completion response with the requested public gateway model alias.
- A contributor can find the response normalization helper without reading provider adapters.
- A maintainer can add future providers without inventing a new success response boundary.
- CI can validate response normalization without network access or provider credentials.
- Existing request validation, provider contract, and error response behavior remains unchanged.

## Response Normalization Requirements

The gateway must normalize successful chat-completion responses after provider dispatch.

The normalizer must:

- accept provider responses as JSON object dictionaries
- preserve provider-supplied fields unless explicitly normalized
- require the `chat.completion` object marker
- require a non-empty `choices` list
- require the first assistant message to include string `content`
- force the public gateway model alias into the response `model` field
- raise an upstream provider error for malformed provider success responses

The normalizer must not:

- mutate the provider response object in place
- synthesize a full response when required provider fields are absent
- validate every OpenAI-compatible optional field during Genesis
- implement streaming response semantics

## Compatibility Requirements

Sprint 14 must preserve:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- current request validation messages
- current error response envelope and status mappings
- current provider configuration and upstream error classes
- current mock and OpenRouter provider behavior
- current config examples
- default offline test behavior

## Testing and CI Requirements

Tests must cover:

- response normalizer preserves provider fields and sets the public model alias
- response normalizer does not mutate the provider response object
- missing or malformed `object`, `choices`, `message`, and `content` fields fail clearly
- gateway app uses the normalization boundary after provider dispatch
- malformed provider success responses return an upstream provider error envelope over HTTP
- regression coverage for existing success endpoints and provider contracts

CI must not require network access, provider credentials, or live upstream providers.

## Documentation Requirements

Documentation must explain:

- the gateway response normalization boundary
- how response normalization relates to providers and provider contract tests
- why streaming and full OpenAI response schema validation remain deferred
- how to run the gateway tests locally
- current Sprint 14 limitations

## Acceptance Criteria

Issue #60 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references ADR-0012
- it defines Sprint 14 response normalization scope before implementation begins

The Sprint 14 response normalization milestone is complete when:

- issue #63 records ADR-0012
- issue #61 implements the response normalization helper boundary
- issue #64 validates response normalization behavior locally and in CI
- issue #62 documents the boundary and prepares `Genesis-0.0.14`

## Examples

Provider response before normalization:

```json
{
  "object": "chat.completion",
  "model": "upstream/provider-model",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Done."
      },
      "finish_reason": "stop"
    }
  ]
}
```

Gateway response after normalization for public model `agentforge-coder`:

```json
{
  "object": "chat.completion",
  "model": "agentforge-coder",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Done."
      },
      "finish_reason": "stop"
    }
  ]
}
```

Expected validation command:

```bash
python -m unittest discover -s apps/gateway/tests
```

## Best Practices

- Keep response normalization centralized.
- Keep provider-specific request mapping and upstream error translation inside provider adapters.
- Keep the normalizer minimal until broader OpenAI compatibility requirements exist.
- Treat malformed provider success bodies as upstream provider failures.
- Keep default response tests offline and deterministic.

## Risks

- Over-validating provider responses too early could reject useful OpenAI-compatible optional shapes.
- Under-validating provider responses can let malformed success responses become public API behavior.
- Adding response schema frameworks during Genesis would add avoidable complexity.
- Moving too much behavior out of providers could blur provider-specific mapping boundaries.

## References

- `.agentforge/adrs/0002-gateway-module-placement.md`
- `.agentforge/adrs/0008-gateway-provider-boundary.md`
- `.agentforge/adrs/0009-gateway-provider-contract-testing.md`
- `.agentforge/adrs/0010-gateway-request-validation-boundary.md`
- `.agentforge/adrs/0011-gateway-error-response-boundary.md`
- `.agentforge/adrs/0012-gateway-response-normalization-boundary.md`
- `apps/gateway/README.md`
- `docs/gateway.md`

## Revision History

- 2026-07-06: Initial requirements draft for Genesis Sprint 14.
