# AICS Validation Rules v0.1

Metadata:

- Status: Draft
- Version: 0.1
- Phase: Genesis Sprint 3
- Related issue: #7
- Related spec: `.agentforge/specs/aics-v0.1.md`
- Last updated: 2026-06-28

## Purpose

This document defines the initial machine-checkable validation rules for AICS v0.1.

The rules are intentionally simple and filesystem-based so they can run locally and in CI without network access or third-party dependencies.

## Scope

In scope:

- required AICS directories
- required AICS files
- metadata block checks
- master AI context checks
- ADR and RFC template checks
- actionable validation messages

Out of scope:

- semantic review of document quality
- Markdown linting
- schema validation for structured front matter
- external link checking
- AI model evaluation

## Validation Levels

AICS v0.1 validation reports three levels:

Level 1, Context Present:
Required directories and files exist.

Level 2, Context Governed:
Required governance files include metadata and templates exist.

Level 3, Context Validated:
The validator runs locally and in CI.

## Required Directories

The validator MUST require:

```text
.agentforge/
.agentforge/adrs/
.agentforge/agents/
.agentforge/rfcs/
.agentforge/standards/
```

## Required Files

The validator MUST require:

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

The validator SHOULD require a `Metadata:` block in these files:

```text
.agentforge/constitution.md
.agentforge/charter.md
.agentforge/decisions.md
.agentforge/architecture.md
.agentforge/repo-map.md
.agentforge/agents/AGENTS.md
```

Template files are exempt from metadata checks in v0.1.

## AI Context Checks

The validator MUST require `.agentforge/agents/AGENTS.md`.

The validator SHOULD check that `.agentforge/agents/AGENTS.md` mentions:

- constitution
- charter
- ADR
- RFC

These checks keep the master AI context connected to the governance hierarchy without forcing exact wording.

## Template Checks

The validator MUST require:

- `.agentforge/adrs/ADR_TEMPLATE.md`
- `.agentforge/rfcs/RFC_TEMPLATE.md`

The validator SHOULD check that the ADR template contains:

- Context
- Decision
- Consequences

The validator SHOULD check that the RFC template contains:

- Purpose
- Proposal
- Risks

## Error Messages

Validation errors SHOULD be actionable and include the relative path.

Examples:

```text
missing AICS file: .agentforge/constitution.md
missing Metadata block: .agentforge/charter.md
missing required text 'Decision': .agentforge/adrs/ADR_TEMPLATE.md
```

## Command

The local command is:

```bash
python scripts/validate_aics.py
```

The bootstrap validator may call the same checks, but AICS validation should remain independently runnable.

## Revision History

- 2026-06-28: Initial validation rules draft.
