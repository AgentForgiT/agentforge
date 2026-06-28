# AgentForge Gateway

OpenAI-compatible local gateway for AgentForge.

This module was migrated from the pre-governance `agentforge-gateway` prototype as part of Genesis Sprint 2.

## Status

- Module: `apps/gateway`
- Status: Genesis MVP
- Related requirements: `.agentforge/requirements/gateway-reconciliation.md`
- Related ADR: `.agentforge/adrs/0002-gateway-module-placement.md`

## Features

- dependency-free Python stdlib HTTP service
- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- deterministic mock provider
- optional OpenRouter provider adapter
- JSON configuration
- offline unit and endpoint tests

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
