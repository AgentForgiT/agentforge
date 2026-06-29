# Context Explanation MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 7
- Related issues: #25, #26, #29, #28, #27
- Related specifications: `.agentforge/specs/aics-v0.1.md`, `.agentforge/specs/aics-validation-v0.1.md`
- Related decisions: ADR-0001, ADR-0003, ADR-0004, ADR-0005, ADR-0006, DEC-0003
- Related policy: `docs/release-policy.md`
- Last updated: 2026-06-29

## Purpose

Define the requirements for the canonical `agentforge explain-context` MVP so AgentForge can provide a read-only orientation report for AICS-compatible projects before implementation introduces richer report formats or diagnostics behavior.

This document exists so Sprint 7 decides command behavior, output scope, and validation relationship before implementation begins in `apps/cli`.

## Scope

In scope:

- the canonical `agentforge explain-context` command surface
- target project path handling for the current directory and one explicit path
- read-only explanation of AICS status and key governance entry points
- relationship between explanation output and existing AICS validation
- human-readable output for contributors and AI assistants
- Sprint 7 traceability across implementation, tests, documentation, and release work

Out of scope:

- environment diagnostics or dependency checks
- network validation
- machine-readable JSON or structured export formats
- interactive prompts
- in-place repair or mutation of project context
- semantic quality scoring of governance documents
- provider, model, or gateway health checks
- broader assistant onboarding features beyond context explanation

## Background

Genesis Sprint 4 and Sprint 5 established the canonical CLI and installable command path.

Genesis Sprint 6 added `agentforge init-context`, which creates a minimal valid AICS baseline for new projects.

The next practical CLI capability is to explain a project context in human-readable form so contributors and AI assistants can quickly orient themselves without reducing everything to pass/fail validation output.

DEC-0003 already identified `agentforge explain-context` as a natural future command inside the canonical monorepo CLI.

## User Workflows

The MVP must support these workflows:

- A contributor explains the current repository context before implementation-heavy work.
- A maintainer explains another local project path that claims AICS compatibility.
- An AI assistant reads a concise explanation of governance entry points and context status before taking action.
- A contributor compares explanatory output with validation output when a context is incomplete or invalid.

The MVP should favor clear textual orientation over rich formatting or deep heuristics.

## Command Requirements

The canonical explanation command must be:

```bash
agentforge explain-context
```

The command must explain the current working directory by default.

The command must also accept one explicit project path:

```bash
agentforge explain-context path/to/project
```

The command may accept `--help`.

The command must not add additional flags in the MVP unless Sprint 7 architecture work explicitly approves them.

## Input Requirements

The default input is the current working directory.

When a path argument is provided, the CLI must resolve it as the project root to explain.

The command should accept relative and absolute paths.

The command must not mutate the target project.

When the target path does not exist, the command must return an actionable error message.

## Output Requirements

The MVP must produce a short, readable explanation report.

The explanation should include:

- the resolved project root
- whether the project currently passes AICS validation
- the location of the AICS context root
- the highest-priority governance files or directories to read next
- whether the explanation is based on a complete or incomplete AICS baseline

For a valid AICS project, the report should summarize key entry points such as:

- `.agentforge/constitution.md`
- `.agentforge/charter.md`
- `.agentforge/decisions.md`
- `.agentforge/architecture.md`
- `.agentforge/agents/AGENTS.md`

For an invalid or incomplete AICS project, the report should remain explanatory and should surface actionable missing-context signals without a Python stack trace.

The MVP output should remain plain text so it is easy to read in terminals and reuse in AI assistant workflows.

## Validation Relationship Requirements

`explain-context` must remain compatible with the current validator and AICS rules.

The command may reuse validation results internally, but it must not become a hidden synonym for `validate-context`.

`validate-context` remains the canonical pass/fail command.

`explain-context` should interpret validation status and context structure into a more guided orientation report.

The explanation command must remain aligned with:

- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `scripts/aics_validation.py`
- `scripts/validate_aics.py`
- `agentforge validate-context`
- `agentforge init-context`

## Exit Code Requirements

The CLI must return:

- `0` when the command successfully explains a project context, even if that context is incomplete
- `1` only when explanation cannot be completed because of a command-level or filesystem-level problem other than invalid usage
- `2` when CLI usage is invalid, such as too many arguments or an unknown command

The MVP should distinguish between an invalid AICS project and a failed explanation run.

## Dependency Requirements

The explanation MVP should use Python standard library functionality by default.

New runtime dependencies require explicit architectural justification in the Sprint 7 decision record.

The explanation flow must not require network access, provider keys, GitHub credentials, or external services.

## Architecture Requirements

Sprint 7 implementation must follow ADR-0006 for the explanation output boundary and relationship to validation results.

The CLI must keep explanation logic separate from command-line parsing so future commands can reuse shared context inspection behavior.

The MVP should prefer deterministic filesystem inspection and validator reuse over heuristic document analysis.

## Testing and CI Requirements

Sprint 7 testing must cover:

- explanation of the canonical AgentForge repository
- explanation of a minimal or scaffolded AICS project
- explanation of an invalid or incomplete context
- missing project path behavior
- regression coverage for existing `validate-context` and `init-context` behavior
- success, explanation-error, and invalid-usage exit codes

CI must run the Sprint 7 explanation checks without external services or secrets.

Tests should verify both the status signal and the presence of important explanation lines, not only raw exact-output snapshots.

## Documentation Requirements

Documentation must explain:

- how to run `agentforge explain-context`
- how explanation differs from validation
- how explanation behaves for valid and incomplete contexts
- how the command fits with `init-context` and `validate-context`
- current MVP limitations during Genesis

## Acceptance Criteria

Issue #25 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references the AICS v0.1 spec and validation rules
- it references ADR-0003, ADR-0004, ADR-0005, ADR-0006, and DEC-0003
- it defines the MVP command surface and validation relationship before implementation begins
- implementation issues #26, #29, #28, and #27 can trace their scope back to this document

The Sprint 7 context explanation milestone is complete when:

- issue #26 records the explanation output and validation boundary
- issue #29 implements `agentforge explain-context`
- issue #28 adds automated explanation tests and CI validation
- issue #27 documents the workflow and prepares `Genesis-0.0.7`

## Examples

Explain the current repository:

```bash
agentforge explain-context
```

Explain another local project:

```bash
agentforge explain-context examples/aics/minimal-project
```

Compare explanation with validation:

```bash
agentforge explain-context examples/aics/minimal-project
agentforge validate-context examples/aics/minimal-project
```

## Best Practices

- Keep explanation output concise and actionable.
- Treat validation as the authority for pass/fail status.
- Prefer stable governance entry points over speculative commentary.
- Make output readable for both humans and AI assistants.
- Defer richer formatting and environment diagnostics until real usage justifies them.

## Risks

- Explanation output could drift into a second validator if the boundary is not kept clear.
- Overly verbose output could reduce usefulness in terminals and AI workflows.
- Overly shallow output could fail to justify the command as distinct from validation.
- Future output format demands could create churn if the MVP overcommits too early.

## References

- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `.agentforge/requirements/canonical-cli-mvp.md`
- `.agentforge/requirements/installable-cli.md`
- `.agentforge/requirements/context-scaffolding-mvp.md`
- `.agentforge/adrs/0003-cli-module-architecture.md`
- `.agentforge/adrs/0004-cli-packaging-and-distribution.md`
- `.agentforge/adrs/0005-context-scaffolding-strategy.md`
- `.agentforge/adrs/0006-context-explanation-boundary.md`
- `.agentforge/decisions/0003-cli-path-for-aics-validation.md`
- `apps/cli/README.md`
- `docs/aics.md`
- `docs/release-policy.md`

## Revision History

- 2026-06-29: Initial requirements draft for Genesis Sprint 7.
