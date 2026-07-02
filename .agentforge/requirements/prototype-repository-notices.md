# Prototype Repository Notices Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 9
- Related issues: #35, #36, #37, #38, #39
- Related decisions: ADR-0001, ADR-0002, ADR-0003, DEC-0001, DEC-0002, DEC-0003, DEC-0004
- Related policy: `docs/release-policy.md`
- Last updated: 2026-07-02

## Purpose

Define the requirements for resolving public pre-governance prototype repository ambiguity after the canonical gateway and CLI paths exist in the `agentforge` monorepo.

This document exists so Sprint 9 clarifies repository status, contributor direction, and non-destructive handling before further Genesis work expands the ecosystem.

## Scope

In scope:

- public pre-governance repositories `agentforge-gateway` and `agentforge-cli`
- canonical monorepo documentation that explains prototype status
- README notices in prototype repositories
- contributor guidance for where new gateway and CLI work should happen
- release notes for the prototype disposition update

Out of scope:

- deleting, archiving, transferring, or renaming prototype repositories
- migrating additional code from prototypes
- creating new standalone repositories
- moving canonical modules out of the monorepo
- changing package names or release history
- modifying private future-scope repositories in the GitHub organization

## Background

DEC-0001 classified `agentforge-gateway` and `agentforge-cli` as pre-governance prototypes.

DEC-0002 kept the prototype repositories public with notices during early Genesis work.

ADR-0002 migrated the gateway MVP into `apps/gateway`.

ADR-0003 placed the canonical CLI in `apps/cli`.

DEC-0003 directed future AICS validation CLI work into the canonical monorepo.

Genesis releases through `Genesis-0.0.8` now provide the canonical gateway module and canonical CLI commands:

- `agentforge validate-context`
- `agentforge init-context`
- `agentforge explain-context`
- `agentforge doctor`

The old follow-up in DEC-0002 said to decide after Genesis Sprint 3 whether either prototype repository should be archived. Sprint 9 resolves that follow-up without destructive action.

## Repository Requirements

The canonical `agentforge` repository must remain the source of truth for early AgentForge engineering.

The public prototype repositories must remain public during Sprint 9.

The prototype repositories must be described as historical prototypes, not canonical development locations.

The canonical development locations must be:

- gateway: `AgentForgiT/agentforge`, `apps/gateway`
- CLI: `AgentForgiT/agentforge`, `apps/cli`
- governance and decisions: `AgentForgiT/agentforge`, `.agentforge/`

## Notice Requirements

Each prototype README notice must state:

- the repository is historical and pre-governance
- the canonical development location
- whether the prototype has been superseded for new canonical work
- why the repository remains public
- that new work should target the canonical monorepo unless a later accepted AgentForge decision says otherwise

The notice should be near the top of the README.

The notice should be concise, plain text, and easy to see on GitHub.

## Canonical Documentation Requirements

The canonical monorepo must update:

- `.agentforge/repo-map.md`
- `.agentforge/roadmap.md`
- `.agentforge/milestones.md`
- `.agentforge/decisions.md`
- `docs/repository.md`
- `docs/gateway.md`
- `README.md`
- `CHANGELOG.md`

The documentation should make clear that the prototype repositories are retained for history and traceability, not used as the primary development surface.

## Decision Requirements

Sprint 9 must record a durable decision that:

- keeps `agentforge-gateway` and `agentforge-cli` public during Genesis
- marks both as superseded for canonical development
- avoids archive/delete actions during Sprint 9
- defines future archive or repurpose criteria
- preserves the monorepo-first strategy from ADR-0001

## Testing and Validation Requirements

Canonical monorepo validation must continue to pass:

- bootstrap validation
- AICS validation for the canonical repo
- AICS validation for the minimal example
- CLI tests
- CLI install smoke tests
- gateway tests

Prototype README notice updates should be reviewed for clarity and committed independently in their repositories.

## Acceptance Criteria

Issue #35 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references DEC-0001, DEC-0002, DEC-0003, ADR-0001, ADR-0002, and ADR-0003
- it defines the Sprint 9 notice and canonical documentation requirements

The Sprint 9 prototype disposition update is complete when:

- issue #36 records DEC-0004
- issue #37 updates canonical repository docs
- issue #39 updates notices in `agentforge-gateway` and `agentforge-cli`
- issue #38 validates and releases `Genesis-0.0.9`

## Examples

Gateway canonical direction:

```text
Canonical gateway development now lives in AgentForgiT/agentforge under apps/gateway.
```

CLI canonical direction:

```text
Canonical CLI development now lives in AgentForgiT/agentforge under apps/cli.
```

## Best Practices

- Preserve prototype history.
- Keep canonical development paths obvious.
- Avoid destructive repository actions without a later decision.
- Prefer clear notices over hidden tribal knowledge.
- Revisit repository extraction only when maturity, ownership, or release cadence justifies it.

## Risks

- Leaving prototype status vague can confuse contributors.
- Archiving too early can break discoverability and migration traceability.
- Continuing development in prototypes can fragment governance.
- Over-documenting status in many places can drift unless the repo map stays authoritative.

## References

- `.agentforge/adrs/0001-modular-monorepo.md`
- `.agentforge/adrs/0002-gateway-module-placement.md`
- `.agentforge/adrs/0003-cli-module-architecture.md`
- `.agentforge/decisions/0001-pre-governance-prototypes.md`
- `.agentforge/decisions/0002-prototype-repository-disposition.md`
- `.agentforge/decisions/0003-cli-path-for-aics-validation.md`
- `.agentforge/decisions/0004-post-sprint-8-prototype-disposition.md`
- `.agentforge/repo-map.md`
- `docs/repository.md`
- `docs/gateway.md`

## Revision History

- 2026-07-02: Initial requirements draft for Genesis Sprint 9.
