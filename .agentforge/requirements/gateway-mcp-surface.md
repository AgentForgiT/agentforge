# Gateway: MCP Server Surface

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 30 |
| Issues | #135, #136, #137, #138, #139 |
| Related ADRs | ADR-0008 (provider boundary), ADR-0019/0020 (Anthropic inbound), ADR-0023 (auth), ADR-0025 (SDK) |

## Background

The Model Context Protocol (MCP) is the emerging standard for exposing tool capabilities to AI clients (Claude Code, etc.). The vision's roadmap names MCP as a module. This kickoff makes the **gateway itself an MCP server**: its existing capabilities (health, model registry, both chat surfaces) surface as MCP tools, so any MCP client can drive the gateway — and its providers — as tools.

## Requirements

R1. **JSON-RPC 2.0 over HTTP**: `POST /mcp` accepts JSON-RPC 2.0 requests and returns JSON-RPC responses (or error objects with `code`/`message`/`data`).
R2. **`initialize`**: returns protocol version + server capabilities (`tools: {listChanged: false}`) + server info (name `agentforge-gateway`, version from the release).
R3. **`tools/list`**: returns tool definitions for:
   - `gateway_health` (no args) → gateway health JSON
   - `gateway_list_models` (no args) → model registry
   - `gateway_chat_completion` (`model`, `messages`, optional `stream` ignored for MCP v1) → chat completion text
   - `gateway_anthropic_message` (`model`, `messages`, optional `max_tokens`) → Anthropic message text
   Tool definitions carry `name`, `description`, and `inputSchema` (JSON Schema subset).
R4. **`tools/call`**: routes by name to the matching gateway capability; returns `{"content": [{"type": "text", "text": ...}], "isError": false}` on success; `isError: true` with an error text content on gateway/provider failure. Unknown tool → JSON-RPC error `-32602` (invalid params).
R5. **Auth**: when `server.api_key_env` is set (ADR-0023), `/mcp` requires the same `Authorization: Bearer` / `x-api-key`; 401 otherwise. Health is not exposed at the MCP layer (the gateway already has `/health`).
R6. **CORS**: `/mcp` participates in CORS (ADR-0018) for browser MCP clients.
R7. Stdlib only (JSON-RPC dispatch implemented by hand — it is a small protocol); offline tests with the mock provider.

## Acceptance Criteria

- [ ] `initialize` handshake returns protocol version + capabilities
- [ ] `tools/list` returns the four tool definitions with schemas
- [ ] `tools/call` routes each tool correctly; unknown tool → JSON-RPC error
- [ ] Gateway error (e.g. unknown model) → `isError: true` result
- [ ] Auth 401 applies when configured; CORS headers on `/mcp`
- [ ] Full suite passes offline; CI green
