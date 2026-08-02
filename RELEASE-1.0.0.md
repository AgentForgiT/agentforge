# AgentForge 1.0.0 — The Stability Line

**The API is frozen. The promise is made.**

Thirty-three Genesis releases built the governed foundation; twelve feature releases (0.1.0 → 0.11.0) made it adoptable; **1.0.0 makes it dependable.**

## The Transition

DEC-0006 defined the 0.1.0 gate (adoptable). DEC-0009 defines this gate (stable). Every box has verifiable evidence (checklist: `.agentforge/requirements/1.0.0-release-gate-checklist.md`):

1. **371 tests green offline** — gateway 250, CLI 60, SDK 11, benchmarks/AICS 50; CI Bootstrap Validate on every push.
2. **38 ADRs + 8 DECs, zero drafts** — every boundary recorded, every decision traceable.
3. **Docs complete** — 9 live site pages plus in-repo docs, community, and contributing guides.
4. **Distribution automated** — wheels + benchmark results attach to every release via the tag-gated publish workflow.
5. **AICS Level-3** — the repo validates itself in CI on every push.
6. **API-surface inventory** — the frozen contract below.
7. **This release note.**

## The Frozen API Surface (backward-compatibility contract)

### Gateway surfaces (5)
`GET /health` · `GET /v1/models` · `POST /v1/chat/completions` (OpenAI-compatible, streaming) · `POST /v1/messages` (Anthropic Messages, streaming) · `POST /mcp` (JSON-RPC 2.0)

### Providers (4)
`mock` (deterministic) · `ollama` (keyless local) · `openrouter` (cloud) · `anthropic` (outbound, Messages API)

### Gateway config (server)
`host`, `port`, `log_level`, `cors_origin`, `api_key_env`, `auth_keys_file`, `rate_limit_rpm`

### CLI commands (8)
`validate-context` · `init-context` · `migrate-context` · `explain-context` · `doctor` · `build-twin` · `serve-twin` · `auth-key` (add/list/revoke, `--encrypt`)

### SDK (4 methods)
`health()` · `models()` · `chat_completions()` · `anthropic_messages()`

### MCP methods (7)
`initialize` · `tools/list` · `tools/call` · `resources/list` · `resources/read` · `prompts/list` · `prompts/get`

### AICS
Spec v0.2 (YAML front matter, adoption levels 1–3, version marker); Level-3 tooling (`migrate-context`, v0.2 scaffolds, front matter schema)

## The Semver Promise

- **Patch** (1.0.x): bug fixes, no behavior change.
- **Minor** (1.x.0): features, additive changes, and — only with an ADR — breaking changes.
- **Breaking** anything else: a decision, a minor bump, and a documented migration path.

## What Rides 1.x

The twin service extensions, MCP client mode, variance-aware tooling, per-benchmark confidence intervals, and the research layer — each behind its own ADR, one governed increment at a time.

## Governing Decisions (the audit trail)

ADR-0001 → ADR-0038 and DEC-0001 → DEC-0009. Every boundary recorded, every choice traceable. That is the product: not just code, but a governed, reproducible way to build AI-native software.

— AgentForge maintainers, 2026-08-01
