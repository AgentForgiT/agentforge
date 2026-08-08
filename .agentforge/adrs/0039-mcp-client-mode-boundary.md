# ADR-0039: MCP Client Mode Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-08
- Deciders: AgentForge maintainers
- Issues: #215, #216, #217, #218, #219
- Related: ADR-0026 (MCP server surface), ADR-0037 (resources/prompts), ADR-0017 (keyless provider), ADR-0021 (outbound provider pattern), ADR-0019/0020 (Anthropic edge translation), DEC-0009 (1.x semver)

## Context

ADR-0026 shipped the gateway's *inbound* MCP surface (`POST /mcp`) and deferred the outbound half; ADR-0037 carried the deferral: "MCP client mode (gateway calling other MCP servers)." RELEASE-1.0.0.md records MCP client mode as a 1.x rider. The gateway currently exposes its capabilities to MCP clients; it cannot call remote MCP servers (external tool servers, registries, project-specific MCP services) and surface their tools to its own OpenAI-compatible clients.

The house rule for second-protocol surfaces is translation at the edge (ADR-0019/0020/0021): the inbound Anthropic surface translates at the edge, providers stay OpenAI-compatible; the outbound Anthropic provider translates at the provider boundary. MCP client mode is another outbound adapter case.

## Decision

Add MCP client mode: the gateway registers one or more remote MCP servers in config and surfaces their tools through the existing OpenAI-compatible chat surface. What changes AND what stays:

**Changes (additive):**

1. **Config** — new optional `server.mcp_servers` block: each entry `{name, url, auth_header_env?}`. Keyless by default (local trust boundary, mirroring ADR-0017); an optional env-named header enables token auth. No `mcp_servers` configured = zero behavior change.
2. **Client transport:** stdlib HTTP JSON-RPC 2.0 (`urllib`), injectable transport function for offline tests (same pattern as `urlopen_fn` in provider adapters). Server failures translate to the existing `upstream_provider_error` envelope — never a raw exception to the gateway client.
3. **Discovery:** lazy `initialize` + `tools/list` on first use per server. Remote tools are namespaced `mcp_<server>.<tool_name>` so they cannot collide with the four built-in gateway tools (`health`, `models`, `chat_completion`, `anthropic_message`).
4. **Dispatch:** a chat-completion request whose tool call references an `mcp_*` tool dispatches to the remote server via `tools/call`; remote `content` arrays flatten to one text string for the `tool` role response. Timeout per call, configurable.
5. **Responses** stream through existing normalization; no new protocol is exposed to the gateway's own clients (they keep using the OpenAI/Anthropic surfaces unchanged).

**Stays (frozen 1.0.0 surface, byte-for-byte unchanged):**

- Inbound `/health`, `/v1/models`, `/v1/chat/completions`, `/v1/messages`, `/mcp` surfaces.
- Four providers, eight CLI commands, SDK methods, AICS v0.2.
- MCP server mode (`McpServer`) untouched.

Boundary rules: remote tools are read-dispatched, never written through; no credentials of remote servers are logged (ADR-0015); resources/prompts from remote servers are accept-but-not-mapped this sprint (deferred, mirroring how `thinking` was accepted-but-not-mapped in ADR-0020).

## Consequences

- MCP client mode ships as **1.1.0** — a minor bump behind this ADR per DEC-0009's semver promise (additive API, no breaking change).
- The gateway becomes a consumer of the MCP ecosystem while remaining a provider — closing the ADR-0026/0037 deferral.
- No new dependencies; tests stay fully offline and deterministic (mock transport).
- Docs must touch all four surfaces' documentation paths (gateway.md, README, CHANGELOG, roadmap/milestones/backlog/decisions) per the surface-counting rule.

## Alternatives Considered

- **Native MCP client as a separate surface** (e.g. `/mcp-client`) — rejected: duplicates the SDK/gateway client contract; translation-at-the-edge keeps one chat surface.
- **Streaming tool-result pass-through** — rejected: adds protocol complexity to the first client-mode sprint; deferred (see below).
- **Per-server dual protocols** (treat each remote server as a special provider) — rejected: violates the house rule; remote MCP tools normalize once into gateway tools.

## Deferred

- Streaming pass-through of remote tool results (next iteration).
- Mapping remote `resources/read` and `prompts/get` into gateway tools.
- Discovery UI / server list endpoint (live registry) — observatory/website concern.