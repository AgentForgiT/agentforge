# AgentForge Repository Map

Metadata:

- Status: Draft
- Phase: Genesis
- Last updated: 2026-07-02

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
| `agentforge-gateway` | Historical gateway prototype | Public historical reference; superseded for canonical development by `agentforge/apps/gateway` |
| `agentforge-cli` | Historical scaffold CLI prototype | Public historical reference; superseded for canonical development by `agentforge/apps/cli` |

## Reconciliation Rule

Prototype repositories should not be deleted hastily. They contain useful implementation and release history. They should be marked as prototypes, referenced from the monorepo, and migrated only after the governance baseline is accepted.

After migration, prototype repositories remain public historical references until a later accepted decision archives or repurposes them.

DEC-0004 confirms that `agentforge-gateway` and `agentforge-cli` remain public during Genesis and are no longer canonical development locations.

## Revision History

- 2026-07-02: Added DEC-0004 post-Sprint-8 prototype disposition status.
- 2026-06-28: Added canonical CLI path for AICS validation.
- 2026-06-28: Updated prototype repository disposition after gateway migration.
- 2026-06-28: Initial map.
