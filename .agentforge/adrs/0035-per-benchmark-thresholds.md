# ADR-0035: Per-Benchmark Threshold Config

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #190, #191, #192, #193, #194
- Related: ADR-0034 (regression gate), DEC-0006 (semver)

## Context

ADR-0034's gate uses one global threshold (default 10%). Benchmarks differ in natural variance: deterministic gateway latency on the mock provider is stable to a few percent, while CLI wall-clock on a shared CI runner jitters far more. A single threshold either false-positives on jittery benchmarks or misses real regressions on stable ones.

## Decision

Add a **checked-in threshold config** (`benchmarks/thresholds.json`):

```json
{
  "default": 10,
  "benchmarks": {
    "gateway.chat_completion.median_latency_ms": 5,
    "cli.validate_context.median_ms": 20
  }
}
```

- **Resolution order**: per-benchmark name > config `default` > CLI inline `--threshold` > 10.
- `check_regressions.py` gains `--thresholds <path>`; `--threshold` remains as the inline fallback default.
- Validation: `default` must be a positive number; `benchmarks` an object of positive numbers; invalid → usage error (exit 2).
- Missing names fall back through the chain; never crash.

## Consequences

- Stable benchmarks can be gated tightly (5% latency), jittery ones loosely (20% CLI timing) — the gate becomes trustworthy for both.
- The config is versioned and reviewed like any other benchmark artifact; changing a threshold is a code review, not a flag tweak in CI.
- The single-default behavior from ADR-0034 is preserved when no config is supplied.

## Alternatives Considered

- **Inline flags per benchmark** — rejected: unmanageable at the CLI; a config file is reviewable and versioned.
- **Automatic variance-based thresholds** — rejected: requires historical sample distributions; YAGNI until real variance data exists.

## Deferred

- Variance-aware (statistical significance) comparison.
- Per-benchmark override UI in the observatory.
