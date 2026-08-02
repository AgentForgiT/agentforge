# ADR-0034: Benchmark Regression Gate

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #185, #186, #187, #188, #189
- Related: ADR-0030 (harness), ADR-0033 (trends), DEC-0006 (semver)

## Context

The trends collector (ADR-0033) proves performance stories after the fact. The platform's own claims ("gateway latency ↓ since 0.3.0") deserve a referee: a release should be flagged when it regresses a benchmark beyond a threshold versus the previous release. This is the natural enforcement half of the benchmark pipeline.

## Decision

Add `benchmarks/check_regressions.py`, a release gate:

- Compares the current release's `results.json` against the previous release's.
- For each benchmark present in both:
  - **lower**-better (latency/timing): current > previous × (1 + threshold/100) → REGRESSED.
  - **higher**-better (throughput): current < previous × (1 − threshold/100) → REGRESSED.
  - Otherwise OK; improvements and within-threshold changes never fail.
- Benchmarks missing from either file are skipped with a note, not failed.
- Default threshold 10%; configurable via `--threshold`.
- Direction comes from `collect_history._better_direction` (one source of truth).
- Exit 0 on no regressions, exit 1 on any regression beyond threshold.

CI wiring: the publish workflow's benchmarks job runs the harness, then fetches the previous release's `results.json` and runs the gate against the fresh output. The job fails on regression — the release pipeline is blocked visibly (manual force-publish remains possible, but the gate is recorded).

## Consequences

- Performance regressions become a release-blocking signal, not a footnote.
- The gate is deterministic and offline-testable (fixtures; direction + threshold are pure math).
- Harness (ADR-0030) and collector (ADR-0033) are untouched; the gate is a consumer of the same artifacts.

## Alternatives Considered

- **Flaky-percentage allowances per benchmark** — rejected: YAGNI until real variance data exists; a single default threshold with a flag is honest v1.
- **Block releases entirely (hard gate in release creation)** — rejected: releases are created by the maintainer flow; the CI gate is the visible referee without a new release mechanism.

## Deferred

- Per-benchmark thresholds.
- Variance-aware comparison (statistical significance over samples).
- Trend-based regression detection beyond adjacent releases.
