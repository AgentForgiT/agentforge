# Doctor Diagnostics MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 8
- Related issues: #30, #31, #33, #34, #32
- Related specifications: `.agentforge/specs/aics-v0.1.md`, `.agentforge/specs/aics-validation-v0.1.md`
- Related decisions: ADR-0001, ADR-0003, ADR-0004, ADR-0005, ADR-0006, ADR-0007, DEC-0003
- Related policy: `docs/release-policy.md`
- Last updated: 2026-06-29

## Purpose

Define the requirements for the canonical `agentforge doctor` MVP so AgentForge can diagnose local AICS project context health without adding network, provider, or package-manager checks during Genesis.

This document exists so Sprint 8 decides diagnostic scope, safety boundaries, output shape, and exit semantics before implementation begins in `apps/cli`.

## Scope

In scope:

- the canonical `agentforge doctor` command surface
- target project path handling for the current directory and one explicit path
- read-only local diagnostics for AICS context health
- reuse of existing AICS validation behavior
- concise human-readable diagnostic output
- deterministic command exit semantics for healthy, unhealthy, and command-error states
- Sprint 8 traceability across implementation, tests, documentation, and release work

Out of scope:

- network checks
- GitHub, package registry, provider, model, or gateway availability checks
- package-manager diagnostics
- dependency vulnerability scanning
- in-place repair or mutation of project context
- interactive prompts
- semantic quality scoring of governance documents
- machine-readable JSON or structured export formats
- diagnostics for non-AICS project concerns

## Background

Genesis Sprint 4 and Sprint 5 established the canonical CLI and installable command path.

Genesis Sprint 6 added `agentforge init-context`, which creates a minimal valid AICS baseline for new projects.

Genesis Sprint 7 added `agentforge explain-context`, which provides a read-only orientation report and can explain incomplete project context without treating the explanation run as failed.

The next practical CLI capability is a diagnostic command that answers whether a local project context is healthy enough for AgentForge work. This is distinct from explanation because diagnostics should return an unhealthy exit code when validation fails.

DEC-0003 already identified `agentforge doctor` as a natural future command inside the canonical monorepo CLI.

## User Workflows

The MVP must support these workflows:

- A contributor checks whether the current repository context is healthy before starting work.
- A maintainer diagnoses a local project path that claims AICS compatibility.
- An AI assistant runs a deterministic local health check before making changes.
- A contributor uses diagnostic output to decide whether to run `init-context`, inspect `explain-context`, or fix missing governance files.

The MVP should favor clear health status and actionable local signals over broad environment inspection.

## Command Requirements

The canonical diagnostics command must be:

```bash
agentforge doctor
```

The command must diagnose the current working directory by default.

The command must also accept one explicit project path:

```bash
agentforge doctor path/to/project
```

The command may accept `--help`.

The command must not add additional flags in the MVP unless Sprint 8 architecture work explicitly approves them.

## Input Requirements

The default input is the current working directory.

When a path argument is provided, the CLI must resolve it as the project root to diagnose.

The command should accept relative and absolute paths.

The command must not mutate the target project.

When the target path does not exist or is not a directory, the command must return an actionable error message.

## Output Requirements

The MVP must produce a short, readable diagnostics report.

The report should include:

- the resolved project root
- an overall diagnostic status
- the AICS validation status
- whether the `.agentforge/` context root is present
- local checks that distinguish required directories, required files, metadata, and required template text
- actionable validation signals when context is unhealthy
- a short suggested next action

For a healthy AICS project, the report should confirm that local context diagnostics passed and recommend continuing with validation or context explanation as needed.

For an unhealthy AICS project, the report should show failed validation signals without a Python stack trace.

The MVP output should remain plain text so it is easy to read in terminals and reuse in AI assistant workflows.

## Validation Relationship Requirements

`doctor` must remain compatible with the current validator and AICS rules.

The command may reuse validation results internally, but it must not become a hidden replacement for `validate-context`.

`validate-context` remains the canonical pass/fail validator for automation.

`doctor` should compose validator results with local diagnostic grouping and next-step guidance.

The diagnostics command must remain aligned with:

- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `scripts/aics_validation.py`
- `scripts/validate_aics.py`
- `agentforge validate-context`
- `agentforge init-context`
- `agentforge explain-context`

## Exit Code Requirements

The CLI must return:

- `0` when local diagnostics complete and the project is healthy
- `1` when local diagnostics complete and the project is unhealthy, or when diagnostics cannot be completed because of a command-level or filesystem-level problem other than invalid usage
- `2` when CLI usage is invalid, such as too many arguments or an unknown command

The MVP should distinguish `doctor` from `explain-context`: an invalid AICS project can still be explained successfully, but it is not diagnostically healthy.

## Dependency Requirements

The diagnostics MVP should use Python standard library functionality by default.

New runtime dependencies require explicit architectural justification in the Sprint 8 decision record.

The diagnostics flow must not require network access, provider keys, GitHub credentials, package registries, or external services.

## Architecture Requirements

Sprint 8 implementation must follow ADR-0007 for the diagnostic safety boundary and relationship to validation results.

The CLI must keep diagnostic logic separate from command-line parsing so future commands can reuse shared context inspection behavior.

The MVP should prefer deterministic filesystem inspection and validator reuse over heuristic document analysis.

## Testing and CI Requirements

Sprint 8 testing must cover:

- diagnostics for the canonical AgentForge repository
- diagnostics for a minimal or scaffolded AICS project
- diagnostics for an invalid or incomplete context
- missing project path behavior
- regression coverage for existing `validate-context`, `init-context`, and `explain-context` behavior
- healthy, unhealthy, command-error, and invalid-usage exit codes

CI must run the Sprint 8 diagnostics checks without external services or secrets.

Tests should verify both status signals and important diagnostic lines, not only raw exact-output snapshots.

## Documentation Requirements

Documentation must explain:

- how to run `agentforge doctor`
- how diagnostics differ from validation and explanation
- how diagnostics behave for healthy and unhealthy contexts
- how the command fits with `init-context`, `validate-context`, and `explain-context`
- current MVP limitations during Genesis

## Acceptance Criteria

Issue #30 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references the AICS v0.1 spec and validation rules
- it references ADR-0003, ADR-0004, ADR-0005, ADR-0006, ADR-0007, and DEC-0003
- it defines the MVP command surface and validation relationship before implementation begins
- implementation issues #31, #33, #34, and #32 can trace their scope back to this document

The Sprint 8 doctor diagnostics milestone is complete when:

- issue #31 records the diagnostics scope and safety boundary
- issue #33 implements `agentforge doctor`
- issue #34 adds automated diagnostics tests and CI validation
- issue #32 documents the workflow and prepares `Genesis-0.0.8`

## Examples

Diagnose the current repository:

```bash
agentforge doctor
```

Diagnose another local project:

```bash
agentforge doctor examples/aics/minimal-project
```

Compare diagnostics with validation and explanation:

```bash
agentforge doctor examples/aics/minimal-project
agentforge validate-context examples/aics/minimal-project
agentforge explain-context examples/aics/minimal-project
```

## Best Practices

- Run diagnostics before implementation-heavy work.
- Treat validation as the authority for pass/fail AICS rules.
- Treat diagnostics as a local health report and next-step guide.
- Keep diagnostic output concise and actionable.
- Defer environment, provider, and network diagnostics until real usage justifies them.

## Risks

- Diagnostics could become a second validator if the boundary is not kept clear.
- Overly broad checks could make the command flaky or environment-dependent.
- Provider or network checks could undermine reproducibility during Genesis.
- Exit-code semantics could confuse users if diagnostics are not clearly distinct from explanation.

## References

- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `.agentforge/requirements/canonical-cli-mvp.md`
- `.agentforge/requirements/installable-cli.md`
- `.agentforge/requirements/context-scaffolding-mvp.md`
- `.agentforge/requirements/context-explanation-mvp.md`
- `.agentforge/adrs/0003-cli-module-architecture.md`
- `.agentforge/adrs/0004-cli-packaging-and-distribution.md`
- `.agentforge/adrs/0005-context-scaffolding-strategy.md`
- `.agentforge/adrs/0006-context-explanation-boundary.md`
- `.agentforge/adrs/0007-doctor-diagnostics-boundary.md`
- `.agentforge/decisions/0003-cli-path-for-aics-validation.md`
- `apps/cli/README.md`
- `docs/aics.md`
- `docs/release-policy.md`

## Revision History

- 2026-06-29: Initial requirements draft for Genesis Sprint 8.
