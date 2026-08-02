# ADR-0028: Engineering Twin Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #145, #146, #147, #148, #149
- Related: ADR-0022/0024 (AICS metadata + tooling), vision "AI Engineering Twin"

## Context

The vision's moonshot is an "AI Engineering Twin" per project: an artifact that understands architecture, ADRs, RFCs, docs, codebase, CI/CD, issues, and benchmarks, so a project can be asked questions directly. A live, continuously-synced twin service is a large platform; attempting it as a first increment would stall.

The AICS work (v0.2 front matter, v0.3 tooling) already made project context machine-parseable. The twin's foundation is therefore a **generated, read-only, machine-readable project profile** that consolidates what the repo already declares.

## Decision

Add `agentforge build-twin`: a CLI command that reads the project's AICS context (and optional gateway config) and writes `context/twin.json` — a structured profile with:

- `schema_version`, `generated_at`, `aics_version`
- `profile` (project name, root, AICS adoption level)
- `governance` (constitution/charter/decisions/architecture/repo-map paths, ADR/RFC counts, decision register)
- `gateway` (optional: models, providers, surfaces, when a gateway config is present)

Boundary rules:

- **Generated and read-only**: `build-twin` never modifies AICS files; the repo remains the single source of truth.
- **Idempotent**: re-running produces the same structure (timestamps aside).
- **Schema-validated**: `context/twin.schema.json` documents the shape; the command validates its own output before writing.
- **Optional location**: `context/` is not required for AICS Level 3; the twin is a consumer artifact, not a governance requirement.
- **Stdlib only**, reusing the CLI's existing AICS loading.

## Consequences

- Every AgentForge project can materialize a machine-readable twin profile in one command — the data layer the future twin service (or any consumer) needs.
- The twin inherits AICS's honesty: it reports what the repo declares; it does not invent understanding.
- The gateway surface is included when configured, so the twin can answer "what models/providers does this project expose?"
- Future increments (a twin *service*, live CI sync, question-answering over the profile) build on this artifact without rework.

## Alternatives Considered

- **Live twin service now** — rejected: needs hosting, auth, sync, and a query layer; violates the ship-thin rule and would stall the increment.
- **Embed the profile in AICS as a required file** — rejected: AICS stays lean; the twin is derived, not required.
- **A single JSON blob with no schema** — rejected: an unvalidated artifact cannot be trusted by consumers.

## Deferred

- Twin service / HTTP endpoint (a consumer of the profile, later).
- CI/CD + issue/benchmark ingestion into the profile.
- Question-answering over the twin (the vision's "ask the project's twin").
