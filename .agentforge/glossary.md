# AgentForge Glossary

Metadata:

- Status: Draft
- Phase: Genesis
- Last updated: 2026-06-28

## Terms

Agentic AI Engineering:
The discipline of designing, building, testing, documenting, and operating software systems that use AI agents or AI-assisted development workflows.

AI Context Layer:
The shared project context that AI assistants read before acting. In AgentForge this begins in `.agentforge/`.

AICS:
AgentForge AI Context Specification, a future portable standard for AI-readable project context.

ADR:
Architecture Decision Record. A durable record of a significant technical decision.

RFC:
Request for Comments. A proposal for non-trivial changes before they become accepted decisions or implementation work.

Gateway:
An OpenAI-compatible routing and provider abstraction layer for model access.

Provider Adapter:
Code that isolates provider-specific request, response, authentication, and error handling.

Modular Monorepo:
A single repository that contains multiple modules with explicit boundaries, used until extraction into standalone repositories is justified.

## Revision History

- 2026-06-28: Initial draft.
