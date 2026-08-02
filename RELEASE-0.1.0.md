# AgentForge 0.1.0 — First Public Release

**The governed foundation is adoptable.** Thirty-three Genesis releases built it; 0.1.0 is where external contributors and researchers can stand on it.

## The Transition

Genesis `0.0.1` → `0.0.33` built the foundation one governed increment at a time: requirements → ADR → implementation → tests → CI → release. DEC-0006 defined the public line and its gate; every gate box has verifiable evidence (checklist: `.agentforge/requirements/0.1.0-release-gate-checklist.md`).

- Distribution: SDK + CLI ship as release assets (DEC-0008); PyPI publication is one settings change away (token-gated workflow, ADR-0027).
- Versioning: `0.1.x` under semantic versioning; breaking changes require a minor bump and an ADR.
- Governance: 28 ADRs, 8 DECs — all accepted; the decision register is the audit trail.

## What Ships

### Gateway (`apps/gateway`) — 215 tests, fully offline
- Two inbound surfaces: OpenAI Chat Completions + Anthropic Messages (ADR-0019/0020)
- Four providers: mock, Ollama (keyless), OpenRouter, Anthropic (outbound, ADR-0021)
- Streaming (OpenAI SSE + Anthropic events), reasoning-model contract, tool-use mapping
- CORS (ADR-0018), opt-in API-key auth + rate limiting (ADR-0023)
- MCP server surface at `/mcp` (ADR-0026) — Claude Code registers in one command

### CLI (`apps/cli`) — 39 tests
`validate-context` · `init-context` · `migrate-context` · `explain-context` · `doctor` · `build-twin`

### SDK (`agentforge-sdk`) — 11 tests
Dependency-free Python client over both surfaces, streaming + auth (ADR-0025)

### AICS
- v0.2 spec: YAML front matter, adoption levels 1–3, version marker (ADR-0022)
- v0.3 tooling: v0.2-first scaffolds, `migrate-context`, front matter schema (ADR-0024)
- AgentForge itself: **Level 3, validated in CI on every push**

### Engineering Twin (ADR-0028)
`agentforge build-twin` materializes a machine-readable project profile — rendered live at [twin](https://agentforgit.github.io/agentforge-docs-site/twin.html).

### Website
Nine live pages, all running on AgentForge: playground, AICS validator (WASM), compatibility matrix, provider explorer, benchmark observatory, twin, gateway, CLI, SDK, MCP, AICS.

## Governing Decisions (the audit trail)

DEC-0001 → DEC-0008 and ADR-0001 → ADR-0028 — every boundary recorded, every choice traceable. That is the product: not just code, but a governed, reproducible way to build AI-native software.

## Next

`0.1.x` continues under semver: the twin service, per-user auth, MCP resources/prompts, benchmark pipelines — each behind its own ADR, each one governed increment at a time.

— AgentForge maintainers, 2026-08-01
