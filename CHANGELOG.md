# Changelog

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
