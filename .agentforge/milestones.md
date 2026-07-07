# AgentForge Milestones

Metadata:

- Status: Draft
- Phase: Genesis
- Last updated: 2026-07-06

## Genesis-0.0.1: Bootstrap Kit

Scope:

- governance baseline
- AI context baseline
- repository structure
- starter templates
- validation workflow placeholder

Exit criteria:

- canonical `agentforge` repository exists
- `.agentforge/` project brain exists
- ADR-0001 records the monorepo decision
- AI assistant context files exist
- CI validates required bootstrap files

## Genesis-0.0.2: Gateway Reconciliation

Scope:

- import or recreate gateway prototype under governance
- document provider adapter boundaries
- preserve OpenAI-compatible API shape
- keep tests deterministic
- decide prototype repository disposition

Exit criteria:

- requirements document exists
- gateway placement ADR is accepted
- gateway MVP is migrated into `apps/gateway`
- gateway tests run in CI
- prototype repository status is documented
- prototype repositories remain public unless a later accepted decision changes their status

## Genesis-0.0.3: AICS Draft

Scope:

- draft AICS v0.1
- define validation rules
- add an example AICS context tree
- plan CLI validation path

Exit criteria:

- AICS v0.1 spec exists
- validation rules are documented
- example context tree exists
- CLI path decision exists

## Genesis-0.0.4: Canonical CLI MVP

Scope:

- define canonical CLI MVP requirements
- decide `apps/cli` architecture and packaging boundaries
- implement `agentforge validate-context`
- add CLI tests and CI validation
- document CLI usage and release limitations

Exit criteria:

- requirements document exists
- ADR-0003 is accepted and linked from the decision register
- `apps/cli` contains the source-tree CLI MVP
- CLI validates the canonical repo and minimal AICS example
- CLI tests run locally and in CI
- docs explain how to run the CLI against the repo and minimal example

## Genesis-0.0.5: Installable CLI

Scope:

- define installable CLI requirements
- decide CLI packaging and distribution strategy
- implement an installable `agentforge` command
- add install smoke tests and CI validation
- document installation and release limitations

Exit criteria:

- requirements document exists for issue #16
- packaging ADR or decision exists for issue #18
- a documented local install exposes `agentforge validate-context`
- installed CLI validates the canonical repo and minimal AICS example
- install smoke tests run locally and in CI for issue #17
- docs explain how to install and run the CLI for issue #19

## Genesis-0.0.6: Context Scaffolding MVP

Scope:

- define context scaffolding requirements
- decide scaffold template and safety strategy
- implement `agentforge init-context`
- add scaffolding tests and CI validation
- document the scaffolding workflow and release limitations

Exit criteria:

- requirements document exists for issue #20
- a scaffolding ADR or durable decision exists for issue #21
- `agentforge init-context` can scaffold a validation-ready AICS baseline for issue #22
- automated tests and CI validate generated scaffold output for issue #23
- docs explain how to initialize and validate a new project for issue #24

## Genesis-0.0.7: Context Explanation MVP

Scope:

- define context explanation requirements
- decide explanation output and validation boundary
- implement `agentforge explain-context`
- add explanation tests and CI validation
- document the explanation workflow and release limitations

Exit criteria:

- requirements document exists for issue #25
- an explanation ADR or durable decision exists for issue #26
- `agentforge explain-context` can explain the canonical repo and a minimal/scaffolded AICS project for issue #29
- automated tests and CI validate explanation output behavior for issue #28
- docs explain how to explain and validate a project context for issue #27

## Genesis-0.0.8: Doctor Diagnostics MVP

Scope:

- define doctor diagnostics requirements
- decide read-only local diagnostics scope and safety boundary
- implement `agentforge doctor`
- add diagnostics tests and CI validation
- document the diagnostics workflow and release limitations

Exit criteria:

- requirements document exists for issue #30
- diagnostics ADR or durable decision exists for issue #31
- `agentforge doctor` can diagnose the canonical repo and a minimal/scaffolded AICS project for issue #33
- automated tests and CI validate diagnostics output behavior for issue #34
- docs explain how diagnostics differs from validation and explanation for issue #32

## Genesis-0.0.9: Prototype Repository Notices

Scope:

- define prototype repository notice requirements
- decide post-Sprint-8 prototype disposition
- update canonical repository docs
- refine public prototype README notices
- validate and release the disposition update

Exit criteria:

- requirements document exists for issue #35
- DEC-0004 records post-Sprint-8 prototype disposition for issue #36
- canonical docs identify prototype repositories as public historical references for issue #37
- `agentforge-gateway` and `agentforge-cli` README notices point to canonical modules for issue #39
- validation passes and release notes document `Genesis-0.0.9` for issue #38

## Genesis-0.0.10: Gateway Provider Boundary MVP

Scope:

- define gateway provider boundary requirements
- decide internal provider adapter module boundary
- refactor provider adapters into explicit internal modules
- add provider boundary tests and CI validation
- document the boundary and release limitations

Exit criteria:

- requirements document exists for issue #40
- ADR-0008 records the internal provider boundary for issue #41
- provider adapters live behind explicit internal modules for issue #42
- automated tests and CI validate provider factory and adapter behavior for issue #44
- docs explain why `packages/providers` extraction remains deferred for issue #43

## Genesis-0.0.11: Gateway Provider Contract Tests MVP

Scope:

- define gateway provider contract test requirements
- decide provider contract testing boundary
- add offline contract tests for current providers
- validate provider contracts in local tests and CI
- document the contract and release limitations

Exit criteria:

- requirements document exists for issue #49
- ADR-0009 records the offline provider contract test boundary for issue #45
- mock and OpenRouter adapters have offline contract coverage for issue #46
- validation passes locally and in CI for issue #48
- docs explain provider contracts and release notes document `Genesis-0.0.11` for issue #47

## Genesis-0.0.12: Gateway Request Validation MVP

Scope:

- define gateway request validation requirements
- decide chat-completion request validation boundary
- add an internal request validation module
- add focused request validation tests
- document the request validation boundary and release limitations

Exit criteria:

- requirements document exists for issue #50
- ADR-0010 records the request validation boundary for issue #52
- request validation lives outside gateway orchestration for issue #54
- validation passes locally and in CI for issue #51
- docs explain request validation and release notes document `Genesis-0.0.12` for issue #53

## Genesis-0.0.13: Gateway Error Contract MVP

Scope:

- define gateway error contract requirements
- decide JSON error response boundary
- centralize gateway error response helpers
- add focused error contract tests
- document the error contract and release limitations

Exit criteria:

- requirements document exists for issue #57
- ADR-0011 records the error response boundary for issue #59
- standard error helpers are used by HTTP handling for issue #55
- validation passes locally and in CI for issue #58
- docs explain the error contract and release notes document `Genesis-0.0.13` for issue #56

## Genesis-0.0.14: Gateway Response Normalization MVP

Scope:

- define gateway response normalization requirements
- decide the chat-completion response normalization boundary
- centralize successful response normalization helpers
- add focused response normalization tests
- document the response normalization boundary and release limitations

Exit criteria:

- requirements document exists for issue #60
- ADR-0012 records the response normalization boundary for issue #63
- successful chat-completion responses pass through a gateway-owned normalizer for issue #61
- validation passes locally and in CI for issue #64
- docs explain response normalization and release notes document `Genesis-0.0.14` for issue #62

## Genesis-0.0.15: Product Foundation Hygiene MVP

Scope:

- define product foundation hygiene requirements
- decide backlog and standards source-of-truth rules
- add product backlog and canonical standards files
- add repository hygiene files for editor and Git behavior
- validate required product foundation artifacts

Exit criteria:

- requirements document exists for issue #68
- DEC-0005 records backlog, standards, and repository hygiene ownership for issue #67
- `.agentforge/backlog.md`, `.agentforge/standards/`, `.editorconfig`, and `.gitattributes` exist for issue #65
- validation passes locally and in CI for issue #66
- docs explain product foundation hygiene and release notes document `Genesis-0.0.15` for issue #69

## Revision History

- 2026-07-06: Added Genesis-0.0.15 product foundation hygiene milestone.
- 2026-07-06: Added Genesis-0.0.14 gateway response normalization milestone.
- 2026-07-05: Added Genesis-0.0.13 gateway error contract milestone.
- 2026-07-05: Added Genesis-0.0.12 gateway request validation milestone.
- 2026-07-04: Added Genesis-0.0.11 gateway provider contract tests milestone.
- 2026-07-03: Added Genesis-0.0.10 gateway provider boundary milestone.
- 2026-07-02: Added Genesis-0.0.9 prototype repository notices milestone.
- 2026-06-29: Added Genesis-0.0.8 doctor diagnostics milestone.
- 2026-06-29: Added Genesis-0.0.7 context explanation milestone.
- 2026-06-29: Added Genesis-0.0.6 context scaffolding milestone.
- 2026-06-29: Confirmed installable CLI smoke-test coverage for Genesis-0.0.5.
- 2026-06-28: Added Genesis-0.0.5 installable CLI milestone.
- 2026-06-28: Added Genesis-0.0.4 canonical CLI MVP milestone.
- 2026-06-28: Added CLI path decision for AICS validation.
- 2026-06-28: Added Genesis-0.0.3 AICS milestone.
- 2026-06-28: Added prototype repository disposition.
- 2026-06-28: Expanded Genesis-0.0.2 exit criteria.
- 2026-06-28: Initial draft.
