# Changelog

## 0.9.0 - 2026-08-01

- Added key-store encryption at rest (ADR-0036):
  - `keystore.py` encrypt/decrypt: PBKDF2-HMAC-SHA256 (210k iters) derives enc + MAC keys; PBKDF2-CTR XOR stream for confidentiality; HMAC-SHA256 encrypt-then-MAC for integrity (stdlib primitives, documented honestly — not audited AEAD).
  - Encrypted stores auto-detect (`"encrypted": true`); gateway decrypts via `AGENTFORGE_AUTH_KEYS_PASSPHRASE`; wrong passphrase/tampering → clear error.
  - `auth-key add --encrypt` (+ `--passphrase-env`); list/revoke work on encrypted stores transparently.
  - Plaintext stores fully supported (backward compatible).
- Added 9 encryption tests (roundtrip, wrong passphrase, tamper detection, plaintext compat, gateway auth, CLI encrypt). Named-key suite now 26.

## 0.8.0 - 2026-08-01

- Added per-benchmark regression thresholds (ADR-0035):
  - `benchmarks/thresholds.json` (checked-in): default 10% + per-name overrides — gateway latency/throughput 5% (stable), CLI/AICS timing 20% (jittery).
  - `check_regressions.py --thresholds <path>`; resolution: per-name > config default > inline `--threshold` > 10; invalid config → usage error (exit 2).
- Added 7 threshold tests (resolution, fallback, validation, CLI exit 2). Gate suite now 16.

## 0.7.0 - 2026-08-01

- Added the benchmark regression gate (ADR-0034):
  - `benchmarks/check_regressions.py`: current vs previous release comparison; lower-better increases and higher-better decreases beyond threshold → REGRESSED (exit 1); improvements and within-threshold changes never fail; benchmarks missing from one side are skipped.
  - Publish workflow benchmarks job now gates the fresh results against the previous release's (fetched via gh) before attaching.
- Added 9 gate tests (both directions, threshold, improvements, skip, CLI exit codes).

## 0.6.0 - 2026-08-01

- Added benchmark trends (ADR-0033):
  - `benchmarks/collect_history.py`: fetches per-release `results.json` assets (injectable fetch, stdlib), merges into versioned `history.json` with per-benchmark series, derived better-direction, and release-to-release deltas.
  - `benchmarks/history.schema.json`; output validated before write.
  - Observatory trends section: rows = benchmarks, columns = releases, delta arrows colored by better direction (green ↓ for lower-better, green ↑ for higher-better).
  - Collected live: 3 releases (0.3.0–0.5.0), 5 trends.
- Added 8 history tests (merging, direction, deltas, schema, skip logic).

## 0.5.0 - 2026-08-01

- Added the twin QA layer (ADR-0032):
  - `serve-twin /ask?q=` — deterministic top-K retrieval (ADR-0029 contract) + optional generation.
  - Generator defaults to the local AgentForge gateway (`http://127.0.0.1:8080/v1/chat/completions`, `mock-coder`); flags `--generator-url/--generator-model/--generator-key` + `AGENTFORGE_GENERATOR_*` env.
  - Honest response: `source: generated | extractive | empty` — extractive fallback quotes the top hits when no model is reachable; the twin never fabricates.
  - Prompt discipline: model answers only from provided excerpts, says "not found in the twin" otherwise.
- Added 10 twin-QA tests (generated/extractive/empty, generator call, 400). Live-verified all three states via the real gateway.

## 0.4.0 - 2026-08-01

- Added per-user auth (ADR-0031):
  - `server.auth_keys_file`: named key store with per-key `rate_limit_rpm`; each key gets its own token bucket.
  - Live reload: `agentforge auth-key add|revoke` takes effect without a gateway restart.
  - Backward-compatible: the shared `api_key_env` key works alongside named keys.
  - `agentforge auth-key add|list|revoke` CLI — keys generated with `secrets`, printed exactly once, never re-shown or logged.
  - Malformed store → startup configuration error (fail fast); live reads tolerate transient absence.
- Added 17 named-key tests (store validation, auth, per-key limits, live reload, persistent buckets, CLI management). Gateway suite now 232.

## 0.3.0 - 2026-08-01

- Added the benchmark pipeline (ADR-0030):
  - `benchmarks/run_benchmarks.py`: reproducible offline harness — gateway chat-completion latency/throughput (mock provider, in-process), CLI validate/build-twin timing, AICS validation timing.
  - `benchmarks/results.schema.json`; output validated before write.
  - CI publishes `results.json` as a release asset on tags (publish workflow gains a benchmarks job).
  - Benchmark Observatory page consumes the published results (measured section with suite/environment footer).
- Added 7 benchmark tests (harness suites, schema validation, runner CLI).

## 0.2.0 - 2026-08-01

- Added the twin service (ADR-0029) — first feature release under semver (DEC-0006):
  - `agentforge serve-twin`: read-only stdlib HTTP service over the twin profile.
  - `GET /twin.json` (404 + run-`build-twin` hint when absent), `GET /search?q=` (deterministic keyword search over ADRs, decision register, governance files, ranked by term overlap), `GET /` (minimal index page).
  - Read-only, 127.0.0.1 by default, zero dependencies; honest retrieval — no embeddings or generation in v1.
- Added 11 twin-service tests (search, endpoints, 404 hints, read-only). CLI suite now 50.

## Genesis-0.0.33 - 2026-08-01

- Added the community layer (DEC-0007):
  - Expanded `CONTRIBUTING.md`: sprint pattern, full validation suite, conventional commits, contribution paths.
  - `docs/community.md`: four contribution paths (code/docs/research/integrations), the release train, the 0.1.0 gate, and where things live.
  - Docs-site contributing page refreshed: live platform pages + the 0.1.0 gate link.

## Genesis-0.0.32 - 2026-08-01

- Defined the public 0.1.0 release scope (DEC-0006):
  - `requirements/public-0.1.0-scope.md` — what's in/out of 0.1.0, six exit criteria, semver policy after 0.1.0.
  - `requirements/0.1.0-release-gate-checklist.md` — the auditable gate (each box needs verifiable evidence).
  - Genesis ends at this release; `0.1.x` follows under semantic versioning.

## Genesis-0.0.31 - 2026-08-01

- Kicked off the Engineering Twin (ADR-0028):
  - `agentforge build-twin` writes `context/twin.json` — a read-only, schema-validated project profile: AICS version + adoption level, governance inventory (constitution/charter/decisions/architecture/repo-map/agents, ADR + RFC counts, decision register), and the gateway surface (models, providers, surfaces) when configs are present.
  - `context/twin.schema.json` documents the shape; the command validates its own output; AICS files are never modified; idempotent.
- Added 7 twin tests (build, governance, read-only, idempotency, gateway surface, CLI).

## Genesis-0.0.30 - 2026-08-01

- Added SDK distribution (ADR-0027):
  - `agentforge-sdk` builds clean sdist + wheel (verified locally).
  - `.github/workflows/publish.yml`: on `Genesis-0.0.x` tags, builds `agentforge-cli` + `agentforge-sdk`, publishes to PyPI gated on `PYPI_TOKEN` (dry-run-safe when absent), and attaches both wheels as release assets.
  - `docs/mcp.md`: canonical MCP registration — Claude Code `claude mcp add agentforge --transport http --url http://127.0.0.1:8080/mcp`, `.mcp.json` project scope, and the auth env note.

## Genesis-0.0.29 - 2026-08-01

- Added the gateway MCP server surface (ADR-0026): `POST /mcp` speaks stdlib JSON-RPC 2.0 with `initialize`, `tools/list`, `tools/call`, and empty `resources/list`/`prompts/list`.
  - Four MCP tools: `gateway_health`, `gateway_list_models`, `gateway_chat_completion`, `gateway_anthropic_message` — a view over existing capabilities, no new providers.
  - JSON-RPC error shapes (-32700/-32600/-32601/-32602/-32603); gateway failures → `isError: true` tool results.
  - Auth (ADR-0023) and CORS (ADR-0018) apply to `/mcp`.
- Added 15 MCP tests (handshake, tool schemas, routing, protocol errors). Suite now 215.

## Genesis-0.0.28 - 2026-08-01

- Added the Python SDK (ADR-0025): `apps/sdk` — dependency-free `AgentForgeClient` covering health, models, chat completions (non-stream + SSE), and Anthropic Messages (non-stream + SSE), with Bearer auth and typed `AgentForgeError` for gateway envelopes.
- Added 10 SDK tests (transport, payloads, auth header, error envelope, both stream parsers, editable-install smoke).
- CLI packaging fix: `context-v0.2` templates now included in package data.

## Genesis-0.0.27 - 2026-08-01

- Added AICS v0.3 tooling (ADR-0024):
  - `init-context` scaffolds v0.2 front matter (`context-v0.2` templates with `aics-version: 0.2` + version marker) — new projects validate at Level 3 immediately.
  - New `migrate-context` command: additive v0.1 → v0.2 conversion (plain `Metadata:` blocks → YAML front matter, version marker written, body content untouched, idempotent).
  - `.agentforge/specs/aics-front-matter.schema.json` documents the canonical front matter shape (required `status` + `aics-version`).
- Added 11 tests (scaffold-at-Level-3, conversion, migration, idempotency, CLI).

## Genesis-0.0.26 - 2026-08-01

- Added opt-in API-key auth and rate limiting (ADR-0023):
  - `server.api_key_env` names an env var; when set, `/v1/chat/completions` and `/v1/messages` require `Authorization: Bearer <key>` or `x-api-key: <key>`; missing/wrong → 401 (standard or Anthropic envelope per surface).
  - `server.rate_limit_rpm` token-bucket rate limiting per key (auth on) or per IP (auth off); exceeding → 429 with `Retry-After: 60`.
  - `GET /health` and CORS preflight exempt; 401/429 carry CORS headers; key never logged (ADR-0015).
  - Keyless default byte-for-byte unchanged; new `config.auth.example.json`.
- Added 21 tests (config validation, auth paths, rate-limit bucket + HTTP 429, CORS-on-error, default unchanged). Suite now 200.

## Genesis-0.0.25 - 2026-08-01

- Added AICS v0.2 — the moat work (ADR-0022):
  - Structured YAML front matter (required `status` + `aics-version`; recommended linkage fields) as the recommended metadata format; v0.1 `Metadata:` blocks remain accepted (backward compatible).
  - Machine-reported adoption levels: Level 1 Context Present / Level 2 Context Governed / Level 3 Context Validated, surfaced by `validate-context` and `scripts/validate_aics.py` with warnings.
  - `.agentforge/aics-version` version marker (content `0.2`); absence caps a context at Level 2 with a warning.
  - AgentForge's own context migrated to front matter — the repo is the first Level-3 context, validated in CI on every push.
  - WASM in-browser validator page re-synced from the canonical script.
- Added 11 tests (front matter parsing, level semantics, marker, dogfooding). CLI suite updated for level output.

## Genesis-0.0.24 - 2026-08-01

- Added the `anthropic` outbound provider adapter (ADR-0021): OpenAI-compatible clients can now reach Anthropic's API through the gateway with `ANTHROPIC_API_KEY` set.
  - OpenAI body → Anthropic Messages payload (system fold, function tools, tool_calls → tool_use, tool role → tool_result, `max_tokens` default 4096)
  - Anthropic response → `chat.completion` (text concat, tool_use → tool_calls, stop_reason → finish_reason, usage mapping)
  - Anthropic SSE events → OpenAI stream chunks with `[DONE]` (text_delta → content, input_json_delta → tool_calls)
  - `x-api-key` + `anthropic-version: 2023-06-01` headers; key from `api_key_env` (default `ANTHROPIC_API_KEY`)
- Added 12 tests (contract: success, headers, system/tools translation, tool round-trip, error translation, streaming text + tool deltas; registration; example config). Suite now 179, fully offline.

## Genesis-0.0.23 - 2026-08-01

- Added Anthropic thinking + tool-use mapping at the inbound boundary (ADR-0020), closing ADR-0019's deferred items:
  - `tools` parameter → OpenAI function tools
  - assistant `tool_use` blocks → OpenAI `tool_calls`
  - user `tool_result` blocks → OpenAI `tool` role messages (one per result, with `tool_call_id`)
  - provider response `tool_calls` → Anthropic `tool_use` content blocks (`stop_reason: "tool_use"`)
  - streaming `delta.tool_calls` → `content_block_start` (tool_use) + `content_block_delta` (`input_json_delta`) events
  - Anthropic `thinking` accepted and passed through (not mapped; logged per ADR-0020)
- Added 10 tests (tools param, block translation, response mapping, streaming events). Suite now 167.

## Genesis-0.0.22 - 2026-08-01

- Added the Anthropic Messages inbound surface (`POST /v1/messages`): Anthropic-protocol clients (Claude Code, Anthropic SDK) can now point their base URL at the gateway and reach the same providers (ADR-0019).
- Translation-at-the-edge: Anthropic request → internal OpenAI-compatible dispatch → Anthropic-shaped response; provider adapters untouched.
- Anthropic SSE streaming events: `message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop` (no `[DONE]` sentinel).
- Anthropic error envelope (`{"type": "error", "error": {...}}`) with the same status mapping as the OpenAI surface.
- Keyless: `x-api-key` accepted but not required and never forwarded upstream (ADR-0017 consistency).
- Added 21 tests (validation, translation, response normalization, streaming events, endpoints incl. wire format). Suite now 157 tests.

## Genesis-0.0.21 - 2026-08-01

- Added opt-in CORS support: `server.cors_origin` config (`*` or a single http(s) origin, validated, disabled by default), `OPTIONS` preflight answering 204 with `Access-Control-Allow-*` headers, and `Access-Control-Allow-Origin` on all JSON responses and SSE streams (ADR-0018).
- Added 14 CORS tests (config parsing, preflight enabled/disabled, header presence on JSON/error responses, wildcard, disabled default). Suite now 136 tests.
- `config.example.json` now ships with `cors_origin` set to the docs-site origin so the web playground works out of the box.

## Genesis-0.0.20 - 2026-08-01

- Added the `ollama` provider adapter: keyless chat completions (non-streaming + SSE streaming) from local open-weight models via Ollama's OpenAI-compatible `/v1` surface. Default `base_url` is `http://127.0.0.1:11434/v1`, overridable per provider config; no API key required or read (ADR-0017).
- Connection-refused and transport failures translate to clear `UpstreamProviderError`s naming the provider (e.g. a stopped local daemon).
- Extracted shared SSE framing and HTTP-error translation to `providers/http.py`, used by both `openrouter` and `ollama` adapters.
- Registered `ollama` in the provider factory; `supported_provider_types()` now returns `("mock", "ollama", "openrouter")`.
- Shipped `config.ollama.example.json` (mock + `local-llama3` → `llama3.2`).
- Added 8 offline tests: provider contract (success, keyless headers, streaming, HTTP 404, connection-refused), factory, config parse, and a `GatewayApp` endpoint test with an injected Ollama provider. Suite now 122 tests.
- Live-verified against Ollama 0.32.5 with `llama3.2:1b` through the gateway: non-streaming completion returned normalized `local-llama3` output (`finish: stop`), and SSE streaming produced 9 chunks ending with `[DONE]`; all gateway log lines `status=200`.

## Genesis-0.0.19 - 2026-08-01

- Live-verified the gateway against the OpenRouter API (non-streaming and streaming completions, alias normalization, reasoning passthrough, `[DONE]` termination).
- Fixed reasoning-model response validation: `message.content: null` is now accepted per the OpenAI-compatible spec (reasoning models emit output in `reasoning` fields), instead of a 502. Non-string non-null content is still rejected.
- Preserved `reasoning`, `reasoning_details`, and provider extras through normalization (ADR-0016).
- Added live-derived reasoning fixtures (OpenRouter `gpt-oss-20b:free`, provider "Darkbloom") to the gateway test suite for both non-streaming and streaming paths.
- Updated `config.openrouter.example.json` to a currently-available free model (`openai/gpt-oss-20b:free`).

## Genesis-0.0.18 - 2026-07-31

- Added Sprint 18 requirements and ADR-0015 for the gateway logging boundary.
- Added structured access logging with method, path, status, and duration records; chat-completion context records with model and stream flag; and configurable `server.log_level` with strict enum validation.
- Added explicit `500` internal error handling for unexpected handler exceptions with exception details logged at `ERROR` only.
- Added logging tests (13) and configuration validation tests for the log level.
- Documented the logging contract, privacy rules, and Sprint 18 limitations.

## Genesis-0.0.17 - 2026-07-24

- Added Sprint 17 requirements and ADR-0014 for the gateway streaming boundary.
- Added OpenAI-compatible SSE streaming to `/v1/chat/completions` with boolean `stream` validation.
- Added deterministic mock provider streaming and OpenRouter SSE forwarding with upstream chunk translation.
- Added gateway-owned streaming chunk normalization and mid-stream error termination.
- Added focused streaming tests: request validation, mock and OpenRouter stream contracts, chunk normalization, and HTTP SSE delivery.

## Genesis-0.0.16 - 2026-07-10

- Added Sprint 16 requirements and ADR-0013 for the gateway configuration validation boundary.
- Hardened gateway config parsing for server, model, provider, timeout, and header fields while preserving default mock config behavior.
- Added focused configuration validation tests and updated gateway documentation.

## Genesis-0.0.15 - 2026-07-06

- Added Sprint 15 requirements and DEC-0005 for product foundation hygiene.
- Added `.agentforge/backlog.md`, canonical standards under `.agentforge/standards/`, `.editorconfig`, and `.gitattributes`.
- Updated bootstrap validation and repository documentation to require and explain product foundation artifacts.

## Genesis-0.0.14 - 2026-07-06

- Added Sprint 14 requirements and ADR-0012 for the gateway response normalization boundary.
- Centralized successful chat-completion response normalization while preserving public model aliases.
- Added focused response normalization tests and endpoint coverage for malformed provider success responses.

## Genesis-0.0.13 - 2026-07-05

- Added Sprint 13 requirements and ADR-0011 for the gateway JSON error response boundary.
- Centralized gateway error envelope helpers while preserving current status mappings.
- Added focused endpoint tests for invalid JSON, non-object bodies, request validation errors, unknown routes, unknown models, provider configuration errors, and upstream provider errors.

## Genesis-0.0.12 - 2026-07-05

- Added Sprint 12 requirements and ADR-0010 for the gateway request validation boundary.
- Moved chat-completion request validation into an internal request module while preserving provider payload forwarding.
- Added focused request validation tests and updated gateway documentation.

## Genesis-0.0.11 - 2026-07-04

- Added Sprint 11 requirements and ADR-0009 for offline gateway provider contract tests.
- Added provider contract tests for mock and OpenRouter adapters without live network or credential requirements.
- Updated gateway documentation to explain provider contract validation and the deferred provider package extraction path.

## Genesis-0.0.10 - 2026-07-03

- Added Sprint 10 requirements and ADR-0008 for the gateway provider adapter boundary.
- Refactored gateway provider adapters behind explicit internal modules while preserving mock and OpenRouter behavior.
- Added provider boundary tests and updated gateway documentation.

## Genesis-0.0.9 - 2026-07-02

- Added Sprint 9 requirements and DEC-0004 for post-Sprint-8 prototype repository disposition.
- Clarified that `agentforge-gateway` and `agentforge-cli` remain public historical references and are superseded for canonical development by monorepo modules.
- Updated repository docs, roadmap, milestones, and prototype notice guidance.

## Genesis-0.0.8 - 2026-06-29

- Added the canonical `agentforge doctor` CLI command for read-only local AICS context diagnostics.
- Added grouped diagnostic checks, unhealthy-context exit semantics, and next-step guidance.
- Added ADR-0007, Sprint 8 requirements, diagnostics tests, install smoke coverage, and docs.

## Genesis-0.0.7 - 2026-06-29

- Added the canonical `agentforge explain-context` CLI command for read-only AICS project orientation.
- Added validation-informed explanation output with key governance entry points and incomplete-context signals.
- Added ADR-0006, Sprint 7 requirements, explanation tests, install smoke coverage, and docs.

## Genesis-0.0.6 - 2026-06-29

- Added the canonical `agentforge init-context` CLI command for scaffolding a minimal AICS v0.1 project context.
- Added CLI-owned scaffold templates, safe no-overwrite initialization behavior, and ADR-0005.
- Added scaffolding tests, editable-install smoke coverage, and Sprint 6 planning artifacts.

## Genesis-0.0.5 - 2026-06-29

- Added explicit install smoke tests and CI validation for the installable CLI.
- Added editable-install packaging for the canonical `agentforge` CLI command.
- Accepted ADR-0004 for installable CLI packaging and editable-install distribution strategy.
- Added installable CLI requirements for Genesis Sprint 5.

## Genesis-0.0.4 - 2026-06-28

- Added CLI command tests and CI validation.
- Implemented the canonical `agentforge validate-context` CLI MVP.
- Accepted ADR-0003 for canonical CLI architecture and packaging boundaries.
- Added canonical CLI MVP requirements for `agentforge validate-context`.

## Genesis-0.0.3 - 2026-06-28

- Documented the canonical CLI path for AICS validation.
- Added a minimal AICS example project context tree.
- Added AICS v0.1 validation rules and local validator.
- Added draft AICS v0.1 specification.

## Genesis-0.0.2 - 2026-06-28

- Migrated the gateway MVP into `apps/gateway`.
- Added gateway tests, examples, docs, and CI validation.
- Documented disposition for pre-governance prototype repositories.
- Added Genesis Sprint 2 gateway reconciliation requirements.
- Added ADR-0002 for gateway module placement and provider adapter boundaries.

## Genesis-0.0.1 - 2026-06-28

- Initialized the canonical AgentForge monorepo.
- Added the `.agentforge/` project brain.
- Recorded ADR-0001 for the modular monorepo strategy.
- Added AI assistant context files and bootstrap validation.
