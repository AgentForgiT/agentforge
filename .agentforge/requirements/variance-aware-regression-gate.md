# Variance-Aware Regression Gate

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 46 |
| Issues | #205, #206, #207, #208, #209 |
| Related | ADR-0034 (gate), ADR-0035 (thresholds), ADR-0038, DEC-0006 (semver) |

## Purpose

The regression gate (ADR-0034/0035) flags a benchmark when its median moves beyond a threshold. That's effect-size only — a jittery benchmark (CLI wall-clock on a shared runner) can cross a 20% threshold by noise. This sprint adds the **statistical half**: a regression is flagged only when the threshold is exceeded **and** the sample difference is statistically significant (Welch's t-test, stdlib only).

## Requirements

R1. **Welch's t-test p-value** (stdlib only):
   - Compute over the `samples` arrays from both results documents.
   - Implementation uses `math.lgamma` + the regularized incomplete beta via continued fraction (Numerical Recipes `betacf`/`betai`) — no scipy, no new deps.
   - Two-tailed p-value; Satterthwaite degrees of freedom.
R2. **Flag rule**: a benchmark is REGRESSED only when BOTH hold:
   - threshold exceeded (existing ADR-0034 rule, per-benchmark thresholds from ADR-0035), AND
   - `p_value < significance` (default `0.05`).
   Improvements never fail (unchanged).
R3. **Insufficient samples**: if either side has < 2 samples, significance is unknown → fall back to threshold-only (current behavior), with the verdict noting "threshold-only".
R4. **CLI**: `--significance 0.05` (default); `--significance 1.0` disables the statistical check (threshold-only).
R5. Output: verdicts include `p_value` and `significant` (or `threshold-only`) so the report is auditable.

## Acceptance Criteria

- [ ] Low-variance benchmark crossing threshold significantly → REGRESSED
- [ ] High-variance benchmark crossing threshold by noise → OK (not significant)
- [ ] Insufficient samples → threshold-only fallback, no crash
- [ ] `--significance 1.0` disables statistics (threshold-only)
- [ ] `p_value`/`significant` appear in the verdict output
- [ ] Full suite passes offline; CI green
