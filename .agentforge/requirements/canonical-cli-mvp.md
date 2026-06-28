# Canonical CLI MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 4
- Related issues: #10, #11, #12, #13, #14
- Related specifications: `.agentforge/specs/aics-v0.1.md`, `.agentforge/specs/aics-validation-v0.1.md`
- Related decisions: ADR-0001, DEC-0003
- Related policy: `docs/release-policy.md`
- Last updated: 2026-06-28

## Purpose

Define the requirements for the first canonical AgentForge CLI command inside the `agentforge` monorepo.

This document exists so `agentforge validate-context` can be implemented after requirements and architecture coverage, without extending the historical `agentforge-cli` prototype as if it were canonical.

## Scope

In scope:

- user workflows for local AICS validation
- initial command names and arguments
- AICS validation behavior
- human-readable input and output expectations
- failure messages and exit codes
- dependency policy
- compatibility with `scripts/aics_validation.py`
- implementation traceability for Sprint 4 issues

Out of scope:

- package publishing to PyPI, npm, Homebrew, or system package managers
- shell completion
- interactive prompts
- project scaffolding commands such as `agentforge init-context`
- network validation
- provider, model, or gateway commands
- replacing the existing standalone validation script
- changing AICS v0.1 validation rules
- repurposing or archiving the historical `agentforge-cli` prototype

## Background

AgentForge now has AICS v0.1, validation rules, a reusable dependency-free validator, and a minimal example context tree in the canonical monorepo.

DEC-0003 states that future AICS validation CLI work starts under `apps/cli` in this repository and should reuse `scripts/aics_validation.py` or a shared module derived from it.

The CLI MVP should make AICS validation easier to run while preserving the script-first validation path used during Genesis Sprint 3.

## User Workflows

The MVP must support these workflows:

- A contributor validates the current repository before making implementation-heavy changes.
- A maintainer validates a different local project path that claims AICS compatibility.
- CI invokes the same behavior without network access or secrets.
- An AI assistant receives actionable validation output that identifies missing or invalid context files.

The MVP should not require users to understand the internal location of `scripts/validate_aics.py`.

## Command Requirements

The first canonical command must be:

```bash
agentforge validate-context
```

The command must validate the current working directory by default.

The command must also accept one explicit project path:

```bash
agentforge validate-context path/to/project
```

The command may accept `--help`.

The command must not add additional flags in the MVP unless Sprint 4 architecture work explicitly approves them.

## Validation Requirements

The CLI must validate AICS v0.1 using the same effective rules as `scripts/validate_aics.py`.

The CLI must check:

- required AICS directories
- required AICS files
- required metadata blocks
- master AI context text checks
- ADR and RFC template text checks

The CLI must validate both:

- the canonical AgentForge repository
- `examples/aics/minimal-project`

The CLI must not require network access.

The CLI must not require provider keys, GitHub credentials, or external services.

## Input Requirements

The default input is the current working directory.

When a path argument is provided, the CLI must resolve it as the project root to validate.

The CLI must handle missing paths with an actionable error message.

The CLI should accept relative and absolute paths.

The CLI should avoid mutating the target project.

## Output Requirements

On success, the CLI must print a short success message:

```text
aics ok
```

On validation failure, the CLI must print one actionable error per line.

Validation errors must include the relative path when the error applies to a project file.

The CLI should preserve the existing validator message style, for example:

```text
missing AICS file: .agentforge/constitution.md
missing Metadata block: .agentforge/charter.md
missing required text 'Decision': .agentforge/adrs/ADR_TEMPLATE.md
```

The CLI should not print stack traces for expected user errors.

## Exit Code Requirements

The CLI must return:

- `0` when validation succeeds
- `1` when AICS validation fails
- `2` when CLI usage is invalid, such as an unknown command or too many arguments

The CLI may use a higher nonzero exit code for unexpected internal errors if the implementation documents it.

## Dependency Policy

The CLI MVP must use Python standard library functionality by default.

New runtime dependencies are out of scope for the MVP unless approved by the Sprint 4 architecture decision.

The implementation may reorganize validation code into a shared importable module if that reduces duplication and keeps `scripts/validate_aics.py` working.

## Compatibility Requirements

The CLI must remain compatible with:

- AICS v0.1
- `.agentforge/specs/aics-validation-v0.1.md`
- `scripts/aics_validation.py`
- `scripts/validate_aics.py`
- CI bootstrap validation
- the minimal AICS example project

The existing command must continue to work:

```bash
python scripts/validate_aics.py
```

## Architecture Requirements

The CLI implementation must wait for issue #11 to decide `apps/cli` architecture and packaging details.

The CLI must keep validation logic separate from command-line parsing so future commands can reuse validation behavior.

The CLI should treat `apps/cli` as the canonical Genesis implementation location unless a later accepted decision supersedes DEC-0003.

## Tests and CI Requirements

Sprint 4 CLI testing must cover:

- validating the canonical repository
- validating `examples/aics/minimal-project`
- missing required file behavior
- invalid metadata behavior
- explicit project path behavior
- success exit code
- validation failure exit code
- invalid usage exit code

CI must run CLI validation without external services or secrets.

## Acceptance Criteria

Issue #10 is complete when:

- this requirements document exists
- it references AICS v0.1
- it references DEC-0003
- it references the release policy
- implementation issues #11, #12, #13, and #14 can trace their scope back to this document

The Sprint 4 CLI MVP is complete when:

- issue #11 records architecture and packaging decisions
- issue #12 implements `agentforge validate-context`
- issue #13 adds automated CLI tests and CI validation
- issue #14 documents usage and prepares `Genesis-0.0.4`

## Examples

Validate the current project:

```bash
agentforge validate-context
```

Validate an explicit project:

```bash
agentforge validate-context examples/aics/minimal-project
```

Expected successful output:

```text
aics ok
```

Expected failed output:

```text
missing AICS file: .agentforge/constitution.md
```

## Best Practices

- Keep CLI behavior small until AICS validation has real users.
- Reuse validation logic instead of duplicating rules.
- Prefer deterministic offline validation.
- Keep failure messages useful to humans and AI assistants.
- Preserve script compatibility while the CLI stabilizes.

## Risks

- Adding packaging decisions too early could distract from validation behavior.
- Diverging from `scripts/aics_validation.py` could create two validators.
- Overloading the MVP with flags could lock in weak interfaces.
- Confusion may persist while the historical `agentforge-cli` prototype remains visible.

## References

- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `.agentforge/decisions/0003-cli-path-for-aics-validation.md`
- `docs/release-policy.md`
- `scripts/aics_validation.py`
- `scripts/validate_aics.py`
- `examples/aics/minimal-project`

## Revision History

- 2026-06-28: Initial requirements draft for Genesis Sprint 4.
