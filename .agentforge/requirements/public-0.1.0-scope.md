# Public 0.1.0 Release Scope

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 35 |
| Issues | #150, #151, #152, #153, #154 |
| Related | DEC-0006, `.agentforge/backlog.md` (0.1.0 scope definition) |

## Purpose

Define what the **public `0.1.0` line** means after the governed Genesis `0.0.x` train, what must be true before it ships, and how the project transitions. This is a scope and gate definition — not a promise of a date.

## Background

Genesis `0.0.x` has shipped 31 governed releases: gateway (dual protocol, 4 providers, streaming, CORS, auth, rate limiting, MCP), CLI (AICS validate/init/migrate/explain/doctor/build-twin), SDK (agentforge-sdk), 28 ADRs, and a Level-3 AICS context validated in CI. The backlog already names "public 0.1.0 scope definition" as near-term work.

## 0.1.0 Definition

`0.1.0` is the first release line intended for **external adoption**: installable, documented, and stable enough for contributors and researchers to build on without the Genesis release cadence.

## Scope: In

- **Gateway**: the current surface (OpenAI + Anthropic + MCP), provider set, auth, rate limiting, and streaming — as shipped, with documentation.
- **CLI**: the current command set (validate, init, migrate, explain, doctor, build-twin) installable from PyPI.
- **SDK**: `agentforge-sdk` published to PyPI (requires the `PYPI_TOKEN` step from ADR-0027).
- **AICS**: v0.2 (or later) spec with Level-3 tooling, documented for external adopters.
- **Website**: the flagship site pages as the public face.

## Scope: Out of 0.1.0 (deferred)

- AICS v0.4+ features (engineering twin *service*, not just the profile).
- MCP resources/prompts, gateway client mode.
- Production auth (per-user keys, key store), distributed rate limiting.
- Benchmark Observatory live data pipelines.
- Enterprise/cloud offerings.

## Exit Criteria (all must hold)

1. `agentforge-sdk` and `agentforge-cli` publishable and published to PyPI from the tag-gated workflow (ADR-0027) — or an explicit decision to keep them on release assets only.
2. Gateway + CLI + SDK test suites green offline (current: 215 + 39 + 11).
3. AICS validation passes at Level 3 on the AgentForge repo itself, and the migration + scaffold tools are documented for external projects.
4. Public docs (website) cover: gateway, CLI, SDK, AICS, MCP registration, compatibility matrix.
5. All 0.1.0 in-scope ADRs are Accepted (no Draft ADRs in the decision register).
6. A 0.1.0 release note records the transition and the governing decisions (this doc + DEC-0006).

## Versioning Policy (forward)

- After 0.1.0: semantic versioning applies (`0.1.x` fixes, `0.2.0` features, `1.0.0` stability).
- The Genesis `0.0.x` train stops at the release that carries the 0.1.0 scope (Genesis-0.0.32); later governance work rides the 0.1.x line.
- Breaking changes require a minor bump and an ADR.

## Acceptance Criteria

- [ ] Requirements doc + DEC-0006 land
- [ ] Exit criteria listed above are recorded in the roadmap/milestones
- [ ] Roadmap/milestones/backlog updated consistently; CI green
- [ ] Genesis-0.0.32 carries this scope as its release note
