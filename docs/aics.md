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

Run validation:

```bash
python scripts/validate_aics.py
python scripts/validate_aics.py examples/aics/minimal-project
```

## Current Adoption Level

The AgentForge monorepo targets AICS Level 3:

- context present
- context governed
- context validated locally and in CI

## Revision History

- 2026-06-28: Added validation rules reference.
- 2026-06-28: Initial public AICS documentation page.
