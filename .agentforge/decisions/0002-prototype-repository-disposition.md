# DEC-0002: Keep Prototype Repositories Public with Canonical Monorepo Notices

Metadata:

- Status: Accepted
- Date: 2026-06-28
- Related issues: #5
- Related decisions: ADR-0001, ADR-0002, DEC-0001

## Context

AgentForge created useful pre-governance prototype repositories before accepting the modular monorepo strategy:

- `agentforge-gateway`
- `agentforge-cli`

The gateway MVP has now been migrated into `apps/gateway` in the canonical `agentforge` monorepo.

## Decision

Keep pre-governance prototype repositories public for now.

They should be treated as historical prototypes, not canonical development locations. Each prototype repository should eventually receive a README notice pointing contributors to the canonical `agentforge` monorepo and explaining whether the prototype is migrated, superseded, or still pending reconciliation.

Do not archive or delete prototype repositories during Genesis Sprint 2.

## Rationale

Keeping the repositories available preserves:

- release and commit history
- discoverability for early links
- migration traceability
- comparison between prototype and canonical module

Adding notices reduces contributor confusion without destructive cleanup.

## Follow-Up Work

- Add a historical prototype notice to `agentforge-gateway`.
- Add a historical prototype notice to `agentforge-cli`.
- Decide after Genesis Sprint 3 whether either repository should be archived.

## Revision History

- 2026-06-28: Initial accepted decision.
