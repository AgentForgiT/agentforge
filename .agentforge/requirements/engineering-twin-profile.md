# Engineering Twin: Buildable Project Profile

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 33 |
| Issues | #145, #146, #147, #148, #149 |
| Related | ADR-0022/0024 (AICS v0.2/v0.3), vision "AI Engineering Twin" |

## Background

The vision's moonshot: every project connected to AgentForge has a digital engineering twin that understands architecture, ADRs, RFCs, docs, codebase, CI/CD, issues, and benchmarks — so instead of asking a chatbot "how does this project work?", you ask the project's own twin.

The honest kickoff is the **twin's knowledge layer**: a buildable, machine-readable project profile that consolidates what the repo already declares (AICS governance, architecture, decisions, models, gateway surface) into one structured artifact. No live service yet — a generated, read-only profile (ADR-0028).

## Requirements

R1. **`agentforge build-twin`** (new CLI command): reads the project's AICS context and the optional gateway config, writes `context/twin.json`:
   - `schema_version` (`0.1`), `generated_at`, `aics_version` (from `.agentforge/aics-version` or `0.1`)
   - `profile`: project name, repo root, AICS adoption level (from `validate-context`)
   - `governance`: constitution/charter/decisions/architecture/repo-map paths, ADR + RFC counts, decision register entries
   - `gateway` (optional, when `apps/gateway/config*.json` present): models, providers, surfaces
R2. **Schema**: `context/twin.schema.json` documents the shape; `build-twin` validates its own output against the schema before writing.
R3. **Read-only + idempotent**: building never modifies AICS files; re-running produces the same structural output (timestamps aside).
R4. **Stdlib only**; the command shares the CLI's existing AICS validation loading.
R5. `context/` is an optional AICS location (not required for Level 3); the twin is a consumer artifact.

## Acceptance Criteria

- [ ] `build-twin` writes `context/twin.json` matching the schema
- [ ] Output includes AICS level, governance inventory, and (when config present) gateway models/providers
- [ ] Idempotent: second run has identical structure; AICS files untouched
- [ ] Schema validates the output; malformed inputs reported clearly
- [ ] Full suite passes offline; CI green
