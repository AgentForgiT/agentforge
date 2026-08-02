# AgentForge SDK Distribution and MCP Registration

| | |
|---|---|
| Status | Draft |
| Sprint | Genesis Sprint 31 |
| Issues | #140, #141, #142, #143, #144 |
| Related ADRs | ADR-0025 (SDK boundary), ADR-0026 (MCP surface) |

## Background

Sprint 29 shipped the SDK (`agentforge_sdk`) with an editable-install smoke test. Sprint 30 shipped the gateway's MCP surface. Both are real artifacts but neither is *distributable* or *discoverable*: the SDK has no published wheel, and MCP clients don't know how to register the gateway. This sprint closes the distribution + registration gap.

## Requirements

R1. **SDK build**: `agentforge-sdk` produces a clean sdist + wheel (`python -m build`), verified locally and in CI. No runtime dependencies (stdlib only).
R2. **CI publish workflow** (`.github/workflows/publish.yml`): on a `Genesis-0.0.x` tag, builds both packages (`agentforge-cli`, `agentforge-sdk`) and:
   - publishes to PyPI via `twine` gated on the `PYPI_TOKEN` repository secret (the user adds it when ready; workflow is dry-run-safe when absent);
   - uploads the SDK + CLI wheels as **release assets** on the GitHub release (no token needed — the release already exists by then).
R3. **MCP registration docs**: canonical docs in the repo (and mirrored to the website) showing how MCP clients register the gateway as a server:
   - Claude Code: `claude mcp add agentforge --transport http --url http://127.0.0.1:8080/mcp` and the `.mcp.json` project-scope form;
   - auth note: when `server.api_key_env` is set, clients must send the bearer key (Claude Code `env` in `.mcp.json`).
R4. **Release asset wiring**: the Genesis release workflow documents (and the release notes state) that wheels are attached to the tag; the tag flow stays the single release path.
R5. All tests remain offline; CI green; no new runtime dependencies.

## Acceptance Criteria

- [ ] `python -m build` produces sdist + wheel for `agentforge-sdk` locally
- [ ] `publish.yml` builds both packages, publishes to PyPI when `PYPI_TOKEN` present (skips gracefully otherwise), uploads wheels as release assets
- [ ] MCP registration doc lands in repo + website (Claude Code `claude mcp add` + `.mcp.json`)
- [ ] Release notes mention the wheels
- [ ] Full suite passes offline; CI green
