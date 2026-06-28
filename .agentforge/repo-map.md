# AgentForge Repository Map

Metadata:

- Status: Draft
- Phase: Genesis
- Last updated: 2026-06-28

## Canonical Repositories

| Repository | Role | Status |
| --- | --- | --- |
| `.github` | Organization governance and defaults | Active |
| `agentforge` | Canonical engineering monorepo | Active |
| `handbook` | Long-form handbook and learning material | Planned |
| `website` | Public site and docs portal | Planned |

## Pre-Governance Prototype Repositories

| Repository | Role | Recommended handling |
| --- | --- | --- |
| `agentforge-gateway` | Historical gateway prototype | Keep public with notice; canonical gateway now lives in `agentforge/apps/gateway` |
| `agentforge-cli` | Working scaffold CLI prototype | Keep public with notice; migrate or supersede through AICS validation tooling |

## Reconciliation Rule

Prototype repositories should not be deleted hastily. They contain useful implementation and release history. They should be marked as prototypes, referenced from the monorepo, and migrated only after the governance baseline is accepted.

After migration, prototype repositories remain public until a later accepted decision archives or repurposes them.

## Revision History

- 2026-06-28: Updated prototype repository disposition after gateway migration.
- 2026-06-28: Initial map.
