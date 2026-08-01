# ADR-0016: Accept Null Content from Reasoning Models

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Related issues: #85, #86, #87, #88, #89
- Related decisions: ADR-0001, ADR-0002, ADR-0008, ADR-0010, ADR-0012, ADR-0014
- Related requirements: `.agentforge/requirements/gateway-reasoning-model-contract.md`

## Context

Live verification against the OpenRouter API (2026-08-01) revealed that
reasoning models return `message.content: null` for non-streaming
completions, emitting their output in `reasoning` and
`reasoning_details` fields. The OpenAI-compatible specification permits
null content on assistant messages; it is not a malformed response.

The gateway's non-streaming validator required `content` to be a `str`
and raised `UpstreamProviderError` otherwise, so every reasoning-model
completion surfaced as a 502. The mock provider never exercised this
path, so the 110-test suite was green while the production path was
broken for an entire model class.

The decision must answer:

- is null content valid?
- do reasoning fields pass through or get rewritten?
- what remains invalid?
- how is this anchored in tests?

## Decision

**Null `message.content` is valid and passes through.**

1. `normalize_chat_completion_response` accepts `choices[0].message.content`
   of type `str` or `null`. Any other type is still rejected with
   `UpstreamProviderError` mentioning "content".
2. Reasoning fields (`reasoning`, `reasoning_details`, provider extras)
   pass through normalization untouched. The gateway normalizes shape,
   not semantics (ADR-0014); mapping reasoning into content is a
   consumer decision.
3. Streaming chunks already tolerate empty-string and null
   `delta.content`; this is now asserted explicitly with
   live-derived fixtures.
4. The public model alias still replaces the upstream `model` field
   (ADR-0012, ADR-0014); the upstream model id passes through raw
   upstream-facing.

## Consequences

Positive:

- Reasoning models (o-series, R1-style, OpenRouter reasoning endpoints)
  work through the gateway non-streaming and streaming.
- Live-verified behavior is now contract-backed: fixtures captured from
  the real OpenRouter exchange (`gpt-oss-20b:free`, provider
  "Darkbloom") pin the shape.
- The 502-on-reasoning-model failure mode is eliminated and regression
  protected.

Negative:

- Consumers asking for reasoning content must read `reasoning` fields
  themselves; the gateway will not synthesize `content`.
- The strictness contract is slightly loosened (null allowed) — but only
  to match the upstream specification, and non-string non-null is still
  hard-rejected.

Deferred:

- Standardizing reasoning field names across providers.
- `stream_options` / streaming usage summaries.
- Exposing reasoning content via a dedicated endpoint or `include_reasoning`
  parameter.
