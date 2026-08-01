# ADR-0017: Ollama / Local Provider Adapter Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Related ADRs: ADR-0008 (provider boundary), ADR-0009 (provider contract
  tests), ADR-0012 (response normalization), ADR-0014 (streaming boundary),
  ADR-0016 (reasoning-model responses)
- Related issues: #90, #91, #92, #93, #94

## Context

The gateway ships `mock` (offline/deterministic) and `openrouter` (remote,
API-key-gated) providers. The vendor-neutral thesis — one API across
models and providers, including the user's own models — requires a local
provider path so completions can run fully offline against open-weight
models.

Ollama is the de-facto local serving standard. It exposes two HTTP
surfaces:

1. a native protocol at `/api/chat` (Ollama-specific shapes), and
2. an OpenAI-compatible surface at `/v1/chat/completions` (standard chat
   completions request/response shapes, including SSE streaming).

The gateway already owns OpenAI-compatible request validation and response
normalization, so the choice of surface determines how much new machinery
the adapter needs.

## Decision

The `ollama` provider adapter targets Ollama's **OpenAI-compatible `/v1`
surface only**.

- Default `base_url` is `http://127.0.0.1:11434/v1` (Ollama's default
  listen address); overridable per provider config, so any
  OpenAI-compatible local server (Ollama, LM Studio, llama.cpp server,
  vLLM) is addressable with the same adapter.
- No API key is required or read; `api_key_env` is ignored for this
  provider type. Local trust boundary: the daemon is on the user's
  machine; no `Authorization` header is sent.
- Non-streaming and streaming completions use the same payload
  substitution (`provider_model` → upstream `model`) and the same
  `UpstreamProviderError` translation as the OpenRouter adapter.
- Connection-refused and other transport failures surface as
  `UpstreamProviderError` naming the provider, so a stopped local daemon
  reads as "provider 'ollama' request failed: ... Connection refused"
  rather than a crash.
- The native `/api/chat` protocol is NOT supported by this adapter.
- Shared SSE parsing and HTTP-error formatting helpers are extracted to a
  common module used by both `openrouter` and `ollama` adapters (single
  implementation of stream framing and error translation).

## Consequences

Benefits:

- Completes the original problem statement: "my keys, my models,
  everywhere" now has a local, offline, keyless half.
- Zero new dependencies: the adapter uses the same stdlib `urllib` +
  `json` machinery as the OpenRouter adapter.
- The gateway's existing request validation, response normalization
  (ADR-0012), reasoning passthrough (ADR-0016), and streaming chunk
  normalization (ADR-0014) apply unchanged because the adapter speaks
  OpenAI-compatible shapes.
- One adapter covers any OpenAI-compatible local server, not just Ollama.

Trade-offs:

- Ollama's native protocol (richer per-token metadata, embeddings, model
  pull APIs) is not accessible through this adapter; a future native
  adapter would be a separate provider type.
- The local daemon must already be running with the target model pulled;
  the gateway does not pull or manage models.

Follow-up obligations:

- Keep the provider contract tests (ADR-0009) covering the Ollama adapter
  with injected transport so CI stays offline.
- Document the adapter in gateway docs and ship an example config.
- Later sprint: auth, rate limiting, and key management remain gateway-wide
  backlog items; local providers are unaffected by key policy.

## Alternatives Considered

1. **Native `/api/chat` adapter.** Rejected: different request/response
   shapes (messages vs. prompt, stream format, no `usage` in the same
   shape) would require a second normalization path in the gateway,
   violating the single OpenAI-compatible normalization boundary
   (ADR-0012/ADR-0014).
2. **Abstract base HTTP provider class.** Rejected for now: the shared
   surface between OpenRouter and Ollama adapters is small (SSE framing,
   HTTP error formatting, URL building); a shared helper module keeps the
   change minimal without forcing a premature abstraction. Revisit when a
   third HTTP provider appears.
3. **SSE passthrough without parsing.** Rejected: the gateway owns chunk
   normalization (ADR-0014); raw passthrough would bypass validation and
   alias substitution.

## Revision History

- 2026-08-01: Initial draft.
