# ADR-0033: Benchmark Trends Boundary

Metadata:

- Status: Accepted
- Date: 2026-08-01
- Deciders: AgentForge maintainers
- Issues: #180, #181, #182, #183, #184
- Related: ADR-0030 (harness), DEC-0006 (semver)

## Context

Since 0.3.0, every release carries a schema-validated `results.json` (ADR-0030). The numbers exist; the trend does not. The observatory should show whether the gateway/CLI is getting faster or slower across releases — but trends must not compromise the harness's reproducibility or add network to the default path.

## Decision

Add a **history collector** separate from the harness:

- `benchmarks/collect_history.py` fetches each release's `results.json` asset (stdlib `urllib`, GitHub public API + download URLs), merges them into `benchmarks/history.json` with per-benchmark series and release-to-release deltas.
- **`better` direction is derived per benchmark**: latency/timing names → `lower`; throughput names → `higher`. The observatory colors deltas accordingly (↓ good for latency, ↑ good for throughput).
- `history.schema.json` validates the output before write.
- The observatory renders a trend table (rows = benchmarks, columns = releases, delta arrows) from a static `docs/results/history.json` copy.
- **Offline-testable**: the collector's fetch is injectable; tests use fixtures, no network. The collector is a publishing tool, not part of the harness (ADR-0030's offline-first harness is untouched).

## Consequences

- Release-to-release performance stories become visible: "gateway latency ↓ 12% since 0.3.0" with evidence.
- The trend artifact is versioned and schema-validated like the results it aggregates.
- No network enters the default test path; the collector runs on demand (or in CI when publishing) to refresh the site copy.

## Alternatives Considered

- **Observatory fetches release assets live** — rejected: GitHub asset URLs + CORS are not reliable for browser fetch; static copies served from the site are deterministic.
- **Extend the harness to emit trends** — rejected: the harness is offline and per-run; trends are cross-run by nature — a separate collector is the honest separation.

## Deferred

- Trend thresholds / regression alerts (a future CI gate: "fail if gateway latency regressed > 10%").
- Long-term storage beyond release assets.
