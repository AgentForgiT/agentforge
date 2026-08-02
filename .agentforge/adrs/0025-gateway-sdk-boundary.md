# ADR-0025: Gateway SDK Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #130, #131, #132, #133, #134
- Related ADRs: ADR-0008 (provider boundary), ADR-0014 (streaming boundary), ADR-0019/0020 (Anthropic inbound), ADR-0023 (auth)

## Context

The gateway is a zero-dependency stdlib HTTP service with two inbound surfaces (OpenAI Chat Completions, Anthropic Messages). Consumers hand-roll HTTP calls; there is no first-party client. The vision's Core product line names an SDK. The SDK must match the project's ethos: dependency-free, offline-testable, governed.

## Decision

Add `apps/sdk` — the `agentforge_sdk` Python package:

- **Thin client over the gateway HTTP API**: `AgentForgeClient(base_url, api_key=None)` with `health()`, `models()`, `chat_completions(...)`, and `anthropic_messages(...)` — no re-implementation of gateway logic, no protocol translation client-side (the gateway owns that).
- **Stdlib only**: `urllib.request` + `json`; no `requests`, no async runtime. Matching the gateway, the SDK is dependency-free by design.
- **Streaming**: SSE parsing for both surfaces (OpenAI `data:` + `[DONE]`; Anthropic `event:`/`data:`).
- **Auth**: `Authorization: Bearer` when `api_key` is provided (ADR-0023); the key is never logged.
- **Offline-testable**: injected `urlopen_fn` (the gateway's own contract-test pattern, ADR-0009) so tests need no network or credentials.
- **Errors**: gateway error envelopes surface as `AgentForgeError(status, body)`.

The SDK is a client, not a second gateway: it does not validate models, normalize responses, or translate protocols. All of that stays server-side, keeping one source of truth.

## Consequences

- First-party consumers (scripts, tools, future CLI features) get a stable client API.
- Zero dependencies keeps install trivial and audit simple; the SDK inherits the gateway's "dependency-free" brand.
- The injected-transport test pattern (ADR-0009) carries over, so SDK tests are deterministic.
- Sync-only (no asyncio) is a deliberate v1 limitation; async can follow when a consumer needs it.

## Alternatives Considered

- **Use `requests`/`httpx`** — rejected: adds a dependency to a project whose identity is dependency-free; urllib suffices for a thin client.
- **Async-first SDK** — rejected: YAGNI until a consumer needs concurrency; sync is simpler to test and audit.
- **Re-implement normalization client-side** — rejected: duplicates gateway logic and invites drift; the gateway is the single source of truth.

## Deferred

- Async (`asyncio`/`httpx`) client variant.
- Typed request/response models (dataclasses) — v1 returns dicts, matching the JSON surface.
- `packages/providers` extraction (ADR-0002/0008) — unrelated refactor, still deferred.
