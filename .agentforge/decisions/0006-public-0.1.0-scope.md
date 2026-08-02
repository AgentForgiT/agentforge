# DEC-0006: Public 0.1.0 Release Scope

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #150, #151, #152, #153, #154
- Related: `.agentforge/requirements/public-0.1.0-scope.md`

## Decision

After 31 governed Genesis `0.0.x` releases, define the **public `0.1.0` line** as the first release intended for external adoption, gated by the exit criteria in the scope requirements:

1. SDK + CLI publishable (tag-gated workflow, ADR-0027) or an explicit recorded decision to stay on release assets.
2. All in-scope suites green offline (gateway, CLI, SDK).
3. AICS Level-3 on the AgentForge repo, with migration + scaffold tooling documented for external projects.
4. Public docs cover gateway, CLI, SDK, AICS, MCP registration, compatibility matrix.
5. No Draft ADRs in the decision register.
6. A 0.1.0 release note records the transition and this decision.

The Genesis train stops at the release carrying this scope (Genesis-0.0.32); later governance rides the `0.1.x` line under semantic versioning. Breaking changes require a minor bump and an ADR.

## Rationale

Genesis shipped one governed increment per release to build the foundation. 0.1.0 marks the point where the foundation is *adoptable*: installable, documented, and stable. The gate exists to keep "public" honest — no date, no promise beyond the artifacts actually shipping.

## Alternatives Considered

- **Skip 0.1.0 and go straight to 1.0.0** — rejected: 0.1.x is the honest first-adopter line; 1.0.0 should follow real external use.
- **No gate (release when "ready")** — rejected: "ready" without criteria is unfalsifiable; the gate makes the decision auditable.
- **Keep Genesis forever** — rejected: the 0.0.x train's value was velocity; adoption needs a stable line.

## Consequences

- Contributors and researchers get a defined target to plan against.
- The gate is checkable at any time; shipping 0.1.0 is a mechanical decision, not a judgment call.
- Deferred items (twin service, per-user auth, MCP extensions) ride later 0.x releases with their own ADRs.
