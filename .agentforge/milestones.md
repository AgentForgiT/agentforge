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

## Revision History

- 2026-06-28: Added CLI path decision for AICS validation.
- 2026-06-28: Added Genesis-0.0.3 AICS milestone.
- 2026-06-28: Added prototype repository disposition.
- 2026-06-28: Expanded Genesis-0.0.2 exit criteria.
- 2026-06-28: Initial draft.
