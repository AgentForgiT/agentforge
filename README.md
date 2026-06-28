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

Genesis Sprint 1 creates the AgentForge Bootstrap Kit: a production-quality AI-native project skeleton that can be opened by Codex, Claude Code, Kiro, Gemini CLI, OpenCode, GitHub Copilot, and future AI coding assistants while preserving one shared architectural truth.

## Governance

Authority flows in this order:

1. Constitution
2. Project Charter
3. ADRs
4. RFCs
5. Engineering Standards
6. Code

If code conflicts with governance, governance wins until superseded by a newer approved decision.
