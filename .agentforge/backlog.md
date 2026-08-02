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
