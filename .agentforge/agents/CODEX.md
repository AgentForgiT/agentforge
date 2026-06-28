# Codex Instructions

Metadata:

- Status: Draft
- Applies to: OpenAI Codex sessions
- Last updated: 2026-06-28

## Required Context

Before making significant changes, read:

1. `.agentforge/agents/AGENTS.md`
2. `.agentforge/constitution.md`
3. `.agentforge/charter.md`
4. `.agentforge/decisions.md`
5. relevant ADRs and RFCs

## Working Style

Use Codex as an implementation partner, but keep governance first.

Prefer small, reviewable commits:

- structure
- governance
- documentation
- implementation
- tests
- release notes

Use local tests and validation before pushing. Keep changes scoped. Do not delete or rewrite prototype repositories unless an accepted ADR explicitly directs that work.

## Current Genesis Guidance

The next major implementation after Bootstrap Kit is gateway reconciliation into `apps/gateway`, not continued feature growth in the standalone gateway prototype.

## Revision History

- 2026-06-28: Initial Codex instructions.
