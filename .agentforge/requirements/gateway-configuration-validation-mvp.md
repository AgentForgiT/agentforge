# Gateway Configuration Validation MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 16
- Related issues: #73, #70, #72, #71, #74
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0009, ADR-0010, ADR-0011, ADR-0012, ADR-0013
- Related policy: `docs/release-policy.md`
- Last updated: 2026-07-10

## Purpose

Define the requirements for explicit gateway configuration validation.

This document exists so Sprint 16 hardens gateway startup configuration before adding logging, streaming, more providers, or broader operational behavior.

## Scope

In scope:

- root JSON object validation
- `server` object validation
- `host` and `port` validation
- model object and required field validation
- provider object and required field validation
- provider timeout and headers validation
- preserving default mock-provider behavior
- offline tests and documentation

Out of scope:

- adding JSON Schema or validation framework dependencies
- adding runtime provider checks
- validating provider credentials
- changing HTTP request or response contracts
- changing provider adapter behavior
- adding live upstream provider tests
- publishing gateway packages

## Background

The gateway currently parses JSON configuration in `agentforge_gateway.config`.

The current parser is small and dependency-free, but it still mixes parsing with implicit casts. For example, some malformed values fail through incidental Python conversion errors, while others are converted to strings without explicit validation.

Sprint 16 should make the gateway configuration boundary explicit and deterministic while preserving the existing default mock config behavior.

## Architecture

Configuration loading remains owned by `agentforge_gateway.config`.

The config module owns:

- parsing raw JSON objects into dataclasses
- validating config structure and scalar values
- applying defaults for omitted server values
- applying default mock provider behavior when providers are omitted

Provider factory and provider adapters continue to own:

- supported provider type checks
- provider-specific runtime authentication behavior
- upstream transport behavior
- provider-specific request and error translation

## User Workflows

The MVP must support these workflows:

- A contributor gets clear startup-time errors for malformed gateway config.
- A maintainer can understand config rules without reading provider adapters.
- CI validates config behavior without network access or provider credentials.
- Existing example configs continue to parse.
- Existing gateway request, response, provider, and error behavior remains unchanged.

## Configuration Validation Requirements

The parser must reject:

- non-object root config
- non-object `server`
- empty or non-string `server.host`
- non-integer or out-of-range `server.port`
- missing or empty `models`
- non-object model entries
- missing, non-string, or empty model `provider`
- missing, non-string, or empty model `provider_model`
- models referencing unknown providers
- non-object provider maps
- non-object provider entries
- missing, non-string, or empty provider `type`
- non-positive or non-numeric provider `timeout_seconds`
- non-object provider `headers`
- non-string provider header names or values
- non-string optional provider `base_url` or `api_key_env`

The parser must preserve:

- default host `127.0.0.1`
- default port `8080`
- default mock provider when provider config is absent
- provider references by model name
- deterministic error messages that mention the invalid field

## Compatibility Requirements

Sprint 16 must preserve:

- `GET /health`
- `GET /v1/models`
- `POST /v1/chat/completions`
- current request validation behavior
- current error response envelope behavior
- current response normalization behavior
- current mock and OpenRouter provider behavior
- current config example files
- default offline test behavior

## Testing and CI Requirements

Tests must cover:

- valid OpenRouter provider config
- missing provider map default behavior
- non-object root config
- non-object server config
- invalid host
- invalid port
- missing models
- malformed model entries
- unknown provider references
- malformed provider entries
- invalid timeout
- invalid headers
- valid example config files

CI must not require network access, provider credentials, or live upstream providers.

## Documentation Requirements

Documentation must explain:

- the gateway configuration validation boundary
- required model and provider fields
- default host, port, and mock provider behavior
- why provider credentials are still runtime environment concerns
- current Sprint 16 limitations

## Acceptance Criteria

Issue #73 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references ADR-0013
- it defines Sprint 16 configuration validation scope before implementation completes

The Sprint 16 configuration validation milestone is complete when:

- issue #70 records ADR-0013
- issue #72 implements the configuration validation helpers
- issue #71 validates configuration behavior locally and in CI
- issue #74 documents the boundary and prepares `Genesis-0.0.16`

## Examples

Valid minimal config:

```json
{
  "models": {
    "mock-coder": {
      "provider": "mock",
      "provider_model": "mock-coder-v1"
    }
  }
}
```

Invalid port:

```json
{
  "server": {
    "port": 0
  },
  "models": {
    "mock-coder": {
      "provider": "mock",
      "provider_model": "mock-coder-v1"
    }
  }
}
```

Expected validation command:

```bash
python -m unittest discover -s apps/gateway/tests
```

## Best Practices

- Keep config validation explicit.
- Keep defaults centralized.
- Reject malformed config at startup rather than during request handling.
- Keep provider credential checks inside provider runtime behavior.
- Keep default config tests offline and deterministic.

## Risks

- Over-validating configuration too early could reject useful future provider options.
- Under-validating configuration can make startup failures confusing.
- Adding schema dependencies during Genesis would add avoidable complexity.
- Changing config defaults can break examples and local workflows.

## References

- `.agentforge/adrs/0002-gateway-module-placement.md`
- `.agentforge/adrs/0008-gateway-provider-boundary.md`
- `.agentforge/adrs/0010-gateway-request-validation-boundary.md`
- `.agentforge/adrs/0013-gateway-configuration-validation-boundary.md`
- `apps/gateway/README.md`
- `docs/gateway.md`

## Revision History

- 2026-07-10: Initial requirements draft for Genesis Sprint 16.
