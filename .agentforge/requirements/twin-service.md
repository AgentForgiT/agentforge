# Twin Service: Read-Only HTTP Consumer

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 37 (first 0.1.x feature line) |
| Issues | #160, #161, #162, #163, #164 |
| Related | ADR-0028 (twin profile), DEC-0006 (0.1.0 gate / semver) |

## Purpose

The vision's "ask the project's twin" needs a live consumer of the twin profile (ADR-0028's deferred item). This sprint ships the first one: a **read-only stdlib HTTP service** that serves the generated `context/twin.json` and answers keyword queries over the governance corpus — honest retrieval, not generation.

## Requirements

R1. **`agentforge serve-twin`** (new CLI command): starts a stdlib `http.server` serving the project's twin profile at `context/twin.json`.
R2. Endpoints:
   - `GET /twin.json` — the generated profile (404 with a clear message if absent; hint to run `build-twin`).
   - `GET /search?q=<terms>` — keyword search over the governance corpus: ADR titles + decision register entries + governance file names; returns `{query, results: [{type, id, title, path}]}` ranked by term hits.
   - `GET /` — minimal HTML page (title, AICS level, link to twin.json, search box posting to /search).
R3. **Read-only**: the service never writes, never modifies AICS files; no auth (it serves only the already-public profile; binding defaults to `127.0.0.1`).
R4. **Stdlib only** (`http.server`, `json`, no dependencies); offline-testable with the built-in server in a thread.
R5. Search is deterministic keyword matching (case-insensitive term overlap) — no ML, no embeddings; honest retrieval is the v1 boundary.

## Acceptance Criteria

- [ ] `serve-twin` serves `/twin.json`, `/search?q=`, and `/`
- [ ] Missing profile → 404 with a run-`build-twin` hint
- [ ] Search returns ADR/decision hits ranked by term overlap; empty query → 400
- [ ] Read-only: AICS files byte-identical before/after serving
- [ ] Full suite passes offline; CI green
