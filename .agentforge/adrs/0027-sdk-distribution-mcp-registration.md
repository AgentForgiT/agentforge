# ADR-0027: SDK Distribution and MCP Registration Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #140, #141, #142, #143, #144
- Related ADRs: ADR-0025 (SDK boundary), ADR-0026 (MCP surface)

## Context

The SDK (`agentforge_sdk`, ADR-0025) and the gateway's MCP surface (ADR-0026) are real, tested artifacts — but the SDK has no published wheel and MCP clients have no canonical registration path. Distribution and discoverability are the missing half of "ship it."

## Decision

1. **Publish `agentforge-sdk` to PyPI via a tag-gated CI workflow** (`.github/workflows/publish.yml`): on any `Genesis-0.0.x` tag, build sdist + wheel for `agentforge-cli` and `agentforge-sdk` with `python -m build`, publish with `twine` gated on the `PYPI_TOKEN` repository secret, and upload both wheels as GitHub release assets. If `PYPI_TOKEN` is absent, the publish step is skipped (dry-run-safe) but the release-asset upload still runs — so releases never depend on a secret being configured.

2. **Canonical MCP registration docs** live in the repo (`docs/mcp.md`) and mirror to the website: Claude Code via `claude mcp add agentforge --transport http --url http://127.0.0.1:8080/mcp` (and the `.mcp.json` project-scope form), with the auth note for `server.api_key_env`.

3. **Release assets are the distribution fallback**: even before PyPI publication, every Genesis tag carries the built wheels, so `pip install <wheel-url>` works immediately.

## Consequences

- The SDK becomes installable: `pip install agentforge-sdk` once published, or `pip install <wheel asset>` immediately.
- MCP clients have a one-command registration path to the gateway.
- The publish step is token-gated and graceful — no hard dependency on secrets in CI.
- Distribution stays governed: the tag flow is the single release path; PyPI is an output, not a workflow fork.

## Alternatives Considered

- **Publish to PyPI manually from a dev machine** — rejected: ungoverned, unrepeatable, and requires local token handling.
- **Always-publish workflow on every push** — rejected: PyPI has no overwrite; tag-gating is the standard, safe pattern.
- **Separate SDK repository** — rejected: monorepo governance (ADR-0001) keeps one release train.

## Deferred

- PyPI token provisioning (the maintainer adds `PYPI_TOKEN` when ready to publish; nothing in CI blocks on it).
- `agentforge-cli` PyPI publication (same workflow covers it; not yet the priority).
- MCP registration for other clients (OpenCode, Cursor, etc.) — Claude Code is the canonical example; the `.mcp.json` shape generalizes.
