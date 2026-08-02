# AICS Validation Rules v0.2

Metadata:

- Status: Draft
- Version: 0.2
- Phase: Genesis Sprint 26
- Related issue: #117
- Related spec: `.agentforge/specs/aics-v0.2.md`, `.agentforge/specs/aics-validation-v0.1.md`
- Last updated: 2026-08-01

## Purpose

This document defines the machine-checkable validation rules for AICS v0.2: the v0.1 rules plus front matter checks, adoption-level reporting, and the version marker.

The validator remains offline, dependency-free (stdlib only), and deterministic — no YAML library; front matter is parsed with string checks.

## Validation Levels

The validator reports the achieved adoption level:

- **Level 1, Context Present** — required directories and files exist.
- **Level 2, Context Governed** — metadata present (either style) + templates + required-text checks.
- **Level 3, Context Validated** — front matter with `aics-version` + version marker + all checks pass.

The level is the highest level whose checks all pass. Warnings are collected but never fail validation.

## Required Directories

Unchanged from v0.1:

```text
.agentforge/
.agentforge/adrs/
.agentforge/agents/
.agentforge/rfcs/
.agentforge/standards/
```

## Required Files

Unchanged from v0.1:

```text
.agentforge/constitution.md
.agentforge/charter.md
.agentforge/decisions.md
.agentforge/architecture.md
.agentforge/repo-map.md
.agentforge/agents/AGENTS.md
.agentforge/adrs/ADR_TEMPLATE.md
.agentforge/rfcs/RFC_TEMPLATE.md
```

## Metadata Checks

Metadata-checked files (unchanged from v0.1):

```text
.agentforge/constitution.md
.agentforge/charter.md
.agentforge/decisions.md
.agentforge/architecture.md
.agentforge/repo-map.md
.agentforge/agents/AGENTS.md
```

A file passes the metadata check when it has **either**:

- a plain `Metadata:` block (v0.1 compatibility), or
- YAML front matter: first line `---`, a closing `---` line, containing `status:` and `aics-version:`.

At Level 3, the metadata-checked files MUST use front matter (with `status` and `aics-version`); plain `Metadata:` blocks demote the context to Level 2 with a warning.

## Version Marker

The validator checks for `.agentforge/aics-version`:

- present and containing `0.2` → Level 3 eligible
- absent → Level 2 maximum, warning emitted

## AI Context Checks

Unchanged from v0.1: `.agentforge/agents/AGENTS.md` required; should mention constitution, charter, ADR, RFC.

## Template Checks

Unchanged from v0.1: ADR template must contain Context, Decision, Consequences; RFC template must contain Purpose, Proposal, Risks.

## Warnings

Warnings do not fail validation. Warnings include:

- recommended optional files missing (vision.md, roadmap.md, etc.) — informational
- plain `Metadata:` style used when front matter is preferred
- Level 3 target declared (version marker absent)

## Error Messages

Unchanged style from v0.1, with paths:

```text
missing AICS file: .agentforge/constitution.md
missing Metadata block: .agentforge/charter.md
missing required text 'Decision': .agentforge/adrs/ADR_TEMPLATE.md
```

## Output Format

`validate-context` prints:

```text
AICS level: 3 (Context Validated)
warnings: 0
```

## Revision History

- 2026-08-01: Initial v0.2 rules draft (front matter, levels, version marker).
