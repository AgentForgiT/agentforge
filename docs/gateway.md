# Gateway

Metadata:

- Status: Genesis MVP
- Module: `apps/gateway`
- Related requirements: `.agentforge/requirements/gateway-reconciliation.md`
- Related ADR: `.agentforge/adrs/0002-gateway-module-placement.md`
- Last updated: 2026-06-28

## Purpose

The AgentForge Gateway provides an OpenAI-compatible local entry point for model providers and future AgentForge services.

## Scope

The Genesis MVP includes:

- `/health`
- `/v1/models`
- `/v1/chat/completions`
- deterministic mock provider
- optional OpenRouter provider
- JSON configuration
- offline tests

## Prototype Lineage

This module was migrated from the pre-governance `agentforge-gateway` repository. That repository remains a prototype until AgentForge decides its final disposition.

## Local Validation

```bash
python -m unittest discover -s apps/gateway/tests
python scripts/validate_bootstrap.py
```

## Configuration

The default config at `apps/gateway/config.example.json` uses only the mock provider and requires no secrets.

The OpenRouter example at `apps/gateway/config.openrouter.example.json` uses `OPENROUTER_API_KEY` from the environment.

## Risks

- Provider adapters are still inside `apps/gateway`; ADR-0002 identifies `packages/providers` as the long-term boundary.
- Streaming is explicitly unsupported in the Genesis MVP.
- OpenRouter live testing is optional and must not be required in default CI.

## Revision History

- 2026-06-28: Initial migrated gateway documentation.
