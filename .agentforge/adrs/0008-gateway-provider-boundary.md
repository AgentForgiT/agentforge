# ADR-0008: Harden Gateway Provider Adapters Behind an Internal Module Boundary

Metadata:

- Status: Accepted
- Date: 2026-07-03
- Deciders: AgentForge maintainers
- Related issues: #40, #41, #42, #44, #43
- Related decisions: ADR-0001, ADR-0002
- Related requirements: `.agentforge/requirements/gateway-provider-boundary-mvp.md`

## Context

ADR-0002 placed the gateway in `apps/gateway` and identified `packages/providers` as a long-term target after the provider boundary becomes stable enough to extract.

The Genesis gateway MVP now has:

- an OpenAI-compatible local HTTP surface
- deterministic mock provider support
- optional OpenRouter provider support
- JSON configuration
- offline tests

Provider behavior currently works, but the protocol, factory, mock adapter, OpenRouter adapter, HTTP error mapping, and helper functions live in one `providers.py` module.

That shape is acceptable for the first MVP, but it will become harder to maintain as additional providers or provider-specific behavior are added.

Sprint 10 needs a boundary improvement that reduces coupling without prematurely extracting standalone packages.

## Decision

Keep provider adapters inside `apps/gateway` during Genesis Sprint 10.

Replace the single mixed-purpose provider module with an internal provider package under `agentforge_gateway/providers/`.

The internal package will define:

- provider protocol in `base.py`
- provider factory in `factory.py`
- deterministic mock provider in `mock.py`
- OpenRouter provider in `openrouter.py`
- public re-exports in `providers/__init__.py`

The gateway app will depend on the provider protocol and factory, not directly on concrete adapter classes.

The long-term `packages/providers` extraction remains deferred until maturity, ownership, release cadence, or governance justify it.

## Boundary Rules

Provider adapter modules own:

- provider-specific payload mapping
- provider-specific credentials lookup
- provider-specific upstream error translation
- provider-specific response normalization

Gateway routing owns:

- HTTP paths
- request body parsing
- OpenAI-compatible request validation
- model registry lookup
- calling the selected provider adapter

Configuration owns:

- provider names
- provider types
- model aliases
- provider model identifiers
- base URL, timeout, headers, and API key environment variable settings

## Compatibility

Sprint 10 must preserve existing behavior for:

- mock provider chat completions
- OpenRouter payload forwarding
- OpenRouter API key environment handling
- existing config examples
- gateway HTTP endpoints
- offline CI tests

The refactor may update internal imports, but it must not require users to change runtime configuration.

## Consequences

Benefits:

- makes provider responsibilities easier to find and review
- gives future provider adapters a clear home
- keeps gateway routing free of provider-specific details
- supports future extraction without doing it too early
- stays compatible with ADR-0001 and ADR-0002

Trade-offs:

- adds a few more files during Genesis
- keeps provider adapters inside the gateway app a little longer
- does not yet provide a shared provider package for other future apps

## Alternatives Considered

Keep all provider code in one module:
Rejected because the file is already mixing protocol, factory, adapter, upstream HTTP, and helper responsibilities.

Extract `packages/providers` immediately:
Rejected because ADR-0002 explicitly deferred extraction until the boundary is proven. Sprint 10 needs a smaller internal hardening step.

Add a plugin system now:
Rejected because the current provider set does not justify plugin loading, discovery, or third-party extension contracts.

Move provider selection into configuration parsing:
Rejected because config parsing should validate data, while provider construction belongs at the runtime boundary.

## Follow-Up Work

- Add future provider adapters only through the internal provider package.
- Revisit `packages/providers` after multiple adapters or consumers exist.
- Consider provider contract tests before adding live provider integrations.
- Keep CI offline by default.

## Revision History

- 2026-07-03: Accepted for Genesis Sprint 10.
