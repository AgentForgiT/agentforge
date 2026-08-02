# AgentForge AI Context Specification v0.2

Metadata:

- Status: Draft
- Version: 0.2
- Phase: Genesis Sprint 26
- Related issue: #117
- Related governance: `.agentforge/adrs/0022-aics-v0.2-front-matter.md`, `.agentforge/specs/aics-v0.1.md`
- Last updated: 2026-08-01

## Purpose

AgentForge AI Context Specification, or AICS, defines a portable project context structure that can be read by humans, AI coding assistants, and validation tools.

AICS v0.2 extends v0.1 with **structured front matter** (machine-parseable metadata) and **machine-reported adoption levels**. v0.1 contexts remain valid.

## Changes from v0.1

1. **Structured front matter** replaces plain `Metadata:` blocks as the recommended metadata format (ADR-0022). Plain `Metadata:` blocks remain accepted.
2. **Adoption levels** (Level 1 Present / Level 2 Governed / Level 3 Validated) are machine-reported by the validator, not just described.
3. **Version marker**: `.agentforge/aics-version` declares the context's spec version.

## Front Matter

A context document uses structured metadata when it begins with:

```text
---
status: active
aics-version: 0.2
---
```

Required front matter fields:

- `status` — document lifecycle status (draft, active, superseded, accepted, etc.)
- `aics-version` — the AICS spec version the document targets (0.2 for this spec)

Recommended fields (from the v0.1 metadata list):

- `version` — document version when applicable
- `phase` — project phase or milestone
- `applies-to` — scope of applicability
- `related-issues` — issue references
- `related-adrs`, `related-rfcs`, `related-decisions` — decision linkage
- `last-updated` — date string

A document passes metadata checks with either front matter (both required fields) or a plain `Metadata:` block (v0.1 compatibility). Front matter is required to declare **Level 3, Context Validated**.

## Version Marker

An AICS v0.2 context SHOULD include `.agentforge/aics-version` containing `0.2`:

```text
0.2
```

Absence of the marker means the context targets v0.1: metadata checks still pass, but the context can report at most Level 2, with a warning when Level 3 is attempted.

## Adoption Levels

| Level | Name | Machine check |
| --- | --- | --- |
| 1 | Context Present | required directories + files exist |
| 2 | Context Governed | metadata (either style) present in metadata-checked files; templates + required-text checks pass |
| 3 | Context Validated | front matter with `aics-version` in metadata-checked files; `.agentforge/aics-version` marker; all checks pass; validation runs locally and in CI |

The validator reports the achieved level and any warnings (recommended files missing, plain-Metadata style at Level 3 target). Warnings never fail validation.

## Required Directory Structure

Unchanged from v0.1:

```text
.agentforge/
  constitution.md
  charter.md
  decisions.md
  architecture.md
  repo-map.md
  agents/
    AGENTS.md
  adrs/
    ADR_TEMPLATE.md
  rfcs/
    RFC_TEMPLATE.md
  standards/
```

## Required Files

Unchanged from v0.1: `constitution.md`, `charter.md`, `decisions.md`, `architecture.md`, `repo-map.md`, `agents/AGENTS.md`, `adrs/ADR_TEMPLATE.md`, `rfcs/RFC_TEMPLATE.md`.

## Optional Files

Unchanged from v0.1 (vision, roadmap, glossary, tech-stack, milestones, requirements/, specs/, decisions/, agent adapter files). Missing recommended files produce warnings, not errors.

## Compatibility

AICS v0.2 is a superset of v0.1:

- All v0.1 checks still pass unchanged.
- v0.1 `Metadata:` blocks are accepted everywhere.
- v0.2 adds front matter, level reporting, and the version marker without breaking v0.1 projects.

## Validation Goals

The v0.2 validation rule set is documented in `.agentforge/specs/aics-validation-v0.2.md`.

## Best Practices

- Use front matter for all new and edited context documents.
- Set `aics-version: 0.2` in front matter.
- Keep the version marker in sync.
- Report your adoption level in CI output.
- Prefer references over duplication (unchanged from v0.1).

## Revision History

- 2026-08-01: Initial AICS v0.2 draft (front matter + adoption levels + version marker).
