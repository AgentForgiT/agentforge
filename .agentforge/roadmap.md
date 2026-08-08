# AgentForge Roadmap

Metadata:

- Status: Accepted
- Phase: Stable (post-1.0.0)
- Last updated: 2026-08-08

## Genesis Sprint 1: Bootstrap Kit

Goal: create the canonical AI-native project skeleton.

Deliverables:

- Constitution and charter
- Decision register
- ADR and RFC templates
- AI assistant context files
- repository architecture
- contribution and security docs
- GitHub templates and starter validation workflow

## Genesis Sprint 2: Gateway Reconciliation

Goal: migrate the useful gateway prototype into the canonical monorepo without losing history context or governance discipline.

Deliverables:

- gateway module requirements
- gateway architecture doc
- ADR for gateway placement and provider adapter boundaries
- imported local MVP under `apps/gateway`
- tests and examples
- prototype repository disposition decision

## Genesis Sprint 3: Context Specification

Goal: define the first draft of the AgentForge AI Context Specification.

Deliverables:

- AICS draft
- validation rules
- example context tree
- CLI validation proposal

## Genesis Sprint 4: Canonical CLI MVP

Goal: make AICS validation available through the canonical monorepo CLI with governance, tests, documentation, and release coverage.

Deliverables:

- CLI MVP requirements
- ADR for `apps/cli` architecture and packaging boundaries
- source-tree `agentforge validate-context` implementation
- CLI tests and CI validation
- CLI docs and `Genesis-0.0.4` release

## Genesis Sprint 5: Installable CLI

Goal: make the canonical AgentForge CLI installable without abandoning the validated source-tree workflow.

Deliverables:

- installable CLI requirements for issue #16
- packaging and distribution ADR for issue #18
- installed `agentforge` command for issue #15
- install smoke tests and CI validation for issue #17
- installation docs and `Genesis-0.0.5` release for issue #19

## Genesis Sprint 6: Context Scaffolding MVP

Goal: let contributors initialize a validation-ready AICS baseline from the canonical AgentForge CLI without hand-authoring the required governance structure.

Deliverables:

- context scaffolding requirements for issue #20
- scaffolding template and safety decision for issue #21
- `agentforge init-context` MVP for issue #22
- scaffolding tests and CI validation for issue #23
- scaffolding docs and `Genesis-0.0.6` release for issue #24

## Genesis Sprint 7: Context Explanation MVP

Goal: let contributors and AI assistants explain an AICS project context through the canonical CLI without reducing orientation to pass/fail validation output alone.

Deliverables:

- context explanation requirements for issue #25
- explanation output and validation boundary decision for issue #26
- `agentforge explain-context` MVP for issue #29
- explanation tests and CI validation for issue #28
- explanation docs and `Genesis-0.0.7` release for issue #27

## Genesis Sprint 8: Doctor Diagnostics MVP

Goal: let contributors and AI assistants diagnose local AICS project context health through the canonical CLI without adding network, provider, package-manager, or repair behavior during Genesis.

Deliverables:

- doctor diagnostics requirements for issue #30
- diagnostics scope and safety boundary ADR for issue #31
- `agentforge doctor` MVP for issue #33
- diagnostics tests and CI validation for issue #34
- diagnostics docs and `Genesis-0.0.8` release for issue #32

## Genesis Sprint 9: Prototype Repository Notices

Goal: close the post-Sprint-8 prototype disposition loop by clarifying that public pre-governance repositories remain historical references while canonical gateway and CLI development continues in the monorepo.

Deliverables:

- prototype notice requirements for issue #35
- post-Sprint-8 prototype disposition decision for issue #36
- canonical repository documentation updates for issue #37
- README notices in `agentforge-gateway` and `agentforge-cli` for issue #39
- validation and `Genesis-0.0.9` release for issue #38

## Genesis Sprint 10: Gateway Provider Boundary MVP

Goal: make the gateway provider adapter boundary explicit inside `apps/gateway` without prematurely extracting standalone provider packages.

Deliverables:

- provider boundary requirements for issue #40
- internal provider adapter boundary ADR for issue #41
- provider adapter module refactor for issue #42
- provider boundary tests and CI validation for issue #44
- provider boundary docs and `Genesis-0.0.10` release for issue #43

## Genesis Sprint 11: Gateway Provider Contract Tests MVP

Goal: validate gateway provider adapters against an offline chat completion contract before adding more providers or extracting packages.

Deliverables:

- provider contract test requirements for issue #49
- provider contract testing boundary ADR for issue #45
- provider contract test implementation for issue #46
- provider contract CI validation for issue #48
- provider contract docs and `Genesis-0.0.11` release for issue #47

## Genesis Sprint 12: Gateway Request Validation MVP

Goal: separate chat-completion request validation from gateway orchestration while preserving the current OpenAI-compatible endpoint behavior.

Deliverables:

- request validation requirements for issue #50
- request validation boundary ADR for issue #52
- internal request validation module for issue #54
- request validation tests and CI validation for issue #51
- request validation docs and `Genesis-0.0.12` release for issue #53

## Genesis Sprint 13: Gateway Error Contract MVP

Goal: centralize and test the gateway JSON error contract while preserving current endpoint behavior.

Deliverables:

- error contract requirements for issue #57
- error response boundary ADR for issue #59
- error response helper implementation for issue #55
- error contract tests and CI validation for issue #58
- error contract docs and `Genesis-0.0.13` release for issue #56

## Genesis Sprint 14: Gateway Response Normalization MVP

Goal: centralize and test successful gateway chat-completion response normalization while preserving current endpoint behavior.

Deliverables:

- response normalization requirements for issue #60
- response normalization boundary ADR for issue #63
- response normalization helper implementation for issue #61
- response normalization tests and CI validation for issue #64
- response normalization docs and `Genesis-0.0.14` release for issue #62

## Genesis Sprint 15: Product Foundation Hygiene MVP

Goal: formalize product backlog, canonical standards, and repository hygiene files before expanding into heavier feature work.

Deliverables:

- product foundation hygiene requirements for issue #68
- backlog and standards source-of-truth decision for issue #67
- backlog, standards, `.editorconfig`, and `.gitattributes` implementation for issue #65
- product foundation validation for issue #66
- product foundation docs and `Genesis-0.0.15` release for issue #69

## Genesis Sprint 16: Gateway Configuration Validation MVP

Goal: make gateway configuration validation explicit and deterministic before adding heavier operational behavior.

Deliverables:

- configuration validation requirements for issue #73
- configuration validation boundary ADR for issue #70
- configuration validation helper implementation for issue #72
- configuration validation tests and CI validation for issue #71
- configuration validation docs and `Genesis-0.0.16` release for issue #74

## Genesis Sprint 17: Gateway Streaming MVP

Goal: add OpenAI-compatible SSE streaming to the gateway so streaming-first clients can consume responses incrementally, without weakening the established provider, request, response, and error boundaries.

Deliverables:

- gateway streaming requirements for issue #75
- gateway streaming boundary ADR for issue #76
- gateway streaming implementation for issue #77
- streaming tests and CI validation for issue #78
- streaming docs and `Genesis-0.0.17` release for issue #79

## Genesis Sprint 18: Gateway Logging and Observability MVP

Goal: add structured access logging to the gateway so operators can observe request traffic, status, and timing through a configurable, privacy-safe log level, without weakening the established validation and error boundaries.

Deliverables:

- logging and observability requirements for issue #80
- logging boundary decision ADR-0015 for issue #81
- structured access records with method, path, status, and duration
- chat-completion context records with model and stream flag
- `server.log_level` configuration with strict enum validation for issue #82
- logging tests and CI validation for issue #83
- logging docs and `Genesis-0.0.18` release for issue #84

Validation: local bootstrap, AICS, AICS minimal project, CLI tests, install test, gateway tests, and `git diff --check`.

## Genesis Sprint 19: Gateway Reasoning-Model Response Contract

Goal: formalize the reasoning-model response boundary discovered during live OpenRouter verification — `message.content: null` is valid and passes through, reasoning fields are preserved, invalid content types stay rejected, and the behavior is pinned by live-derived fixtures.

Deliverables:

- reasoning-model contract requirements for issue #85
- reasoning boundary decision ADR-0016 for issue #86
- null-content acceptance and reasoning passthrough hardening for issue #87
- reasoning fixtures and CI validation for issue #88
- reasoning contract docs and `Genesis-0.0.19` release for issue #89

Validation: local bootstrap, AICS, AICS minimal project, CLI tests, install test, gateway tests, and `git diff --check`.

## Sprint 47: 1.0.0 Readiness Gate

Goal: ship the stability line — audit all gate boxes with evidence, freeze the API surface, release 1.0.0 (DEC-0009).

Deliverables:

- 1.0.0 readiness requirements for issue #210
- readiness gate decision DEC-0009 for issue #211
- audit evidence (suites, register, docs, distribution, AICS, API surface) for issue #212
- RELEASE-1.0.0.md for issue #213
- 1.0.0 tag + release + publish verification for issue #214

Validation: local bootstrap, AICS, AICS minimal project, CLI tests, install test, gateway tests, SDK tests, benchmark tests, and `git diff --check`.

## Revision History

- 2026-08-01: Added Sprint 47 1.0.0 readiness deliverables.
- 2026-08-01: Added Sprint 46 variance-aware gate deliverables.
- 2026-08-01: Added Sprint 45 MCP content deliverables.
- 2026-08-01: Added Sprint 44 encryption deliverables.
- 2026-08-01: Added Sprint 43 per-benchmark thresholds deliverables.
- 2026-08-01: Added Sprint 42 regression gate deliverables.
- 2026-08-01: Added Sprint 41 benchmark trends deliverables.
- 2026-08-01: Added Sprint 40 twin QA deliverables.
- 2026-08-01: Added Sprint 39 per-user auth deliverables.
- 2026-08-01: Added Sprint 38 benchmark pipeline deliverables.
- 2026-08-01: Added Sprint 37 twin-service deliverables.
- 2026-08-01: Added Sprint 36 community deliverables.
- 2026-08-01: Added Sprint 35 public 0.1.0 scope deliverables.
- 2026-08-01: Added Sprint 33 engineering-twin deliverables.
- 2026-08-01: Added Sprint 31 distribution deliverables.
- 2026-08-01: Added Sprint 30 MCP surface deliverables.
- 2026-08-01: Added Sprint 29 SDK deliverables.
- 2026-08-01: Added Sprint 28 AICS v0.3 tooling deliverables.
- 2026-08-01: Added Sprint 27 gateway auth/rate-limit deliverables.
- 2026-08-01: Added Sprint 26 AICS v0.2 structured metadata deliverables.
- 2026-08-01: Added Sprint 25 anthropic outbound provider deliverables.
- 2026-08-01: Added Sprint 24 thinking/tool-use mapping deliverables.
- 2026-08-01: Added Sprint 23 Anthropic Messages inbound deliverables.
- 2026-08-01: Added Sprint 21 gateway CORS deliverables.
- 2026-08-01: Added Sprint 20 Ollama/local provider deliverables.
- 2026-08-01: Added Sprint 19 gateway reasoning deliverables.
- 2026-07-31: Added Sprint 18 gateway logging deliverables.
- 2026-07-24: Added Sprint 17 gateway streaming deliverables.
- 2026-07-10: Added Sprint 16 gateway configuration validation deliverables.
- 2026-07-06: Added Sprint 15 product foundation hygiene deliverables.
- 2026-07-06: Added Sprint 14 gateway response normalization deliverables.
- 2026-07-05: Added Sprint 13 gateway error contract deliverables.
- 2026-07-05: Added Sprint 12 gateway request validation deliverables.
- 2026-07-04: Added Sprint 11 gateway provider contract test deliverables.
- 2026-07-03: Added Sprint 10 gateway provider boundary deliverables.
- 2026-07-02: Added Sprint 9 prototype repository notice deliverables.
- 2026-06-29: Added Sprint 8 doctor diagnostics deliverables.
- 2026-06-29: Added Sprint 7 context explanation deliverables.
- 2026-06-29: Added Sprint 6 context scaffolding deliverables.
- 2026-06-28: Added Sprint 4 and Sprint 5 CLI deliverables.
- 2026-06-28: Added AICS v0.1 draft.
- 2026-06-28: Added gateway reconciliation requirements and ADR deliverables.
- 2026-06-28: Initial roadmap draft.
