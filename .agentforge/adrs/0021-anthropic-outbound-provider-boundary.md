# ADR-0021: Anthropic Outbound Provider Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #110, #111, #112, #113, #114
- Related ADRs: ADR-0008 (provider boundary), ADR-0009 (provider contract testing), ADR-0017 (keyless local trust), ADR-0019/0020 (Anthropic inbound translation)

## Context

The gateway has two inbound surfaces (OpenAI Chat Completions and Anthropic Messages) and three provider adapters (mock, ollama, openrouter). The Anthropic story is half-closed: Anthropic-protocol clients can reach OpenAI-compatible providers, but OpenAI-compatible clients cannot reach Anthropic's API — there is no `anthropic` outbound provider.

The provider protocol (ADR-0008) is OpenAI-compatible: adapters receive an OpenAI-shaped body and must return OpenAI-shaped responses (or stream OpenAI chunks). Anthropic's API speaks a different protocol (Messages API, `x-api-key` auth, content blocks, Anthropic SSE events).

## Decision

Add an `anthropic` provider adapter that translates at the **provider boundary**, exactly mirroring the inbound edge translation (ADR-0019/0020) in the outbound direction:

- **Request**: OpenAI body → Anthropic Messages payload. `system` messages fold into the `system` parameter; OpenAI function `tools` → Anthropic `tools` (`input_schema` from `parameters`); assistant `tool_calls` → `tool_use` blocks; `tool` role messages → `tool_result` blocks; `max_tokens` defaults to 4096 (Anthropic requires it).
- **Auth**: `x-api-key` + `anthropic-version: 2023-06-01`; key from `api_key_env` (default `ANTHROPIC_API_KEY`) — the standard credentialed provider pattern (contrast ADR-0017's keyless local trust).
- **Response**: Anthropic message → OpenAI `chat.completion`. Text blocks concatenate into `content`; `tool_use` blocks → `tool_calls` (arguments = JSON of `input`); `stop_reason` → `finish_reason` (`end_turn`→`stop`, `max_tokens`→`length`, `tool_use`→`tool_calls`); usage maps input/output tokens.
- **Streaming**: Anthropic SSE events → OpenAI `chat.completion.chunk` stream with `data: [DONE]` terminator; text deltas → `delta.content`, `input_json_delta` → `delta.tool_calls`.
- Errors translate to `UpstreamProviderError` in the standard style.

The gateway core, both inbound surfaces, and the other adapters are untouched. Translation lives inside the adapter (its private concern), keeping the provider protocol clean.

## Consequences

- Any OpenAI-compatible client (Codex CLI, OpenCode, Cursor, the playground) can reach Anthropic's models through the gateway with `ANTHROPIC_API_KEY` set — the Anthropic story closes in both directions.
- The same translation knowledge (blocks, stop reasons, tool mapping) now exists in two places: inbound (`anthropic.py`) and outbound (this adapter). They are inverse mappings by construction; the drift risk is contained by contract tests on both sides.
- Anthropic is a credentialed cloud provider like OpenRouter: live verification is optional, offline tests are deterministic via injected transport (ADR-0009).
- Anthropic's native tool-calling and thinking work through the OpenAI surface: `tool_use` blocks round-trip as `tool_calls`; thinking blocks are concatenated into content (Anthropic's extended thinking text is not separately exposed yet).

## Alternatives Considered

- **Dual-protocol provider protocol (adapters speak both shapes)** — rejected: violates ADR-0008 and duplicates translation N times.
- **Reverse-proxy a second gateway** — rejected: external dependency, breaks the single-governance story.
- **Skip until a consumer needs it** — rejected: the Compatibility Matrix lists "needs adapter" for Anthropic; this closes it.

## Deferred

- Anthropic extended-thinking block exposure as a first-class field (currently concatenated into text content).
- `computer`/`web_search` tool types (no OpenAI analogue).
- Streaming usage events passthrough (`message_delta` usage is dropped; usage comes from non-stream responses).
