# Gateway Ollama / Local Provider Adapter

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 20 |
| Issues | #90, #91, #92, #93, #94 |
| Related ADRs | ADR-0001, ADR-0002, ADR-0008, ADR-0009, ADR-0016 |
| Last updated | 2026-08-01 |

## Background

The gateway currently ships two providers: a deterministic `mock` provider
(offline tests, demos) and an `openrouter` provider (remote, API-key-gated).
The vendor-neutral promise — "my keys, my models, everywhere" — is only half
delivered: every real completion currently flows through a third-party cloud.

Ollama is the de-facto standard for local model serving: it exposes an
OpenAI-compatible HTTP surface (`/v1/chat/completions`, `/v1/models`) on a
default local endpoint (`http://127.0.0.1:11434/v1`), requires no API key,
and serves open-weight models (Llama, Qwen, Mistral, Phi, Gemma, ...).

Adding an `ollama` provider lets the gateway serve completions from models
that never leave the machine — completing the original personal problem
statement and giving the vendor-neutral thesis a local, offline, provable
half.

## Goals

- Add an `ollama` provider type that talks to Ollama's OpenAI-compatible
  `/v1` surface (NOT its native `/api/chat` protocol).
- Default `base_url` of `http://127.0.0.1:11434/v1`; configurable per
  provider config.
- No API key requirement: `api_key_env` stays optional and is ignored by
  the Ollama adapter (local trust boundary).
- Full parity with the OpenRouter adapter: non-streaming chat completions
  and SSE streaming chat completions, same payload substitution
  (`provider_model` → upstream `model`), same error translation for HTTP
  and transport failures.
- Connection-refused / unreachable-local-daemon errors translate to
  `UpstreamProviderError` with a clear message, never a crash.
- Register the provider in the factory so `type: "ollama"` configs build,
  and `supported_provider_types()` reflects it.
- Ship a working `config.ollama.example.json`.

## Non-Goals

- No Ollama native `/api/chat` protocol support (separate protocol,
  separate adapter, no current requirement).
- No automatic model listing or model pulling from the Ollama daemon.
- No streaming passthrough of Ollama's native `/api/chat` stream shape.
- No auth, rate limiting, or key management (Sprint backlog, gateway-wide).

## Requirements

### R1: Ollama provider type

`providers/ollama.py` defines `OllamaProvider` with the same protocol shape
as `OpenRouterProvider` (`chat_completion` + `chat_completion_stream`).
The factory maps `type: "ollama"` to `OllamaProvider`.

### R2: OpenAI-compatible surface

The adapter targets `{base_url}/chat/completions` where the default
`base_url` is `http://127.0.0.1:11434/v1`. The upstream `model` field is
set from `provider_model`. The request body is the OpenAI-compatible chat
completions payload.

### R3: No API key

The adapter must NOT read or require `api_key_env`. If present in config
it is ignored. No `Authorization` header is sent.

### R4: Non-streaming completion

`chat_completion` POSTs the payload, parses the JSON object response, sets
`parsed["model"] = model.name` (public alias), and returns it. HTTP and
transport errors translate to `UpstreamProviderError` with the provider
name and status/message, mirroring the OpenRouter adapter's translation
behavior.

### R5: Streaming completion

`chat_completion_stream` POSTs with `stream: true`, reads SSE `data:`
lines, yields parsed chunk objects, stops at `[DONE]`, and terminates the
response context. Malformed stream lines and transport failures translate
to `UpstreamProviderError`.

### R6: Connection-refused clarity

A local daemon that is down (`URLError` with `ConnectionRefusedError`
reason) surfaces as `UpstreamProviderError` including the provider name —
e.g. "provider 'ollama' request failed: [Errno 111] Connection refused" —
so operators immediately know the local daemon is not running.

### R7: Example configuration

`apps/gateway/config.ollama.example.json` defines an `ollama` provider and
a model alias (e.g. `local-llama3` → `provider_model: llama3.2`) plus the
existing mock, usable end-to-end against a local Ollama install.

### R8: Test coverage

- Provider contract tests with injected transport (parity with
  `OpenRouterProviderContractTests`): non-streaming success, streaming
  success (chunks + `[DONE]`), HTTP error translation, connection-refused
  translation, no Authorization header sent.
- Factory test: `build_provider` returns `OllamaProvider` for
  `type: "ollama"`; `supported_provider_types()` includes `"ollama"`.
- Endpoint test: `GatewayApp` with an injected Ollama provider serves a
  non-streaming completion through `/v1/chat/completions`.
- All tests remain offline (no real Ollama daemon required).

## Acceptance Criteria

- [ ] R1–R8 all implemented and tested.
- [ ] Full local validation: bootstrap, AICS, CLI tests, install test,
      gateway tests, `git diff --check`.
- [ ] CI (`bootstrap-validate.yml`) green on the sprint commit.
- [ ] ADR-0017 records the boundary.
- [ ] Docs (gateway.md, gateway README, CHANGELOG, roadmap, milestones,
      backlog, decisions register) updated.
- [ ] Release `Genesis-0.0.20` tagged and issues #90–#94 closed.
