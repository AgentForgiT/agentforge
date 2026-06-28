# Gateway Reconciliation Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 2
- Related issues: #4, #1, #2, #3, #5
- Related decisions: ADR-0001, DEC-0001, ADR-0002
- Last updated: 2026-06-28

## Purpose

Define the requirements for moving useful gateway work from the pre-governance `agentforge-gateway` prototype into the canonical `agentforge` monorepo.

This document exists so gateway implementation does not continue ahead of governance.

## Scope

In scope:

- inventory the current gateway prototype
- define what should migrate into `apps/gateway`
- define provider adapter boundaries
- define configuration and key-management expectations
- define tests, examples, and validation expectations
- preserve prototype lineage without making the prototype repository canonical

Out of scope:

- deleting or archiving prototype repositories
- adding new model provider features during migration
- adding streaming responses
- adding production authentication and rate limiting
- adopting a full workspace/package manager before a separate ADR

## Background

The `agentforge-gateway` repository was created before AgentForge accepted the modular monorepo strategy. It contains useful work:

- dependency-free Python stdlib HTTP gateway
- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- JSON config loading
- in-memory model registry
- deterministic mock provider
- OpenRouter provider adapter
- OpenAI-compatible response shape
- unit and endpoint tests
- GitHub Actions CI
- release `v0.1.0-alpha`

ADR-0001 makes `agentforge` the canonical engineering monorepo. DEC-0001 classifies `agentforge-gateway` as a pre-governance prototype that should be preserved while useful work is migrated.

## Functional Requirements

Gateway reconciliation must preserve these capabilities:

- expose `/health`
- expose `/v1/models`
- expose `/v1/chat/completions`
- support a deterministic mock provider for offline testing
- support OpenRouter as an optional provider adapter
- keep an OpenAI-compatible request and response shape where practical
- reject unsupported streaming requests clearly
- return predictable JSON error envelopes
- load model and provider configuration from JSON during Genesis
- keep provider API keys in environment variables

## Non-Functional Requirements

The migrated gateway must:

- run locally without external provider keys using the mock provider
- use no required third-party runtime dependencies during Genesis Sprint 2 unless a new ADR approves them
- keep tests deterministic and offline by default
- preserve clear provider adapter boundaries
- avoid provider lock-in
- avoid logging secrets
- keep docs and examples aligned with actual behavior
- integrate with monorepo validation

## Proposed Module Placement

- `apps/gateway`: runnable gateway application, CLI entry point, HTTP handling, local config examples
- `packages/providers`: provider interfaces and provider adapters once boundaries are stable
- `tests/gateway`: gateway tests if cross-module test organization is needed
- `examples/gateway`: curl examples and local usage examples

During the first migration commit, provider code may remain inside `apps/gateway` if extracting it immediately adds avoidable complexity. ADR-0002 defines the target boundary.

## Migration Requirements

Migration should happen in this order:

1. Add requirements and ADR coverage.
2. Create `apps/gateway` structure.
3. Bring in the mock-provider MVP.
4. Bring in the OpenRouter adapter with offline tests.
5. Add gateway-specific validation to CI.
6. Update docs, examples, and changelog.
7. Decide prototype repo disposition separately.

## Acceptance Criteria

Issue #4 is complete when:

- this requirements document exists
- it references ADR-0001 and DEC-0001
- it identifies current prototype capabilities
- it defines what migrates into `apps/gateway`
- it defines non-goals and acceptance criteria

Gateway migration is complete when:

- `apps/gateway` contains the migrated MVP
- local tests pass without provider keys
- bootstrap validation still passes
- CI runs gateway tests
- docs explain prototype lineage
- no hidden secrets are required

## Risks

- Migrating too much at once could obscure architectural decisions.
- Keeping provider code in the application too long could blur boundaries.
- Splitting provider packages too early could create ceremony before need.
- Prototype repos may confuse contributors if not clearly labeled.

## References

- `.agentforge/adrs/0001-modular-monorepo.md`
- `.agentforge/decisions/0001-pre-governance-prototypes.md`
- `.agentforge/adrs/0002-gateway-module-placement.md`
- `https://github.com/AgentForgiT/agentforge-gateway`

## Revision History

- 2026-06-28: Initial draft for Genesis Sprint 2.
