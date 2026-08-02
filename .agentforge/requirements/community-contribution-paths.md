# Community and Contribution Paths

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 36 |
| Issues | #155, #156, #157, #158, #159 |
| Related | DEC-0007, `.agentforge/backlog.md` (Epic 9 Community), 0.1.0 gate (DEC-0006) |

## Purpose

Define the community layer: how people (and AI assistants) contribute to AgentForge, how the release train works, and how the 0.1.0 gate frames external adoption. This is the human half of the adoption loop.

## Requirements

R1. **Expanded root `CONTRIBUTING.md`**: the sprint pattern (requirements → ADR → implementation → tests → CI → release), the exact validation command set, conventional-commit rules, and pointers to `docs/community.md`.
R2. **`docs/community.md`** (repo):
   - Contribution paths: code, docs, research, benchmarks, integrations.
   - The release train explained: every Genesis `0.0.x` = one governed increment; the 0.1.0 gate (DEC-0006) frames the public line.
   - Governance for contributors: RFC for major proposals, ADR for durable decisions, AI-assistant contributions follow the same hierarchy.
   - Where things live: the monorepo, the docs site, the handbook.
R3. **Docs-site refresh**: `contributing.md` links to the repo's `docs/community.md`, lists the live pages (playground, validator, compatibility, providers, benchmarks, twin), and states the 0.1.0 gate.
R4. Governance consistency: decisions register gains DEC-0007; roadmap/milestones/backlog updated.

## Acceptance Criteria

- [ ] `CONTRIBUTING.md` covers the sprint pattern + validation + commits
- [ ] `docs/community.md` covers paths, release train, gate, governance
- [ ] Docs-site contributing page refreshed and linked
- [ ] Decisions register, roadmap, milestones, backlog consistent; CI green
