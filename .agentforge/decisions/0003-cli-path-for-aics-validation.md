# DEC-0003: Build AICS Validation CLI in the Canonical Monorepo

Metadata:

- Status: Accepted
- Date: 2026-06-28
- Related issue: #9
- Related decisions: ADR-0001, DEC-0001, DEC-0002

## Context

AgentForge has a pre-governance `agentforge-cli` prototype that scaffolds repositories and validates early repository structures.

AgentForge now also has AICS v0.1, AICS validation rules, a reusable local validator, and a minimal example context tree inside the canonical `agentforge` monorepo.

The project needs a clear path for commands such as:

```bash
agentforge validate-context
agentforge validate-context path/to/project
```

without extending the prototype repository in a way that contradicts ADR-0001.

## Decision

Future AICS validation CLI work will start inside the canonical `agentforge` monorepo, under `apps/cli`.

The CLI should reuse the existing validation code in `scripts/aics_validation.py` or a future shared module derived from it.

The standalone `agentforge-cli` repository remains public as a historical scaffold CLI prototype. It should not receive new architecture-level CLI work until a later decision migrates, archives, or repurposes it.

## Rationale

This keeps AICS validation close to the specification, examples, and CI while the interface is still evolving.

It also avoids splitting CLI governance across a standalone prototype repo and the canonical monorepo.

## Expected Commands

The first canonical CLI should eventually support:

```bash
agentforge validate-context
agentforge validate-context path/to/project
```

Future commands may include:

```bash
agentforge init-context
agentforge explain-context
agentforge doctor
```

## Migration Criteria

The standalone `agentforge-cli` repository may be migrated or superseded after:

- AICS validation commands exist in `apps/cli`
- the monorepo CLI has tests and CI coverage
- README notices in the prototype repo point to the canonical CLI path
- an accepted decision records whether the prototype repo is archived, retained, or repurposed

## Consequences

Benefits:

- keeps AICS validation and CLI behavior governed in one repository
- avoids extending a pre-governance prototype as if it were canonical
- allows CLI interfaces to evolve next to specs and examples
- preserves useful prototype history

Trade-offs:

- short-term duplication may exist between old scaffold CLI ideas and new AICS CLI work
- users may see two CLI-related locations until notices and docs are clear
- packaging decisions remain deferred

## Follow-Up Work

- Create `apps/cli` only when implementation begins.
- Add a requirements document or issue for `agentforge validate-context`.
- Decide packaging and distribution separately.
- Revisit `agentforge-cli` disposition after canonical CLI validation exists.

## Revision History

- 2026-06-28: Initial accepted decision.
