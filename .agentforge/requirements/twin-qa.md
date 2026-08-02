# Twin QA: Ask the Project's Twin

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 40 |
| Issues | #175, #176, #177, #178, #179 |
| Related | ADR-0029 (twin service + retrieval contract), ADR-0031 (auth), DEC-0006 (semver) |

## Purpose

The vision's "ask the project's twin" — a question-answering layer over the twin profile. ADR-0029 deferred generation *behind* the retrieval contract; this sprint delivers it honestly: **deterministic retrieval + optional generation, with a faithful extractive fallback** so the twin never fabricates.

## Requirements

R1. **`GET /ask?q=<question>`** on the twin service:
   - Retrieval: top-K results from the existing deterministic `search_twin` (ADR-0029 contract, unchanged).
   - Generation: when a generator is configured/reachable, the question + retrieved excerpts are sent to an OpenAI-compatible chat-completions endpoint (stdlib `urllib`), and the model's answer is returned with `source: "generated"`.
   - Fallback: when no generator is configured or the call fails, return a **faithful extractive answer** — the top hits with quoted excerpts and a note that no model was used (`source: "extractive"`). Never fabricate.
R2. **Generator config**: `--generator-url <base>` and `--generator-model <name>` flags on `serve-twin`; defaults: `http://127.0.0.1:8080/v1/chat/completions` (the local AgentForge gateway) and `mock-coder`. Optional `--generator-key` for gateway auth (ADR-0031). Environment overrides: `AGENTFORGE_GENERATOR_URL`, `AGENTFORGE_GENERATOR_MODEL`.
R3. **Prompt discipline**: the system prompt instructs the model to answer *only from the provided excerpts*, to say "not found in the twin" when the excerpts don't answer, and to cite excerpt ids. The response is trimmed to the model's `content`.
R4. **Honest response shape**:
   ```json
   {
     "query": "...",
     "source": "generated" | "extractive" | "empty",
     "answer": "...",
     "excerpts": [{"id": "...", "title": "...", "excerpt": "..."}]
   }
   ```
   `source: "empty"` when retrieval finds nothing (no answer, no fabricated content).
R5. Read-only + offline tests: generator calls use injected transport; fallback tested by an unreachable URL; all suites stay offline.

## Acceptance Criteria

- [ ] `/ask` retrieves top-K and returns excerpts in every response
- [ ] Generated answers when the gateway answers; `source: "generated"`
- [ ] Extractive fallback (quoted excerpts, no model) when unreachable; `source: "extractive"`
- [ ] Empty retrieval → `source: "empty"` with no fabricated content
- [ ] Empty/missing `q` → 400
- [ ] Full suite passes offline; CI green
