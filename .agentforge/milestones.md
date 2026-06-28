# AgentForge Milestones

Metadata:

- Status: Draft
- Phase: Genesis
- Last updated: 2026-06-28

## Genesis-0.0.1: Bootstrap Kit

Scope:

- governance baseline
- AI context baseline
- repository structure
- starter templates
- validation workflow placeholder

Exit criteria:

- canonical `agentforge` repository exists
- `.agentforge/` project brain exists
- ADR-0001 records the monorepo decision
- AI assistant context files exist
- CI validates required bootstrap files

## Genesis-0.0.2: Gateway Reconciliation

Scope:

- import or recreate gateway prototype under governance
- document provider adapter boundaries
- preserve OpenAI-compatible API shape
- keep tests deterministic
- decide prototype repository disposition

Exit criteria:

- requirements document exists
- gateway placement ADR is accepted
- gateway MVP is migrated into `apps/gateway`
- gateway tests run in CI
- prototype repository status is documented
- prototype repositories remain public unless a later accepted decision changes their status

## Genesis-0.0.3: AICS Draft

Scope:

- draft AICS v0.1
- define validation rules
- add an example AICS context tree
- plan CLI validation path

Exit criteria:

- AICS v0.1 spec exists
- validation rules are documented
- example context tree exists
- CLI path decision exists

## Genesis-0.0.4: Canonical CLI MVP

Scope:

- define canonical CLI MVP requirements
- decide `apps/cli` architecture and packaging boundaries
- implement `agentforge validate-context`
- add CLI tests and CI validation
- document CLI usage and release limitations

Exit criteria:

- requirements document exists
- ADR-0003 is accepted and linked from the decision register
- `apps/cli` contains the source-tree CLI MVP
- CLI validates the canonical repo and minimal AICS example
- CLI tests run locally and in CI
- docs explain how to run the CLI against the repo and minimal example

## Genesis-0.0.5: Installable CLI

Scope:

- define installable CLI requirements
- decide CLI packaging and distribution strategy
- implement an installable `agentforge` command
- add install smoke tests and CI validation
- document installation and release limitations

Exit criteria:

- requirements document exists for issue #16
- packaging ADR or decision exists for issue #18
- a documented local install exposes `agentforge validate-context`
- installed CLI validates the canonical repo and minimal AICS example
- install smoke tests run locally and in CI for issue #17
- docs explain how to install and run the CLI for issue #19

## Revision History

- 2026-06-28: Added Genesis-0.0.5 installable CLI milestone.
- 2026-06-28: Added Genesis-0.0.4 canonical CLI MVP milestone.
- 2026-06-28: Added CLI path decision for AICS validation.
- 2026-06-28: Added Genesis-0.0.3 AICS milestone.
- 2026-06-28: Added prototype repository disposition.
- 2026-06-28: Expanded Genesis-0.0.2 exit criteria.
- 2026-06-28: Initial draft.
