# Gateway Streaming MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 17
- Related issues: #75, #76, #77, #78, #79
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0010, ADR-0011, ADR-0012
- Related policy: `docs/release-policy.md`
- Last updated: 2026-07-24

## Purpose

Define the requirements for streaming chat completions in the AgentForge Gateway.

This document exists so `stream: true` requests can be implemented after requirements and architecture coverage, without expanding the HTTP surface, provider contract, or response contract in an undocumented way.

## Scope

In scope:

- OpenAI-compatible server-sent event (SSE) streaming for chat completions
- `stream: true` acceptance in request validation
- a provider streaming method on the provider protocol
- deterministic mock provider streaming
- OpenRouter SSE forwarding with public model alias normalization
- gateway-owned streaming chunk normalization
- `text/event-stream` HTTP delivery
- streaming tests and CI validation
- documentation of the streaming contract and release limitations

Out of scope:

- streaming usage summaries or `stream_options` handling
- gateway error events inside a started stream
- client disconnect handling beyond safe stream termination
- retries, backpressure, or queue-based streaming
- streaming for other OpenAI-compatible endpoints (embeddings, responses)
- changing the non-streaming chat completion contract
- adding runtime dependencies
- publishing gateway packages

## Background

The gateway has established explicit internal boundaries for provider adapters (ADR-0008), request validation (ADR-0010), JSON error envelopes (ADR-0011), and successful response normalization (ADR-0012).

Streaming is currently rejected in request validation with the message `streaming responses are not supported yet`.

Streaming changes three existing boundaries at once:

- request validation must accept and type the `stream` flag
- provider adapters need a way to produce incremental chunks
- the HTTP handler needs a second response mode with a different content type and no fixed content length

Sprint 17 should introduce streaming without weakening those boundaries and without adopting a web framework.

## User Workflows

The MVP must support these workflows:

- A client sends a chat completion request with `stream: true` and receives an OpenAI-compatible SSE response.
- A client can consume the stream with tools that already understand OpenAI streaming responses.
- A contributor can run the mock provider with streaming and observe deterministic chunks.
- A maintainer can add a future provider with streaming support by implementing one protocol method.
- CI can validate streaming behavior without network access or provider credentials.
- Existing non-streaming requests behave exactly as before.

## Request Requirements

The gateway must accept `stream: true` in chat completion requests.

The `stream` field must be validated as a boolean when present:

- `true` selects streaming delivery
- `false` or absence selects the existing non-streaming delivery
- non-boolean values such as strings or numbers must be rejected with a `400` bad request error

The request validation module must expose the stream flag on its typed result so the HTTP handler can choose the delivery mode.

The original request body must continue to be preserved and passed to provider adapters unchanged.

## Streaming Contract Requirements

Streaming responses must follow the OpenAI-compatible chat completion chunk shape:

- response content type `text/event-stream`
- one `data:` event per chunk followed by a blank line
- each chunk object uses `object: "chat.completion.chunk"`
- each chunk carries the public gateway model alias
- chunk choices contain `delta` objects instead of `message` objects
- the first content chunk should carry the assistant role delta
- a final chunk signals completion with an empty delta and `finish_reason: "stop"`
- the stream terminates with a `data: [DONE]` event

Chunks must use the same `id` and `created` values across the stream so clients can correlate events.

## Provider Requirements

The provider protocol must gain a streaming method with this behavior:

- accepts the same model config and request body as non-streaming chat completion
- returns an iterator of chunk dictionaries
- each chunk satisfies the minimal streaming chunk shape

The mock provider must produce deterministic streaming chunks that assemble to the same content as its non-streaming response, using the same completion id and timestamp.

The OpenRouter provider must support streaming by:

- forwarding `stream: true` to the upstream endpoint
- forwarding the provider model identifier in the upstream payload
- reading the upstream SSE response incrementally
- translating upstream chunk events into gateway chunks
- normalizing the public gateway model alias on each chunk
- passing the `[DONE]` terminator through
- translating upstream HTTP and transport failures into gateway errors before the stream starts

Provider streaming must not require live credentials or network access in default tests.

## Response Normalization Requirements

Streaming chunks must pass through a gateway-owned normalizer consistent with the ADR-0012 boundary.

The normalizer must validate the minimal chunk shape and set the public gateway model alias on every chunk.

Malformed provider chunks must be translated into `UpstreamProviderError` so a broken provider cannot leak a malformed stream to clients.

## HTTP Delivery Requirements

The HTTP handler must deliver streaming responses with:

- status `200`
- `Content-Type: text/event-stream`
- no fixed `Content-Length`
- one flushed write per chunk followed by a blank line
- a final `data: [DONE]` event

Errors detected before the first chunk is written must use the standard JSON error envelope with the appropriate status code.

Errors detected after streaming has started cannot change the HTTP status. The MVP must terminate the stream safely without writing further chunks.

The MVP must not buffer the full stream before sending.

## Compatibility Requirements

Sprint 17 must preserve:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions` non-streaming behavior
- current mock provider non-streaming behavior
- current OpenRouter payload mapping and alias normalization
- current configuration examples
- default offline test behavior

Clients that never set `stream` must observe no change.

## Testing and CI Requirements

Tests must cover:

- request validation accepts `stream: true`
- request validation rejects non-boolean stream values
- mock provider stream chunks assemble to the full response content
- mock provider chunk object markers, role delta, finish reason, and stable id
- OpenRouter streaming payload forwarding with injected transport
- OpenRouter chunk translation and model alias normalization
- OpenRouter upstream error translation before stream start
- chunk normalization rejection of malformed chunks
- HTTP-level SSE delivery: content type, chunk framing, and `[DONE]` terminator
- non-streaming endpoint regression coverage

CI must continue to require no network access, provider credentials, or live upstream providers.

## Documentation Requirements

Documentation must explain:

- the streaming request contract and example curl usage
- the chunk shape and `[DONE]` terminator
- the provider streaming boundary and how to add a streaming provider
- error behavior before and mid-stream
- current Sprint 17 limitations

## Acceptance Criteria

Issue #75 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references ADR-0008, ADR-0010, ADR-0011, and ADR-0012
- it defines the Sprint 17 streaming scope before implementation begins

The Sprint 17 streaming milestone is complete when:

- issue #76 records ADR-0014
- issue #77 implements streaming in `apps/gateway`
- issue #78 adds streaming tests and CI validation
- issue #79 documents streaming and prepares `Genesis-0.0.17`

## Examples

Streaming request:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mock-coder",
    "stream": true,
    "messages": [
      { "role": "user", "content": "Write a Python function." }
    ]
  }'
```

Expected response shape:

```text
HTTP/1.1 200 OK
Content-Type: text/event-stream

data: {"id":"chatcmpl-...","object":"chat.completion.chunk","created":123,"model":"mock-coder","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-...","object":"chat.completion.chunk","created":123,"model":"mock-coder","choices":[{"index":0,"delta":{"content":"Mock"},"finish_reason":null}]}

data: {"id":"chatcmpl-...","object":"chat.completion.chunk","created":123,"model":"mock-coder","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]

```

## Best Practices

- Keep streaming deterministic for the mock provider.
- Keep the public chunk contract gateway-owned, not adapter-owned.
- Reject malformed stream values at validation time.
- Preserve provider request bodies for streaming forwarding.
- Keep default tests offline and credential-free.

## Risks

- Streaming can hide malformed provider output if chunks are not validated.
- A stream that is buffered defeats the purpose of streaming.
- Mid-stream errors cannot use the JSON error envelope; the MVP must document this limitation clearly.
- Client disconnects can interrupt provider reads if not handled safely.

## References

- `.agentforge/adrs/0002-gateway-module-placement.md`
- `.agentforge/adrs/0008-gateway-provider-boundary.md`
- `.agentforge/adrs/0010-gateway-request-validation-boundary.md`
- `.agentforge/adrs/0011-gateway-error-response-boundary.md`
- `.agentforge/adrs/0012-gateway-response-normalization-boundary.md`
- `apps/gateway/README.md`
- `docs/gateway.md`

## Revision History

- 2026-07-24: Initial requirements draft for Genesis Sprint 17.
