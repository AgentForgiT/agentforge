# ADR-0026: Gateway MCP Server Surface

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #135, #136, #137, #138, #139
- Related ADRs: ADR-0008 (provider boundary), ADR-0019/0020 (Anthropic inbound), ADR-0023 (auth), ADR-0025 (SDK)

## Context

MCP (Model Context Protocol) is the emerging standard for AI clients to discover and invoke tool capabilities. The gateway already exposes two HTTP surfaces (OpenAI Chat Completions, Anthropic Messages) behind providers and governance. The vision's roadmap names MCP as a future module. This kickoff makes the gateway itself an MCP server: its capabilities surface as MCP tools, so MCP clients (Claude Code, etc.) can drive the gateway — and therefore its providers — as tools.

## Decision

Add a **JSON-RPC 2.0 MCP server surface** at `POST /mcp`:

- **Protocol**: JSON-RPC 2.0 (request/response/error objects) over HTTP, implemented with stdlib only (no MCP SDK dependency) — consistent with the gateway's zero-dependency ethos.
- **Methods**:
  - `initialize` → protocol version, server capabilities (`tools`), server info (`name: "agentforge-gateway"`).
  - `tools/list` → four tool definitions: `gateway_health`, `gateway_list_models`, `gateway_chat_completion`, `gateway_anthropic_message`, each with `name`, `description`, `inputSchema`.
  - `tools/call` → routes to the matching gateway capability; success returns `{"content": [{"type": "text", "text": ...}], "isError": false}`; gateway/provider failures return `isError: true` with error text; unknown tools return JSON-RPC error `-32602`.
- **Auth**: when `server.api_key_env` is configured (ADR-0023), `/mcp` requires the same bearer/x-api-key credential; otherwise keyless local trust (ADR-0017).
- **CORS**: `/mcp` participates in CORS (ADR-0018) for browser MCP clients.

The MCP surface is a **view over existing gateway capabilities** — it adds no new providers, no new protocol translation, and no client-side logic. The gateway remains the single source of truth.

## Consequences

- MCP clients (Claude Code, other MCP hosts) can call the gateway's providers as tools with zero new infrastructure.
- The implementation is small (JSON-RPC 2.0 is a small protocol) and fully offline-testable with the mock provider.
- Stdlib-only keeps the dependency-free brand; no MCP SDK vendored in.
- Streaming is not exposed via MCP in v1 (MCP tool results are content blocks); the OpenAI/Anthropic surfaces remain the streaming paths.

## Alternatives Considered

- **Use an MCP SDK** (e.g. `mcp` Python package) — rejected: adds a dependency; JSON-RPC 2.0 dispatch is small and the gateway's identity is dependency-free.
- **Separate MCP server process** — rejected: splits governance; the gateway should own its surfaces.
- **Resources/prompts extensions** — deferred: tools are the kickoff; resources/prompts can follow if a consumer needs them.

## Deferred

- MCP resources (`resources/list`) and prompts (`prompts/list`) — return empty for now per the spec.
- Streaming tool results over MCP.
- MCP client mode (the gateway calling other MCP servers) — a later module.
