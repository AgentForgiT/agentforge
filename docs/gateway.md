# Gateway

Metadata:

- Status: Genesis MVP
- Module: `apps/gateway`
- Related requirements: `.agentforge/requirements/gateway-reconciliation.md`, `.agentforge/requirements/gateway-streaming-mvp.md`, `.agentforge/requirements/gateway-logging-observability-mvp.md`
- Related ADRs: `.agentforge/adrs/0002-gateway-module-placement.md`, `.agentforge/adrs/0008-gateway-provider-boundary.md`, `.agentforge/adrs/0009-gateway-provider-contract-testing.md`, `.agentforge/adrs/0010-gateway-request-validation-boundary.md`, `.agentforge/adrs/0011-gateway-error-response-boundary.md`, `.agentforge/adrs/0012-gateway-response-normalization-boundary.md`, `.agentforge/adrs/0013-gateway-configuration-validation-boundary.md`, `.agentforge/adrs/0014-gateway-streaming-boundary.md`, `.agentforge/adrs/0015-gateway-logging-observability-boundary.md`
- Last updated: 2026-07-31

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
- structured access logging with configurable log level
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
- optional `server.log_level`
- required model `provider` and `provider_model`
- provider `type`
- positive provider `timeout_seconds`
- provider `headers`
- model references to configured providers

The parser preserves default host `127.0.0.1`, default port `8080`, default log level `INFO`, and default mock provider behavior when provider config is omitted.

Provider credentials remain runtime environment concerns owned by provider adapters, not config parsing. Live provider availability is intentionally excluded from default validation.

## Provider Boundary

Gateway provider adapters live inside `apps/gateway` during Genesis.

ADR-0008 defines the internal provider package boundary:

- provider protocol and factory are separated from concrete adapters
- deterministic mock behavior lives in its own adapter module
- OpenRouter payload mapping and upstream error handling live in their own adapter module
- Ollama/local payload mapping and upstream error handling live in their own adapter module
- Anthropic outbound payload mapping and upstream error handling live in their own adapter module (ADR-0021)
- gateway routing depends on the provider protocol and factory, not concrete adapters

`packages/providers` remains a long-term extraction target from ADR-0002, but extraction is deferred until provider maturity, ownership, or release cadence justifies it.

## Ollama / Local Provider

ADR-0017 defines the local-provider boundary.

The `ollama` provider talks to Ollama's OpenAI-compatible `/v1` surface (default `http://127.0.0.1:11434/v1`, overridable per provider config — any OpenAI-compatible local server works). It is keyless: no `api_key_env` is required or read, and no `Authorization` header is sent (local trust boundary).

Non-streaming and streaming completions behave like the OpenRouter adapter: `provider_model` is substituted as the upstream `model`, responses/chunks get the public gateway alias, and HTTP/transport errors translate to the standard `UpstreamProviderError` envelope. A stopped local daemon surfaces as e.g. `provider 'ollama' request failed: ... Connection refused`.

The adapter intentionally does NOT use Ollama's native `/api/chat` protocol; the gateway owns one OpenAI-compatible normalization path (ADR-0012, ADR-0014), and the native protocol would require a second one. Example config: `apps/gateway/config.ollama.example.json`.

## Anthropic Outbound Provider

ADR-0021 defines the outbound Anthropic provider boundary — the mirror of the inbound Anthropic surface (ADR-0019/0020): OpenAI-compatible clients reach Anthropic's API through the gateway.

The `anthropic` provider translates at the provider boundary:

- **Request**: OpenAI body → Anthropic Messages payload. `system` messages fold into the `system` parameter; OpenAI function `tools` → Anthropic `tools` (`input_schema` from `parameters`); assistant `tool_calls` → `tool_use` blocks; `tool` role messages → `tool_result` blocks; `max_tokens` defaults to 4096 (Anthropic requires it).
- **Auth**: `x-api-key` + `anthropic-version: 2023-06-01`; key from `api_key_env` (default `ANTHROPIC_API_KEY`), like the OpenRouter pattern — the credentialed counterpoint to the keyless local trust of ADR-0017.
- **Response**: Anthropic message → OpenAI `chat.completion`. Text blocks concatenate into `content`; `tool_use` blocks → `tool_calls` (arguments = JSON of `input`); `stop_reason` → `finish_reason` (`end_turn`→`stop`, `max_tokens`→`length`, `tool_use`→`tool_calls`); usage maps input/output tokens.
- **Streaming**: Anthropic SSE events → OpenAI `chat.completion.chunk` stream with `data: [DONE]` terminator; `text_delta` → `delta.content`, `input_json_delta` → `delta.tool_calls`.

Example config: `apps/gateway/config.anthropic.example.json`:

```bash
ANTHROPIC_API_KEY=... PYTHONPATH=apps/gateway/src python -m agentforge_gateway.cli --config apps/gateway/config.anthropic.example.json
```

Provider keys must stay in environment variables and must not be committed.

## Provider Contract Tests

ADR-0009 defines offline provider contract tests for the Genesis gateway.

The contract tests verify that gateway providers return the minimal OpenAI-compatible chat completion shape expected by the gateway:

- `chat.completion` object marker
- public gateway model alias
- non-empty choices
- assistant message role and string content
- finish reason

The current suite covers the deterministic mock provider, the OpenRouter provider, and the Ollama provider through injected offline transport. Live upstream calls and provider credentials are intentionally excluded from default validation.

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

## Reasoning-Model Responses

ADR-0016 defines the reasoning-model response contract, discovered through live verification against the OpenRouter API (2026-08-01).

Reasoning models — OpenAI o-series, DeepSeek R1-style, and OpenRouter reasoning endpoints such as `openai/gpt-oss-20b:free` — legally return `message.content: null` in non-streaming completions, emitting their output in `reasoning` and `reasoning_details` fields. The OpenAI-compatible specification permits null content; the gateway accepts it:

- non-streaming `message.content` may be `str` or `null`; any other type is still rejected with an upstream provider error
- `reasoning`, `reasoning_details`, and provider-specific extras pass through normalization untouched (the gateway normalizes shape, not semantics)
- streaming deltas with empty-string or null `delta.content` alongside `delta.reasoning` fields stream through without error
- `finish_reason: "stop"` and the `[DONE]` terminator are still delivered

Consumers asking for reasoning output read the `reasoning` fields themselves; the gateway does not synthesize `content` from them. The public model alias still replaces the upstream `model` field on responses and chunks.

The test suite pins these behaviors with fixtures captured from the live OpenRouter exchange (`gpt-oss-20b:free`, provider "Darkbloom").

## Anthropic Messages Inbound

ADR-0019 defines the Anthropic inbound boundary; ADR-0020 extends it with thinking and tool-use mapping.

The gateway exposes `POST /v1/messages` — the Anthropic Messages API — alongside the OpenAI Chat Completions surface. Anthropic-protocol clients (Claude Code, Anthropic SDK users) point their base URL at the gateway:

```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:8080 curl http://127.0.0.1:8080/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: anything" \
  -d '{"model": "mock-coder", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hello"}]}'
```

Request validation accepts the Messages shape (`model`, `messages` with role/content, optional `system`, `max_tokens`, `stream`, `tools`, `thinking`). Translation happens at the edge (ADR-0019/0020): the request becomes the internal OpenAI-compatible dispatch, provider adapters are untouched, and responses are rendered in the Anthropic shape (`type: "message"`, content text blocks, `stop_reason`, `usage`).

Tool-use mapping (ADR-0020):

- Anthropic `tools` → OpenAI function tools (`type: "function"`, `function.parameters` from `input_schema`).
- Assistant `tool_use` blocks → OpenAI `tool_calls`; `input` is JSON-stringified into `arguments`.
- User `tool_result` blocks → OpenAI `tool` role messages carrying `tool_call_id` and text content.
- Provider `tool_calls` responses → Anthropic `tool_use` content blocks with parsed `input`; `finish_reason: "tool_calls"` maps to `stop_reason: "tool_use"`.
- Streaming tool calls → `content_block_start` (tool_use, index 1 when a text block precedes) + `content_block_delta` (`input_json_delta`/`partial_json`), then the standard tail.

Anthropic `thinking` is accepted and passed through in the raw body but not mapped to provider reasoning fields (ADR-0020 defers that mapping until a concrete consumer needs it).

Streaming emits Anthropic SSE events (`message_start` → `content_block_start`* → `content_block_delta`* → `content_block_stop`* → `message_delta` → `message_stop`) with no `[DONE]` sentinel.

Errors use the Anthropic envelope (`{"type": "error", "error": {...}}`) with the same status mapping as the OpenAI surface. `x-api-key` is accepted but not required and never forwarded upstream (keyless local trust, ADR-0017).

Image blocks are rejected with a clear bad-request error. Computer/web-search tool types and tool-result images remain deferred per ADR-0020.

## Logging

ADR-0015 defines the gateway logging boundary.

The gateway emits structured access records through the standard library `logging` module under the `agentforge.gateway` logger:

```text
method=POST path=/v1/chat/completions status=200 duration_ms=3
```

Access records include HTTP method, request path, response status, and elapsed time in milliseconds.

Chat-completion context records are emitted after successful request validation:

```text
chat_completion model=mock-coder stream=false
```

The log level is configurable through `server.log_level` with accepted values `DEBUG`, `INFO`, `WARNING`, and `ERROR` (case-insensitive), defaulting to `INFO`.

Unexpected handler errors are logged at `ERROR` with a `500` status record and a generic `internal_error` JSON envelope; exception details are written to the log only.

Request bodies, response bodies, headers, and credentials are never logged.

Provider adapters do not emit gateway logs during Genesis; provider-side diagnostics, metrics endpoints, request IDs, and trace IDs remain deferred.

## CORS

ADR-0018 defines the gateway CORS boundary.

CORS is opt-in through `server.cors_origin` in the gateway configuration:

- absent or empty → CORS disabled; no `Access-Control-Allow-*` headers are emitted and `OPTIONS` requests fall through to the normal 404 path
- `"*"` → `Access-Control-Allow-Origin: *` on every response
- a single `https://` or `http://` origin → that exact origin is echoed on every response
- any other value (non-http(s) scheme, embedded whitespace) → configuration load error

When CORS is enabled, the gateway answers `OPTIONS` with HTTP 204 and `Access-Control-Allow-Methods: GET, POST, OPTIONS`, `Access-Control-Allow-Headers: Content-Type`, and `Access-Control-Max-Age: 86400`, and emits `Access-Control-Allow-Origin` on all JSON responses (including error envelopes) and in the SSE header block of streaming responses.

`Access-Control-Allow-Credentials` is never emitted; the gateway has no cookie/session auth.

The shipped `config.example.json` sets `cors_origin` to the public docs-site origin so the web playground works out of the box.

## Risks

- Provider adapters are still inside `apps/gateway`; ADR-0002 and ADR-0008 identify `packages/providers` as a later extraction target.
- Mid-stream errors cannot use the JSON error envelope; the gateway terminates the stream safely and documents this limitation.
- OpenRouter live testing is optional and must not be required in default CI.
- Streaming usage summaries and error events remain deferred.
- Provider-side diagnostics, metrics endpoints, request IDs, and trace IDs remain deferred beyond the Sprint 18 access record baseline.
- CORS supports a single configured origin (or `*`); a multi-origin allow-list is deferred per ADR-0018.

## Revision History

- 2026-08-01: Documented anthropic outbound provider from ADR-0021.
- 2026-08-01: Documented thinking/tool-use mapping from ADR-0020.
- 2026-08-01: Documented Anthropic Messages inbound surface from ADR-0019.
- 2026-08-01: Documented CORS boundary from ADR-0018.
- 2026-08-01: Documented Ollama/local provider boundary from ADR-0017.
- 2026-08-01: Documented reasoning-model response contract from ADR-0016 and live OpenRouter verification.
- 2026-07-31: Documented logging boundary from ADR-0015.
- 2026-07-24: Documented streaming boundary from ADR-0014.
- 2026-07-10: Documented configuration validation boundary from ADR-0013.
- 2026-07-06: Documented response normalization boundary from ADR-0012.
- 2026-07-05: Documented JSON error contract from ADR-0011.
- 2026-07-05: Documented internal request validation boundary from ADR-0010.
- 2026-07-04: Documented offline provider contract tests from ADR-0009.
- 2026-07-03: Documented internal provider adapter boundary from ADR-0008.
- 2026-07-02: Clarified post-Sprint-8 prototype repository disposition.
- 2026-06-28: Initial migrated gateway documentation.
