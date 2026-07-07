# DEC-0005: Treat Backlog, Standards, and Repository Hygiene as Required Product Foundation

Metadata:

- Status: Accepted
- Date: 2026-07-06
- Related issues: #68, #67, #65, #66, #69
- Related decisions: ADR-0001, DEC-0001, DEC-0002, DEC-0003, DEC-0004
- Related requirements: `.agentforge/requirements/product-foundation-hygiene-mvp.md`

## Context

AgentForge has moved beyond a single bootstrap repository. It now operates as a release-managed engineering product with governance, CLI, gateway, tests, examples, CI, and repeated Genesis releases.

The original product direction called for durable epics, release-by-release execution, engineering standards, repository standards, and a persistent workspace.

Most of that foundation now exists, but three gaps remain:

- product backlog and epics are implied rather than recorded as a source of truth
- `.agentforge/standards/` exists but has no canonical standard documents
- `.editorconfig` and `.gitattributes` are absent from the required bootstrap baseline

Leaving those gaps unresolved would make future work more dependent on chat history and maintainer memory than on repository artifacts.

## Decision

Treat product backlog, canonical standards, and repository hygiene files as required AgentForge product-foundation artifacts.

The product backlog and durable epic map will live at:

- `.agentforge/backlog.md`

Canonical standards will live under:

- `.agentforge/standards/`

Public docs may summarize or explain standards for humans, but they must not silently contradict `.agentforge/standards/`.

The repository baseline will require:

- `.editorconfig`
- `.gitattributes`

Bootstrap validation will check that these foundation artifacts exist.

GitHub issues remain the sprint execution queue. The backlog is the strategic product map, not a replacement for issue tracking.

## Rationale

This preserves the AgentForge operating model:

- release-by-release execution
- governance-first development
- durable source-of-truth files
- AI-readable project context
- explicit standards
- reproducible repository behavior

It also closes a practical gap before the project expands into more provider, MCP, benchmark, website, community, and research work.

## Source of Truth Rules

Authority continues to flow:

1. Constitution
2. Project Charter
3. ADRs
4. RFCs
5. Engineering Standards
6. Code

The product backlog is planning context. It does not override accepted decisions.

Standards under `.agentforge/standards/` are canonical standards. Human-facing files under `docs/` may restate, explain, or link to them.

## Consequences

Benefits:

- gives contributors a durable backlog and epic map
- gives AI assistants a stable standards entry point
- reduces editor and line-ending ambiguity
- makes the bootstrap validator protect product-foundation files
- keeps issue tracking focused on sprint execution

Trade-offs:

- adds a small amount of governance surface area
- requires docs and standards to be kept aligned
- may need future refinement as the project approaches a public `0.1.0` line

## Alternatives Considered

Keep backlog only in GitHub issues:
Rejected because issues are good execution records but weaker as a durable strategic source of truth for AI-assisted context.

Keep standards only in `docs/`:
Rejected because `.agentforge/standards/` is already named in the authority hierarchy and should be the canonical standards home.

Defer `.editorconfig` and `.gitattributes`:
Rejected because they are low-cost repository hygiene files and become more painful to add after more contributors and generated artifacts arrive.

Create a separate backlog repository:
Rejected because ADR-0001 keeps early engineering work in the canonical monorepo until maturity or ownership requires extraction.

## Follow-Up Work

- Keep backlog changes tied to release planning.
- Expand standards only when they remove real ambiguity.
- Revisit public `0.1.0` release framing through a later requirements document or decision.
- Consider additional standards for security, releases, benchmarks, and compatibility as those areas mature.

## Revision History

- 2026-07-06: Accepted for Genesis Sprint 15.
