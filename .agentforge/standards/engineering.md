# Engineering Standards

Metadata:

- Status: Draft
- Phase: Genesis
- Related decisions: DEC-0005
- Last updated: 2026-07-06

## Purpose

Define the canonical engineering standards for AgentForge contributors and AI assistants.

## Scope

These standards apply to repository changes, implementation work, tests, examples, automation, and release preparation across the canonical `agentforge` monorepo.

## Background

AgentForge prioritizes maintainability, reproducibility, governance, and release discipline. Engineering standards must be explicit enough to guide future contributors without turning Genesis into a tooling-heavy project before the architecture is ready.

## Architecture

Authority flows through:

1. Constitution
2. Project Charter
3. ADRs
4. RFCs
5. Engineering Standards
6. Code

If implementation conflicts with governance, governance wins until superseded by a newer accepted decision.

## Standards

Before significant implementation:

- define requirements
- write an RFC when the change is broad or exploratory
- record an ADR when the architecture decision is durable
- update documentation before or alongside implementation
- add tests proportionate to risk
- validate locally
- document release scope and limitations

Code should:

- prefer readable control flow over clever abstractions
- keep interfaces explicit
- use dependency injection at module boundaries
- avoid provider lock-in
- avoid hidden configuration
- avoid duplicated business logic
- keep provider-specific behavior inside provider adapters
- keep default validation offline and deterministic

Repository changes should:

- stay scoped to the sprint or issue
- avoid unrelated refactors
- preserve monorepo-first strategy unless an accepted ADR says otherwise
- keep generated or bulky artifacts out of the repo unless justified
- update bootstrap validation when a file becomes part of the required foundation

## Examples

Good implementation flow:

```text
requirements -> ADR -> docs -> implementation -> tests -> validation -> release notes
```

Poor implementation flow:

```text
implementation -> undocumented behavior -> retroactive rationale
```

## Best Practices

- Keep changes small enough to review.
- Let tests describe behavior, not implementation trivia.
- Prefer structured parsers or APIs over ad hoc string manipulation.
- Keep secrets in environment variables.
- Keep default CI independent of live providers.
- Treat release notes as part of the feature.

## Risks

- Standards can become performative if they are not enforced by validation or review.
- Too many rules too early can slow useful Genesis work.
- Skipping governance for convenience can create long-term architecture debt.

## References

- `.agentforge/constitution.md`
- `.agentforge/charter.md`
- `.agentforge/architecture.md`
- `.agentforge/decisions.md`
- `.agentforge/roadmap.md`
- `docs/coding-standards.md`

## Revision History

- 2026-07-06: Initial canonical engineering standards for Genesis Sprint 15.
