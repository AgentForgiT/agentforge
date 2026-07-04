# ADR-0009: Validate Gateway Providers Through Offline Contract Tests

Metadata:

- Status: Accepted
- Date: 2026-07-04
- Deciders: AgentForge maintainers
- Related issues: #49, #45, #46, #48, #47
- Related decisions: ADR-0001, ADR-0002, ADR-0008
- Related requirements: `.agentforge/requirements/gateway-provider-contract-tests-mvp.md`

## Context

ADR-0008 hardened the gateway provider adapter boundary by replacing one mixed-purpose provider module with an internal package under `agentforge_gateway.providers`.

The gateway now has clear internal homes for:

- provider protocol
- provider factory
- deterministic mock provider
- OpenRouter provider

The next risk is provider contract drift. Future adapters can accidentally return inconsistent response shapes, skip public model alias normalization, or require live credentials in tests.

Genesis needs a contract test boundary before adding more providers or extracting provider packages.

## Decision

Add offline provider contract tests inside `apps/gateway/tests` during Genesis Sprint 11.

The tests will define reusable assertions for the minimal chat completion response contract expected from gateway providers.

The contract test boundary will cover:

- OpenAI-compatible `chat.completion` response marker
- public gateway model alias in provider responses
- non-empty choices
- assistant message role and string content
- finish reason on choices

Adapter-specific tests may add checks for mock usage reporting, OpenRouter payload mapping, OpenRouter upstream model forwarding, injected transport behavior, and upstream error translation.

Provider contract tests must use local fakes or injected transports. They must not call live providers, require credentials, or add runtime dependencies.

## Boundary Rules

Provider contract tests own:

- shared response-shape assertions
- adapter conformance checks
- offline fake upstream behavior
- provider-level error translation checks

Gateway endpoint tests own:

- HTTP routing behavior
- request parsing
- endpoint status codes
- JSON response delivery

Configuration tests own:

- config parsing
- provider references
- model aliases
- provider-specific settings

## Compatibility

Sprint 11 must preserve existing behavior for:

- gateway HTTP endpoints
- deterministic mock provider responses
- OpenRouter request payload mapping
- OpenRouter API key environment handling
- existing configuration examples
- offline CI validation

The tests may introduce shared test helpers, but no runtime configuration changes are required.

## Consequences

Benefits:

- gives future providers a clear conformance pattern
- reduces duplicate response-shape assertions across adapter tests
- strengthens ADR-0008 without extracting packages too early
- keeps default CI offline and reproducible
- makes provider behavior easier to review

Trade-offs:

- adds test code before adding new provider features
- defines only a minimal contract during Genesis
- keeps provider contract tests inside `apps/gateway` until extraction is justified

## Alternatives Considered

Wait for a third provider before adding contract tests:
Rejected because ADR-0008 created the boundary now, and contract tests are a low-cost way to keep that boundary honest.

Use live provider smoke tests:
Rejected because default CI must remain offline, deterministic, and credential-free during Genesis.

Extract provider tests into `packages/providers` immediately:
Rejected because ADR-0008 keeps provider adapters inside `apps/gateway` until maturity, ownership, release cadence, or reuse justify extraction.

Define a full provider certification suite:
Rejected because the Genesis provider set is too small for a broad certification framework.

## Follow-Up Work

- Apply the contract pattern to future provider adapters.
- Revisit the contract when streaming support is introduced.
- Consider moving provider contract tests with adapters if `packages/providers` is later extracted.
- Keep live provider checks optional and separate from default CI.

## Revision History

- 2026-07-04: Accepted for Genesis Sprint 11.
