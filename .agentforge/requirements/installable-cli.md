# Installable CLI Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 5
- Related issues: #16, #18, #15, #17, #19
- Related specifications: `.agentforge/specs/aics-v0.1.md`, `.agentforge/specs/aics-validation-v0.1.md`
- Related decisions: ADR-0001, ADR-0003, DEC-0003
- Related policy: `docs/release-policy.md`
- Last updated: 2026-06-28

## Purpose

Define the requirements for making the canonical AgentForge CLI installable from the monorepo while preserving the validated source-tree workflow introduced in Genesis Sprint 4.

This document exists so installation behavior, packaging boundaries, and command expectations are decided before implementation adds packaging metadata or distribution workflows.

## Scope

In scope:

- contributor and CI install workflows from the monorepo
- availability of the `agentforge` command after installation
- compatibility with existing `validate-context` behavior
- relationship between installed and source-tree invocation paths
- runtime and dependency expectations for installable CLI packaging
- implementation traceability for Sprint 5 issues

Out of scope:

- public registry publishing to PyPI or npm
- Homebrew, apt, winget, or chocolatey distribution
- standalone binary packaging
- shell completion
- scaffolding commands beyond `validate-context`
- network validation
- provider, model, or gateway commands
- replacing the script validator path
- archiving or repurposing the historical `agentforge-cli` prototype

## Background

Genesis Sprint 4 established `apps/cli` as the canonical CLI module, shipped a source-tree `validate-context` command, added CLI tests, and released `Genesis-0.0.4`.

ADR-0003 intentionally deferred installer-level packaging and global `agentforge` command distribution until a later decision.

The next practical step is to make the CLI installable for contributors and CI without losing the deterministic source-tree behavior that already works.

## User Workflows

The installable CLI must support these workflows:

- A contributor installs the CLI from a local checkout and runs `agentforge validate-context`.
- CI installs the CLI from the repository and validates the canonical repo and minimal AICS example.
- A maintainer keeps using the source-tree wrapper while verifying that installed behavior matches it.
- An AI assistant can rely on the installed command shape without needing private shell aliases or custom environment setup.

The install workflow should remain simple enough for project contributors to use without package registry publication.

## Command Requirements

After installation, the canonical command must be:

```bash
agentforge validate-context
```

The installed command must preserve Sprint 4 CLI behavior:

- validate the current working directory by default
- accept one explicit project path
- print `aics ok` on success
- return `1` for AICS validation failures
- return `2` for invalid CLI usage

The source-tree wrapper must continue to work during Genesis:

```bash
python apps/cli/bin/agentforge.py validate-context
```

## Installation Requirements

The project must document at least one supported local install path from the monorepo.

The supported install path should work on contributor machines and in CI without relying on unpublished private artifacts.

Editable install behavior may be supported if the Sprint 5 packaging decision approves it.

The install path must make the `agentforge` executable available in a standard Python environment.

The install path should avoid hidden shell assumptions beyond normal Python environment activation.

## Packaging Requirements

Packaging metadata must live in or clearly point to the canonical CLI module under `apps/cli`, unless the Sprint 5 packaging ADR approves a different monorepo-level arrangement.

The installable CLI must keep command-line parsing separate from AICS validation logic.

Packaging choices must preserve compatibility with:

- `apps/cli`
- `scripts/aics_validation.py`
- `scripts/validate_aics.py`
- current CLI tests
- bootstrap validation

The project must not require public registry publishing to make local installation work.

## Dependency Requirements

The installed CLI should keep runtime dependencies minimal.

New runtime dependencies require explicit architectural justification in the Sprint 5 packaging decision.

Build-time packaging dependencies may be introduced if they are documented, bounded, and justified by the packaging strategy.

The install workflow must not require provider keys, GitHub credentials, or external services.

## Compatibility Requirements

The installable CLI must remain compatible with:

- AICS v0.1
- `.agentforge/specs/aics-validation-v0.1.md`
- the canonical repository root
- `examples/aics/minimal-project`
- the existing source-tree wrapper
- the existing script validator

The following command must continue to work:

```bash
python scripts/validate_aics.py
```

## Testing and CI Requirements

Sprint 5 testing must cover:

- installation from the monorepo
- invocation through installed `agentforge`
- validation of the canonical repository
- validation of `examples/aics/minimal-project`
- regression coverage for source-tree invocation
- install or invocation failure messages when setup is wrong

CI must run install and command checks without external services or secrets.

Local validation should remain runnable with one command per test surface.

## Documentation Requirements

Documentation must explain:

- the supported install workflow
- how to run `agentforge validate-context` after installation
- how to validate the canonical repo
- how to validate `examples/aics/minimal-project`
- how source-tree and installed invocation differ
- current installation limitations during Genesis

## Acceptance Criteria

Issue #16 is complete when:

- this requirements document exists
- it references ADR-0003
- it references DEC-0003
- it references the release policy
- implementation issues #18, #15, #17, and #19 can trace their scope back to this document

The Sprint 5 installable CLI milestone is complete when:

- issue #18 records packaging and distribution decisions
- issue #15 implements an installable `agentforge` command
- issue #17 adds install smoke tests and CI validation
- issue #19 documents installation and prepares `Genesis-0.0.5`

## Examples

Target installed command:

```bash
agentforge validate-context
agentforge validate-context examples/aics/minimal-project
```

Compatibility command that must remain valid:

```bash
python apps/cli/bin/agentforge.py validate-context
```

## Best Practices

- Keep installed and source-tree behavior aligned.
- Prefer simple contributor installation paths before broad distribution.
- Reuse existing validation logic instead of creating packaging-specific behavior.
- Keep failure messages actionable for humans and AI assistants.
- Defer public distribution channels until local installation is stable.

## Risks

- Packaging decisions could introduce avoidable complexity if they optimize for public distribution too early.
- Installed and source-tree command behavior could drift if tests only cover one path.
- Build tooling could add maintenance burden if chosen without clear long-term fit.
- Contributors may be confused if installation docs overpromise beyond the Genesis workflow.

## References

- `.agentforge/requirements/canonical-cli-mvp.md`
- `.agentforge/adrs/0003-cli-module-architecture.md`
- `.agentforge/decisions/0003-cli-path-for-aics-validation.md`
- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `docs/release-policy.md`
- `apps/cli/README.md`
- `scripts/validate_aics.py`

## Revision History

- 2026-06-28: Initial requirements draft for Genesis Sprint 5.
