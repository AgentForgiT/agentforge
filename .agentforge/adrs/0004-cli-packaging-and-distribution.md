# ADR-0004: Package the Canonical CLI from `apps/cli` with Editable Install First

Metadata:

- Status: Accepted
- Date: 2026-06-28
- Deciders: AgentForge maintainers
- Related issues: #16, #18, #15, #17, #19
- Related decisions: ADR-0001, ADR-0003, DEC-0003
- Related requirements: `.agentforge/requirements/installable-cli.md`

## Context

Genesis Sprint 4 shipped a source-tree CLI MVP under `apps/cli` and intentionally deferred installer-level packaging.

Genesis Sprint 5 now needs an installable `agentforge` command, but the project still wants to avoid premature public distribution complexity and preserve the validated source-tree workflow.

The packaging decision must answer:

- where packaging metadata lives
- how the `agentforge` console command is exposed
- what install workflow contributors and CI should use during Genesis
- how installed behavior stays aligned with source-tree behavior
- how future public distribution paths remain possible without forcing them now

## Decision

The canonical AgentForge CLI will be packaged from `apps/cli`.

Genesis will use Python `pyproject.toml` packaging for the CLI module, with metadata and build configuration owned by `apps/cli`.

The installable command will be exposed as a console script named:

```text
agentforge
```

The primary supported Genesis install workflow will be editable installation from the monorepo checkout.

The source-tree wrapper and direct module invocation will remain supported during Genesis:

```bash
python apps/cli/bin/agentforge.py validate-context
PYTHONPATH=apps/cli/src python -m agentforge_cli validate-context
```

The installed command must preserve the same command semantics and exit codes as the source-tree CLI.

Public registry publishing, standalone binaries, Homebrew, and other system-level distribution channels are deferred until a later decision.

## Packaging Boundary

`apps/cli` owns:

- CLI package metadata
- build configuration
- console script definition
- CLI-specific tests and installation smoke tests
- CLI documentation for installation and usage

Shared validation logic remains outside packaging-specific code and must continue to be reusable by:

- the installed CLI
- the source-tree wrapper
- `python -m agentforge_cli`
- `scripts/validate_aics.py`

## Install Strategy

Genesis will optimize for local contributor and CI installation rather than public release channels.

Editable install is the default supported path because it:

- keeps development feedback fast
- maps well to monorepo iteration
- avoids private artifact hosting
- lets installed command behavior track current checkout state

Non-editable local installation may be supported later if tests show value, but it is not required to complete the first installable milestone.

## Build Backend Direction

The project should use a standard Python build backend compatible with `pyproject.toml` and console scripts.

The implementation should prefer the smallest reasonable packaging surface that:

- works without custom wrappers
- supports editable install
- keeps source layout under `apps/cli/src`
- does not require moving the canonical CLI package out of `apps/cli`

The exact backend selection may be implemented in Sprint 5 code without a second ADR as long as it follows this decision and introduces no surprising runtime dependency burden.

## Consequences

Benefits:

- keeps packaging decisions aligned with ADR-0003
- makes `agentforge` available through standard Python installation behavior
- preserves the existing source-tree development path
- keeps install workflows simple for contributors and CI
- avoids committing to public distribution before the installable CLI is proven

Trade-offs:

- editable install is less final than a published package workflow
- future public distribution work still needs a later decision
- packaging metadata inside `apps/cli` adds another project artifact to maintain
- multiple invocation paths must stay behaviorally aligned

## Future Distribution Paths

The following are explicitly deferred:

- PyPI publication
- Homebrew formulas
- standalone executables
- operating-system package managers
- installer UX beyond normal Python environment workflows

A later ADR should revisit those paths only after:

- the installable CLI is stable
- install smoke tests are in CI
- contributor documentation is clear
- the command surface has proven durable enough for broader distribution

## Alternatives Considered

Keep the CLI source-tree only:
Rejected because Sprint 5 requires an installable `agentforge` command for contributors and CI.

Package from the repository root instead of `apps/cli`:
Rejected because it blurs module ownership and weakens the `apps/cli` boundary established by ADR-0003.

Adopt public PyPI publishing immediately:
Deferred because it adds release-channel complexity before local installation is proven.

Create a standalone binary distribution first:
Rejected because it is unnecessary for the Genesis install milestone and would expand the packaging surface too early.

Move CLI code into a top-level package directory:
Rejected because the CLI is already established under `apps/cli`, and moving it now would add churn without solving the core installation problem.

## Follow-Up Work

- Implement packaging metadata under `apps/cli`.
- Expose the installed `agentforge` console command.
- Add install smoke tests and CI validation.
- Update docs for editable installation and installed usage.
- Revisit public distribution after `Genesis-0.0.5`.

## Revision History

- 2026-06-28: Accepted for Genesis Sprint 5.
