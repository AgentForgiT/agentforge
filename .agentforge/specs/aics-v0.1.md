# AgentForge AI Context Specification v0.1

Metadata:

- Status: Draft
- Version: 0.1
- Phase: Genesis Sprint 3
- Related issue: #6
- Related governance: `.agentforge/constitution.md`, `.agentforge/charter.md`, `.agentforge/adrs/0001-modular-monorepo.md`
- Last updated: 2026-06-28

## Purpose

AgentForge AI Context Specification, or AICS, defines a portable project context structure that can be read by humans, AI coding assistants, and validation tools.

AICS v0.1 captures the minimum viable structure needed for AI-native software projects to preserve governance, architecture, decisions, standards, and tool-specific instructions without relying on private chat history.

## Scope

AICS v0.1 defines:

- required context directory structure
- required governance files
- optional supporting files
- metadata expectations
- AI assistant context hierarchy
- tool adapter expectations
- validation goals

AICS v0.1 does not define:

- a package manager
- a programming language
- a CI provider
- a model provider
- a mandatory documentation site generator
- a permanent schema format

## Background

AgentForge uses `.agentforge/` as the project brain. The project brain already contains governance, decisions, ADRs, RFCs, standards, and AI assistant instructions.

AICS generalizes that pattern so other projects can adopt it and so AgentForge can eventually validate it with tooling.

## Design Goals

AICS should be:

- vendor-neutral
- readable without special tools
- useful to humans and AI assistants
- machine-verifiable
- incrementally adoptable
- compatible with multiple coding assistants
- governed by explicit decisions

## Context Root

An AICS-compatible project SHOULD place project context under:

```text
.agentforge/
```

Projects MAY expose root-level pointer files such as `AGENTS.md`, `CODEX.md`, or `CLAUDE.md`, but those files should point back to the context root rather than duplicate long-lived project memory.

## Required Directory Structure

AICS v0.1 requires:

```text
.agentforge/
  constitution.md
  charter.md
  decisions.md
  architecture.md
  repo-map.md
  agents/
    AGENTS.md
  adrs/
    ADR_TEMPLATE.md
  rfcs/
    RFC_TEMPLATE.md
  standards/
```

## Required Files

The following files are required:

| File | Purpose |
| --- | --- |
| `.agentforge/constitution.md` | durable principles and highest authority |
| `.agentforge/charter.md` | project mission, scope, non-goals, and success criteria |
| `.agentforge/decisions.md` | index of durable decisions |
| `.agentforge/architecture.md` | current architecture baseline |
| `.agentforge/repo-map.md` | repository and module map |
| `.agentforge/agents/AGENTS.md` | master AI assistant operating manual |
| `.agentforge/adrs/ADR_TEMPLATE.md` | architecture decision template |
| `.agentforge/rfcs/RFC_TEMPLATE.md` | proposal template |

## Optional Files

AICS v0.1 recommends but does not require:

- `.agentforge/vision.md`
- `.agentforge/roadmap.md`
- `.agentforge/glossary.md`
- `.agentforge/tech-stack.md`
- `.agentforge/milestones.md`
- `.agentforge/requirements/`
- `.agentforge/specs/`
- `.agentforge/decisions/`
- `.agentforge/agents/CODEX.md`
- `.agentforge/agents/CLAUDE.md`
- `.agentforge/agents/KIRO.md`
- `.agentforge/agents/GEMINI.md`
- `.agentforge/agents/COPILOT.md`
- `.agentforge/agents/OPENCODE.md`

## Metadata Requirements

Every significant AICS document SHOULD include a metadata block near the top.

Recommended metadata fields:

- Status
- Version when applicable
- Phase or milestone
- Applies to
- Related issues
- Related ADRs, RFCs, or decisions
- Last updated

Metadata may be plain Markdown text in v0.1. A future version may define structured front matter.

## Authority Hierarchy

AICS-compatible projects SHOULD define an explicit authority hierarchy.

AgentForge uses:

1. Constitution
2. Project Charter
3. ADRs
4. RFCs
5. Engineering Standards
6. Code and tests
7. Tool-specific context files

If lower-level artifacts conflict with higher-level governance, higher-level governance wins until superseded by an accepted decision.

## AI Assistant Context Hierarchy

AI assistants SHOULD read context in this order:

1. Root pointer file, if present
2. `.agentforge/agents/AGENTS.md`
3. `.agentforge/constitution.md`
4. `.agentforge/charter.md`
5. `.agentforge/decisions.md`
6. Relevant ADRs and RFCs
7. Relevant standards and module docs
8. Tool-specific adapter file, if present

Tool-specific files may add execution details, but they must not silently contradict the master context.

## Tool Adapter Files

Tool adapter files describe how a specific assistant should apply the shared context.

Examples:

- `CODEX.md`
- `CLAUDE.md`
- `KIRO.md`
- `GEMINI.md`
- `COPILOT.md`
- `OPENCODE.md`

Adapter files SHOULD be short and should point back to `AGENTS.md` and the governance hierarchy.

## Root Pointer Files

Projects MAY include root-level files for tools that discover context from the repository root.

Examples:

- `AGENTS.md`
- `CODEX.md`
- `CLAUDE.md`
- `GEMINI.md`

These files SHOULD be pointers, not separate sources of truth.

## Validation Goals

AICS validation should check:

- required directories exist
- required files exist
- required templates exist
- `AGENTS.md` exists in the AI context directory
- required files contain a metadata block
- decision register exists
- ADR and RFC templates exist

Validation SHOULD produce actionable messages.

Validation SHOULD NOT require network access.

The initial validation rule set is documented in `.agentforge/specs/aics-validation-v0.1.md`.

## Adoption Levels

AICS v0.1 defines three adoption levels:

Level 1, Context Present:
Required directories and files exist.

Level 2, Context Governed:
Documents include metadata, authority hierarchy, decision register, and templates.

Level 3, Context Validated:
Machine validation runs locally and in CI.

AgentForge targets Level 3 for its own repositories.

## Compatibility Goals

AICS v0.1 is designed to support:

- OpenAI Codex
- Claude Code
- Kiro
- Gemini CLI
- GitHub Copilot
- OpenCode
- Hermes
- OpenClaw
- AION
- future AI coding assistants

AICS does not assume any one assistant is canonical.

## Best Practices

- Keep long-lived context in `.agentforge/`.
- Keep root context files short.
- Use ADRs for durable decisions.
- Use RFCs for major proposals.
- Treat AI-generated changes as ordinary engineering changes.
- Validate context before implementation-heavy work.
- Prefer references over duplication.

## Risks

- Context can become stale if not validated and reviewed.
- Tool-specific files can drift if they duplicate too much information.
- Overly rigid validation can slow early project evolution.
- Under-specified validation can allow context drift.

## References

- `.agentforge/constitution.md`
- `.agentforge/charter.md`
- `.agentforge/agents/AGENTS.md`
- `.agentforge/adrs/0001-modular-monorepo.md`

## Revision History

- 2026-06-28: Added reference to AICS validation rules.
- 2026-06-28: Initial AICS v0.1 draft.
