# ADR-0001: Start with a Modular Monorepo

Metadata:

- Status: Accepted
- Date: 2026-06-28
- Deciders: AgentForge maintainers
- Applies to: AgentForge repository strategy

## Context

AgentForge is intended to become a broad ecosystem including gateway, providers, MCP tooling, integrations, workflows, benchmarks, SDKs, documentation, and automation.

An early plan proposed many standalone repositories. That would make each subsystem explicit but would also create high maintenance overhead before the project has enough contributors, release cadence, or governance maturity to justify fragmentation.

## Decision

AgentForge will start with a modular monorepo named `agentforge`.

Engineering modules begin inside the monorepo. Repositories are split only when maturity justifies extraction.

The initial organization-level repository set is:

- `.github`
- `agentforge`
- `handbook`
- `website`

## Consequences

Benefits:

- simpler CI and release management during Genesis
- easier refactoring across modules
- fewer issue and PR queues
- stronger governance consistency
- lower contributor onboarding overhead

Trade-offs:

- module boundaries must be documented and enforced deliberately
- release tooling may need to support partial releases later
- future extraction requires care to preserve history and context

## Extraction Criteria

Extraction requires a new ADR and should be considered only when a module has independent ownership, release cadence, governance needs, CI scale, or downstream consumption requirements.

## Revision History

- 2026-06-28: Accepted during Genesis Sprint 1 bootstrap.
