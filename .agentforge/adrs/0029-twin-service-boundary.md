# ADR-0029: Twin Service Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #160, #161, #162, #163, #164
- Related: ADR-0028 (twin profile), DEC-0006 (0.1.0 gate / semver)

## Context

ADR-0028 deferred the twin *service*: a consumer of the generated `context/twin.json` that realizes the vision's "ask the project's twin." The profile exists; the live read layer does not. The tempting path is a full question-answering service (embeddings, a model, a store) — large, and a mismatch for the project's stdlib-only, honest-retrieval ethos.

## Decision

Add `agentforge serve-twin`: a **read-only stdlib HTTP service** over the twin profile with three endpoints:

- `GET /twin.json` — the generated profile; 404 with a run-`build-twin` hint when absent.
- `GET /search?q=<terms>` — deterministic keyword search over the governance corpus (ADR titles, decision register, governance file names), ranked by case-insensitive term overlap; empty query → 400.
- `GET /` — minimal HTML landing (profile summary + search box).

Boundary rules:

- **Read-only**: never writes, never touches AICS files; no auth (it serves the already-public profile; binds `127.0.0.1` by default).
- **Honest retrieval**: keyword matching only in v1 — no embeddings, no LLM, no generation. The twin *finds* what the repo declared; it does not invent understanding.
- **Stdlib only**: `http.server` + `json`; no dependencies, matching the gateway/SDK/CLI ethos.

## Consequences

- The twin gains a live read layer in one command: `agentforge serve-twin`.
- Search is deterministic and testable — results are a function of the corpus, not a model.
- A later generation-based "ask" layer can sit *behind* this retrieval boundary without changing the service contract.
- The service is a consumer of the profile, so the repo remains the single source of truth (ADR-0028 preserved).

## Alternatives Considered

- **Full QA service (embeddings + LLM)** — rejected: heavy, non-deterministic, violates the stdlib ethos; the retrieval layer is the honest v1 and the future QA layer's foundation.
- **Extend the gateway with /twin** — rejected: the gateway serves models; the twin is project knowledge. Separate concerns.
- **Write/search endpoints** — rejected: ADR-0028 makes the profile read-only; write paths belong to build-twin only.

## Deferred

- Generation-based "ask the twin" (embeddings + model) behind this retrieval boundary.
- Live ingestion of CI/CD, issues, and benchmarks into the profile.
- Auth/binding options beyond 127.0.0.1.
