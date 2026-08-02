# ADR-0024: AICS Tooling Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #125, #126, #127, #128, #129
- Related: ADR-0022 (AICS v0.2 front matter), `.agentforge/specs/aics-v0.2.md`

## Context

ADR-0022 made YAML front matter the AICS v0.2 metadata standard, but the tooling still scaffolds v0.1 contexts: `init-context` writes plain `Metadata:` blocks, so every new project starts capped at Level 2. Migration from v0.1 was explicitly deferred. The front matter shape had no machine-checkable contract beyond the validator's string checks.

## Decision

Three tooling decisions, all additive and non-breaking:

1. **Scaffolds are v0.2-first.** `init-context` templates move to `templates/context-v0.2/`: all six metadata files carry YAML front matter (`status`, `applies-to`/`last-updated` where relevant, `aics-version: 0.2`), templates get front matter, and the scaffold writes `.agentforge/aics-version` containing `0.2`. A newly scaffolded project validates at **Level 3** immediately.

2. **`migrate-context` converts v0.1 → v0.2 additively.** New CLI command that:
   - converts plain `Metadata:` blocks in the six metadata-checked files into YAML front matter (field mapping `Status` → `status`, `Phase` → `phase`, `Applies to` → `applies-to`, `Last updated` → `last-updated`, plus `aics-version: 0.2`);
   - writes the `.agentforge/aics-version` marker when absent;
   - never deletes or rewrites document body content; files already in front matter are skipped; unparseable blocks are reported, not clobbered.

3. **A canonical JSON Schema** (`.agentforge/specs/aics-front-matter.schema.json`) documents the front matter shape — the machine-checkable contract that tools (validators, editors, CI) can use, while the gateway/CLI validator keeps its dependency-free string checks for consistency.

## Consequences

- New projects start Level-3-ready; the "adoption" story is: scaffold, write code, validate in CI.
- Existing v0.1 projects have a one-command upgrade path with no content loss.
- The schema gives third-party tooling a stable contract; it is declarative documentation, not a runtime dependency of the validator (the validator remains stdlib-only).
- v0.1 templates remain in the repo as historical reference but are no longer used by `init-context`.

## Alternatives Considered

- **Scaffold v0.1 and let users migrate** — rejected: new projects should not start below the target level when the tooling can do better.
- **In-place destructive migration** — rejected: the whole point of AICS is trust; migration must be additive and report-safe.
- **Validator gains a YAML dependency to validate against the schema** — rejected: violates the stdlib-only constraint; string checks already implement the same contract.

## Deferred

- GitHub Action publishing Level-3 CI badges (website tooling sprint).
- Schema-driven validation as a separate opt-in tool.
- Auto-migration of ADRs/RFCs (their front matter is optional; only templates are checked).
