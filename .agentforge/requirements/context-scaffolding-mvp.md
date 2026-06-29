# Context Scaffolding MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 6
- Related issues: #20, #21, #22, #23, #24
- Related specifications: `.agentforge/specs/aics-v0.1.md`, `.agentforge/specs/aics-validation-v0.1.md`
- Related decisions: ADR-0001, ADR-0003, ADR-0004, ADR-0005, DEC-0003
- Related policy: `docs/release-policy.md`
- Last updated: 2026-06-29

## Purpose

Define the requirements for the canonical `agentforge init-context` MVP so AgentForge can scaffold a validation-ready AICS baseline before implementation introduces templates, file-generation logic, or overwrite behavior.

This document exists so Sprint 6 decides command behavior, scaffold boundaries, and safety expectations before implementation work begins in `apps/cli`.

## Scope

In scope:

- the canonical `agentforge init-context` command surface
- target directory handling for new and existing local project folders
- generation of the required AICS v0.1 directory structure and files
- starter content expectations for required governance files and templates
- safety rules for overwrite prevention and rerun behavior
- compatibility with the existing `validate-context` command and validator
- Sprint 6 traceability across implementation, tests, documentation, and release work

Out of scope:

- public template registries or remote starter kits
- interactive prompts or wizards
- merge or in-place upgrade logic for pre-existing context files
- semantic project customization beyond bounded starter placeholders
- project code scaffolding outside the AICS baseline
- provider, model, gateway, or network-aware setup
- public package distribution changes beyond the Sprint 5 editable install path
- archiving or repurposing the historical `agentforge-cli` prototype

## Background

Genesis Sprint 3 defined AICS v0.1 and the validator rules required to confirm a project has the minimum AI-native governance baseline.

Genesis Sprint 4 and Sprint 5 established `apps/cli` as the canonical CLI location, shipped `agentforge validate-context`, and made the CLI installable through an editable install workflow.

The next practical CLI capability is to create a validation-ready context baseline so contributors do not need to hand-author the required AICS structure before they can use the validator.

## User Workflows

The MVP must support these workflows:

- A contributor initializes AICS in the current repository root before writing deeper project docs.
- A maintainer initializes a new local project directory with a minimal valid `.agentforge/` baseline.
- CI and tests can scaffold a temporary project, then validate the generated output without network access.
- An AI assistant initializes project context in a deterministic way without inventing file structure from scratch.

The MVP should favor deterministic filesystem behavior over customization breadth.

## Command Requirements

The first canonical scaffolding command must be:

```bash
agentforge init-context
```

The command must initialize the current working directory by default.

The command must also accept one explicit target path:

```bash
agentforge init-context path/to/project
```

The command may accept `--help`.

The command must not add additional flags in the MVP unless Sprint 6 architecture work explicitly approves them.

## Target Path Requirements

The default target is the current working directory.

When a path argument is provided, the CLI must resolve it as the target project root.

The command should accept relative and absolute paths.

When the explicit target path does not exist, the CLI may create the target directory and any missing parent directories needed for the scaffold.

When the target path cannot be created or accessed, the command must return an actionable error without partial silent success.

## Generated Artifact Requirements

The MVP must create a minimal valid AICS v0.1 baseline under the target project root.

At minimum, the generated scaffold must include:

```text
.agentforge/
  constitution.md
  charter.md
  decisions.md
  architecture.md
  repo-map.md
  agents/
    AGENTS.md
  adrs/
    ADR_TEMPLATE.md
  rfcs/
    RFC_TEMPLATE.md
  standards/
```

Generated required files must include bounded starter content that satisfies the current validator, including metadata blocks where AICS validation expects them.

Template files must include the required section text checked by the validator.

The MVP may generate a small number of recommended optional files only if Sprint 6 architecture work determines they materially improve the starter experience without widening maintenance cost.

Root-level pointer files such as `AGENTS.md`, `CODEX.md`, or `CLAUDE.md` are deferred unless the Sprint 6 architecture decision explicitly approves a bounded default set.

## Safety Requirements

The MVP must be safe by default.

The command must not overwrite existing files implicitly.

If one or more scaffold-managed files already exist and would need to be replaced, the command must fail with actionable conflict output and must not modify target files.

Rerunning the command against a target that already contains scaffold-managed files must fail safely in the MVP rather than merge or rewrite content.

Force, merge, update-in-place, or interactive conflict resolution behavior is out of scope for Sprint 6.

## Validation Requirements

Generated scaffold output must pass the canonical AICS validator without manual edits for the MVP baseline.

The scaffold must remain compatible with:

- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `scripts/aics_validation.py`
- `scripts/validate_aics.py`
- `agentforge validate-context`

The scaffolding command must not require network access, provider keys, GitHub credentials, or external services.

## Output and Exit Code Requirements

On success, the CLI must print a short success message that identifies the initialized target directory.

On expected scaffold failure, such as an invalid target path or conflicting existing files, the CLI must print actionable output and avoid stack traces.

The CLI must return:

- `0` when scaffolding succeeds
- `1` when scaffolding cannot complete because of target-state or filesystem conflicts
- `2` when CLI usage is invalid, such as too many arguments or an unknown command

The CLI may use a higher nonzero exit code for unexpected internal errors if the implementation documents it.

## Dependency Requirements

The scaffolding MVP should use Python standard library functionality by default.

New runtime dependencies require explicit architectural justification in the Sprint 6 decision record.

The scaffold generation flow should remain deterministic and usable in local development and CI without network access.

## Architecture Requirements

Sprint 6 implementation must follow ADR-0005 for template storage, root pointer strategy, and approved optional-file defaults.

The CLI must keep scaffolding logic separate from command-line parsing so future commands can reuse shared filesystem and template behavior.

The implementation should preserve the current CLI packaging and installation path established in Sprint 5.

The MVP should avoid baking long-term assumptions into generated content that would make future AICS revisions harder to evolve.

## Testing and CI Requirements

Sprint 6 testing must cover:

- initialization in a new target directory
- initialization in an existing directory without conflicting scaffold files
- conflict behavior when scaffold-managed files already exist
- invalid or inaccessible target path behavior
- validation of generated scaffold output
- regression coverage for existing `validate-context` behavior
- success, expected failure, and invalid-usage exit codes

CI must run the Sprint 6 scaffolding checks without external services or secrets.

Automated tests should be able to scaffold a temporary project and validate it within the same test flow.

## Documentation Requirements

Documentation must explain:

- how to run `agentforge init-context`
- what files and directories the MVP creates
- the safety behavior for existing files
- how to validate the generated scaffold
- current MVP limitations and deferred capabilities during Genesis

Documentation should make clear that the scaffold is a starting baseline, not a substitute for project-specific governance work.

## Acceptance Criteria

Issue #20 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references the AICS v0.1 spec and validation rules
- it references ADR-0003, ADR-0004, ADR-0005, and DEC-0003
- it defines the MVP command surface and safety expectations before implementation begins
- implementation issues #21, #22, #23, and #24 can trace their scope back to this document

The Sprint 6 context scaffolding milestone is complete when:

- issue #21 records the scaffolding template and safety strategy
- issue #22 implements `agentforge init-context`
- issue #23 adds automated scaffolding tests and CI validation
- issue #24 documents the workflow and prepares `Genesis-0.0.6`

## Examples

Initialize the current repository root:

```bash
agentforge init-context
```

Initialize an explicit target directory:

```bash
agentforge init-context examples/new-project
```

Validate the generated baseline:

```bash
agentforge validate-context
agentforge validate-context examples/new-project
```

## Best Practices

- Keep the MVP focused on a minimal valid AICS baseline.
- Prefer deterministic file generation over broad customization.
- Keep conflict messages actionable for humans and AI assistants.
- Reuse the existing validator as the acceptance oracle for generated output.
- Defer richer upgrade and merge behavior until the scaffold surface proves stable.

## Risks

- Overly rich starter content could create maintenance burden before the scaffold surface stabilizes.
- Overly sparse starter content could pass validation while still feeling unhelpful to contributors.
- Conflict handling can become confusing if the MVP does not clearly distinguish safe creation from blocked overwrite cases.
- Generated templates may drift from the validator or spec if Sprint 6 tests do not check them directly.

## References

- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `.agentforge/requirements/canonical-cli-mvp.md`
- `.agentforge/requirements/installable-cli.md`
- `.agentforge/adrs/0003-cli-module-architecture.md`
- `.agentforge/adrs/0004-cli-packaging-and-distribution.md`
- `.agentforge/adrs/0005-context-scaffolding-strategy.md`
- `.agentforge/decisions/0003-cli-path-for-aics-validation.md`
- `apps/cli/README.md`
- `docs/aics.md`
- `docs/release-policy.md`

## Revision History

- 2026-06-29: Initial requirements draft for Genesis Sprint 6.
