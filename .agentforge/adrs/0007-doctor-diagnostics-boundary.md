# ADR-0007: Diagnose Local AICS Context Health with Read-Only Doctor Checks

Metadata:

- Status: Accepted
- Date: 2026-06-29
- Deciders: AgentForge maintainers
- Related issues: #30, #31, #33, #34, #32
- Related decisions: ADR-0001, ADR-0003, ADR-0004, ADR-0005, ADR-0006, DEC-0003
- Related requirements: `.agentforge/requirements/doctor-diagnostics-mvp.md`

## Context

Genesis Sprint 8 introduces the next canonical CLI follow-up command after `validate-context`, `init-context`, and `explain-context`:

```text
agentforge doctor
```

AgentForge now has:

- AICS v0.1 structure and validation rules
- a canonical CLI under `apps/cli`
- an installable editable CLI path
- a scaffolding command that can generate a minimal valid AICS baseline
- an explanation command that can orient contributors and AI assistants to a valid or incomplete context

What Sprint 8 still needs is an architectural decision about what doctor diagnostics mean before implementation adds local health checks.

The decision must answer:

- whether `doctor` is primarily a validator, explainer, environment checker, or local diagnostic report
- how it should reuse validation behavior without duplicating validator authority
- whether it may perform network, provider, GitHub, package-manager, or dependency checks
- how invalid or incomplete contexts affect exit codes
- what richer diagnostic modes should be deferred

Without this decision, `doctor` could expand too early into flaky environment inspection, become a second validator with slightly different rules, or blur the distinction between validation, explanation, and diagnostics.

## Decision

The canonical `agentforge doctor` MVP will be a read-only local diagnostics report for AICS project context health.

The command may reuse validation results internally, but `validate-context` remains the authoritative pass/fail validator for AICS rules.

`doctor` will compose validator results with deterministic local context checks and next-step guidance.

For the Genesis MVP, diagnostics must stay local-only, plain text, deterministic, and terminal-friendly.

The MVP report should include:

- the resolved project root
- an overall diagnostic status
- whether AICS validation currently passes
- whether the `.agentforge/` context root is present
- grouped local checks for required directories, required files, metadata, and required template text
- actionable validation signals when context is unhealthy
- a short suggested next action

The command must remain read-only and must not mutate the project.

## Safety Boundary

The Sprint 8 MVP must not perform:

- network checks
- GitHub API checks
- package registry checks
- provider, model, or gateway availability checks
- package-manager diagnostics
- dependency vulnerability scanning
- in-place repair or mutation of project context

Those checks require later requirements and an accepted ADR because they add credentials, network availability, security, reproducibility, or scope concerns.

## Validation Boundary

`validate-context` owns:

- canonical pass/fail AICS status
- validator error output
- validation-oriented exit semantics for automation

`explain-context` owns:

- orientation text
- prioritization of key governance entry points
- successful explanation of valid or incomplete contexts

`doctor` owns:

- local health status
- grouped diagnostic checks
- next-step guidance based on validation results
- unhealthy exit status when context validation fails

The diagnostics command must not invent new AICS validation rules or silently reinterpret AICS requirements.

The validator remains the source of truth for whether the project passes AICS validation.

## Exit Code Strategy

The MVP exit code boundary is:

- `0` when diagnostics complete and the project is healthy
- `1` when diagnostics complete and the project is unhealthy
- `1` when diagnostics cannot be completed because of a command-level or filesystem-level problem other than invalid usage
- `2` when CLI usage is invalid

This intentionally differs from `explain-context`: an invalid AICS project can still be explained successfully, but it is not diagnostically healthy.

## Diagnostic Boundary

The Genesis MVP report should rely on deterministic local inspection:

- validator results
- known AICS-required file locations
- known AICS-required directory locations
- known metadata requirements
- known required template text
- presence of the `.agentforge/` context root

The MVP should avoid:

- semantic summarization of long documents
- heuristic scoring of document quality
- speculative architecture commentary
- machine-readable export formats
- environment or dependency diagnostics
- provider, gateway, model, or network diagnostics

Future JSON, verbose, repair, environment-aware, provider-aware, or CI-oriented modes require a later requirements document and decision.

## Relationship to Existing CLI Commands

`doctor` must stay aligned with:

- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `scripts/aics_validation.py`
- `scripts/validate_aics.py`
- `agentforge validate-context`
- `agentforge init-context`
- `agentforge explain-context`

The diagnostics command should make it easier to decide whether to validate, initialize, explain, or fix context without replacing those commands.

## Consequences

Benefits:

- gives contributors and AI assistants a fast local health check before work begins
- keeps validation authority with the existing validator
- keeps explanation distinct from health diagnostics
- avoids network, provider, and dependency flakiness during Genesis
- preserves a narrow, deterministic MVP boundary

Trade-offs:

- local-only diagnostics may feel limited compared with broader environment checks
- plain-text output is less machine-friendly than structured formats
- unhealthy contexts return nonzero even though `explain-context` can still explain them
- future diagnostic expansion will require additional governance work

## Alternatives Considered

Make `doctor` a thin alias for `validate-context`:
Rejected because it does not justify a separate command surface and would fail to provide grouped diagnostic context or next-step guidance.

Make `doctor` a thin alias for `explain-context`:
Rejected because explanation and diagnostics have different exit-code semantics and user intent.

Add network, provider, gateway, and GitHub checks in the MVP:
Rejected because those checks introduce credentials, availability, and reproducibility concerns that are too broad for Sprint 8.

Return success for invalid AICS contexts:
Rejected because `doctor` is a health diagnostic. An invalid context can be explainable, but it is not healthy.

Introduce JSON or structured export in the MVP:
Deferred because the Genesis need is immediate human and AI terminal diagnostics, not a committed machine-readable contract.

Add repair or autofix behavior:
Rejected for the MVP because mutation belongs in explicitly scoped initialization or future repair commands, not in a read-only diagnostic.

## Follow-Up Work

- Implement a read-only diagnostics layer in `apps/cli`.
- Reuse validator results without duplicating validation rules.
- Add tests for healthy, unhealthy, and missing-path diagnostics behavior.
- Document how diagnostics differs from validation and explanation.
- Revisit richer diagnostic modes only after the MVP proves useful.

## Revision History

- 2026-06-29: Accepted for Genesis Sprint 8.
