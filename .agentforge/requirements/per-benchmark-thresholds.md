# Per-Benchmark Regression Thresholds

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 43 |
| Issues | #190, #191, #192, #193, #194 |
| Related | ADR-0034 (gate), ADR-0035, DEC-0006 (semver) |

## Purpose

The regression gate (ADR-0034) uses a single global threshold (10%). Different benchmarks have different natural variance: gateway latency is stable to 1%, CLI timing on a shared runner can jitter 20%. This sprint makes thresholds **per-benchmark**, with a global default retained.

## Requirements

R1. **Threshold config** (`benchmarks/thresholds.json`, checked in):
   ```json
   {
     "default": 10,
     "benchmarks": {
       "gateway.chat_completion.median_latency_ms": 5,
       "cli.validate_context.median_ms": 20
     }
   }
   ```
   `default` is the global fallback (10 if absent); per-name entries override it.
R2. **Resolution order**: per-name threshold > global default > 10 (CLI default).
R3. **CLI**: `check_regressions.py` gains `--thresholds <path>` (config file). `--threshold` remains as the inline global override (highest precedence when both given? no — define: inline `--threshold` overrides the config `default`, but per-name config entries still win over the inline default).
R4. Validation: config must be an object with optional `default` (positive number) and optional `benchmarks` (object of positive numbers); invalid → clear error, exit 2 (usage).
R5. Missing benchmark names fall back to default (never crash).
R6. All tests offline; existing gate tests keep passing (default 10 unchanged).

## Acceptance Criteria

- [ ] Per-name threshold overrides the global default
- [ ] Missing names use the default; absent config uses 10
- [ ] Invalid config → exit 2 with a clear message
- [ ] Inline `--threshold` behaves as the fallback default when no config
- [ ] Full suite passes offline; CI green
