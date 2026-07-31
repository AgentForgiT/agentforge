# ADR-0014: Add OpenAI-Compatible SSE Streaming with Gateway-Owned Chunk Normalization

Metadata:

- Status: Accepted
- Date: 2026-07-24
- Deciders: AgentForge maintainers
- Related issues: #75, #76, #77, #78, #79
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0010, ADR-0011, ADR-0012
- Related requirements: `.agentforge/requirements/gateway-streaming-mvp.md`

## Context

The gateway has established explicit internal boundaries for provider adapters, request validation, error responses, and successful response normalization.

Streaming is currently rejected in request validation with `streaming responses are not supported yet`.

Streaming is the most requested OpenAI-compatible capability for an AI gateway: agentic coding tools and chat interfaces commonly enable `stream: true` by default. Sprint 17 needs a streaming boundary decision before implementation because streaming changes request validation, the provider protocol, response normalization, and HTTP delivery at the same time.

The decision must answer:

- how providers expose incremental output
- what the public chunk contract looks like
- who owns chunk validation and model alias normalization
- how errors behave before and during a stream
- what remains deferred

## Decision

Add OpenAI-compatible SSE streaming to `apps/gateway` during Genesis Sprint 17.

Request validation will accept `stream: true` as a boolean flag and expose it on the typed request result.

The provider protocol will gain a streaming method that returns an iterator of chunk dictionaries.

The gateway will own the streaming chunk contract through a normalizer in `agentforge_gateway.responses`, consistent with the ADR-0012 response normalization boundary.

The HTTP handler will deliver streaming responses with `Content-Type: text/event-stream`, flushing each chunk as it is produced, and terminating with `data: [DONE]`.

The mock provider will produce deterministic chunks that assemble to its non-streaming content.

The OpenRouter provider will forward `stream: true` to the upstream endpoint, translate upstream chunk events, and normalize the public gateway model alias on each chunk.

## Streaming Contract

A streaming response is an SSE sequence of `data:` events:

- chunk objects use `object: "chat.completion.chunk"`
- chunks carry the public gateway model alias
- chunk choices contain `delta` objects
- the first content chunk carries the assistant role delta
- a final chunk carries an empty delta and `finish_reason: "stop"`
- the stream terminates with `data: [DONE]`

Chunks in one stream share the same completion id and created timestamp.

## Boundary Rules

Request validation owns:

- `stream` boolean acceptance and typing
- rejection of non-boolean stream values
- preserving the request body for providers

Provider adapters own:

- incremental output production
- provider-specific chunk translation
- provider-specific transport and credential behavior

Response normalization owns:

- minimal streaming chunk shape validation
- public gateway model alias normalization on chunks
- translation of malformed provider chunks to `UpstreamProviderError`

HTTP handling owns:

- `text/event-stream` content type
- per-chunk flushing
- `[DONE]` termination
- JSON error envelopes for failures before the stream starts

## Error Semantics

Errors detected before the first chunk is written use the standard JSON error envelope with the appropriate status code.

Errors detected after streaming has started cannot change the HTTP status. The MVP terminates the stream safely without writing further chunks. Gateway error events inside a stream are deferred.

## Compatibility

Sprint 17 must preserve:

- non-streaming chat completion behavior
- existing gateway HTTP endpoints
- current mock and OpenRouter provider behavior for non-streaming requests
- current configuration examples
- offline CI validation

Clients that never set `stream` observe no change.

## Consequences

Benefits:

- makes the gateway usable by streaming-first clients
- keeps chunk contract authority with the gateway rather than adapters
- gives future providers a single streaming method to implement
- keeps default tests offline and deterministic
- preserves all existing internal boundaries

Trade-offs:

- adds a second HTTP delivery mode to the handler
- streaming error handling is weaker than non-streaming (no status change mid-stream)
- the mock stream is deterministic but does not simulate real token timing
- OpenRouter translation assumes upstream OpenAI-compatible SSE framing

## Alternatives Considered

Keep rejecting streaming:
Rejected because streaming is the most common client expectation for chat completion APIs and is explicitly deferred work in the product backlog.

Buffer the full provider response and send it as one chunk:
Rejected because it defeats the purpose of streaming and misrepresents incremental delivery.

Let provider adapters own chunk validation:
Rejected because ADR-0012 established that the gateway owns its public response contract.

Adopt a web framework for streaming support:
Rejected because the Genesis gateway intentionally remains dependency-free and the stdlib HTTP server can deliver SSE with explicit flushing.

Send gateway error events mid-stream in the MVP:
Deferred because error-event framing, client expectations, and provider behaviour need more design; the MVP documents the safe-termination limitation instead.

## Follow-Up Work

- Revisit streaming usage summaries and `stream_options` after usage requirements exist.
- Consider gateway error events inside streams for a later sprint.
- Keep future provider streaming adapters routed through the chunk normalizer.
- Revisit provider contract tests to cover the streaming contract for new providers.

## Revision History

- 2026-07-24: Accepted for Genesis Sprint 17.
