# AgentForge Python SDK

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 29 |
| Issues | #130, #131, #132, #133, #134 |
| Related ADRs | ADR-0008 (provider boundary), ADR-0014 (streaming), ADR-0019/0020 (Anthropic inbound), ADR-0023 (auth) |

## Background

The gateway exposes two HTTP surfaces (OpenAI Chat Completions + Anthropic Messages) behind one governance story. Consumers today must hand-roll HTTP calls. The vision's Core product line includes an SDK. This sprint ships the first SDK: a **stdlib-only Python client** (`apps/sdk`, package `agentforge_sdk`) that wraps both surfaces with a clean API, streaming, and auth — mirroring the gateway's zero-dependency ethos.

## Requirements

R1. `AgentForgeClient(base_url, api_key=None)`:
   - `health()` → gateway `/health`
   - `models()` → gateway `/v1/models`
   - `chat_completions(model, messages, stream=False, **kwargs)` → non-streaming dict or iterator of chunks
   - `anthropic_messages(model, messages, max_tokens=4096, stream=False, **kwargs)` → Anthropic-shaped dict or SSE event iterator
R2. Auth: when `api_key` is set, sends `Authorization: Bearer <key>`; `x-api-key` also supported via a flag for Anthropic-style clients. Never logs the key.
R3. Streaming: SSE parsing (stdlib) yielding parsed JSON chunks; `[DONE]` handling for OpenAI surface; Anthropic `event:`/`data:` handling for Messages surface.
R4. Errors: gateway error envelopes (OpenAI or Anthropic shape) surface as `AgentForgeError` with `status` and the envelope body.
R5. Stdlib only (`urllib.request`, `json`) — no `requests`, no SDK deps. Injected `urlopen_fn` for offline tests (the gateway's own contract-test pattern).
R6. Packaging: `apps/sdk/pyproject.toml` with a `console`-free library package; editable-install test in CI (mirrors `apps/cli`).

## Acceptance Criteria

- [ ] Client hits both surfaces with correct paths/payloads (verified via injected transport)
- [ ] Streaming parses OpenAI chunks + `[DONE]`; Anthropic events parse correctly
- [ ] Auth header sent when key provided; absent otherwise
- [ ] Error envelopes raise typed errors with status
- [ ] Full suite passes offline; CI green
