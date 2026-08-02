# DEC-0007: Community and Contribution Paths

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #155, #156, #157, #158, #159
- Related: DEC-0006 (0.1.0 scope), backlog Epic 9 (Community)

## Decision

Adopt four contribution paths and make the community layer an explicit, documented surface:

1. **Paths**: code (gateway, CLI, SDK), docs (repo + website), research (benchmarks, papers, datasets), and integrations (providers, MCP, IDE). All follow the same governance hierarchy.
2. **Release train as the frame**: contributions land against the governed sprint pattern (requirements → ADR → implementation → tests → CI → release). The 0.1.0 gate (DEC-0006) is the public adoption frame.
3. **Governance for everyone**: RFC for major proposals, ADR for durable decisions, and AI-assistant contributions follow the identical hierarchy — an AI-written change is an ordinary engineering change.
4. **Documentation location**: the canonical community docs live in the repo (`CONTRIBUTING.md`, `docs/community.md`); the website mirrors and links them.

## Rationale

The adoption loop's human half was thin: `CONTRIBUTING.md` existed but did not explain the sprint pattern, the release train, or the gate, and there was no community overview. External contributors and researchers need a defined, honest frame to plan against — the same discipline that governed the code.

## Alternatives Considered

- **Separate community repo/site** — rejected: splits governance; community docs belong beside the artifacts they describe.
- **Code-only contribution path** — rejected: the moat is AICS + governance + research; docs and research contributions are first-class.
- **Ungoverned "just open a PR"** — rejected: contradicts the project's entire premise.

## Consequences

- Contributors get a defined on-ramp: which path, which artifacts, which governance.
- The 0.1.0 gate is the shared frame for external participation.
- Community docs become part of the governed corpus (validated, versioned, revised like everything else).
