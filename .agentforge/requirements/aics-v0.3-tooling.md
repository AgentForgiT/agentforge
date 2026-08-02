# AICS v0.3 Tooling: Scaffolds, Migration, Schema

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 28 |
| Issues | #125, #126, #127, #128, #129 |
| Related | ADR-0022 (front matter), ADR-0024 (tooling boundary) |

## Background

AICS v0.2 (ADR-0022) made front matter the metadata standard, but tooling lagged: `init-context` scaffolds v0.1 plain-`Metadata:` contexts (capped at Level 2), and v0.1 → v0.2 migration was deferred. Adoption needs the tooling loop closed: new projects Level-3-ready from birth, old projects one command from upgrade.

## Requirements

R1. **v0.2 scaffolds**: `init-context` writes YAML front matter (`status`, `aics-version: 0.2`, plus applicable fields) in all six metadata files and the templates; writes `.agentforge/aics-version` = `0.2`. A freshly scaffolded project validates at **Level 3**.
R2. **`migrate-context` command**: converts v0.1 plain `Metadata:` blocks to front matter additively (field mapping per ADR-0024), writes the version marker when absent, never touches document body content, skips already-front-matter files, reports unparseable blocks without clobbering. Exit 0 with a per-file report; exit 1 on errors.
R3. **JSON Schema**: `.agentforge/specs/aics-front-matter.schema.json` documents the canonical shape (required `status` + `aics-version`; recommended linkage fields). Declarative only — the validator stays stdlib string-check based.
R4. The v0.1 template set remains as historical reference; `TEMPLATE_VERSION` constant points at v0.2.
R5. All tests offline; existing init/validate/doctor/install tests updated where output changed.

## Acceptance Criteria

- [ ] `init-context` scaffold validates at Level 3 (CLI + script)
- [ ] `migrate-context` converts a v0.1 fixture to v0.2 with no body-content change
- [ ] `migrate-context` is idempotent (second run: nothing to migrate)
- [ ] Schema file present and internally consistent with the validator's field set
- [ ] Full suite passes offline; CI green
