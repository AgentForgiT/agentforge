# Gateway Provider Contract Tests MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 11
- Related issues: #49, #45, #46, #48, #47
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0009
- Related policy: `docs/release-policy.md`
- Last updated: 2026-07-04

## Purpose

Define the requirements for an offline provider contract test suite for the AgentForge Gateway.

This document exists so Sprint 11 strengthens the provider adapter boundary from ADR-0008 before AgentForge adds more live providers or extracts standalone provider packages.

## Scope

In scope:

- reusable provider contract assertions for chat completion responses
- deterministic mock provider contract coverage
- OpenRouter provider contract coverage through injected transport
- provider model alias normalization checks
- provider factory compatibility checks where they support the contract
- offline local and CI validation
- documentation of the provider contract test boundary

Out of scope:

- live provider calls
- new provider integrations
- streaming support
- changing the OpenAI-compatible HTTP API surface
- changing gateway configuration format
- extracting `packages/providers`
- adding runtime dependencies
- publishing gateway packages

## Background

ADR-0008 split gateway provider behavior into explicit internal modules under `agentforge_gateway.providers`.

That boundary gives future providers a clear home, but the next maintainability risk is contract drift. Future adapters should conform to a minimal OpenAI-compatible chat completion shape without every adapter test inventing its own expectations.

Sprint 11 should add an offline contract test suite while provider adapters remain inside `apps/gateway`.

## User Workflows

The MVP must support these workflows:

- A contributor can run one gateway test command and verify provider contract conformance.
- A maintainer can add a future provider adapter with a clear contract test pattern.
- CI can validate provider behavior without network access or provider credentials.
- Gateway users can continue using existing mock and OpenRouter configuration files unchanged.
- Documentation can explain what the provider contract guarantees and what it does not yet guarantee.

## Contract Requirements

Provider contract tests must verify that a chat provider response includes:

- an OpenAI-compatible `chat.completion` object marker
- the public gateway model alias as `model`
- at least one choice
- assistant message role and string content
- a finish reason on each returned choice

Provider-specific tests may add checks for:

- deterministic mock response content and usage shape
- OpenRouter upstream payload mapping
- OpenRouter provider model forwarding
- OpenRouter public model alias normalization
- OpenRouter credential lookup behavior
- upstream error translation

## Compatibility Requirements

Sprint 11 must preserve:

- current gateway HTTP endpoints
- current mock provider behavior
- current OpenRouter request payload mapping
- current OpenRouter API key environment behavior
- current configuration examples
- default offline test behavior

The contract tests may add new test helpers, but they must not require runtime users to change configuration.

## Testing and CI Requirements

Tests must cover:

- mock provider conformance to the shared chat completion contract
- OpenRouter provider conformance with injected offline transport
- provider alias normalization for upstream responses
- upstream provider error translation where practical without network calls

CI must continue to require no network access, provider credentials, or live upstream provider availability.

## Documentation Requirements

Documentation must explain:

- the purpose of provider contract tests
- that provider contract tests are offline during Genesis
- how the contract relates to ADR-0008
- why `packages/providers` extraction remains deferred
- how to run the gateway tests locally

## Acceptance Criteria

Issue #49 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references ADR-0008 and ADR-0009
- it defines the Sprint 11 provider contract test scope before implementation begins

The Sprint 11 provider contract milestone is complete when:

- issue #45 records ADR-0009
- issue #46 implements offline provider contract tests
- issue #48 validates provider contracts locally and in CI
- issue #47 documents provider contracts and prepares `Genesis-0.0.11`

## Examples

Expected test focus:

```text
provider -> chat_completion(model, body) -> OpenAI-compatible response shape
```

Expected validation command:

```bash
python -m unittest discover -s apps/gateway/tests
```

## Best Practices

- Keep provider contract tests offline and deterministic.
- Prefer injected transports over live upstream calls.
- Keep adapter-specific assertions close to the adapter behavior they verify.
- Test the public gateway model alias, not only upstream provider model names.
- Add new providers only after contract coverage is clear.

## Risks

- A contract that is too broad can freeze implementation details too early.
- A contract that is too narrow may miss provider drift.
- Live provider checks would make default CI flaky and credential-dependent.
- Premature package extraction would distract from proving the contract first.

## References

- `.agentforge/adrs/0002-gateway-module-placement.md`
- `.agentforge/adrs/0008-gateway-provider-boundary.md`
- `.agentforge/adrs/0009-gateway-provider-contract-testing.md`
- `.agentforge/requirements/gateway-provider-boundary-mvp.md`
- `apps/gateway/README.md`
- `docs/gateway.md`

## Revision History

- 2026-07-04: Initial requirements draft for Genesis Sprint 11.
