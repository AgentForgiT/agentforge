# Gateway: Anthropic Thinking + Tool-Use Mapping

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 24 |
| Issues | #105, #106, #107, #108, #109 |
| Related ADRs | ADR-0019 (Anthropic inbound boundary — this sprint closes its deferred items) |

## Background

ADR-0019 shipped the Anthropic Messages inbound surface with two explicitly deferred items: **thinking blocks** and **tool-use block mapping**. Real Anthropic-protocol clients (Claude Code, claude-mem, tool-using agents) send `tools` parameters, emit `tool_use` blocks from the assistant, and receive `tool_result` blocks from the user. Without mapping, the gateway rejects those requests (bad_request on unsupported block type), limiting `/v1/messages` to plain text chat.

This sprint maps Anthropic tools/thinking onto the OpenAI-compatible provider protocol at the edge — still translation-only, still zero provider changes (ADR-0019 architecture preserved).

## Requirements

R1. **`tools` parameter translation**: Anthropic `tools: [{name, description, input_schema}]` → OpenAI `tools: [{type: "function", function: {name, description, parameters}}]`.
R2. **Assistant `tool_use` block translation (request side)**: Anthropic assistant message containing `tool_use` blocks → OpenAI assistant message with `tool_calls` (`id`, `type: "function"`, `function: {name, arguments: JSON-stringified input}`).
R3. **User `tool_result` block translation**: Anthropic user message with `tool_result` blocks → OpenAI `tool` role messages (`tool_call_id`, `content`), one per result. Tool results with structured `content` arrays surface their text parts.
R4. **Response side**: provider OpenAI `tool_calls` in the assistant message → Anthropic `content: [{type: "tool_use", id, name, input}]` blocks, appended after text blocks.
R5. **Streaming response side**: OpenAI stream chunks carrying `delta.tool_calls` → Anthropic `content_block_start` (tool_use) + `content_block_delta` (`input_json_delta` with `partial_json`) events, followed by the standard tail. The text content block and tool-use block both use index 0/1 sequentially (text block index 0 when present, tool block next index).
R6. **Thinking acceptance**: Anthropic `thinking: {type: "enabled", budget_tokens}` is accepted. It is currently **pass-through only at the request level** (no provider reasoning-mapping yet — OpenAI reasoning models use a different mechanism); response-side thinking blocks are preserved as content blocks when a provider emits them, otherwise absent. This is documented, not silently dropped: a log line records thinking requested.
R7. All translation stays offline-testable with the mock provider and fixture responses; no new external dependencies; `x-api-key` semantics unchanged (keyless).

## Acceptance Criteria

- [ ] `tools` param on `/v1/messages` translates to OpenAI function tools before dispatch
- [ ] Assistant `tool_use` blocks translate to OpenAI `tool_calls` in the request
- [ ] User `tool_result` blocks translate to OpenAI `tool` role messages
- [ ] Provider response with `tool_calls` renders as Anthropic `tool_use` content blocks
- [ ] Streaming tool calls render as `content_block_start`/`input_json_delta` events
- [ ] `thinking` accepted without error; logged when present
- [ ] Full suite passes offline (157 existing + new)
