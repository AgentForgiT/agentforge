# ADR-0020: Anthropic Tool-Use and Thinking Mapping

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #105, #106, #107, #108, #109
- Related ADRs: ADR-0019 (Anthropic Messages inbound boundary — this ADR closes its deferred items)

## Context

ADR-0019 introduced the Anthropic Messages inbound surface with translation-at-the-edge: Anthropic requests become OpenAI-compatible dispatch, provider adapters stay untouched. Two items were deferred: thinking blocks and tool-use block mapping.

Real Anthropic-protocol clients are tool-driven. Claude Code emits `tools` parameters, assistant turns carry `tool_use` blocks, and follow-up user turns carry `tool_result` blocks. Today the gateway rejects those requests. Completing the mapping is required for the surface to be genuinely usable by its primary client.

## Decision

Map Anthropic tools and thinking onto the OpenAI-compatible protocol **at the inbound/outbound edges only** — extending the ADR-0019 translation layer, never the providers.

Request side:

- Anthropic `tools: [{name, description, input_schema}]` → OpenAI `tools: [{type: "function", function: {name, description, parameters}}]`.
- Assistant `tool_use` blocks → OpenAI `tool_calls` (`id`, `type: "function"`, `function.arguments` as JSON string).
- User `tool_result` blocks → OpenAI `tool` role messages, one per result, carrying `tool_call_id` and text content.
- Anthropic `thinking` is **accepted and logged, not mapped**: OpenAI reasoning models use `reasoning_effort`, not budget tokens; forcing a mapping would be guesswork. Providers that can reason do so via their own request fields; the Anthropic `thinking` param passes through in the raw body for adapters that might honor it.

Response side:

- Provider `tool_calls` → Anthropic `content` `tool_use` blocks appended after text blocks.
- Streaming: `content_block_start` with a `tool_use` block, then `content_block_delta` with `input_json_delta` carrying `partial_json` — the Anthropic streaming shape for tools. The text block (index 0, when present) precedes the tool block (index 1).
- Provider-emitted reasoning/thinking fields pass through as Anthropic `thinking` content blocks when present; otherwise the field is simply absent.

## Consequences

- Claude Code and tool-using Anthropic clients can do real agentic loops through the gateway (declare tools, receive tool calls, send results back) — the surface becomes genuinely usable.
- Zero provider changes: the mapping is a pure edge translation, so every provider (mock, ollama, openrouter) gains tool support through the Anthropic surface for free — including, potentially, providers whose models don't support tools (the upstream provider simply returns an error or text, which translates honestly).
- The OpenAI surface is unchanged; request validation now accepts richer Anthropic shapes.
- `thinking` is a documented no-op at the translation layer (accepted, logged, passed through in the raw body). A future sprint may map it to OpenAI reasoning fields per provider capability.

## Alternatives Considered

- **Map `thinking` to `reasoning_effort`** — rejected: budget tokens and reasoning effort are not equivalent; per-provider mapping is speculative until a real consumer needs it.
- **Provider-side tool translation** — rejected: violates the ADR-0019 edge-translation architecture and duplicates mapping N times.
- **Reject tools until providers mature** — rejected: it would keep the gateway's primary Anthropic client unusable.

## Deferred

- `thinking` → provider reasoning-field mapping (waiting on a concrete consumer).
- Anthropic `computer`/`web_search` tool types (Claude-specific server tools) — no OpenAI analogue; surface only when a provider supports them.
- Tool-result structured content beyond text parts (images in tool results).
