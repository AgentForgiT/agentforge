# Gateway: Anthropic Outbound Provider Adapter

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 25 |
| Issues | #110, #111, #112, #113, #114 |
| Related ADRs | ADR-0008 (provider boundary), ADR-0009 (provider contract testing), ADR-0017 (keyless local trust — this provider is the credentialed counterpoint), ADR-0019/0020 (Anthropic inbound translation — this is the outbound direction) |

## Background

Sprint 23–24 gave the gateway an **inbound** Anthropic surface: Anthropic-protocol clients (Claude Code) can reach OpenAI-compatible providers through `/v1/messages`. The reverse direction is missing: **OpenAI-compatible clients (Codex CLI, OpenCode, Cursor, the playground) cannot reach Anthropic's API** through the gateway, because there is no `anthropic` provider adapter.

This sprint adds the `anthropic` provider: an outbound adapter that translates the gateway's OpenAI-compatible dispatch into Anthropic Messages API calls (`POST https://api.anthropic.com/v1/messages`), and translates Anthropic responses (non-streaming and SSE streaming) back into the gateway's normalized OpenAI-compatible shapes.

## Requirements

R1. `AnthropicProvider` implements the provider protocol (`chat_completion`, `chat_completion_stream`) with the same shape as OpenRouter/Ollama — the gateway core and inbound Anthropic surface are untouched.
R2. Request translation (OpenAI body → Anthropic Messages):
   - `system` messages fold into the Anthropic `system` parameter; remaining messages map role/content.
   - OpenAI function `tools` translate to Anthropic `tools` (`input_schema` from `parameters`).
   - Assistant `tool_calls` translate to `tool_use` content blocks; `tool` role messages translate to `tool_result` blocks.
   - `model` maps to `provider_model`; `max_tokens` is required by Anthropic — default to 4096 when absent.
R3. Auth: `x-api-key: <ANTHROPIC_API_KEY>` header + `anthropic-version: 2023-06-01`. Key comes from `api_key_env` (default `ANTHROPIC_API_KEY`), matching the OpenRouter pattern; missing key → `ProviderConfigurationError`.
R4. Response translation (Anthropic message → OpenAI `chat.completion`):
   - `content` text blocks concatenate into `message.content`; `tool_use` blocks → `tool_calls` (`arguments` = JSON of `input`).
   - `stop_reason` maps to `finish_reason` (`end_turn` → `stop`, `max_tokens` → `length`, `tool_use` → `tool_calls`).
   - `usage` maps `input_tokens` → `prompt_tokens`, `output_tokens` → `completion_tokens`; `object: "chat.completion"`; `model` set to the public alias.
R5. Streaming translation: Anthropic SSE events (`message_start`, `content_block_start`, `content_block_delta` text_delta/input_json_delta, `content_block_stop`, `message_delta`, `message_stop`) → OpenAI `chat.completion.chunk` SSE with `data: [DONE]` terminator, delta `content` for text and `tool_calls` for input deltas.
R6. Error translation: Anthropic error envelope (`{"type": "error", "error": {...}}`) and HTTP statuses → `UpstreamProviderError` with the same message style as OpenRouter (`provider '<name>' request failed: ...`).
R7. All tests offline and deterministic (injected `urlopen_fn` fixtures per ADR-0009); no network, no Anthropic credentials in tests. Default validation stays credential-free (the provider only fails at call time if the key is absent).
R8. Config: example config file (`config.anthropic.example.json`) with `api_key_env: ANTHROPIC_API_KEY` documented.

## Acceptance Criteria

- [ ] `anthropic` provider registered in factory + `supported_provider_types` + exports
- [ ] OpenAI-compatible request → Anthropic Messages payload correct (system fold, tools, tool_calls, max_tokens default)
- [ ] Anthropic response → OpenAI `chat.completion` shape correct (text, tool_calls, usage, finish_reason)
- [ ] Streaming translates Anthropic events → OpenAI chunks with `[DONE]`
- [ ] Missing key → `ProviderConfigurationError`; upstream HTTP/JSON errors → `UpstreamProviderError`
- [ ] Example config parses; full suite passes offline
