# ADR-0030: Benchmark Pipeline Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #165, #166, #167, #168, #169
- Related: Benchmark Observatory (website), DEC-0006 (semver), ADR-0015 (logging, no creds)

## Context

The Benchmark Observatory is a static registry with live local probes; it has no AgentForge-measured data behind it. The vision calls for benchmark pipelines. The tempting path is LLM evals (coding benchmarks etc.) — those require providers, keys, network, and are non-deterministic, colliding with the project's offline-first, reproducible ethos.

## Decision

Add a **reproducible, offline-first benchmark harness** in the monorepo:

- `benchmarks/` stdlib runner with three suites: `gateway` (mock-provider latency/throughput, in-process, no network), `cli` (validate/init/build-twin wall-clock), `aics` (validation timing on a scaffolded project).
- **Results schema** (`benchmarks/results.schema.json`): versioned, validated before write; `run_benchmarks.py` emits `benchmarks/results.json` with suite, environment, timestamp, and per-benchmark `{name, unit, value, samples}`.
- **CI**: an on-demand job runs the harness, validates the schema, and uploads `results.json` as a release asset on tags (reusing the publish workflow's asset pattern). Not part of the default validate workflow (keeps it fast).
- **Observatory consumption**: the website serves a static copy of the published `results.json` (like `twin.json`) and renders AgentForge's measured numbers beside the live probes.

Boundary rules:

- **Offline-only**: mock provider, in-process app, no network, no credentials, no LLM runs. Live model evals are explicitly deferred (a future optional suite, never required in default CI).
- **Reproducible**: medians over N samples; environment recorded so re-runs are comparable, not just numbers.
- **Schema-validated**: an unvalidated artifact cannot be trusted; the schema is the contract.

## Consequences

- The observatory gains real, honest, comparable numbers for the gateway and CLI — the "AgentForge-measured" half the vision wants.
- Benchmarks are reproducible by anyone with a checkout; no keys, no network.
- Live model evals stay out of the default path, preserving the offline ethos.

## Alternatives Considered

- **LLM coding evals (HumanEval etc.) in CI** — rejected: needs providers/keys/network, non-deterministic, expensive; deferred as an optional suite.
- **A separate benchmarks repo** — rejected: the harness measures the monorepo; it belongs beside the code.
- **No schema (freeform JSON)** — rejected: unvalidated artifacts cannot be compared across releases.

## Deferred

- Live model evals (optional suite with provider config; never in default CI).
- Historical trend storage/dashboards (the observatory can evolve once data exists).
- Benchmark comparisons across releases (release-to-release diffs).
