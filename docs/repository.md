# Repository Architecture

AgentForge uses a modular monorepo during Genesis.

Core directories:

- `.agentforge/`: governance, memory, AI context, ADRs, RFCs, standards
- `apps/`: runnable applications
- `packages/`: reusable modules
- `docs/`: public documentation
- `examples/`: examples
- `scripts/`: automation
- `tests/`: cross-module tests
- `tools/`: development tools

See `.agentforge/repo-map.md` for the canonical repository map.

## Prototype Repositories

The public `agentforge-gateway` and `agentforge-cli` repositories are historical pre-governance prototypes.

They remain public during Genesis to preserve history, releases, early links, and migration context.

They are not canonical development locations:

- gateway work belongs in `AgentForgiT/agentforge`, under `apps/gateway`
- CLI and AICS tooling work belongs in `AgentForgiT/agentforge`, under `apps/cli`
- governance decisions belong in `AgentForgiT/agentforge`, under `.agentforge/`

DEC-0004 records the post-Sprint-8 disposition. Archiving, deleting, repurposing, or splitting repositories requires a later accepted decision.
