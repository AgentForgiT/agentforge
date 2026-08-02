---
status: Active
phase: Genesis
last-updated: 2026-08-01
aics-version: 0.2
---
# AgentForge Decision Register

## Purpose

This file indexes accepted decisions and their current status.

Durable architecture decisions should be recorded as ADRs in `.agentforge/adrs/`.

## Decisions

| ID | Date | Status | Title | Record |
| --- | --- | --- | --- | --- |
| ADR-0001 | 2026-06-28 | Accepted | Start with a modular monorepo | `.agentforge/adrs/0001-modular-monorepo.md` |
| ADR-0002 | 2026-06-28 | Accepted | Place Gateway in `apps/gateway` with provider adapter boundary | `.agentforge/adrs/0002-gateway-module-placement.md` |
| ADR-0003 | 2026-06-28 | Accepted | Place canonical CLI in `apps/cli` with shared validation boundary | `.agentforge/adrs/0003-cli-module-architecture.md` |
| ADR-0004 | 2026-06-28 | Accepted | Package the canonical CLI from `apps/cli` with editable install first | `.agentforge/adrs/0004-cli-packaging-and-distribution.md` |
| ADR-0005 | 2026-06-29 | Accepted | Scaffold AICS context from packaged templates with safe no-overwrite initialization | `.agentforge/adrs/0005-context-scaffolding-strategy.md` |
| ADR-0006 | 2026-06-29 | Accepted | Explain AICS context through a read-only orientation report with validation-informed status | `.agentforge/adrs/0006-context-explanation-boundary.md` |
| ADR-0007 | 2026-06-29 | Accepted | Diagnose local AICS context health with read-only doctor checks | `.agentforge/adrs/0007-doctor-diagnostics-boundary.md` |
| ADR-0008 | 2026-07-03 | Accepted | Harden Gateway provider adapters behind an internal module boundary | `.agentforge/adrs/0008-gateway-provider-boundary.md` |
| ADR-0009 | 2026-07-04 | Accepted | Validate Gateway providers through offline contract tests | `.agentforge/adrs/0009-gateway-provider-contract-testing.md` |
| ADR-0010 | 2026-07-05 | Accepted | Separate Gateway chat completion request validation | `.agentforge/adrs/0010-gateway-request-validation-boundary.md` |
| ADR-0011 | 2026-07-05 | Accepted | Centralize Gateway JSON error responses | `.agentforge/adrs/0011-gateway-error-response-boundary.md` |
| ADR-0012 | 2026-07-06 | Accepted | Normalize Gateway chat completion responses | `.agentforge/adrs/0012-gateway-response-normalization-boundary.md` |
| ADR-0013 | 2026-07-10 | Accepted | Validate Gateway configuration explicitly | `.agentforge/adrs/0013-gateway-configuration-validation-boundary.md` |
| ADR-0014 | 2026-07-24 | Accepted | Add OpenAI-compatible SSE streaming with gateway-owned chunk normalization | `.agentforge/adrs/0014-gateway-streaming-boundary.md` |
| ADR-0015 | 2026-07-31 | Accepted | Add structured access logging with configurable log level | `.agentforge/adrs/0015-gateway-logging-observability-boundary.md` |
| ADR-0016 | 2026-08-01 | Accepted | Accept null content from reasoning models with field passthrough | `.agentforge/adrs/0016-reasoning-model-response-boundary.md` |
| ADR-0017 | 2026-08-01 | Accepted | Add keyless Ollama provider over the OpenAI-compatible local surface | `.agentforge/adrs/0017-ollama-local-provider-boundary.md` |
| ADR-0018 | 2026-08-01 | Accepted | Add opt-in CORS support for browser clients | `.agentforge/adrs/0018-cors-browser-boundary.md` |
| ADR-0019 | 2026-08-01 | Accepted | Translate Anthropic Messages at the inbound boundary | `.agentforge/adrs/0019-anthropic-messages-inbound-boundary.md` |
| ADR-0020 | 2026-08-01 | Accepted | Map Anthropic thinking and tool-use at the inbound boundary | `.agentforge/adrs/0020-anthropic-tool-use-mapping.md` |
| ADR-0021 | 2026-08-01 | Accepted | Add the Anthropic outbound provider adapter | `.agentforge/adrs/0021-anthropic-outbound-provider-boundary.md` |
| ADR-0022 | 2026-08-01 | Accepted | Adopt YAML front matter for AICS v0.2 | `.agentforge/adrs/0022-aics-v0.2-front-matter.md` |
| ADR-0023 | 2026-08-01 | Accepted | Add opt-in API-key auth and rate limiting | `.agentforge/adrs/0023-api-key-auth-rate-limit.md` |
| ADR-0024 | 2026-08-01 | Accepted | Adopt v0.2-first scaffolds, additive migration, and a front matter schema | `.agentforge/adrs/0024-aics-tooling-boundary.md` |
| ADR-0025 | 2026-08-01 | Accepted | Add a dependency-free Python SDK client | `.agentforge/adrs/0025-gateway-sdk-boundary.md` |
| ADR-0026 | 2026-08-01 | Accepted | Expose gateway capabilities as MCP tools | `.agentforge/adrs/0026-gateway-mcp-surface.md` |
| ADR-0027 | 2026-08-01 | Accepted | Distribute the SDK via tag-gated PyPI publish and release assets | `.agentforge/adrs/0027-sdk-distribution-mcp-registration.md` |
| ADR-0028 | 2026-08-01 | Accepted | Build the engineering twin as a generated read-only profile | `.agentforge/adrs/0028-engineering-twin-boundary.md` |
| ADR-0029 | 2026-08-01 | Accepted | Serve the twin as a read-only stdlib HTTP service | `.agentforge/adrs/0029-twin-service-boundary.md` |
| ADR-0030 | 2026-08-01 | Accepted | Benchmark the platform with an offline reproducible harness | `.agentforge/adrs/0030-benchmark-pipeline-boundary.md` |
| ADR-0031 | 2026-08-01 | Accepted | Authenticate per user with a named key store | `.agentforge/adrs/0031-per-user-auth-boundary.md` |
| ADR-0032 | 2026-08-01 | Accepted | Answer twin questions with retrieval + optional generation | `.agentforge/adrs/0032-twin-qa-boundary.md` |
| ADR-0033 | 2026-08-01 | Accepted | Track benchmark trends across releases | `.agentforge/adrs/0033-benchmark-trends-boundary.md` |
| ADR-0034 | 2026-08-01 | Accepted | Gate releases on benchmark regressions | `.agentforge/adrs/0034-benchmark-regression-gate.md` |
| ADR-0035 | 2026-08-01 | Accepted | Configure per-benchmark regression thresholds | `.agentforge/adrs/0035-per-benchmark-thresholds.md` |
| ADR-0036 | 2026-08-01 | Accepted | Encrypt the named key store at rest with stdlib primitives | `.agentforge/adrs/0036-store-encryption-boundary.md` |
| ADR-0037 | 2026-08-01 | Accepted | Expose MCP resources and prompts on the gateway | `.agentforge/adrs/0037-mcp-resources-prompts-boundary.md` |
| ADR-0038 | 2026-08-01 | Accepted | Require statistical significance in the regression gate | `.agentforge/adrs/0038-variance-aware-regression-gate.md` |
| DEC-0001 | 2026-06-28 | Accepted | Treat early gateway and CLI repos as pre-governance prototypes | `.agentforge/decisions/0001-pre-governance-prototypes.md` |
| DEC-0002 | 2026-06-28 | Accepted | Keep prototype repositories public with canonical monorepo notices | `.agentforge/decisions/0002-prototype-repository-disposition.md` |
| DEC-0003 | 2026-06-28 | Accepted | Build AICS validation CLI in the canonical monorepo | `.agentforge/decisions/0003-cli-path-for-aics-validation.md` |
| DEC-0004 | 2026-07-02 | Accepted | Keep public prototype repositories as historical references after canonical gateway and CLI paths exist | `.agentforge/decisions/0004-post-sprint-8-prototype-disposition.md` |
| DEC-0005 | 2026-07-06 | Accepted | Treat backlog, standards, and repository hygiene as required product foundation | `.agentforge/decisions/0005-product-foundation-hygiene.md` |
| DEC-0006 | 2026-08-01 | Accepted | Define the public 0.1.0 release scope and gate | `.agentforge/decisions/0006-public-0.1.0-scope.md` |
| DEC-0007 | 2026-08-01 | Accepted | Adopt four contribution paths and a community overview | `.agentforge/decisions/0007-community-contribution-paths.md` |
| DEC-0008 | 2026-08-01 | Accepted | Ship 0.1.0 SDK/CLI as release assets until the PyPI token is provisioned | `.agentforge/decisions/0008-0.1.0-distribution-release-assets.md` |
| DEC-0009 | 2026-08-01 | Accepted | Define the public 1.0.0 readiness gate and stability line | `.agentforge/decisions/0009-1.0.0-readiness-gate.md` |

## Revision History

- 2026-08-01: Added DEC-0009 (1.0.0 readiness gate).
- 2026-08-01: Added ADR-0038.
- 2026-08-01: Added ADR-0037.
- 2026-08-01: Added ADR-0036.
- 2026-08-01: Added ADR-0035.
- 2026-08-01: Added ADR-0034.
- 2026-08-01: Added ADR-0033.
- 2026-08-01: Added ADR-0032.
- 2026-08-01: Added ADR-0031.
- 2026-08-01: Added ADR-0030.
- 2026-08-01: Added ADR-0029.
- 2026-08-01: Added DEC-0008 (0.1.0 release-assets distribution).
- 2026-08-01: Added DEC-0007 (community contribution paths).
- 2026-08-01: Added DEC-0006 (public 0.1.0 release scope).
- 2026-08-01: Added ADR-0028.
- 2026-08-01: Added ADR-0027.
- 2026-08-01: Added ADR-0026.
- 2026-08-01: Added ADR-0025.
- 2026-08-01: Added ADR-0024.
- 2026-08-01: Added ADR-0023.
- 2026-08-01: Added ADR-0022.
- 2026-08-01: Added ADR-0021.
- 2026-08-01: Added ADR-0020.
- 2026-08-01: Added ADR-0019.
- 2026-08-01: Added ADR-0018.
- 2026-08-01: Added ADR-0017.
- 2026-08-01: Added ADR-0016.
- 2026-07-31: Added ADR-0015.
- 2026-07-24: Added ADR-0014.
- 2026-07-10: Added ADR-0013.
- 2026-07-06: Added DEC-0005.
- 2026-07-06: Added ADR-0012.
- 2026-07-05: Added ADR-0011.
- 2026-07-05: Added ADR-0010.
- 2026-07-04: Added ADR-0009.
- 2026-07-03: Added ADR-0008.
- 2026-07-02: Added DEC-0004.
- 2026-06-29: Added ADR-0007.
- 2026-06-29: Added ADR-0006.
- 2026-06-29: Added ADR-0005.
- 2026-06-28: Added ADR-0003.
- 2026-06-28: Added ADR-0004.
- 2026-06-28: Added DEC-0003.
- 2026-06-28: Added DEC-0002.
- 2026-06-28: Added ADR-0002.
- 2026-06-28: Initial register.
