# ADR-0037: MCP Resources and Prompts Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #200, #201, #202, #203, #204
- Related: ADR-0026 (MCP surface), ADR-0015 (logging/privacy), DEC-0006 (semver)

## Context

ADR-0026 shipped the gateway's MCP surface and deferred `resources/list` and `prompts/list` (empty responses). The MCP spec expects these methods to carry real, useful content: resources are read-only documents a model can fetch; prompts are reusable message templates. The gateway owns exactly two natural resources (its model registry and its configuration) and a handful of task templates.

## Decision

Add real content to the MCP surface:

**Resources** (read-only, gateway-owned):
- `models://registry` — live `/v1/models` output.
- `models://config` — active configuration, **redacted**: `api_key_env` values and provider secrets are masked (never rendered), honoring ADR-0015's privacy rule.
- `resources/read` returns `{contents: [{uri, mimeType: "application/json", text}]}`; unknown URI → JSON-RPC `-32602`.

**Prompts** (static templates, argument substitution):
- `request-builder` (`model`, `system?`, `user`) — builds an OpenAI-compatible chat-completions request body.
- `config-review` (`config`) — walks the common gateway pitfalls (keyless trust boundary, CORS, rate limits, named keys).
- `error-diagnosis` (`error`) — explains a gateway error envelope and suggests fixes.
- `prompts/get` returns `{description, messages: [{role, content: {type: "text", text}}]}` with `{{arg}}` substitution; unknown name or missing required arg → `-32602`.

Boundary rules: resources expose only gateway-owned data, read-only; prompts contain no user data; nothing is written or mutated through either method.

## Consequences

- MCP clients (Claude Code, etc.) can now fetch the gateway's registry and a redacted config, and build/diagnose against pre-built templates — the surface becomes genuinely useful beyond tools.
- Privacy holds: config resource is redacted; prompts are static.
- All existing MCP tool tests stay green; the surface grows additively.

## Alternatives Considered

- **Expose full config including keys** — rejected: violates ADR-0015; a redacted view is the honest contract.
- **Dynamic/prompt-chaining prompts** — rejected: static templates with substitution are deterministic and testable; chaining belongs to the client.

## Deferred

- Streaming tool results over MCP (unchanged from ADR-0026).
- MCP client mode (gateway calling other MCP servers).
- Per-resource access control beyond the existing auth gate.
