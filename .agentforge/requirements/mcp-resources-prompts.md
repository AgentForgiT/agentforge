# MCP Resources and Prompts

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 45 |
| Issues | #200, #201, #202, #203, #204 |
| Related | ADR-0026 (MCP surface — deferred resources/prompts), ADR-0037, DEC-0006 (semver) |

## Purpose

ADR-0026 shipped the gateway's MCP surface with `resources/list` and `prompts/list` returning empty, deferring real content. This sprint fills them: **resources** expose the gateway's own data read-only (model registry, configuration); **prompts** are pre-built templates for the gateway's core tasks. No user data, no write paths.

## Requirements

R1. **Resources** (read-only, gateway-owned):
   - `resources/list` → `{resources: [...]}` with two resources:
     - `models://registry` — the live model registry (`/v1/models` shape)
     - `models://config` — the active gateway configuration (redacted: no API keys, no provider secrets; per ADR-0015 privacy)
   - `resources/read` (`uri` param) → `{contents: [{uri, mimeType: "application/json", text}]}`; unknown URI → JSON-RPC error `-32602`.
R2. **Prompts** (static templates, argument substitution):
   - `prompts/list` → `{prompts: [...]}` with three:
     - `request-builder` (args: `model`, `system?`, `user`) — builds a chat-completions request body
     - `config-review` (args: `config`) — reviews a gateway config for the common pitfalls (keyless trust, CORS, rate limits)
     - `error-diagnosis` (args: `error`) — explains a gateway error envelope and suggests fixes
   - `prompts/get` (`name` + `arguments`) → `{description, messages: [{role, content: {type: "text", text}}]}`; unknown name → `-32602`; missing required args → `-32602`.
R3. **Privacy**: config resource redacts `api_key_env` values and provider secrets (never renders keys); prompts contain no user data.
R4. Read-only: resources never accept writes; all existing MCP tests stay green.

## Acceptance Criteria

- [ ] `resources/list` returns the two resources; `resources/read` returns each
- [ ] Config resource contains no secret values
- [ ] Unknown resource URI → JSON-RPC error
- [ ] `prompts/list` returns the three templates; `prompts/get` substitutes arguments
- [ ] Unknown prompt name / missing required arg → JSON-RPC error
- [ ] Full suite passes offline; CI green
