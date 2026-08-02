# AICS v0.2: Structured Front Matter + Adoption Levels

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 26 |
| Issues | #115, #116, #117, #118, #119 |
| Related | `.agentforge/specs/aics-v0.1.md`, `aics-validation-v0.1.md`, backlog "AICS metadata structure refinement" |

## Background

AICS v0.1 defines portable project context with plain-Markdown `Metadata:` blocks and promises: "A future version may define structured front matter." It also defines three adoption levels (Present / Governed / Validated) that the validator never actually reports — it returns only a flat error list.

AICS is the project's moat: the portable context standard that humans and AI tools both read. v0.2 closes the v0.1 promises: machine-parseable metadata and explicit adoption-level reporting.

## Requirements

R1. **Structured front matter** becomes the recommended metadata format: a YAML block delimited by `---` at the top of each context document, with `status` and `aics-version` fields. Plain `Metadata:` blocks (v0.1 style) remain **accepted and backward-compatible** — v0.2 validation passes both.
R2. **Adoption-level reporting**: `validate-context` reports the project's adoption level:
   - Level 1 (Context Present): required directories + files exist.
   - Level 2 (Context Governed): metadata present (either style) + templates + required-text checks.
   - Level 3 (Context Validated): front matter present with `aics-version` + a version marker + the checks pass locally and in CI.
   Warnings (recommended files missing, plain-Metadata style at Level 3 target) are reported but do not fail validation.
R3. **Version marker**: a `.agentforge/aics-version` file containing `0.2` declares the context's spec version. Absent marker = v0.1 context (Level 2 max, warning at Level 3 target).
R4. **Dogfooding**: AgentForge's own core context files (constitution, charter, decisions, architecture, repo-map, agents/AGENTS.md) migrate to YAML front matter with `aics-version: 0.2`; the repo gains `.agentforge/aics-version`; its own validation reports Level 3.
R5. The in-browser WASM validator (docs site) embeds the updated `aics_validation.py` so the public page validates v0.2 contexts.
R6. All validation remains offline, dependency-free, and deterministic; CLI tests cover the new rules.

## Acceptance Criteria

- [ ] `aics-v0.2.md` spec + `aics-validation-v0.2.md` rules land
- [ ] Validator parses YAML front matter and plain Metadata blocks; both pass
- [ ] `validate-context` reports Level 1/2/3 with warnings
- [ ] `.agentforge/aics-version` marker checked
- [ ] AgentForge's own context migrates to front matter and validates at Level 3
- [ ] WASM validator page embeds the v0.2 script
- [ ] Full suite passes offline; CI green
