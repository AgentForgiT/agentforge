# ADR-0019: Anthropic Messages Inbound Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #100, #101, #102, #103, #104
- Related ADRs: ADR-0008 (provider boundary), ADR-0010 (request validation boundary), ADR-0011 (error response boundary), ADR-0012 (response normalization boundary), ADR-0014 (streaming boundary), ADR-0017 (keyless local trust), ADR-0018 (CORS)

## Context

The gateway currently exposes one inbound surface: OpenAI Chat Completions (`POST /v1/chat/completions`). Anthropic-protocol clients — Claude Code, claude-mem, Anthropic SDK users — speak the Anthropic Messages API (`POST /v1/messages`) and cannot route through the gateway. The Sprint 22 Compatibility Matrix documented this as the gateway's largest "needs adapter" cell.

Two architectural options exist:

1. **Provider-side adaptation** — teach each provider adapter to also speak Anthropic shapes (outbound translation per provider).
2. **Inbound translation at the edge** — add `/v1/messages` as a second inbound surface; translate Anthropic request → internal normalized request → OpenAI-compatible provider dispatch; translate provider responses back to Anthropic shape.

## Decision

Adopt **translation at the edge** (option 2):

- Add `POST /v1/messages` as a first-class inbound surface alongside `POST /v1/chat/completions`.
- Anthropic request validation lives in a dedicated module (`agentforge_gateway.anthropic`) that validates the Messages request shape and converts it to the gateway's internal normalized request (model alias resolution, message flattening, `system` folding).
- Provider adapters are **untouched**: dispatch uses the existing OpenAI-compatible provider protocol. Translation happens only at the inbound/outbound edges.
- Anthropic response normalization produces the Messages response shape (`id`, `type: "message"`, `content` text blocks, `stop_reason`, `usage`) from the normalized provider response.
- Streaming translates normalized chunks into Anthropic SSE events (`message_start`, `content_block_start`, `content_block_delta`, `content_block_stop`, `message_delta`, `message_stop`).
- Errors use the Anthropic error envelope with the same status mapping as the OpenAI surface.
- `x-api-key` is accepted but not required and never forwarded upstream (keyless local trust, ADR-0017).

## Consequences

- Claude Code and other Anthropic-protocol clients can point `ANTHROPIC_BASE_URL` at the gateway and reach mock, ollama, and openrouter providers — closing the matrix's largest gap.
- One translation layer, not N provider-specific translations: new providers automatically gain Anthropic compatibility.
- The gateway now owns two inbound protocol surfaces over one internal model — the protocol-agnostic core that the vision's "one platform, every IDE" requires.
- Anthropic-specific features without OpenAI analogues (thinking blocks, tool_use blocks) are initially translated conservatively: tool blocks surface as plain text in content; thinking is not yet mapped (deferred).
- The OpenAI surface and its tests are unchanged; the suite grows with a new anthropic test module.

## Alternatives Considered

- **Provider-side dual-protocol adapters** — rejected: duplicates translation N times, risks drift, and couples providers to both protocols.
- **Reverse-proxy passthrough of `/v1/messages` to a second gateway** — rejected: external dependency, breaks the single-surface governance story.
- **Native Anthropic provider adapter (outbound only)** — deferred: a later sprint may add a direct `anthropic` provider; this ADR covers the inbound surface only.

## Deferred

- Thinking blocks and tool-use block mapping for Anthropic clients.
- Direct `anthropic` outbound provider adapter (OpenAI-compatible clients reaching Anthropic's API).
- Anthropic-specific usage streaming events.
