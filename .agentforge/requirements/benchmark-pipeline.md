# Benchmark Pipeline

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 38 |
| Issues | #165, #166, #167, #168, #169 |
| Related | ADR-0030, Benchmark Observatory (website), DEC-0006 (semver) |

## Purpose

Give the Benchmark Observatory real data: a **reproducible benchmark harness** in the monorepo that measures the gateway and CLI (offline, deterministic), emits a schema-validated `results.json`, publishes it with each release, and lets the website consume it. The observatory stops being a static registry and starts carrying AgentForge's own measured numbers.

## Requirements

R1. **Harness** (`benchmarks/`): a stdlib Python runner with three offline suites:
   - `gateway`: chat-completion latency (median/p95) + throughput (completions/sec, tokens/sec) against the mock provider via an in-process app (no network).
   - `cli`: `validate-context`, `init-context` (temp project), `build-twin` wall-clock timing.
   - `aics`: AICS validation of a scaffolded project (files + front matter checks).
R2. **Results schema** (`benchmarks/results.schema.json`): versioned artifact with `suite`, `environment` (python version, platform), `timestamp`, and per-benchmark `{name, unit, value, samples}`. Validated before write.
R3. **`run_benchmarks.py`**: runs all suites, validates against the schema, writes `benchmarks/results.json`. Deterministic enough that re-runs are comparable (medians over N samples).
R4. **CI**: a job runs the harness, validates the schema, and uploads `results.json` as a release asset on tags (reusing the publish workflow pattern). Not required for the main validate workflow (keeps it fast), but green when run.
R5. **Observatory consumption**: the website fetches the published `results.json` (static copy served like `twin.json`) and renders AgentForge's own measured numbers alongside the live probes.
R6. **Live model evals are out of scope**: no provider keys, no network, no LLM runs in the harness. A future optional suite can extend it (documented in ADR-0030).

## Acceptance Criteria

- [ ] `run_benchmarks.py` produces schema-validated `results.json` offline
- [ ] Three suites run deterministically (mock provider, no network)
- [ ] CI job runs the harness on demand and attaches results to releases
- [ ] Observatory page renders the published results (static results.json served)
- [ ] Full suite passes offline; CI green
