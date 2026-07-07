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

## Product Foundation

The durable product backlog and epic map live at `.agentforge/backlog.md`.

Canonical engineering and documentation standards live under `.agentforge/standards/`. Human-facing docs may summarize those standards, but `.agentforge/standards/` is the source of truth.

The repository baseline includes `.editorconfig` and `.gitattributes` so contributors and automation have explicit editor and Git text handling defaults.

## Prototype Repositories

The public `agentforge-gateway` and `agentforge-cli` repositories are historical pre-governance prototypes.

They remain public during Genesis to preserve history, releases, early links, and migration context.

They are not canonical development locations:

- gateway work belongs in `AgentForgiT/agentforge`, under `apps/gateway`
- CLI and AICS tooling work belongs in `AgentForgiT/agentforge`, under `apps/cli`
- governance decisions belong in `AgentForgiT/agentforge`, under `.agentforge/`

DEC-0004 records the post-Sprint-8 disposition. Archiving, deleting, repurposing, or splitting repositories requires a later accepted decision.
