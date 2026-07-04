# Gateway

Metadata:

- Status: Genesis MVP
- Module: `apps/gateway`
- Related requirements: `.agentforge/requirements/gateway-reconciliation.md`
- Related ADRs: `.agentforge/adrs/0002-gateway-module-placement.md`, `.agentforge/adrs/0008-gateway-provider-boundary.md`, `.agentforge/adrs/0009-gateway-provider-contract-testing.md`, `.agentforge/adrs/0010-gateway-request-validation-boundary.md`
- Last updated: 2026-07-05

## Purpose

The AgentForge Gateway provides an OpenAI-compatible local entry point for model providers and future AgentForge services.

## Scope

The Genesis MVP includes:

- `/health`
- `/v1/models`
- `/v1/chat/completions`
- deterministic mock provider
- optional OpenRouter provider
- internal provider adapter boundary
- offline provider contract tests
- internal request validation boundary
- JSON configuration
- offline tests

## Prototype Lineage

This module was migrated from the pre-governance `agentforge-gateway` repository.

DEC-0004 keeps that repository public as a historical reference, but canonical gateway development now belongs in `AgentForgiT/agentforge` under `apps/gateway`.

## Local Validation

```bash
python -m unittest discover -s apps/gateway/tests
python scripts/validate_bootstrap.py
```

## Configuration

The default config at `apps/gateway/config.example.json` uses only the mock provider and requires no secrets.

The OpenRouter example at `apps/gateway/config.openrouter.example.json` uses `OPENROUTER_API_KEY` from the environment.

## Provider Boundary

Gateway provider adapters live inside `apps/gateway` during Genesis.

ADR-0008 defines the internal provider package boundary:

- provider protocol and factory are separated from concrete adapters
- deterministic mock behavior lives in its own adapter module
- OpenRouter payload mapping and upstream error handling live in their own adapter module
- gateway routing depends on the provider protocol and factory, not concrete adapters

`packages/providers` remains a long-term extraction target from ADR-0002, but extraction is deferred until provider maturity, ownership, or release cadence justifies it.

## Provider Contract Tests

ADR-0009 defines offline provider contract tests for the Genesis gateway.

The contract tests verify that gateway providers return the minimal OpenAI-compatible chat completion shape expected by the gateway:

- `chat.completion` object marker
- public gateway model alias
- non-empty choices
- assistant message role and string content
- finish reason

The current suite covers the deterministic mock provider and the OpenRouter provider through injected offline transport. Live upstream calls and provider credentials are intentionally excluded from default validation.

## Request Validation

ADR-0010 defines the internal request validation boundary for `/v1/chat/completions`.

Request validation lives in `agentforge_gateway.requests` and validates:

- required `model`
- non-empty `messages`
- unsupported streaming requests
- message `role` and `content` presence

`GatewayApp` remains responsible for model lookup and provider dispatch after validation succeeds. The original request body is preserved so optional provider payload fields continue to pass through to provider adapters.

## Risks

- Provider adapters are still inside `apps/gateway`; ADR-0002 and ADR-0008 identify `packages/providers` as a later extraction target.
- Streaming is explicitly unsupported in the Genesis MVP and requires later design work before implementation.
- OpenRouter live testing is optional and must not be required in default CI.

## Revision History

- 2026-07-05: Documented internal request validation boundary from ADR-0010.
- 2026-07-04: Documented offline provider contract tests from ADR-0009.
- 2026-07-03: Documented internal provider adapter boundary from ADR-0008.
- 2026-07-02: Clarified post-Sprint-8 prototype repository disposition.
- 2026-06-28: Initial migrated gateway documentation.
