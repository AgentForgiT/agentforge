# MCP Client Mode MVP

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 48 |
| Issues | #215, #216, #217, #218, #219 |
| Related | ADR-0026 (inbound /mcp server), ADR-0037 (resources/prompts), ADR-0017 (keyless provider pattern), ADR-0021 (outbound provider pattern), DEC-0009 (1.x semver) |

## Purpose

The gateway already **serves** an MCP surface: `POST /mcp` exposes gateway capabilities as MCP tools to external MCP clients (ADR-0026/0037, `apps/gateway/src/agentforge_gateway/mcp.py`, `McpServer`). This sprint adds the **outbound mirror**: the gateway becomes an MCP **client** that connects to remote MCP servers, discovers their tools, and exposes those tools through the gateway's own OpenAI-compatible chat surface. This was ADR-0026's explicitly deferred item and a recorded 1.x rider in RELEASE-1.0.0.md.

The boundary follows the house rule for second-protocol surfaces: **translation at the edge, never per-provider dual protocols** — remote MCP tools are normalized once into gateway tools, exactly as Anthropic Messages was normalized at the edge (ADR-0019/0020/0021).

## Requirements

R1. **MCP client transport** (stdlib only):
   - HTTP/JSON-RPC 2.0 transport to remote MCP endpoints (`POST`, JSON-RPC body), configured per server.
   - Injectable transport function for offline tests (same pattern as `urlopen_fn` in provider adapters).
   - Connection errors translate to the gateway's existing error envelope (e.g. `upstream_provider_error`), never raw exceptions to the client.

R2. **Server discovery + registration**:
   - Gateway config gains an optional `mcp_servers` section: each entry has a name, a `url`, and (keyless default) optional auth header env reference — mirroring the keyless-by-default Ollama boundary (ADR-0017).
   - `MCP*` tool names are namespaced as `mcp_<server>.<tool_name>` to avoid collisions with the four built-in tools (`health`, `models`, `chat_completion`, `anthropic_message`).

R3. **Handshake + discovery**:
   - On registration (lazy, first call), client performs `initialize` then `tools/list`.
   - `resources`/`prompts` from remote servers are accepted-but-not-mapped in this MVP (deferred list), mirroring how `thinking` was accepted-but-not-mapped in ADR-0020.

R4. **Tool call translation**:
   - A gateway chat-completion request that includes a system/`assistant` tool use for an `mcp_*` tool dispatches to the remote server via `tools/call`.
   - Arguments passed through as-is (JSON); the remote result's `content` array is flattened to a single text string for the gateway's `tool` role response.
   - Timeout per call, configurable; no streaming pass-through of tool calls in this scope.

R5. **Offline determinism**: full test suite runs with zero network (mock transport). Live verification is a manual/CI-optional step, same as prior live-verification gates.

R6. **API surface**: strictly additive — the frozen 1.0.0 inbound surface (`/health`, `/v1/models`, `/v1/chat/completions`, `/v1/messages`, `/mcp`), 4 providers, and 8 CLI commands are byte-for-byte unchanged. New capability ships as `1.1.0` (minor bump + ADR-0039 per DEC-0009).

## Acceptance Criteria

- [ ] Gateway declares one or more `mcp_servers` in config; no servers = zero behavior change
- [ ] `initialize` + `tools/list` complete lazily; remote tools appear as `mcp_<server>.<tool_name>` in `/v1/models`-adjacent tool list
- [ ] A chat-completion tool call to an `mcp_*` tool dispatches via `tools/call` and returns flattened text content
- [ ] Remote server down / bad response → gateway error envelope with `upstream_provider_error`, never a raw exception
- [ ] Namespacing: no collision with built-in gateway tools
- [ ] Full offline suite green (existing 371 + new); CI Bootstrap Validate green
- [ ] `git diff --check` clean; no network in unit tests