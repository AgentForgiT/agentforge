# Benchmark Regression Gate

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 42 |
| Issues | #185, #186, #187, #188, #189 |
| Related | ADR-0030 (harness), ADR-0033 (trends), ADR-0034, DEC-0006 (semver) |

## Purpose

The trends collector (ADR-0033) shows release-to-release deltas; the **regression gate** makes them enforceable: a release fails if a benchmark regressed beyond a threshold relative to the previous release. The platform stops lying about its own performance — CI is the referee.

## Requirements

R1. **`benchmarks/check_regressions.py`**:
   - Inputs: `--previous <results.json>`, `--current <results.json>`, `--threshold <percent>` (default 10).
   - For each benchmark present in both files:
     - `lower`-better (latency/timing): current > previous × (1 + threshold/100) → **REGRESSED**.
     - `higher`-better (throughput): current < previous × (1 − threshold/100) → **REGRESSED**.
     - Otherwise → OK (improvements and within-threshold changes never fail).
   - Benchmarks only in one file → skipped with a note.
   - Output: per-benchmark verdict line (`OK` / `REGRESSED` with Δ%) and a summary.
   - Exit 0 when no regressions; exit 1 when any regression exceeds threshold.
R2. **Direction reuse**: import `_better_direction` from `collect_history` (single source of truth).
R3. **CI wiring** (publish workflow benchmarks job): after running the harness, fetch the previous release's `results.json` (via `gh release download` or the download URL) and run the gate against the freshly produced `results.json`. The job fails on regression — blocking the release's automated pipeline (the release can still be force-published manually, but the gate is visible).
R4. Offline-testable: fixtures for regression / improvement / within-threshold / missing-benchmark cases; no network in tests.

## Acceptance Criteria

- [ ] Gate detects a >threshold regression in both directions and exits 1
- [ ] Improvements and within-threshold changes exit 0
- [ ] Benchmarks missing from either file are skipped, not failed
- [ ] CI job runs the gate and fails on regression
- [ ] Full suite passes offline; CI green
