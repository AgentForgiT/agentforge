# DEC-0004: Keep Public Prototype Repositories as Historical References After Canonical Gateway and CLI Paths Exist

Metadata:

- Status: Accepted
- Date: 2026-07-02
- Related issues: #35, #36, #37, #38, #39
- Related decisions: ADR-0001, ADR-0002, ADR-0003, DEC-0001, DEC-0002, DEC-0003
- Related requirements: `.agentforge/requirements/prototype-repository-notices.md`

## Context

AgentForge has two public pre-governance prototype repositories:

- `agentforge-gateway`
- `agentforge-cli`

DEC-0001 classified both repositories as pre-governance prototypes.

DEC-0002 kept both repositories public with canonical monorepo notices and deferred any archive decision until later Genesis work.

Since then, the canonical monorepo has established:

- gateway module placement in `apps/gateway` through ADR-0002
- canonical CLI placement in `apps/cli` through ADR-0003
- canonical CLI packaging through ADR-0004
- canonical AICS commands through Genesis releases `0.0.4` through `0.0.8`

The prototypes still preserve useful context, but leaving their status ambiguous risks splitting future work across historical repositories and the canonical monorepo.

## Decision

Keep `agentforge-gateway` and `agentforge-cli` public during Genesis.

Treat both repositories as historical pre-governance prototypes that are superseded for canonical development.

New gateway work must target `AgentForgiT/agentforge` under `apps/gateway` unless a later accepted AgentForge decision changes that.

New CLI and AICS tooling work must target `AgentForgiT/agentforge` under `apps/cli` unless a later accepted AgentForge decision changes that.

Do not archive, delete, rename, or transfer either prototype repository in Sprint 9.

Add or refine README notices in both prototype repositories so contributors can identify the canonical development location quickly.

## Rationale

This preserves:

- prototype commit and release history
- discoverability for early links
- migration traceability
- evidence for decisions already made during Genesis

It also prevents:

- accidental feature work in superseded repositories
- confusion between historical prototypes and canonical modules
- premature repository destruction before the ecosystem matures

## Future Archive or Repurpose Criteria

A later decision may archive or repurpose a prototype repository when:

- the canonical monorepo contains the relevant migrated functionality or an explicit replacement
- README notices have existed long enough for contributors to orient
- release notes and docs clearly point to the canonical location
- no active workflow depends on the prototype as a development surface
- the project has a reason stronger than tidiness for changing repository status

Until then, public historical visibility is preferred.

## Consequences

Benefits:

- keeps repository history intact
- reduces contributor confusion
- reinforces ADR-0001 monorepo-first governance
- closes the DEC-0002 follow-up without destructive action

Trade-offs:

- public prototype repositories may still appear in searches
- notices must remain accurate as canonical modules evolve
- future maintainers may need another decision before archival or repurposing

## Alternatives Considered

Archive both prototype repositories immediately:
Rejected because early Genesis links, releases, and migration context are still useful.

Delete prototype repositories:
Rejected because deletion would destroy useful history and contradict the preservation rationale in DEC-0001 and DEC-0002.

Resume development in prototype repositories:
Rejected because canonical gateway and CLI development now have governed monorepo homes.

Split gateway or CLI back out into standalone repositories:
Rejected for Sprint 9 because ADR-0001 says extraction requires maturity, ownership, release cadence, or governance justification that does not yet exist.

## Follow-Up Work

- Update canonical repository docs to reference this decision.
- Refine README notices in `agentforge-gateway` and `agentforge-cli`.
- Revisit archive or repurpose only through a later accepted decision.

## Revision History

- 2026-07-02: Accepted for Genesis Sprint 9.
