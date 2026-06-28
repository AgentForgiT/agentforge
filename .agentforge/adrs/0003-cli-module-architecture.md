# ADR-0003: Place Canonical CLI in `apps/cli` with Shared Validation Boundary

Metadata:

- Status: Accepted
- Date: 2026-06-28
- Deciders: AgentForge maintainers
- Related issues: #10, #11, #12, #13, #14
- Related decisions: ADR-0001, DEC-0001, DEC-0003
- Related requirements: `.agentforge/requirements/canonical-cli-mvp.md`

## Context

AgentForge has accepted a modular monorepo strategy in ADR-0001 and a canonical CLI path in DEC-0003.

The project now needs implementation guidance for `agentforge validate-context` before code is added. Without a clear architecture decision, CLI work could drift into the historical `agentforge-cli` prototype, duplicate validation logic, or introduce packaging commitments before the command surface is proven.

Genesis Sprint 4 requirements define a narrow MVP: validate AICS v0.1 context locally, reuse the existing validation logic, avoid network access, and keep packaging minimal.

## Decision

The canonical AgentForge CLI application will live under:

```text
apps/cli
```

The first CLI package should provide the `agentforge validate-context` command and should be implemented with Python standard library tooling during Genesis.

The CLI must keep command-line parsing separate from AICS validation logic. The implementation should reuse `scripts/aics_validation.py` directly or move the validation logic into a shared importable module while preserving this command:

```bash
python scripts/validate_aics.py
```

The initial package entry point strategy is source-tree execution from the monorepo. Installer-level distribution, console script packaging, PyPI publishing, and standalone binary packaging are deferred until a later decision.

The CLI may include a small wrapper script or module entry point that makes local execution ergonomic, but it must not require third-party runtime dependencies for the Sprint 4 MVP.

## Consequences

Benefits:

- keeps CLI work in the canonical monorepo
- follows DEC-0003 before implementation starts
- avoids extending the historical `agentforge-cli` prototype as canonical
- keeps AICS specification, validation, tests, examples, and CLI behavior close together
- allows validation logic to become reusable without duplicating rules
- avoids premature packaging commitments during Genesis

Trade-offs:

- users may need repository-local invocation before formal package installation exists
- source-tree execution is less polished than an installed global CLI
- packaging decisions remain future work
- the repository must preserve script compatibility while CLI structure evolves

## Package Boundary

`apps/cli` owns:

- command-line parsing
- command dispatch
- user-facing CLI help text
- CLI-specific exit-code mapping
- CLI tests and fixtures when they are local to the CLI

AICS validation logic owns:

- required AICS directories
- required AICS files
- metadata checks
- template checks
- reusable validation result structures
- validation error messages

The CLI must call the validation layer instead of reimplementing validation rules.

## Dependency Boundary

The Sprint 4 CLI MVP must use the Python standard library by default.

New runtime dependencies require a later ADR or decision that explains:

- why the dependency is needed
- why standard library behavior is insufficient
- packaging impact
- security and supply-chain impact
- maintenance obligations

## Relationship to `scripts/aics_validation.py`

`scripts/aics_validation.py` is the current validation module.

The CLI implementation may:

- import it directly, or
- move it into a shared package/module if that keeps imports cleaner.

If validation logic moves, `scripts/validate_aics.py` must remain a working compatibility wrapper.

## Relationship to Historical `agentforge-cli`

The standalone `agentforge-cli` repository remains a historical scaffold CLI prototype.

It must not receive new architecture-level CLI work for AICS validation unless a later accepted decision supersedes DEC-0003 and this ADR.

Notices in the prototype repository should continue pointing users to the canonical monorepo path.

## Extraction Criteria

The CLI may be extracted from the monorepo only after a later ADR determines that extraction is justified by one or more of:

- independent release cadence
- independent maintainer ownership
- packaging or distribution needs that materially differ from the monorepo
- CI scale or runtime cost
- downstream consumption requirements

Extraction must preserve AICS governance context and validation compatibility.

## Alternatives Considered

Keep developing the standalone `agentforge-cli` repository:
Rejected because it contradicts DEC-0003 and would split governance while the CLI surface is still small.

Place CLI code under `packages/cli`:
Rejected for the MVP because the CLI is a runnable application, not only a reusable library.

Create a fully packaged installable CLI immediately:
Deferred because packaging is not necessary to validate the MVP behavior and would add decisions before real usage feedback.

Duplicate AICS validation rules inside the CLI:
Rejected because it would create two sources of truth for validation behavior.

## Follow-Up Work

- Implement `agentforge validate-context` under `apps/cli`.
- Add tests for success, validation failure, invalid usage, and explicit project paths.
- Update CI to run CLI tests.
- Document local CLI usage.
- Prepare `Genesis-0.0.4` after CLI MVP validation passes.

## Revision History

- 2026-06-28: Accepted for Genesis Sprint 4.
