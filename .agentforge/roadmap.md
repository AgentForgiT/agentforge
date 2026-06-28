# AgentForge Roadmap

Metadata:

- Status: Draft
- Phase: Genesis
- Last updated: 2026-06-28

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

## Revision History

- 2026-06-28: Added Sprint 4 and Sprint 5 CLI deliverables.
- 2026-06-28: Added AICS v0.1 draft.
- 2026-06-28: Added gateway reconciliation requirements and ADR deliverables.
- 2026-06-28: Initial roadmap draft.
