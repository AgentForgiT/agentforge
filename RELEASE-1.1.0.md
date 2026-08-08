# AgentForge 1.1.0 — MCP Client Mode

The first post-stability feature release on the 1.x semver line (DEC-0009: additive features are minor bumps, each behind an ADR).

## What's New

The gateway can now **call** remote MCP servers and expose their tools — the outbound mirror of the inbound `/mcp` server surface (ADR-0026/0037), closing the ADR-0026 deferral that RELEASE-1.0.0.md carried as a 1.x rider.

- **`server.mcp_servers`** config (optional — absent means zero behavior change): keyless by default (local trust boundary, ADR-0017 pattern), with an optional `auth_header_env` bearer-token env reference (never stored in the config file).
- **Lazy discovery**: `initialize` + `tools/list` only on first use per server.
- **Namespaced tools**: remote tools surface as `mcp_<server>.<tool_name>` so they cannot collide with the four built-in gateway tools.
- **Dispatch**: `GatewayApp.call_mcp_tool()` → `tools/call` with content flattening; remote failures become error-envelope records, never raw exceptions.
- **Fully offline**: injectable transport (`mcp_transport` on `GatewayApp`) keeps the suite deterministic; 17 new tests.

See `docs/gateway.md` § MCP Client Mode and `apps/gateway/config.mcp-client.example.json`.

## Validation

Local: bootstrap ok · AICS Level-3 · AICS minimal project ok · CLI tests OK · install test OK · SDK OK · benchmark tests OK (50) · gateway tests OK (267) · `git diff --check` clean.

CI: Bootstrap Validate green on `25001af`.

## Governance

ADR-0039 (Accepted, 2026-08-08) recorded in the decisions register. All sprint-48 issues #215–#219 closed by this release.

— AgentForge maintainers, 2026-08-08