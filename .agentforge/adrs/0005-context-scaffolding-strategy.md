# ADR-0005: Scaffold AICS Context from Packaged Templates with Safe No-Overwrite Initialization

Metadata:

- Status: Accepted
- Date: 2026-06-29
- Deciders: AgentForge maintainers
- Related issues: #20, #21, #22, #23, #24
- Related decisions: ADR-0001, ADR-0003, ADR-0004, DEC-0003
- Related requirements: `.agentforge/requirements/context-scaffolding-mvp.md`

## Context

Genesis Sprint 6 introduces the first scaffolding command for the canonical AgentForge CLI:

```text
agentforge init-context
```

The project already has:

- AICS v0.1 structure and validation rules
- a canonical CLI under `apps/cli`
- an installable editable CLI path

What Sprint 6 still needs is an architectural decision about how scaffolding works before implementation adds templates or file-generation logic.

The decision must answer:

- where scaffold templates live
- whether scaffolding uses static templates, programmatic generation, or both
- which AICS files are created in the MVP
- whether root pointer files are created by default
- how reruns and existing files are handled safely

Without this decision, `init-context` could grow into an unsafe overwrite tool, duplicate sources of truth, or generate a wider template surface than the current AICS and CLI maturity can support.

## Decision

The canonical `agentforge init-context` MVP will scaffold a minimal valid AICS v0.1 baseline from versioned templates owned by the canonical CLI package in `apps/cli`.

The implementation will use a hybrid approach:

- versioned template assets for stable scaffold content
- small standard-library rendering logic for bounded substitutions such as target-project-specific names or dates when needed

The scaffold surface for the MVP is limited to the AICS v0.1 required directories and files needed to pass the current validator.

The MVP will not generate root-level pointer files such as `AGENTS.md`, `CODEX.md`, or `CLAUDE.md` by default.

The `.agentforge/` directory remains the source of truth for generated context.

The command must be safe by default:

- perform a full preflight before writing files
- detect conflicts for all scaffold-managed files
- abort without modifying managed files if conflicts are found
- avoid force, merge, or in-place update behavior in the MVP

An existing target directory may be initialized only when the required scaffold-managed files do not already exist in conflicting form.

## Template Boundary

`apps/cli` owns:

- scaffold template assets
- render logic for bounded substitutions
- path planning and conflict detection
- user-facing success and failure messages
- scaffolding tests and fixtures

The scaffold should be stored as CLI-owned template assets rather than copied from the current repository's live `.agentforge/` tree at runtime.

This keeps generated output versioned with the CLI, reduces coupling to incidental repository edits, and makes tests deterministic.

The implementation may organize templates under a package path such as:

```text
apps/cli/src/agentforge_cli/templates/context-v0.1/
```

The exact internal path may vary if the Sprint 6 implementation preserves this ownership boundary and keeps packaging straightforward.

## Generated Baseline Boundary

The MVP scaffold must create the required AICS v0.1 baseline:

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

Generated file content must satisfy the current validation rules, including metadata blocks where required and required section text in the ADR and RFC templates.

Optional files such as roadmap, milestones, glossary, extra tool adapters, and root pointer files are deferred unless a later decision expands the scaffold surface.

## Safety Strategy

The MVP safety model is fail-fast and no-overwrite.

Before writing any managed file, the command must:

1. resolve the target project root
2. determine the full set of directories and files it intends to create
3. detect existing scaffold-managed file conflicts
4. abort with actionable output if any conflict exists

The implementation should minimize partial writes. If practical within the standard-library-only approach, the command should stage planned writes in memory and create directories only after preflight succeeds.

The MVP must not try to merge with existing user-authored context files.

The MVP must not introduce `--force`, `--merge`, or interactive conflict prompts.

Those capabilities require a later requirements document and decision if real usage justifies them.

## Relationship to Validation

The scaffold is accepted only if its generated output passes the existing AICS validator.

`agentforge init-context` must stay aligned with:

- `.agentforge/specs/aics-v0.1.md`
- `.agentforge/specs/aics-validation-v0.1.md`
- `scripts/aics_validation.py`
- `scripts/validate_aics.py`
- `agentforge validate-context`

The validator remains the source of truth for scaffold acceptability during Genesis.

## Consequences

Benefits:

- keeps scaffolding owned by the canonical CLI package
- produces deterministic, versioned starter content
- avoids coupling scaffold output to incidental repo-local document edits
- preserves `.agentforge/` as the source of truth
- keeps the MVP safe by default in existing directories
- limits the Sprint 6 implementation surface to the current AICS maturity level

Trade-offs:

- static template assets require explicit maintenance when AICS evolves
- the MVP will feel intentionally narrow compared with richer project generators
- no-overwrite behavior means reruns are blocked instead of helpful in some cases
- deferring root pointer files leaves some tool ergonomics for later follow-up

## Alternatives Considered

Generate files entirely in Python code:
Rejected as the primary strategy because it makes large starter documents harder to review, compare, and evolve than versioned template assets. Small bounded rendering logic is still allowed where it improves template reuse.

Copy files from the repository's current `.agentforge/` tree at runtime:
Rejected because it couples scaffolding output to the state of the local repository instead of to a CLI-owned scaffold baseline, making tests and installation behavior less deterministic.

Generate optional files and root pointer files by default:
Deferred because Sprint 6 should prove the minimal valid AICS baseline first and avoid expanding maintenance surface prematurely.

Allow overwrite, merge, or force behavior in the MVP:
Rejected because it adds hidden risk and broader semantics before the scaffolding command has stable usage patterns.

Store templates outside `apps/cli`:
Rejected because ADR-0003 and ADR-0004 already establish `apps/cli` as the canonical CLI ownership boundary.

## Follow-Up Work

- Implement CLI-owned scaffold template assets.
- Add preflight conflict detection and deterministic file creation.
- Add tests for new-directory success, existing-directory success without conflicts, and conflict failure behavior.
- Validate generated output with the existing AICS validator in automated tests.
- Document the generated baseline and current safety limitations.

## Revision History

- 2026-06-29: Accepted for Genesis Sprint 6.
