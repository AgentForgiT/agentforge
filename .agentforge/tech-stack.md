# AgentForge Tech Stack

Metadata:

- Status: Draft
- Phase: Genesis
- Last updated: 2026-06-28

## Current Position

AgentForge does not lock into a full stack during Genesis Sprint 1.

## Initial Constraints

- Prefer dependency-free or low-dependency foundations during bootstrap.
- Use Python where AI gateway and automation work benefits from simple local execution.
- Use TypeScript where web, CLI, IDE, and integration ecosystems require it.
- Keep interfaces explicit so modules can move between runtimes later.

## Future Decisions

Workspace tooling, package managers, runtime versions, and build orchestration require ADRs before standardization.

Candidates include:

- Python stdlib first for early gateway prototypes
- `uv` for future Python workspace management
- `pnpm` for TypeScript packages
- Docusaurus or equivalent for website documentation

## Revision History

- 2026-06-28: Initial draft.
