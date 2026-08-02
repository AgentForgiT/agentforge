# ADR-0038: Variance-Aware Regression Gate

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #205, #206, #207, #208, #209
- Related: ADR-0034 (gate), ADR-0035 (thresholds), DEC-0006 (semver)

## Context

The regression gate (ADR-0034/0035) flags when a benchmark's value moves beyond a per-benchmark threshold. This is purely effect-size based: it cannot distinguish a real regression from noise on a jittery benchmark. CLI wall-clock on a shared CI runner varies run to run; a 20% threshold is a blunt instrument that either false-flags (tight) or misses real regressions (loose). The results documents already carry per-sample arrays (`samples`), so the data for a statistical test is already collected.

## Decision

Add the **statistical half** to the gate:

- A benchmark is REGRESSED only when **both** hold:
  1. the threshold is exceeded (existing ADR-0034 rule with ADR-0035 per-benchmark thresholds), AND
  2. the sample difference is **statistically significant** via Welch's t-test (`p_value < significance`, default `0.05`).
- Welch's t-test is implemented **stdlib-only**: two-tailed p-value from the regularized incomplete beta via `math.lgamma` + continued fraction (Numerical Recipes `betacf`/`betai`); Satterthwaite degrees of freedom. No scipy, no new dependencies.
- **Insufficient samples** (either side < 2): significance unknown → fall back to threshold-only (current behavior), verdict notes "threshold-only".
- `--significance 0.05` default; `--significance 1.0` disables statistics entirely.
- Verdicts report `p_value` and `significant`/`threshold-only` for auditability.

## Consequences

- Jittery benchmarks (CLI timing) stop false-flagging: a 25% swing on high-variance samples is not significant → OK.
- Stable benchmarks (gateway latency) flag real regressions: a 6% shift on tight samples is significant → REGRESSED.
- The threshold remains the effect-size gate; significance is the noise gate — two orthogonal filters, both must fire.
- Zero new dependencies: the t-distribution math is ~40 lines of stdlib.

## Alternatives Considered

- **Mann-Whitney U** — rejected: non-parametric but underpowered at n≈5 (min achievable p is ~1/252); Welch's t is the standard choice for comparing two small sample means and is well-documented in Numerical Recipes.
- **Significance-only (drop thresholds)** — rejected: a tiny but "significant" change at scale is still irrelevant; effect size matters.
- **Bayesian estimation** — rejected: heavy for the benefit; the frequentist p-value is a familiar, defensible gate.

## Deferred

- Paired tests when samples are paired across releases.
- Effect-size confidence intervals in the observatory.
- Trend-based regression detection beyond adjacent releases.
