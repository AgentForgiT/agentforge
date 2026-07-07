# Documentation Standards

Metadata:

- Status: Draft
- Phase: Genesis
- Related decisions: DEC-0005
- Last updated: 2026-07-06

## Purpose

Define the canonical documentation standards for AgentForge.

## Scope

These standards apply to significant governance documents, requirements, ADRs, decisions, RFCs, specs, module docs, and public technical documentation.

## Background

AgentForge is documentation-first because AI-assisted engineering depends on durable, readable context. Documentation should preserve decisions, explain trade-offs, and make future work easier to audit.

## Architecture

Canonical project memory lives in `.agentforge/`.

Human-facing docs live in `docs/` and may summarize, explain, or teach the canonical records. They must not silently contradict the Constitution, Charter, ADRs, RFCs, decisions, or standards.

## Required Sections

Significant documents should include:

- Metadata
- Purpose
- Scope
- Background
- Architecture or Design
- Examples where relevant
- Best Practices where relevant
- Risks
- References
- Revision History

Short documents may omit irrelevant sections, but they should still identify purpose and revision history when they shape project behavior.

## Metadata

Metadata should identify:

- status
- phase or date
- related issues where useful
- related decisions where useful
- last updated date where useful

## Examples

Good reference style:

```text
- `.agentforge/adrs/0001-modular-monorepo.md`
- `docs/repository.md`
```

Poor reference style:

```text
- the thing we discussed earlier
```

## Best Practices

- Prefer durable file references over chat references.
- Explain why a decision exists, not only what changed.
- Keep docs close to the module or concern they explain.
- Update revision history when meaningful behavior or guidance changes.
- Keep release notes concise but explicit about scope, validation, and limitations.

## Risks

- Duplicated documentation can drift.
- Overlong docs can hide the actual decision.
- Missing references make future audits harder.

## References

- `.agentforge/constitution.md`
- `.agentforge/charter.md`
- `.agentforge/decisions.md`
- `.agentforge/standards/engineering.md`
- `docs/documentation-standards.md`
- `docs/release-policy.md`

## Revision History

- 2026-07-06: Initial canonical documentation standards for Genesis Sprint 15.
