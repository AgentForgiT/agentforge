# AgentForge AI Context Specification

Metadata:

- Status: Draft
- Version: 0.1
- Phase: Genesis Sprint 3
- Last updated: 2026-06-28

## Purpose

The AgentForge AI Context Specification, or AICS, defines a portable project context structure for AI-native engineering.

The canonical draft lives at `.agentforge/specs/aics-v0.1.md`.

## Summary

AICS v0.1 standardizes:

- a `.agentforge/` project brain
- governance files such as constitution, charter, decisions, ADRs, and RFCs
- a master AI assistant context file
- optional tool-specific adapter files
- validation goals for machine-checkable context

Validation rules are documented in `.agentforge/specs/aics-validation-v0.1.md`.

Run script validation:

```bash
python scripts/validate_aics.py
python scripts/validate_aics.py examples/aics/minimal-project
```

Run the canonical source-tree CLI:

```bash
python apps/cli/bin/agentforge.py validate-context
python apps/cli/bin/agentforge.py validate-context examples/aics/minimal-project
```

The CLI path is governed by `.agentforge/decisions/0003-cli-path-for-aics-validation.md` and `.agentforge/adrs/0003-cli-module-architecture.md`.

## Troubleshooting

If validation fails, read each output line as an actionable file-level fix.

Examples:

```text
missing AICS file: .agentforge/constitution.md
missing Metadata block: .agentforge/charter.md
missing required text 'Decision': .agentforge/adrs/ADR_TEMPLATE.md
```

The CLI returns `0` when validation succeeds, `1` when AICS validation fails, and `2` for invalid CLI usage such as a missing project path.

## Current Adoption Level

The AgentForge monorepo targets AICS Level 3:

- context present
- context governed
- context validated locally and in CI

## Revision History

- 2026-06-28: Added canonical CLI usage and troubleshooting.
- 2026-06-28: Added CLI path decision reference.
- 2026-06-28: Added validation rules reference.
- 2026-06-28: Initial public AICS documentation page.
