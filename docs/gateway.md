# Gateway

Metadata:

- Status: Genesis MVP
- Module: `apps/gateway`
- Related requirements: `.agentforge/requirements/gateway-reconciliation.md`
- Related ADRs: `.agentforge/adrs/0002-gateway-module-placement.md`, `.agentforge/adrs/0008-gateway-provider-boundary.md`
- Last updated: 2026-07-03

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

## Risks

- Provider adapters are still inside `apps/gateway`; ADR-0002 and ADR-0008 identify `packages/providers` as a later extraction target.
- Streaming is explicitly unsupported in the Genesis MVP.
- OpenRouter live testing is optional and must not be required in default CI.

## Revision History

- 2026-07-03: Documented internal provider adapter boundary from ADR-0008.
- 2026-07-02: Clarified post-Sprint-8 prototype repository disposition.
- 2026-06-28: Initial migrated gateway documentation.
