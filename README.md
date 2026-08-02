# AgentForge

The Open Platform for Agentic AI Engineering.

AgentForge is an open, vendor-neutral engineering ecosystem for AI gateways, agent orchestration, IDE compatibility, MCP tooling, benchmarks, documentation, and automation.

## Status

- Phase: Genesis
- Release line: Genesis-0.0.x
- Canonical repository: `agentforge`
- GitHub organization: `AgentForgiT`

This repository is the canonical modular monorepo for early AgentForge engineering work. Subsystems begin here as modules and are extracted into standalone repositories only when maturity, ownership, release cadence, or governance justify the split.

## Repository Brain

The `.agentforge/` directory is the institutional memory of the project. It contains the constitution, charter, roadmap, architecture, decisions, standards, ADRs, RFCs, and AI assistant context files.

Every human contributor and AI assistant should treat `.agentforge/` as the first source of truth.

The draft AgentForge AI Context Specification is available at `.agentforge/specs/aics-v0.1.md`.

## Initial Layout

- `.agentforge/`: project governance, memory, standards, and AI context
- `apps/`: runnable applications such as gateway, CLI, and playground
- `packages/`: reusable libraries and integrations
- `docs/`: human-facing technical documentation
- `examples/`: runnable examples and reference use cases
- `scripts/`: repository automation
- `tests/`: cross-module tests
- `tools/`: internal development tools

## Current Priority

Sprint 43 ships per-benchmark thresholds (ADR-0035): `benchmarks/thresholds.json` (checked-in default + per-name overrides) consumed by the regression gate — tight 5% on stable gateway latency, loose 20% on jittery CLI timing. Release 0.8.0.

Gateway provider adapters live behind explicit internal modules under `agentforge_gateway.providers`, chat-completion request validation lives under `agentforge_gateway.requests`, gateway errors use a standard JSON envelope, successful chat-completion responses and streaming chunks pass through `agentforge_gateway.responses`, JSON configuration is validated by `agentforge_gateway.config`, and structured access records are emitted through `agentforge_gateway.logger`. Product backlog and epics live in `.agentforge/backlog.md`, canonical standards live in `.agentforge/standards/`, and repository hygiene is anchored by `.editorconfig` and `.gitattributes`. The public `agentforge-gateway` and `agentforge-cli` repositories remain historical pre-governance prototypes; new canonical gateway and CLI work belongs in this repository under `apps/gateway` and `apps/cli`.

Run local validation:

```bash
python scripts/validate_bootstrap.py
python scripts/validate_aics.py
python scripts/validate_aics.py examples/aics/minimal-project
python -m unittest discover -s apps/cli/tests
python -m unittest apps.cli.tests.test_install
python -m unittest discover -s apps/gateway/tests
```

Run the source-tree CLI:

```bash
python apps/cli/bin/agentforge.py validate-context
python apps/cli/bin/agentforge.py validate-context examples/aics/minimal-project
python apps/cli/bin/agentforge.py init-context demo-project
python apps/cli/bin/agentforge.py explain-context demo-project
python apps/cli/bin/agentforge.py doctor demo-project
```

Install the CLI from the monorepo:

```bash
python -m pip install -e apps/cli
agentforge validate-context
agentforge validate-context examples/aics/minimal-project
agentforge init-context demo-project
agentforge explain-context demo-project
agentforge doctor demo-project
```

## Governance

Authority flows in this order:

1. Constitution
2. Project Charter
3. ADRs
4. RFCs
5. Engineering Standards
6. Code

If code conflicts with governance, governance wins until superseded by a newer approved decision.

## Links

- **Docs site:** <https://agentforgit.github.io/agentforge-docs-site/>
- **Handbook:** <https://github.com/AgentForgiT/agentforge-handbook>
- **Community:** <https://github.com/AgentForgiT/agentforge-community>
- **Organization:** <https://github.com/AgentForgiT>
