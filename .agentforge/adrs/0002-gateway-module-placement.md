# ADR-0002: Place Gateway in `apps/gateway` with Provider Adapter Boundary

Metadata:

- Status: Accepted
- Date: 2026-06-28
- Deciders: AgentForge maintainers
- Related issues: #1, #2, #3, #4
- Related decisions: ADR-0001, DEC-0001

## Context

The `agentforge-gateway` prototype contains a useful local MVP and an optional OpenRouter adapter, but ADR-0001 establishes `agentforge` as the canonical modular monorepo.

AgentForge needs a clear place for the gateway application and a clear boundary for provider-specific behavior.

## Decision

Gateway application code will live under `apps/gateway`.

Provider-specific behavior should be isolated behind an adapter boundary. The long-term target is `packages/providers`, but migration may temporarily keep provider adapters inside `apps/gateway` until the boundary is stable enough to extract without ceremony.

The gateway must preserve an OpenAI-compatible API surface where practical and must keep provider credentials in environment variables.

## Consequences

Benefits:

- keeps the gateway as a first-class application in the canonical monorepo
- preserves monorepo simplicity during Genesis
- makes provider-specific logic replaceable
- avoids committing too early to standalone provider packages
- gives the prototype repository a clear migration path

Trade-offs:

- initial migration may duplicate some prototype history instead of preserving exact git history
- provider adapter extraction becomes a future cleanup task
- the application boundary must be watched carefully to avoid tight coupling

## Alternatives Considered

Keep `agentforge-gateway` as canonical:
Rejected because it contradicts ADR-0001 and increases early repository fragmentation.

Move gateway directly to `packages/gateway`:
Rejected because the gateway is a runnable application, not only a reusable package.

Create standalone `packages/providers` immediately:
Deferred because premature package splitting may add ceremony before the boundary is proven.

## Follow-Up Work

- Migrate the gateway MVP into `apps/gateway`.
- Add gateway tests and CI validation.
- Document the prototype lineage.
- Decide the disposition of `agentforge-gateway` after migration.

## Revision History

- 2026-06-28: Accepted for Genesis Sprint 2.
