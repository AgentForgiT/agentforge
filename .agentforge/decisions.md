# AgentForge Decision Register

Metadata:

- Status: Active
- Phase: Genesis
- Last updated: 2026-06-29

## Purpose

This file indexes accepted decisions and their current status.

Durable architecture decisions should be recorded as ADRs in `.agentforge/adrs/`.

## Decisions

| ID | Date | Status | Title | Record |
| --- | --- | --- | --- | --- |
| ADR-0001 | 2026-06-28 | Accepted | Start with a modular monorepo | `.agentforge/adrs/0001-modular-monorepo.md` |
| ADR-0002 | 2026-06-28 | Accepted | Place Gateway in `apps/gateway` with provider adapter boundary | `.agentforge/adrs/0002-gateway-module-placement.md` |
| ADR-0003 | 2026-06-28 | Accepted | Place canonical CLI in `apps/cli` with shared validation boundary | `.agentforge/adrs/0003-cli-module-architecture.md` |
| ADR-0004 | 2026-06-28 | Accepted | Package the canonical CLI from `apps/cli` with editable install first | `.agentforge/adrs/0004-cli-packaging-and-distribution.md` |
| ADR-0005 | 2026-06-29 | Accepted | Scaffold AICS context from packaged templates with safe no-overwrite initialization | `.agentforge/adrs/0005-context-scaffolding-strategy.md` |
| ADR-0006 | 2026-06-29 | Accepted | Explain AICS context through a read-only orientation report with validation-informed status | `.agentforge/adrs/0006-context-explanation-boundary.md` |
| ADR-0007 | 2026-06-29 | Accepted | Diagnose local AICS context health with read-only doctor checks | `.agentforge/adrs/0007-doctor-diagnostics-boundary.md` |
| DEC-0001 | 2026-06-28 | Accepted | Treat early gateway and CLI repos as pre-governance prototypes | `.agentforge/decisions/0001-pre-governance-prototypes.md` |
| DEC-0002 | 2026-06-28 | Accepted | Keep prototype repositories public with canonical monorepo notices | `.agentforge/decisions/0002-prototype-repository-disposition.md` |
| DEC-0003 | 2026-06-28 | Accepted | Build AICS validation CLI in the canonical monorepo | `.agentforge/decisions/0003-cli-path-for-aics-validation.md` |

## Revision History

- 2026-06-29: Added ADR-0007.
- 2026-06-29: Added ADR-0006.
- 2026-06-29: Added ADR-0005.
- 2026-06-28: Added ADR-0003.
- 2026-06-28: Added ADR-0004.
- 2026-06-28: Added DEC-0003.
- 2026-06-28: Added DEC-0002.
- 2026-06-28: Added ADR-0002.
- 2026-06-28: Initial register.
