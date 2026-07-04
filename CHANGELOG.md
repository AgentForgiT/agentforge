# Changelog

## Unreleased

## Genesis-0.0.11 - 2026-07-04

- Added Sprint 11 requirements and ADR-0009 for offline gateway provider contract tests.
- Added provider contract tests for mock and OpenRouter adapters without live network or credential requirements.
- Updated gateway documentation to explain provider contract validation and the deferred provider package extraction path.

## Genesis-0.0.10 - 2026-07-03

- Added Sprint 10 requirements and ADR-0008 for the gateway provider adapter boundary.
- Refactored gateway provider adapters behind explicit internal modules while preserving mock and OpenRouter behavior.
- Added provider boundary tests and updated gateway documentation.

## Genesis-0.0.9 - 2026-07-02

- Added Sprint 9 requirements and DEC-0004 for post-Sprint-8 prototype repository disposition.
- Clarified that `agentforge-gateway` and `agentforge-cli` remain public historical references and are superseded for canonical development by monorepo modules.
- Updated repository docs, roadmap, milestones, and prototype notice guidance.

## Genesis-0.0.8 - 2026-06-29

- Added the canonical `agentforge doctor` CLI command for read-only local AICS context diagnostics.
- Added grouped diagnostic checks, unhealthy-context exit semantics, and next-step guidance.
- Added ADR-0007, Sprint 8 requirements, diagnostics tests, install smoke coverage, and docs.

## Genesis-0.0.7 - 2026-06-29

- Added the canonical `agentforge explain-context` CLI command for read-only AICS project orientation.
- Added validation-informed explanation output with key governance entry points and incomplete-context signals.
- Added ADR-0006, Sprint 7 requirements, explanation tests, install smoke coverage, and docs.

## Genesis-0.0.6 - 2026-06-29

- Added the canonical `agentforge init-context` CLI command for scaffolding a minimal AICS v0.1 project context.
- Added CLI-owned scaffold templates, safe no-overwrite initialization behavior, and ADR-0005.
- Added scaffolding tests, editable-install smoke coverage, and Sprint 6 planning artifacts.

## Genesis-0.0.5 - 2026-06-29

- Added explicit install smoke tests and CI validation for the installable CLI.
- Added editable-install packaging for the canonical `agentforge` CLI command.
- Accepted ADR-0004 for installable CLI packaging and editable-install distribution strategy.
- Added installable CLI requirements for Genesis Sprint 5.

## Genesis-0.0.4 - 2026-06-28

- Added CLI command tests and CI validation.
- Implemented the canonical `agentforge validate-context` CLI MVP.
- Accepted ADR-0003 for canonical CLI architecture and packaging boundaries.
- Added canonical CLI MVP requirements for `agentforge validate-context`.

## Genesis-0.0.3 - 2026-06-28

- Documented the canonical CLI path for AICS validation.
- Added a minimal AICS example project context tree.
- Added AICS v0.1 validation rules and local validator.
- Added draft AICS v0.1 specification.

## Genesis-0.0.2 - 2026-06-28

- Migrated the gateway MVP into `apps/gateway`.
- Added gateway tests, examples, docs, and CI validation.
- Documented disposition for pre-governance prototype repositories.
- Added Genesis Sprint 2 gateway reconciliation requirements.
- Added ADR-0002 for gateway module placement and provider adapter boundaries.

## Genesis-0.0.1 - 2026-06-28

- Initialized the canonical AgentForge monorepo.
- Added the `.agentforge/` project brain.
- Recorded ADR-0001 for the modular monorepo strategy.
- Added AI assistant context files and bootstrap validation.
