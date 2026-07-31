# Gateway

Metadata:

- Status: Genesis MVP
- Module: `apps/gateway`
- Related requirements: `.agentforge/requirements/gateway-reconciliation.md`, `.agentforge/requirements/gateway-streaming-mvp.md`
- Related ADRs: `.agentforge/adrs/0002-gateway-module-placement.md`, `.agentforge/adrs/0008-gateway-provider-boundary.md`, `.agentforge/adrs/0009-gateway-provider-contract-testing.md`, `.agentforge/adrs/0010-gateway-request-validation-boundary.md`, `.agentforge/adrs/0011-gateway-error-response-boundary.md`, `.agentforge/adrs/0012-gateway-response-normalization-boundary.md`, `.agentforge/adrs/0013-gateway-configuration-validation-boundary.md`, `.agentforge/adrs/0014-gateway-streaming-boundary.md`
- Last updated: 2026-07-24

## Purpose

The AgentForge Gateway provides an OpenAI-compatible local entry point for model providers and future AgentForge services.

## Scope

The Genesis MVP includes:

- `/health`
- `/v1/models`
- `/v1/chat/completions`
- deterministic mock provider
- optional OpenRouter provider
- OpenAI-compatible SSE streaming for chat completions
- internal provider adapter boundary
- offline provider contract tests
- internal request validation boundary
- standard JSON error envelope
- successful response normalization boundary
- streaming chunk normalization boundary
- explicit configuration validation
- JSON configuration
- offline tests

## Prototype Lineage

This module was migrated from the pre-governance `agentforge-gateway` repository.

DEC-0004 keeps that repository public as a historical reference, but canonical gateway development now belongs in `AgentForgiT/agentforge` under `apps/gateway`.

## Local Validation

```bash
python -m unittest discover -s apps/gateway/tests
python scripts/validate_bootstrap.py
```

## Configuration

The default config at `apps/gateway/config.example.json` uses only the mock provider and requires no secrets.

The OpenRouter example at `apps/gateway/config.openrouter.example.json` uses `OPENROUTER_API_KEY` from the environment.

ADR-0013 defines the gateway configuration validation boundary.

Configuration validation lives in `agentforge_gateway.config` and validates:

- root JSON object shape
- optional `server.host` and `server.port`
- required model `provider` and `provider_model`
- provider `type`
- positive provider `timeout_seconds`
- provider `headers`
- model references to configured providers

The parser preserves default host `127.0.0.1`, default port `8080`, and default mock provider behavior when provider config is omitted.

Provider credentials remain runtime environment concerns owned by provider adapters, not config parsing. Live provider availability is intentionally excluded from default validation.

## Provider Boundary

Gateway provider adapters live inside `apps/gateway` during Genesis.

ADR-0008 defines the internal provider package boundary:

- provider protocol and factory are separated from concrete adapters
- deterministic mock behavior lives in its own adapter module
- OpenRouter payload mapping and upstream error handling live in their own adapter module
- gateway routing depends on the provider protocol and factory, not concrete adapters

`packages/providers` remains a long-term extraction target from ADR-0002, but extraction is deferred until provider maturity, ownership, or release cadence justifies it.

## Provider Contract Tests

ADR-0009 defines offline provider contract tests for the Genesis gateway.

The contract tests verify that gateway providers return the minimal OpenAI-compatible chat completion shape expected by the gateway:

- `chat.completion` object marker
- public gateway model alias
- non-empty choices
- assistant message role and string content
- finish reason

The current suite covers the deterministic mock provider and the OpenRouter provider through injected offline transport. Live upstream calls and provider credentials are intentionally excluded from default validation.

## Request Validation

ADR-0010 defines the internal request validation boundary for `/v1/chat/completions`.

Request validation lives in `agentforge_gateway.requests` and validates:

- required `model`
- non-empty `messages`
- boolean `stream` flag
- message `role` and `content` presence

`GatewayApp` remains responsible for model lookup and provider dispatch after validation succeeds. The original request body is preserved so optional provider payload fields continue to pass through to provider adapters.

## Error Contract

ADR-0011 defines the gateway JSON error contract.

Gateway errors use this envelope:

```json
{
  "error": {
    "message": "human-readable message",
    "type": "machine_readable_type"
  }
}
```

Current status mappings:

- bad request: `400`
- unknown model: `404`
- provider configuration error: `500`
- upstream provider error: `502`
- unknown route: `404`

## Response Normalization

ADR-0012 defines the gateway response normalization boundary for successful `/v1/chat/completions` responses.

Response normalization lives in `agentforge_gateway.responses` and validates the minimal successful chat-completion shape expected by the gateway:

- `chat.completion` object marker
- non-empty choices list
- first assistant message with string content
- public gateway model alias in the response `model` field

Provider adapters still own provider-specific request mapping, authentication, transport behavior, upstream JSON parsing, and upstream error translation. Malformed provider success responses are treated as upstream provider errors and returned through the standard error envelope.

Full OpenAI response schema validation remains deferred until explicit requirements and ADR coverage exist.

## Streaming

ADR-0014 adds OpenAI-compatible SSE streaming to the gateway.

Requests with `stream: true` are delivered as an SSE event stream with `Content-Type: text/event-stream`. Streaming chunks follow the OpenAI chat completion chunk contract:

- chunk objects use `object: "chat.completion.chunk"`
- chunks carry the public gateway model alias
- chunk choices contain `delta` objects
- the first content chunk carries the assistant role delta
- a final chunk carries an empty delta and `finish_reason: "stop"`
- the stream terminates with `data: [DONE]`

The mock provider produces deterministic chunks that assemble to the same content as its non-streaming response. The OpenRouter provider forwards `stream: true` upstream, translates upstream chunk events, and terminates when the upstream `[DONE]` event arrives; the gateway HTTP layer emits the client-facing `[DONE]`.

Streaming chunks pass through the gateway-owned normalizer in `agentforge_gateway.responses`, which validates the minimal chunk shape and sets the public model alias on every chunk. Malformed provider chunks are translated to upstream provider errors.

Errors detected before the first chunk is written use the standard JSON error envelope. Errors detected after streaming has started cannot change the HTTP status; the gateway terminates the stream safely without writing further chunks. Gateway error events inside a stream remain deferred.

Streaming usage summaries, `stream_options`, and client disconnect handling beyond safe stream termination remain deferred.

## Risks

- Provider adapters are still inside `apps/gateway`; ADR-0002 and ADR-0008 identify `packages/providers` as a later extraction target.
- Mid-stream errors cannot use the JSON error envelope; the gateway terminates the stream safely and documents this limitation.
- OpenRouter live testing is optional and must not be required in default CI.
- Streaming usage summaries and error events remain deferred.

## Revision History

- 2026-07-24: Documented streaming support from ADR-0014.
- 2026-07-10: Documented configuration validation boundary from ADR-0013.
- 2026-07-06: Documented response normalization boundary from ADR-0012.
- 2026-07-05: Documented JSON error contract from ADR-0011.
- 2026-07-05: Documented internal request validation boundary from ADR-0010.
- 2026-07-04: Documented offline provider contract tests from ADR-0009.
- 2026-07-03: Documented internal provider adapter boundary from ADR-0008.
- 2026-07-02: Clarified post-Sprint-8 prototype repository disposition.
- 2026-06-28: Initial migrated gateway documentation.
