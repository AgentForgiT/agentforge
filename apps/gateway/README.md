# AgentForge Gateway

OpenAI-compatible local gateway for AgentForge.

This module was migrated from the pre-governance `agentforge-gateway` prototype as part of Genesis Sprint 2.

## Status

- Module: `apps/gateway`
- Status: Genesis MVP
- Related requirements: `.agentforge/requirements/gateway-reconciliation.md`
- Related ADRs: `.agentforge/adrs/0002-gateway-module-placement.md`, `.agentforge/adrs/0008-gateway-provider-boundary.md`, `.agentforge/adrs/0009-gateway-provider-contract-testing.md`

## Features

- dependency-free Python stdlib HTTP service
- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- deterministic mock provider
- optional OpenRouter provider adapter
- explicit internal provider adapter boundary
- offline provider contract tests
- JSON configuration
- offline unit and endpoint tests

## Provider Boundary

Provider adapter code lives under `agentforge_gateway.providers`.

The Genesis boundary keeps adapters inside `apps/gateway` while separating:

- provider protocol and factory
- deterministic mock adapter
- OpenRouter adapter

`packages/providers` extraction remains deferred until the boundary is proven by more provider maturity or reuse.

## Provider Contract Tests

Provider contract tests live under `apps/gateway/tests`.

They verify the minimal chat completion response shape expected from gateway providers while keeping default validation offline and credential-free.

Current contract coverage includes:

- deterministic mock provider response shape and usage reporting
- OpenRouter payload mapping through injected transport
- public model alias normalization
- upstream HTTP error translation

## Run Tests

From the repository root:

```bash
python -m unittest discover -s apps/gateway/tests
```

## Run Locally

```bash
PYTHONPATH=apps/gateway/src python -m agentforge_gateway.cli --config apps/gateway/config.example.json
```

Windows PowerShell:

```powershell
$env:PYTHONPATH = "apps/gateway/src"
python -m agentforge_gateway.cli --config apps/gateway/config.example.json
```

## OpenRouter

OpenRouter is optional. The default config requires no external provider key.

```bash
OPENROUTER_API_KEY=... PYTHONPATH=apps/gateway/src python -m agentforge_gateway.cli --config apps/gateway/config.openrouter.example.json
```

Provider keys must stay in environment variables and must not be committed.
