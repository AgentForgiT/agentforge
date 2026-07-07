# Product Foundation Hygiene MVP Requirements

Metadata:

- Status: Draft
- Phase: Genesis Sprint 15
- Related issues: #68, #67, #65, #66, #69
- Related decisions: ADR-0001, DEC-0005
- Related policy: `docs/release-policy.md`
- Last updated: 2026-07-06

## Purpose

Define the requirements for formalizing the AgentForge product foundation after the first fourteen Genesis releases.

This document exists so Sprint 15 closes small but important repository-product gaps before the project continues into deeper gateway, provider, MCP, benchmark, website, and community work.

## Scope

In scope:

- product backlog and epic source of truth
- canonical standards files under `.agentforge/standards/`
- repository hygiene files for editor and Git behavior
- bootstrap validation coverage for the new foundation artifacts
- documentation and release notes

Out of scope:

- changing application runtime behavior
- adding new gateway features
- changing AICS validation rules
- introducing package managers or formatter dependencies
- migrating to public `0.1.0` release semantics
- reorganizing repositories outside the canonical monorepo

## Background

AgentForge has evolved from a bootstrap repository into a release-managed engineering product. Genesis releases now include governance, AICS, CLI, gateway, tests, examples, CI validation, and release notes.

The foundation still has a few gaps:

- `.agentforge/standards/` exists but contains no canonical standard documents
- backlog and epics are implied by roadmap and issues, but not recorded as a durable product artifact
- `.editorconfig` and `.gitattributes` are absent
- bootstrap validation does not yet require those product-foundation files

Sprint 15 should close those gaps without adding runtime complexity.

## User Workflows

The MVP must support these workflows:

- A contributor can find the canonical product backlog and long-term epic map.
- A contributor can find canonical engineering and documentation standards under `.agentforge/standards/`.
- Editors and Git clients have explicit baseline whitespace and line-ending guidance.
- CI validates that required product-foundation artifacts remain present.
- Release notes explain the scope and limitations of the hygiene sprint.

## Foundation Requirements

The repository must include:

- `.editorconfig`
- `.gitattributes`
- `.agentforge/backlog.md`
- `.agentforge/standards/engineering.md`
- `.agentforge/standards/documentation.md`
- `.agentforge/decisions/0005-product-foundation-hygiene.md`

The product backlog must:

- identify the durable AgentForge epics
- distinguish strategic backlog from sprint execution issues
- preserve the Genesis release-train framing
- avoid pretending every future feature has already been designed

The standards files must:

- live under `.agentforge/standards/`
- be treated as canonical by contributors and AI assistants
- preserve the Constitution, Charter, ADR, RFC, standards, code authority hierarchy
- be summarized by public docs where helpful

The hygiene files must:

- keep defaults simple and portable
- prefer LF line endings for repository text files
- preserve CRLF where Windows command files require it
- avoid formatter or runtime dependencies during Genesis

## Compatibility Requirements

Sprint 15 must preserve:

- current CLI behavior
- current gateway behavior
- current AICS validation behavior
- current release process
- current GitHub Actions workflow
- current monorepo-first repository strategy

## Testing and CI Requirements

Validation must cover:

- presence of the new backlog, standards, decision, and hygiene files
- existing bootstrap file requirements
- canonical AICS validation
- minimal AICS example validation
- CLI tests
- CLI install smoke test
- gateway tests
- whitespace validation through `git diff --check`

CI must not require network access, provider credentials, or live upstream providers.

## Documentation Requirements

Documentation must explain:

- where product backlog and epics live
- where canonical standards live
- how public docs relate to `.agentforge/standards/`
- which repo hygiene files are required
- current Sprint 15 limitations

## Acceptance Criteria

Issue #68 is complete when:

- this requirements document exists under `.agentforge/requirements/`
- it references DEC-0005
- it defines Sprint 15 product foundation scope before implementation completes

The Sprint 15 product foundation milestone is complete when:

- issue #67 records DEC-0005
- issue #65 implements backlog, standards, and hygiene files
- issue #66 validates the foundation locally and in CI
- issue #69 documents the foundation and prepares `Genesis-0.0.15`

## Examples

Expected backlog location:

```text
.agentforge/backlog.md
```

Expected standards locations:

```text
.agentforge/standards/engineering.md
.agentforge/standards/documentation.md
```

Expected validation command:

```bash
python scripts/validate_bootstrap.py
```

## Best Practices

- Keep product backlog strategic and durable.
- Keep sprint issues concrete and releasable.
- Keep standards canonical under `.agentforge/standards/`.
- Keep public docs as human-facing summaries rather than competing sources of truth.
- Keep hygiene files minimal until stronger tooling requirements exist.

## Risks

- Overly detailed backlog entries can become stale quickly.
- Standards split between docs and `.agentforge/standards/` can drift unless source-of-truth rules are explicit.
- Line-ending policy changes can create noisy diffs if unmanaged.
- Treating hygiene work as a feature sprint can distract from product delivery unless the scope stays tight.

## References

- `.agentforge/constitution.md`
- `.agentforge/charter.md`
- `.agentforge/architecture.md`
- `.agentforge/backlog.md`
- `.agentforge/standards/engineering.md`
- `.agentforge/standards/documentation.md`
- `.agentforge/decisions/0005-product-foundation-hygiene.md`
- `docs/coding-standards.md`
- `docs/documentation-standards.md`

## Revision History

- 2026-07-06: Initial requirements draft for Genesis Sprint 15.
