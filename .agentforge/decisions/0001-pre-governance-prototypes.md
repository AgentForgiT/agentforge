# DEC-0001: Treat Early Gateway and CLI Repos as Pre-Governance Prototypes

Metadata:

- Status: Accepted
- Date: 2026-06-28
- Applies to: `agentforge-gateway`, `agentforge-cli`

## Context

Before the monorepo decision was recorded, useful work was created in standalone repositories:

- `agentforge-gateway`
- `agentforge-cli`

These repositories contain real value, including a mock gateway MVP, an OpenRouter adapter, tests, CI, a prerelease, and scaffolding tooling.

## Decision

These repositories are considered pre-governance prototypes.

They should remain available while the canonical `agentforge` repository is bootstrapped. Their useful implementation and lessons should be migrated into the monorepo only after governance, architecture, and ADRs are in place.

## Consequences

- No useful work is discarded.
- The canonical architecture remains monorepo-first.
- Future contributors can understand why these repos exist.
- Migration work can be tracked explicitly rather than hidden.

## Revision History

- 2026-06-28: Initial decision.
