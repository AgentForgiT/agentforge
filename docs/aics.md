# AgentForge AI Context Specification

Metadata:

- Status: Draft
- Version: 0.1
- Phase: Genesis Sprint 8
- Last updated: 2026-06-29

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

Run the installed CLI:

```bash
python -m pip install -e apps/cli
agentforge validate-context
agentforge validate-context examples/aics/minimal-project
```

Initialize a minimal AICS project context:

```bash
python apps/cli/bin/agentforge.py init-context demo-project
agentforge init-context demo-project
agentforge validate-context demo-project
```

Explain an AICS project context:

```bash
python apps/cli/bin/agentforge.py explain-context demo-project
agentforge explain-context demo-project
```

Diagnose local AICS project context health:

```bash
python apps/cli/bin/agentforge.py doctor demo-project
agentforge doctor demo-project
```

The CLI path is governed by `.agentforge/decisions/0003-cli-path-for-aics-validation.md`, `.agentforge/adrs/0003-cli-module-architecture.md`, `.agentforge/adrs/0004-cli-packaging-and-distribution.md`, `.agentforge/adrs/0005-context-scaffolding-strategy.md`, `.agentforge/adrs/0006-context-explanation-boundary.md`, and `.agentforge/adrs/0007-doctor-diagnostics-boundary.md`.

## Scaffolding Behavior

`agentforge init-context` creates the required AICS v0.1 baseline under `.agentforge/`.

The Sprint 6 MVP:

- scaffolds the required directories and files
- creates validator-compatible starter content
- avoids overwriting scaffold-managed files
- defers merge, force, and interactive update flows

## Explanation Behavior

`agentforge explain-context` prints a read-only orientation report for a project context.

The Sprint 7 MVP:

- reports the resolved project root
- reports whether AICS validation currently passes
- points to the `.agentforge/` context root
- lists primary governance entry points
- includes validation signals when context is incomplete

`agentforge validate-context` remains the canonical pass/fail command. Explanation can succeed when it successfully explains an incomplete context.

## Diagnostics Behavior

`agentforge doctor` prints a read-only local diagnostics report for AICS context health.

The Sprint 8 MVP:

- reports the resolved project root
- reports whether local diagnostics passed
- reports whether AICS validation currently passes
- groups local checks for required directories, required files, metadata, and required template text
- includes validation signals when context is unhealthy
- suggests a next action

`doctor` returns success only when the local context is healthy. It does not perform network, provider, GitHub, package-manager, dependency, or repair checks during Genesis.

## Troubleshooting

If validation fails, read each output line as an actionable file-level fix.

Examples:

```text
missing AICS file: .agentforge/constitution.md
missing Metadata block: .agentforge/charter.md
missing required text 'Decision': .agentforge/adrs/ADR_TEMPLATE.md
```

The CLI returns `0` when validation succeeds, `1` when AICS validation fails, and `2` for invalid CLI usage such as a missing project path.

`agentforge doctor` returns `0` when local context diagnostics pass and `1` when the project is unhealthy or cannot be inspected.

Editable installation is the supported Genesis install path. Public registry distribution and standalone binaries remain deferred.

## Current Adoption Level

The AgentForge monorepo targets AICS Level 3:

- context present
- context governed
- context validated locally and in CI

## Revision History

- 2026-06-29: Added `doctor` usage and ADR-0007 reference.
- 2026-06-29: Added `explain-context` usage and ADR-0006 reference.
- 2026-06-29: Added `init-context` scaffolding usage and ADR-0005 reference.
- 2026-06-29: Added installable CLI usage.
- 2026-06-28: Added canonical CLI usage and troubleshooting.
- 2026-06-28: Added CLI path decision reference.
- 2026-06-28: Added validation rules reference.
- 2026-06-28: Initial public AICS documentation page.
