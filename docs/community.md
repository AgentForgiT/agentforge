# Community

AgentForge is an open engineering platform for agentic AI systems. This page is the community overview: how to contribute, how the release train works, and how the public `0.1.0` line frames external adoption (DEC-0006, DEC-0007).

## Contribution Paths

### Code
Gateway (`apps/gateway`), CLI (`apps/cli`), SDK (`apps/sdk`). Follow the sprint pattern in `CONTRIBUTING.md`: requirements → ADR → implementation → tests → CI → release.

### Docs
The repo docs (`docs/`) and the public website ([agentforgit.github.io/agentforge-docs-site](https://agentforgit.github.io/agentforge-docs-site/)). Docs change with code, in the same commit.

### Research
Benchmarks, datasets, evaluations, and engineering analyses. The Benchmark Observatory and the research portal are the home for these; every number traces to a source.

### Integrations
New providers, MCP servers/clients, IDE registrations, and adapter work. The compatibility matrix is the living map of what works.

All paths follow the same governance hierarchy: RFC for major proposals, ADR for durable decisions, AI-assistant contributions treated as ordinary engineering changes.

## The Release Train

Every governed increment ships the same way — one issue set, one release:

```text
requirements doc → ADR/DEC → implementation + tests + docs → local validation → CI → tag → release notes → issue close-out
```

Genesis `0.0.1` through `0.0.32` built the foundation: a dual-protocol gateway (OpenAI + Anthropic + MCP) with four providers, a seven-command CLI, the `agentforge-sdk`, 28 ADRs, 6 decisions, and AICS Level-3 validated in CI.

## The 0.1.0 Gate

Genesis ends at `0.0.32`. The public `0.1.0` line is defined by DEC-0006 with an auditable gate — six exit criteria, each requiring verifiable evidence (see `requirements/0.1.0-release-gate-checklist.md`):

1. SDK + CLI publishable (tag-gated) or a recorded decision to stay on release assets.
2. All in-scope suites green offline.
3. AICS Level-3 on the AgentForge repo, with migration + scaffold tooling documented.
4. Public docs cover gateway, CLI, SDK, AICS, MCP registration, compatibility.
5. No Draft ADRs in the decision register.
6. A 0.1.0 release note records the transition.

When all six boxes are checked, shipping 0.1.0 is a mechanical act. Until then, Genesis-era work continues under the same governance.

## Where Things Live

| Surface | Location |
| --- | --- |
| Monorepo (gateway, CLI, SDK, AICS, governance) | [github.com/AgentForgiT/agentforge](https://github.com/AgentForgiT/agentforge) |
| Public website | [agentforgit.github.io/agentforge-docs-site](https://agentforgit.github.io/agentforge-docs-site/) |
| Narrative handbook | [AgentForgiT/agentforge-handbook](https://github.com/AgentForgiT/agentforge-handbook) |
| Issue tracker + release train | GitHub issues + releases on the monorepo |
| Compatibility matrix | [compatibility.html](https://agentforgit.github.io/agentforge-docs-site/compatibility.html) |

## Revision History

- 2026-08-01: Initial community overview (DEC-0007).
