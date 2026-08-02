# Contributing

AgentForge contributions should preserve architectural integrity, documentation quality, and long-term maintainability.

Before implementation, check whether the change requires a requirement note, RFC, architecture update, ADR, documentation update, tests, examples, or release notes.

## Expected Workflow

1. Understand the relevant `.agentforge/` context.
2. Open or reference an issue for concrete work.
3. Use an RFC for major proposals.
4. Use an ADR for durable architecture decisions.
5. Update docs and tests with implementation changes.
6. Keep changes scoped and reviewable.

## The Sprint Pattern

Every governed increment (a Genesis `0.0.x` release, and later `0.1.x`) ships the same way:

1. **Requirements** — a requirements doc under `.agentforge/requirements/` with acceptance criteria.
2. **Decision** — an ADR (architecture) or DEC (product/operating) recorded in the register.
3. **Implementation** — code, tests, and docs in the same commit.
4. **Validation** — the full local suite below, then CI.
5. **Release** — tag `Genesis-0.0.x`, release notes, issue close-out.

Contribute against this pattern: a change that needs a durable decision comes with its ADR; a change that needs acceptance criteria comes with its requirements note.

## Validation

Run everything from the repository root — all offline, no credentials:

```bash
python scripts/validate_bootstrap.py
python scripts/validate_aics.py          # reports AICS adoption level
python -m unittest discover -s apps/cli/tests
python -m unittest discover -s apps/gateway/tests
python -m unittest discover -s apps/sdk/tests
git diff --check
```

## Commits

Conventional prefixes (`feat:`, `fix:`, `test:`, `docs:`, `chore:`) with a body that explains what and why. Small, reviewable commits. Close issues with reference comments in the release step.

## Contribution Paths

See [docs/community.md](docs/community.md) for the four paths (code, docs, research, integrations), the release-train explanation, and the public `0.1.0` gate (DEC-0006).

## AI Assistance

AI assistants may contribute, but their work must follow the same governance hierarchy as human work — an AI-written change is an ordinary engineering change.

## Revision History

- 2026-08-01: Expanded with the sprint pattern, validation suite, and contribution paths.
- 2026-06-28: Initial draft.
