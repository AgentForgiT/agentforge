# ADR-0032: Twin QA Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #175, #176, #177, #178, #179
- Related: ADR-0029 (twin service + retrieval), ADR-0031 (auth), DEC-0006 (semver)

## Context

ADR-0029 shipped the twin's retrieval layer and deferred generation *behind* that contract. The vision's "ask the project's twin" needs the QA layer — but the project's ethos is stdlib-only, offline-first, and honest. A generation layer that can hallucinate would betray the twin's core promise: it finds what the repo declared, it does not invent understanding.

## Decision

Add `GET /ask?q=` to the twin service, built as **deterministic retrieval + optional generation with a faithful extractive fallback**:

- **Retrieval**: top-K results from the existing `search_twin` (ADR-0029 contract unchanged).
- **Generation**: when a generator is configured, send the question + retrieved excerpts to an OpenAI-compatible chat-completions endpoint via stdlib `urllib`. The generator **defaults to the local AgentForge gateway** (`http://127.0.0.1:8080/v1/chat/completions`, model `mock-coder`), so "ask the twin" can run fully local using the project's own platform.
- **Fallback**: no generator configured, or the call fails → return a **faithful extractive answer**: top hits with quoted excerpts and `source: "extractive"`. Never fabricate.
- **Prompt discipline**: the system prompt requires the model to answer only from the provided excerpts, to say "not found in the twin" when they don't answer, and to cite excerpt ids.
- **Response shape**: `{query, source: generated|extractive|empty, answer, excerpts[]}` — `empty` when retrieval finds nothing.
- Config: `--generator-url/--generator-model/--generator-key` flags + `AGENTFORGE_GENERATOR_*` env overrides.

## Consequences

- The twin can answer questions with a model — including via the gateway itself — while remaining honest: the extractive fallback guarantees the twin never hallucinates.
- Retrieval stays deterministic (ADR-0029 preserved); generation is an optional layer on top.
- Stdlib-only holds: `urllib` for the generator call; no SDK dependency.
- Offline-testable: injected transport for generation; fallback tested via unreachable URL.

## Alternatives Considered

- **Embeddings + vector store** — rejected: adds heavy machinery; keyword retrieval already works for a governance corpus of dozens of docs.
- **Generation-only (no fallback)** — rejected: the twin must never fabricate; the extractive fallback is the honesty guarantee.
- **Always require a model** — rejected: "ask the twin" should degrade gracefully on an offline machine.

## Deferred

- Embeddings/vector retrieval at corpus scale.
- Multi-document citation formatting beyond excerpt ids.
- Streaming answers over the twin service.
