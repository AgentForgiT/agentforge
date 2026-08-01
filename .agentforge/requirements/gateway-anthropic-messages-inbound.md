# Gateway: Anthropic Messages Inbound Surface

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 23 |
| Issues | #100, #101, #102, #103, #104 |
| Related ADRs | ADR-0008 (provider boundary), ADR-0010 (request validation), ADR-0011 (error contract), ADR-0012 (response normalization), ADR-0014 (streaming boundary), ADR-0017 (keyless local trust), ADR-0018 (CORS) |

## Background

The Compatibility Matrix (Sprint 22, website) exposed the gateway's largest interoperability gap: **Anthropic-protocol clients (Claude Code, claude-mem, Anthropic SDK users) cannot route through the gateway** because it exposes only the OpenAI Chat Completions surface (`POST /v1/chat/completions`). Claude Code speaks the Anthropic Messages API (`POST /v1/messages`) via `ANTHROPIC_BASE_URL` and is not OpenAI-compatible natively.

This sprint adds an **Anthropic Messages inbound surface** so that any Anthropic-protocol client can point its base URL at the gateway and reach the same providers (mock, ollama, openrouter) behind the same governance.

## Requirements

R1. The gateway accepts `POST /v1/messages` with the Anthropic Messages request shape: required `model` and `messages` (role/content blocks), optional `system`, `max_tokens`, `temperature`, `stream`, and `metadata`.
R2. The Anthropic request is translated at the inbound boundary into the gateway's internal normalized request (model alias resolution, message flattening), then dispatched to the same provider adapters — **provider adapters remain OpenAI-compatible and untouched** (translation-at-the-edge, ADR-0019).
R3. Successful non-streaming responses use the Anthropic Messages response shape: `id`, `type: "message"`, `role: "assistant"`, `content: [{type: "text", text}]`, `model` (public alias), `stop_reason`, `usage` (input_tokens/output_tokens).
R4. Streaming responses emit Anthropic SSE events: `message_start`, `content_block_start`, `content_block_delta` (text_delta), `content_block_stop`, `message_delta` (stop_reason), `message_stop` — translated from the gateway's normalized chunks.
R5. Errors use the Anthropic error envelope (`{"type": "error", "error": {"type": ..., "message": ...}}`) with the same status mapping as the OpenAI surface (400 bad_request, 404 not_found, 500 internal_error, 502 upstream_provider_error).
R6. The `x-api-key` header is accepted but **not required and never sent upstream** — consistent with the keyless local trust boundary (ADR-0017). Any non-empty value is accepted; missing header does not fail the request.
R7. CORS behavior (ADR-0018) applies identically to the new surface (preflight + `Access-Control-Allow-Origin` on responses).
R8. All tests are offline and deterministic — mock provider drives both non-streaming and streaming translation tests. No Anthropic credentials, no network.
R9. Access logging (ADR-0015) records the new surface with the existing structured format (`method=POST path=/v1/messages status=200`).

## Acceptance Criteria

- [ ] `POST /v1/messages` returns an Anthropic-shaped response for mock provider
- [ ] Model alias resolution works (`mock-coder` etc.)
- [ ] Streaming returns valid Anthropic SSE events in order (start → delta → stop)
- [ ] Malformed requests → Anthropic error envelope with correct status
- [ ] Missing `x-api-key` does not fail the request (keyless)
- [ ] CORS preflight + headers work on `/v1/messages`
- [ ] Full gateway suite passes offline (no new external deps)
