# ADR-0006: Explain AICS Context Through a Read-Only Orientation Report with Validation-Informed Status

Metadata:

- Status: Accepted
- Date: 2026-06-29
- Deciders: AgentForge maintainers
- Related issues: #25, #26, #29, #28, #27
- Related decisions: ADR-0001, ADR-0003, ADR-0004, ADR-0005, DEC-0003
- Related requirements: `.agentforge/requirements/context-explanation-mvp.md`

## Context

Genesis Sprint 7 introduces the next canonical CLI follow-up command after `validate-context` and `init-context`:

```text
agentforge explain-context
```

AgentForge now has:

- AICS v0.1 structure and validation rules
- a canonical CLI under `apps/cli`
- an installable editable CLI path
- a scaffolding command that can generate a minimal valid AICS baseline

What Sprint 7 still needs is an architectural decision about what explanation means before implementation adds report logic.

The decision must answer:

- whether `explain-context` is primarily a validator, explainer, or both
- how it should reuse validation behavior without duplicating validator authority
- what output surface is appropriate for the Genesis MVP
- how invalid or incomplete contexts affect exit codes
- what richer output modes should be deferred

Without this decision, `explain-context` could become a second validator with slightly different semantics, a vague document summarizer, or an unstable report surface that overcommits before real usage exists.

## Decision

The canonical `agentforge explain-context` MVP will be a read-only orientation report for AICS-compatible or partially AICS-compatible project contexts.

The command may reuse validation results internally, but `validate-context` remains the authoritative pass/fail CLI command.

`explain-context` will interpret validation status and stable filesystem entry points into a guided human-readable report.

For the Genesis MVP, the report must stay plain text and terminal-friendly.

The MVP report should include:

- the resolved project root
- whether AICS validation currently passes
- the AICS context root location
- the primary governance files or directories to read next
- when relevant, actionable missing or invalid context signals derived from the validator

The command must remain read-only and must not mutate the project.

## Validation Boundary

`validate-context` owns:

- canonical pass/fail AICS status
- validator error output
- validation-oriented exit semantics

`explain-context` owns:

- orientation text
- prioritization of key governance entry points
- interpretation of validator status into explanatory language
- reporting incomplete context without treating explanation itself as a failure

The explanation command must not invent new validation rules or silently reinterpret AICS requirements.

The validator remains the source of truth for whether the project passes AICS validation.

## Exit Code Strategy

The MVP exit code boundary is:

- `0` when the command successfully explains the target project, including when the AICS context is incomplete or invalid
- `1` when explanation cannot be completed because of a command-level or filesystem-level problem other than invalid usage
- `2` when CLI usage is invalid

This means an invalid AICS project is still a successful explanation target if the command can inspect it and explain what is missing.

## Report Boundary

The Genesis MVP report should rely on deterministic context inspection:

- validator results
- known AICS-required file locations
- known governance entry points

The MVP should avoid:

- semantic summarization of long documents
- heuristic scoring of document quality
- speculative architecture commentary
- machine-readable export formats
- environment or dependency diagnostics

Future JSON, markdown, verbose, or environment-aware modes require a later requirements document and decision.

## Relationship to Existing CLI Commands

`explain-context` must stay aligned with:

- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `scripts/aics_validation.py`
- `scripts/validate_aics.py`
- `agentforge validate-context`
- `agentforge init-context`

The explanation command should make it easier to understand the output of `init-context` and the meaning of `validate-context` without replacing either command.

## Consequences

Benefits:

- gives contributors and AI assistants a clearer entry point into project context
- keeps validation authority with the existing validator
- makes incomplete contexts understandable without conflating explanation with failure
- stays compatible with the current terminal-first CLI surface
- preserves a narrow, deterministic MVP boundary

Trade-offs:

- plain-text output is less machine-friendly than structured formats
- orientation output may feel limited compared with richer future report modes
- incomplete contexts will still need `validate-context` for canonical pass/fail automation
- careful test coverage is needed to keep explanation distinct from validation

## Alternatives Considered

Make `explain-context` a thin alias for `validate-context`:
Rejected because it does not justify a separate command surface and would fail to provide orientation value beyond existing error lines.

Return nonzero exit status for invalid AICS contexts:
Rejected because the explanation command is meant to explain the current state, including missing context, not only celebrate valid contexts.

Parse and summarize the full contents of governance documents:
Rejected for the MVP because it widens the surface too quickly and risks unstable or subjective output.

Introduce JSON or structured export in the MVP:
Deferred because the Genesis need is immediate human and AI terminal orientation, not a committed machine-readable contract.

Fold explanation behavior into `init-context` or `validate-context` output:
Rejected because explanation is a distinct workflow that should remain available independently for existing projects.

## Follow-Up Work

- Implement a read-only explanation layer in `apps/cli`.
- Reuse validator results without duplicating validation rules.
- Add tests for valid, invalid, and missing-path explanation behavior.
- Document how explanation differs from validation.
- Revisit richer output modes only after the MVP proves useful.

## Revision History

- 2026-06-29: Accepted for Genesis Sprint 7.
