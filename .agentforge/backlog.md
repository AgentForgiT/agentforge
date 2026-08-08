# AgentForge Product Backlog

Metadata:

- Status: Draft
- Phase: Genesis
- Related decisions: ADR-0001, DEC-0005
- Last updated: 2026-07-31

## Purpose

This backlog records the durable AgentForge product direction, epic map, and release planning context.

GitHub issues remain the sprint execution queue. This file is the strategic source of truth for what kinds of work belong in the AgentForge ecosystem.

## Scope

This backlog covers:

- durable product epics
- Genesis release-train priorities
- near-term candidate work
- deferred work that needs future requirements or decisions

This backlog does not replace:

- accepted ADRs
- accepted RFCs
- issue-level acceptance criteria
- release notes
- implementation plans

## Background

AgentForge began as a governance-first project and has become a release-managed engineering product. The product needs a durable backlog so future contributors and AI assistants do not rely on chat history to understand the long-term map.

## Product Epics

| Epic | Name | Purpose | Genesis Status |
| --- | --- | --- | --- |
| Epic 1 | Foundation | Governance, repository structure, release process, standards, and validation. | Active |
| Epic 2 | Documentation | Human-facing technical docs, handbook path, examples, and release notes. | Active |
| Epic 3 | AI Context | AgentForge AI Context Specification, validation, scaffolding, explanation, and diagnostics. | Active |
| Epic 4 | Gateway | OpenAI-compatible gateway, provider boundaries, request/response contracts, and future routing. | Active |
| Epic 5 | IDE Compatibility | Integration guidance for AI coding tools and IDE workflows. | Planned |
| Epic 6 | Benchmarks | Evaluation, reproducibility, and benchmark-driven engineering. | Planned |
| Epic 7 | MCP | Model Context Protocol tooling and integration patterns. | Planned |
| Epic 8 | Website | Public website and documentation portal. | Planned |
| Epic 9 | Community | Contribution paths, governance maturity, maintainership, and community workflows. | Planned |
| Epic 10 | Research | Research notes, experiments, comparisons, and long-form engineering analysis. | Planned |

## Genesis Release Train

Genesis `0.0.x` releases are used to build the governed foundation before a later public `0.1.0` line is defined.

Current Genesis themes:

- keep the canonical monorepo coherent
- preserve governance before implementation
- keep gateway and CLI work deterministic and offline-testable
- expand module boundaries only when justified
- keep public prototypes as historical references
- make release validation routine

## Near-Term Candidates

Near-term work should remain small and releasable:

- gateway model catalog contract hardening
- AICS metadata structure refinement
- standards expansion for release, security, and compatibility
- public `0.1.0` scope definition

## Done and Removed

- MCP client mode (Sprint 48, 2026-08-08): gateway calls remote MCP servers (`server.mcp_servers`, `McpClient` stdlib HTTP JSON-RPC 2.0, `mcp_<server>.<tool>` namespacing, injectable transport); ADR-0039; released as 1.1.0, the first post-stability semver feature release.
- Public 1.0.0 stability line (Sprint 47, 2026-08-01): audited gate (371 tests, 38 ADRs, 9 DECs, docs, distribution, AICS Level-3, API-surface inventory), RELEASE-1.0.0.md; DEC-0009; tagged 1.0.0.
- Variance-aware regression gate (Sprint 46, 2026-08-01): Welch's t-test significance (stdlib betai) gates every threshold breach — jittery benchmarks no longer false-flag; `--significance` flag; ADR-0038; released as 0.11.0.
- MCP resources and prompts (Sprint 45, 2026-08-01): resources/list + read (model registry, redacted config), prompts/list + get (request-builder, config-review, error-diagnosis); ADR-0037; released as 0.10.0.
- Key store encryption at rest (Sprint 44, 2026-08-01): PBKDF2-CTR + HMAC-SHA256 encrypt-then-MAC envelope (stdlib primitives), `auth-key --encrypt`, gateway `AGENTFORGE_AUTH_KEYS_PASSPHRASE`, plaintext stores still supported; ADR-0036; released as 0.9.0.
- Per-benchmark thresholds (Sprint 43, 2026-08-01): `thresholds.json` (default + per-name overrides), `--thresholds` flag, resolution per-name > config default > inline > 10; ADR-0035; released as 0.8.0.
- Benchmark regression gate (Sprint 42, 2026-08-01): `check_regressions.py` — current vs previous release comparison, threshold in percent, both better-directions, improvements never fail; wired into the publish workflow; ADR-0034; released as 0.7.0.
- Benchmark trends (Sprint 41, 2026-08-01): `collect_history.py` merging per-release results assets into versioned history.json with deltas + derived better-direction; observatory trends section; ADR-0033; released as 0.6.0.
- Twin QA layer (Sprint 40, 2026-08-01): `/ask` — deterministic retrieval + optional generation (default local gateway) with faithful extractive fallback; ADR-0032; released as 0.5.0.
- Per-user auth (Sprint 39, 2026-08-01): named key store (server.auth_keys_file), per-key rate limits, live add/revoke without restart, `agentforge auth-key` CLI; ADR-0031; released as 0.4.0.
- Benchmark pipeline (Sprint 38, 2026-08-01): offline harness (gateway/CLI/AICS), schema-validated results.json, CI publishing to releases, observatory consumption; ADR-0030; released as 0.3.0.
- Twin service (Sprint 37, 2026-08-01): `agentforge serve-twin` — read-only stdlib HTTP consumer of the twin profile (twin.json, governance search, index); ADR-0029; released as 0.2.0, the first feature release under semver.
- Community and contribution paths (Genesis Sprint 36, 2026-08-01): expanded CONTRIBUTING (sprint pattern, validation, paths), `docs/community.md`, site contributing refresh; DEC-0007.
- Public 0.1.0 release scope (Genesis Sprint 35, 2026-08-01): scope requirements, release-gate checklist, DEC-0006; Genesis ends at 0.0.32 and 0.1.x follows under semver.
- Engineering twin profile (Genesis Sprint 33, 2026-08-01): `agentforge build-twin` writes read-only, schema-validated `context/twin.json` (AICS governance, decisions, gateway surface); ADR-0028.
- SDK distribution + MCP registration (Genesis Sprint 31, 2026-08-01): clean sdist/wheel, tag-gated `publish.yml` (token-gated PyPI, release assets), `docs/mcp.md` Claude Code registration; ADR-0027.
- Gateway MCP surface (Genesis Sprint 30, 2026-08-01): `POST /mcp` — stdlib JSON-RPC 2.0 server exposing health, models, and both chat surfaces as MCP tools; ADR-0026.
- Python SDK (Genesis Sprint 29, 2026-08-01): `agentforge_sdk` — dependency-free `AgentForgeClient` over both gateway surfaces with streaming and auth; ADR-0025.
- AICS v0.3 tooling (Genesis Sprint 28, 2026-08-01): v0.2-first scaffolds (Level 3 from birth), additive `migrate-context` command, canonical front matter JSON Schema; ADR-0024.
- Gateway API-key auth + rate limiting (Genesis Sprint 27, 2026-08-01): opt-in `server.api_key_env` + `server.rate_limit_rpm`, token-bucket per key/IP, 401/429 with CORS headers, keyless default unchanged; ADR-0023.
- AICS v0.2 structured metadata (Genesis Sprint 26, 2026-08-01): YAML front matter, adoption levels 1/2/3, version marker; AgentForge repo is the first Level-3 context; ADR-0022.
- Anthropic outbound provider adapter (Genesis Sprint 25, 2026-08-01): `anthropic` provider speaking the Messages API with OpenAI↔Anthropic translation at the provider boundary; ADR-0021.
- Anthropic thinking + tool-use mapping (Genesis Sprint 24, 2026-08-01): `tools` → OpenAI function tools, `tool_use`/`tool_result` → `tool_calls`/`tool` role, response `tool_calls` → `tool_use` blocks, streaming `input_json_delta`; ADR-0020.
- Anthropic Messages inbound surface (Genesis Sprint 23, 2026-08-01): `POST /v1/messages` with translation-at-the-edge to the OpenAI-compatible provider protocol; ADR-0019.
- Gateway CORS support (Genesis Sprint 21, 2026-08-01): opt-in `server.cors_origin`, preflight handling, and `Access-Control-Allow-*` headers on JSON and SSE responses; ADR-0018.
- Ollama / local provider adapter (Genesis Sprint 20, 2026-08-01): keyless `ollama` provider over Ollama's OpenAI-compatible `/v1` surface; ADR-0017.
- gateway reasoning-model response contract (Genesis Sprint 19, 2026-08-01): live OpenRouter verification surfaced `content: null` from reasoning models; the boundary is now contract, tests, and docs.
- gateway structured access logging (Genesis Sprint 18, 2026-07-31).
- gateway streaming support (Genesis Sprint 17, 2026-07-24).

## Deferred Work

The following need explicit requirements and, where durable, ADR or RFC coverage before implementation:

- streaming usage summaries and error events
- production authentication and rate limiting
- provider package extraction
- public package registry publishing
- standalone binaries
- live provider CI checks
- public website launch
- benchmark suite design
- MCP module implementation
- repository extraction or fragmentation

## Backlog Rules

- Keep backlog entries strategic and durable.
- Track sprint execution in GitHub issues.
- Add requirements before significant implementation.
- Record durable architecture decisions as ADRs.
- Record durable governance or product-operating decisions as decisions.
- Do not use backlog text to override accepted decisions.

## Examples

Good backlog entry:

```text
gateway configuration validation boundary
```

Too detailed for this file:

```text
Change line 42 in config.py to reject timeout_seconds <= 0.
```

## Best Practices

- Keep epics stable.
- Keep near-term candidates small enough to become one Genesis sprint.
- Promote backlog items into issues only when they have a clear release path.
- Revisit deferred work only when the surrounding boundaries are mature enough.

## Risks

- A stale backlog can mislead contributors.
- Too much detail can turn the backlog into a second issue tracker.
- Backlog entries without requirements can encourage premature implementation.

## References

- `.agentforge/constitution.md`
- `.agentforge/charter.md`
- `.agentforge/roadmap.md`
- `.agentforge/milestones.md`
- `.agentforge/decisions/0005-product-foundation-hygiene.md`

## Revision History

- 2026-08-01: Promoted 1.0.0 readiness into Sprint 47.
- 2026-08-01: Promoted variance-aware gate into Sprint 46.
- 2026-08-01: Promoted MCP resources/prompts into Sprint 45.
- 2026-08-01: Promoted key store encryption into Sprint 44.
- 2026-08-01: Promoted per-benchmark thresholds into Sprint 43.
- 2026-08-01: Promoted regression gate into Sprint 42.
- 2026-08-01: Promoted benchmark trends into Sprint 41.
- 2026-08-01: Promoted twin QA layer into Sprint 40.
- 2026-08-01: Promoted per-user auth into Sprint 39.
- 2026-08-01: Promoted benchmark pipeline into Sprint 38.
- 2026-08-01: Promoted twin service into Sprint 37.
- 2026-08-01: Promoted community and contribution paths into Genesis Sprint 36.
- 2026-08-01: Promoted public 0.1.0 scope into Genesis Sprint 35.
- 2026-08-01: Promoted engineering-twin profile into Genesis Sprint 33.
- 2026-08-01: Promoted SDK distribution into Genesis Sprint 31.
- 2026-08-01: Promoted gateway MCP surface into Genesis Sprint 30.
- 2026-08-01: Promoted gateway Python SDK into Genesis Sprint 29.
- 2026-08-01: Promoted AICS v0.3 tooling into Genesis Sprint 28.
- 2026-08-01: Promoted gateway auth/rate limiting into Genesis Sprint 27.
- 2026-08-01: Promoted AICS v0.2 structured metadata into Genesis Sprint 26.
- 2026-08-01: Promoted anthropic outbound provider into Genesis Sprint 25.
- 2026-08-01: Promoted Anthropic thinking/tool-use mapping into Genesis Sprint 24.
- 2026-08-01: Promoted Anthropic Messages inbound surface into Genesis Sprint 23.
- 2026-08-01: Promoted gateway CORS support into Genesis Sprint 21.
- 2026-07-10: Promoted gateway configuration validation boundary into Genesis Sprint 16.
- 2026-07-06: Initial backlog for Genesis Sprint 15.
