# AgentForge Gateway

OpenAI-compatible local gateway for AgentForge.

This module was migrated from the pre-governance `agentforge-gateway` prototype as part of Genesis Sprint 2.

## Status

- Module: `apps/gateway`
- Status: Genesis MVP
- Related requirements: `.agentforge/requirements/gateway-reconciliation.md`, `.agentforge/requirements/gateway-streaming-mvp.md`, `.agentforge/requirements/gateway-logging-observability-mvp.md`
- Related ADRs: `.agentforge/adrs/0002-gateway-module-placement.md`, `.agentforge/adrs/0008-gateway-provider-boundary.md`, `.agentforge/adrs/0009-gateway-provider-contract-testing.md`, `.agentforge/adrs/0010-gateway-request-validation-boundary.md`, `.agentforge/adrs/0011-gateway-error-response-boundary.md`, `.agentforge/adrs/0012-gateway-response-normalization-boundary.md`, `.agentforge/adrs/0013-gateway-configuration-validation-boundary.md`, `.agentforge/adrs/0014-gateway-streaming-boundary.md`, `.agentforge/adrs/0015-gateway-logging-observability-boundary.md`

## Features

- dependency-free Python stdlib HTTP service
- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- OpenAI-compatible SSE streaming for chat completions
- structured access logging with configurable log level
- deterministic mock provider
- optional OpenRouter provider adapter
- explicit internal provider adapter boundary
- offline provider contract tests
- internal request validation boundary
- standard JSON error envelope
- successful response normalization boundary
- streaming chunk normalization boundary
- explicit configuration validation
- JSON configuration
- offline unit and endpoint tests

## Provider Boundary

Provider adapter code lives under `agentforge_gateway.providers`.

The Genesis boundary keeps adapters inside `apps/gateway` while separating:

- provider protocol and factory
- deterministic mock adapter
- OpenRouter adapter

`packages/providers` extraction remains deferred until the boundary is proven by more provider maturity or reuse.

## Provider Contract Tests

Provider contract tests live under `apps/gateway/tests`.

They verify the minimal chat completion response shape expected from gateway providers while keeping default validation offline and credential-free.

Current contract coverage includes:

- deterministic mock provider response shape and usage reporting
- OpenRouter payload mapping through injected transport
- public model alias normalization
- upstream HTTP error translation

## Request Validation

Chat-completion request validation lives in `agentforge_gateway.requests`.

The request boundary validates required `model` and `messages` fields, validates `stream` as a boolean flag, and preserves the original request body passed to provider adapters. Non-boolean `stream` values are rejected as bad requests.

## Streaming

Streaming chat completions follow the OpenAI-compatible SSE contract (ADR-0014):

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "mock-coder", "stream": true, "messages": [{"role": "user", "content": "Write a Python function."}]}'
```

The response is an SSE stream with `Content-Type: text/event-stream`:

```text
data: {"id":"chatcmpl-...","object":"chat.completion.chunk","created":123,"model":"mock-coder","choices":[{"index":0,"delta":{"role":"assistant"},"finish_reason":null}]}

data: {"id":"chatcmpl-...","object":"chat.completion.chunk","created":123,"model":"mock-coder","choices":[{"index":0,"delta":{"content":"Mock"},"finish_reason":null}]}

data: {"id":"chatcmpl-...","object":"chat.completion.chunk","created":123,"model":"mock-coder","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]

```

The mock provider streams deterministic chunks that assemble to its non-streaming content. The OpenRouter provider forwards `stream: true` upstream and translates upstream chunk events.

Every chunk passes through the gateway-owned normalizer in `agentforge_gateway.responses`, which validates the minimal chunk shape and sets the public model alias.

Errors before the first chunk use the standard JSON error envelope. Errors after streaming has started terminate the stream safely; they cannot change the HTTP status. Streaming usage summaries, error events, and `stream_options` remain deferred.

## Logging

The gateway emits structured access records through the standard library `logging` module under the `agentforge.gateway` logger (ADR-0015):

```text
method=POST path=/v1/chat/completions status=200 duration_ms=3
```

Access records include HTTP method, request path, response status, and elapsed time in milliseconds. Chat-completion context records are emitted after successful request validation:

```text
chat_completion model=mock-coder stream=false
```

The log level is configurable through `server.log_level` with accepted values `DEBUG`, `INFO`, `WARNING`, and `ERROR` (case-insensitive), defaulting to `INFO`.

Unexpected handler errors are logged at `ERROR` with a `500` status record and a generic `internal_error` JSON envelope; exception details are written to the log only.

Request bodies, response bodies, headers, and credentials are never logged. Provider adapters do not emit gateway logs during Genesis; provider-side diagnostics, metrics endpoints, request IDs, and trace IDs remain deferred.

## Error Contract

Gateway errors use a standard JSON envelope:

```json
{"error": {"message": "not found", "type": "not_found"}}
```

Known gateway errors map to explicit HTTP status codes, including bad request `400`, unknown model `404`, provider configuration `500`, and upstream provider `502`.

## Response Normalization

Successful chat-completion responses pass through `agentforge_gateway.responses` after provider dispatch.

The normalizer preserves provider response fields, validates the minimal `chat.completion` shape expected by the gateway, and sets the response `model` field to the public gateway model alias. Malformed provider success responses are returned as upstream provider errors through the standard error envelope.

Streaming chunks pass through the same module's `normalize_stream_chunk`, which validates the minimal `chat.completion.chunk` shape and sets the public model alias on every chunk. Malformed provider chunks become upstream provider errors.

Full OpenAI response schema validation remains deferred during Genesis.

## Configuration Validation

Gateway configuration parsing lives in `agentforge_gateway.config`.

The parser validates root, server, model, and provider object shapes; required model and provider fields; server port range; `server.log_level` against the supported levels; positive provider timeouts; provider headers; and model references to configured providers. It preserves the default host, port, log level, and mock provider behavior for local offline use.

Provider API keys remain environment variables checked by provider adapters at runtime.

## Run Tests

From the repository root:

```bash
python -m unittest discover -s apps/gateway/tests
```

## Run Locally

```bash
PYTHONPATH=apps/gateway/src python -m agentforge_gateway.cli --config apps/gateway/config.example.json
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "apps/gateway/src"
python -m agentforge_gateway.cli --config apps/gateway/config.example.json
```

## OpenRouter

OpenRouter is optional. The default config requires no external provider key.

```bash
OPENROUTER_API_KEY=... PYTHONPATH=apps/gateway/src python -m agentforge_gateway.cli --config apps/gateway/config.openrouter.example.json
```

Provider keys must stay in environment variables and must not be committed.
