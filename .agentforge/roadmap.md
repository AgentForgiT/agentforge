# AgentForge Roadmap

Metadata:

- Status: Draft
- Phase: Genesis
- Last updated: 2026-06-29

## Genesis Sprint 1: Bootstrap Kit

Goal: create the canonical AI-native project skeleton.

Deliverables:

- Constitution and charter
- Decision register
- ADR and RFC templates
- AI assistant context files
- repository architecture
- contribution and security docs
- GitHub templates and starter validation workflow

## Genesis Sprint 2: Gateway Reconciliation

Goal: migrate the useful gateway prototype into the canonical monorepo without losing history context or governance discipline.

Deliverables:

- gateway module requirements
- gateway architecture doc
- ADR for gateway placement and provider adapter boundaries
- imported local MVP under `apps/gateway`
- tests and examples
- prototype repository disposition decision

## Genesis Sprint 3: Context Specification

Goal: define the first draft of the AgentForge AI Context Specification.

Deliverables:

- AICS draft
- validation rules
- example context tree
- CLI validation proposal

## Genesis Sprint 4: Canonical CLI MVP

Goal: make AICS validation available through the canonical monorepo CLI with governance, tests, documentation, and release coverage.

Deliverables:

- CLI MVP requirements
- ADR for `apps/cli` architecture and packaging boundaries
- source-tree `agentforge validate-context` implementation
- CLI tests and CI validation
- CLI docs and `Genesis-0.0.4` release

## Genesis Sprint 5: Installable CLI

Goal: make the canonical AgentForge CLI installable without abandoning the validated source-tree workflow.

Deliverables:

- installable CLI requirements for issue #16
- packaging and distribution ADR for issue #18
- installed `agentforge` command for issue #15
- install smoke tests and CI validation for issue #17
- installation docs and `Genesis-0.0.5` release for issue #19

## Genesis Sprint 6: Context Scaffolding MVP

Goal: let contributors initialize a validation-ready AICS baseline from the canonical AgentForge CLI without hand-authoring the required governance structure.

Deliverables:

- context scaffolding requirements for issue #20
- scaffolding template and safety decision for issue #21
- `agentforge init-context` MVP for issue #22
- scaffolding tests and CI validation for issue #23
- scaffolding docs and `Genesis-0.0.6` release for issue #24

## Genesis Sprint 7: Context Explanation MVP

Goal: let contributors and AI assistants explain an AICS project context through the canonical CLI without reducing orientation to pass/fail validation output alone.

Deliverables:

- context explanation requirements for issue #25
- explanation output and validation boundary decision for issue #26
- `agentforge explain-context` MVP for issue #29
- explanation tests and CI validation for issue #28
- explanation docs and `Genesis-0.0.7` release for issue #27

## Revision History

- 2026-06-29: Added Sprint 7 context explanation deliverables.
- 2026-06-29: Added Sprint 6 context scaffolding deliverables.
- 2026-06-28: Added Sprint 4 and Sprint 5 CLI deliverables.
- 2026-06-28: Added AICS v0.1 draft.
- 2026-06-28: Added gateway reconciliation requirements and ADR deliverables.
- 2026-06-28: Initial roadmap draft.
