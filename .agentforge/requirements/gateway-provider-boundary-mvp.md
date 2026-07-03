# Gateway Provider Boundary MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 10
- Related issues: #40, #41, #42, #44, #43
- Related decisions: ADR-0001, ADR-0002, ADR-0008
- Related policy: `docs/release-policy.md`
- Last updated: 2026-07-03

## Purpose

Define the requirements for hardening the AgentForge Gateway provider adapter boundary without prematurely extracting standalone provider packages during Genesis.

This document exists so Sprint 10 improves maintainability of provider integrations while preserving the monorepo-first architecture from ADR-0001 and the gateway placement decision from ADR-0002.

## Scope

In scope:

- internal provider adapter module boundaries inside `apps/gateway`
- provider protocol and factory behavior
- mock provider adapter preservation
- OpenRouter provider adapter preservation
- offline tests for provider boundary behavior
- documentation of the current boundary and future extraction path
- Sprint 10 traceability across implementation, tests, documentation, and release work

Out of scope:

- extracting `packages/providers`
- adding new live provider integrations
- changing the OpenAI-compatible HTTP API surface
- changing configuration file format
- adding streaming support
- requiring live provider credentials in CI
- introducing non-standard-library runtime dependencies
- publishing gateway packages

## Background

ADR-0002 placed the gateway in `apps/gateway` and identified `packages/providers` as a long-term target once the provider boundary is stable enough to extract.

The current Genesis MVP includes a deterministic mock provider and an optional OpenRouter provider. Provider behavior currently works, but the protocol, factory, mock adapter, OpenRouter adapter, HTTP mapping, and helper functions live in one module.

Sprint 10 should make the provider boundary explicit inside `apps/gateway` first. That gives the project a better extension point without creating package ceremony before usage justifies it.

## User Workflows

The MVP must support these workflows:

- A contributor can locate the provider protocol and factory quickly.
- A contributor can inspect mock and OpenRouter adapters separately.
- A maintainer can add future provider adapters without editing unrelated adapter implementations.
- CI can validate provider behavior without network access or provider credentials.
- Gateway users can continue using existing mock and OpenRouter configuration files unchanged.

## Boundary Requirements

The gateway must expose a stable internal provider boundary inside `apps/gateway`.

The provider boundary must include:

- a `ChatProvider` protocol
- a provider factory
- one module for the deterministic mock adapter
- one module for the OpenRouter adapter
- shared provider helper behavior only where it reduces duplication

The gateway application must depend on the provider protocol and factory, not on concrete adapter classes directly.

Provider-specific behavior must stay isolated from request routing and HTTP handler code.

## Compatibility Requirements

Sprint 10 must preserve:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- current mock provider behavior
- current OpenRouter request payload mapping
- current OpenRouter API key environment behavior
- current config examples
- default offline test behavior

Existing imports used by tests may be updated to the new boundary, but runtime behavior must not change.

## Testing and CI Requirements

Tests must cover:

- provider factory selection for `mock`
- provider factory selection for `openrouter`
- unsupported provider type errors
- mock provider deterministic response shape
- OpenRouter payload mapping and model alias preservation
- OpenRouter missing API key behavior
- regression coverage for existing gateway endpoints

CI must not require network access, provider credentials, or live upstream providers.

## Documentation Requirements

Documentation must explain:

- the internal provider boundary inside `apps/gateway`
- why `packages/providers` extraction remains deferred
- how provider adapters relate to gateway routing
- how to run offline validation
- current Sprint 10 limitations

## Acceptance Criteria

Issue #40 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references ADR-0002 and ADR-0008
- it defines the Sprint 10 provider boundary scope before implementation begins

The Sprint 10 provider boundary milestone is complete when:

- issue #41 records ADR-0008
- issue #42 implements internal provider adapter modules
- issue #44 adds provider boundary tests and CI validation
- issue #43 documents the provider boundary and prepares `Genesis-0.0.10`

## Examples

Expected internal shape:

```text
agentforge_gateway/providers/
  __init__.py
  base.py
  factory.py
  mock.py
  openrouter.py
```

Gateway app dependency direction:

```text
app -> providers.factory -> concrete adapters
```

## Best Practices

- Keep provider-specific behavior out of HTTP routing.
- Keep default tests offline and deterministic.
- Preserve existing configuration compatibility.
- Extract packages only when maturity and release cadence justify it.
- Prefer explicit modules over a growing mixed-purpose file.

## Risks

- Moving code can create import churn without user-visible value if the boundary is not documented.
- Extracting too far too early would contradict ADR-0002's staged approach.
- Provider factories can become opaque if they hide too much configuration behavior.
- Live provider testing could make CI flaky if it becomes required.

## References

- `.agentforge/adrs/0001-modular-monorepo.md`
- `.agentforge/adrs/0002-gateway-module-placement.md`
- `.agentforge/adrs/0008-gateway-provider-boundary.md`
- `.agentforge/requirements/gateway-reconciliation.md`
- `apps/gateway/README.md`
- `docs/gateway.md`

## Revision History

- 2026-07-03: Initial requirements draft for Genesis Sprint 10.
