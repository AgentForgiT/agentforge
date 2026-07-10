# ADR-0013: Validate Gateway Configuration Explicitly

Metadata:

- Status: Accepted
- Date: 2026-07-10
- Deciders: AgentForge maintainers
- Related issues: #73, #70, #72, #71, #74
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0009, ADR-0010, ADR-0011, ADR-0012
- Related requirements: `.agentforge/requirements/gateway-configuration-validation-mvp.md`

## Context

The gateway has established internal boundaries for provider adapters, provider contracts, request validation, error responses, and response normalization.

Configuration parsing still lives in a small dependency-free module, but it relies partly on implicit Python casts. Some invalid values fail with incidental conversion errors, while others are silently coerced.

Before the gateway adds logging, streaming, more providers, or broader operational behavior, configuration should fail fast with clear validation rules.

## Decision

Keep gateway configuration parsing and validation inside `agentforge_gateway.config`.

The config module will own:

- root config object validation
- server object validation
- host and port validation
- model object and field validation
- provider object and field validation
- provider timeout and header validation
- default server values
- default mock provider behavior when providers are omitted

The parser will continue to raise `ValueError` for malformed configuration during Genesis.

Provider factory and adapters will continue to own supported-provider checks, runtime credential checks, upstream transport behavior, and provider-specific behavior.

No JSON Schema library, web framework, or validation dependency will be introduced during Sprint 16.

## Boundary Rules

Configuration validation owns:

- JSON object shape
- required model and provider scalar fields
- server host and port constraints
- provider timeout and header constraints
- conversion into immutable config dataclasses

Provider factory owns:

- mapping provider type names to provider adapter implementations
- rejecting unsupported provider types

Provider adapters own:

- provider credentials
- upstream endpoints
- provider-specific payload mapping
- upstream error translation

HTTP handling owns:

- request routing
- request body parsing
- response delivery
- gateway error envelopes

## Compatibility

Sprint 16 must preserve existing behavior for:

- default config when no config path is provided
- example config files
- mock provider defaults when providers are omitted
- provider references from models
- gateway HTTP endpoints
- offline CI validation

The new validation may reject malformed configuration that previously passed through by implicit coercion. That is an intentional hardening of startup behavior.

## Consequences

Benefits:

- makes config expectations easier to review
- improves startup failure messages
- keeps provider-specific runtime behavior out of config parsing
- prevents malformed config from reaching request handling
- keeps Genesis dependency-free

Trade-offs:

- adds small helper surface area in `config.py`
- keeps validation hand-written during Genesis
- does not yet define a public JSON Schema
- does not validate live provider credentials or upstream availability

## Alternatives Considered

Keep implicit casts:
Rejected because implicit casts make malformed config behavior harder to reason about and test.

Adopt JSON Schema now:
Rejected because the config surface is still small and Genesis should avoid extra runtime or tooling dependencies.

Move provider validation into adapters:
Rejected because structure and scalar validation belong at config parse time, while adapters own runtime provider behavior.

Validate provider credentials during config parsing:
Rejected because credentials live in environment variables and should not be required for default offline validation.

## Follow-Up Work

- Revisit public config schema after provider and deployment needs mature.
- Keep future provider config fields explicit and tested.
- Consider config diagnostics in a later gateway or CLI diagnostic sprint.
- Keep live provider checks optional and outside default CI.

## Revision History

- 2026-07-10: Accepted for Genesis Sprint 16.
