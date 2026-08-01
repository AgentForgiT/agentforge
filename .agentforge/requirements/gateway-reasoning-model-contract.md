# Gateway Reasoning-Model Response Contract

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 19 |
| Issues | #85, #86, #87, #88, #89 |
| Related ADRs | ADR-0001, ADR-0002, ADR-0008, ADR-0010, ADR-0012, ADR-0014, ADR-0016 |
| Last updated | 2026-08-01 |

## Background

Live verification of the gateway against the OpenRouter API (2026-08-01)
uncovered a contract gap that the mock-driven test suite could not expose:

Reasoning models — OpenAI o-series, DeepSeek R1-style, and OpenRouter
reasoning endpoints such as `openai/gpt-oss-20b:free` — legally return
`message.content: null` in non-streaming completions, with the model's
output delivered in `reasoning` and `reasoning_details` fields. The
OpenAI-compatible specification permits `content` to be `null` for such
models.

The gateway's response validator rejected any non-string `content`,
including `null`, producing `502 upstream_provider_error` responses for
every reasoning-model completion. A minimal fix shipped in commit
`ee19076`; this sprint formalizes the boundary so the behavior is
specified, tested, and documented.

## Goals

- Accept `message.content: null` in non-streaming chat completions from
  reasoning models.
- Preserve reasoning fields (`reasoning`, `reasoning_details`, and any
  provider-specific extras) through normalization untouched.
- Keep rejecting genuinely invalid content (non-string, non-null).
- Handle streaming deltas from reasoning models correctly: empty-string
  or null `delta.content` alongside `delta.reasoning` fields must stream
  through without error.
- Anchor the behavior with fixtures captured from the live OpenRouter
  exchange.

## Non-goals

- Mapping or rewriting `reasoning` into `content` — that is a consumer
  concern, not a gateway contract (ADR-0014: the gateway normalizes
  shape, not semantics).
- Standardizing reasoning field names across providers — passthrough
  only, for now.
- `stream_options` / usage summaries in streaming (deferred).

## Requirements

### R1 — Non-streaming null content (REQUIRED)

`normalize_chat_completion_response` must accept
`choices[0].message.content` of type `str` or `null` (`None`). Any other
type must still raise `UpstreamProviderError` with a message containing
"content".

### R2 — Reasoning passthrough (REQUIRED)

All fields other than `model` must be preserved on the normalized
response. In particular `message.reasoning` and
`message.reasoning_details` must survive normalization byte-for-byte.

### R3 — Streaming reasoning deltas (REQUIRED)

Stream chunks whose `delta.content` is `""` (empty string) or `null`,
with or without `delta.reasoning` / `delta.reasoning_details`, must pass
stream chunk validation. `finish_reason: "stop"` and the `[DONE]`
terminator must still be delivered.

### R4 — Invalid content still rejected (REQUIRED)

`message.content` of any type other than `str` or `null` (e.g. `int`,
`list`, `dict`) must raise `UpstreamProviderError`.

### R5 — Live-derived fixtures (REQUIRED)

The test suite must include at least one non-streaming fixture and one
streaming fixture derived from the recorded OpenRouter exchange
(`gpt-oss-20b:free`, provider "Darkbloom"), with the identifying fields
intact.

### R6 — Alias normalization preserved (REQUIRED)

The normalized response and chunks must still expose the public model
alias (`model.name`) as `model`, per ADR-0012/0014. The upstream model
id passes through raw in the upstream-facing contract.

## Acceptance criteria

1. `python -m unittest discover -s apps/gateway/tests` passes with the
   new reasoning fixtures (suite grows to 112+).
2. A non-streaming completion against a live reasoning model returns
   200 with `content: null` preserved (verified 2026-08-01).
3. A streaming completion against a live reasoning model delivers
   reasoning chunks, `finish_reason: "stop"`, and `[DONE]` (verified
   2026-08-01).
4. CI `bootstrap-validate.yml` is green on the sprint commit.
5. `docs/gateway.md` documents the reasoning-model contract and the
   `content: null` semantics.
