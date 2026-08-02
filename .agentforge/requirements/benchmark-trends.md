# Benchmark Trends: Release-to-Release

| | |
|---|---|
| Status | Draft |
| Sprint | Sprint 41 |
| Issues | #180, #181, #182, #183, #184 |
| Related | ADR-0030 (harness), ADR-0033, DEC-0006 (semver) |

## Purpose

The observatory has per-release `results.json` (attached by the publish workflow since 0.3.0). This sprint makes the numbers tell a story: a **history collector** merges per-release results into a trend artifact, and the observatory renders release-to-release deltas.

## Requirements

R1. **History collector** (`benchmarks/collect_history.py`):
   - Fetches `results.json` from each release's assets (GitHub public API + download URLs via stdlib `urllib`; injectable fetch for offline tests).
   - Default repo: `AgentForgiT/agentforge`, tags from `0.3.0` onward (the first release with results).
   - Merges into `benchmarks/history.json`:
     ```json
     {
       "schema_version": "0.1",
       "releases": [{"tag": "0.5.0", "timestamp": "...", "benchmarks": {"name": value}}],
       "trends": [{"name": "...", "unit": "...", "better": "lower"|"higher", "values": [{"tag": "...", "value": ...}]}]
     }
     ```
   - `better` is derived per benchmark name: latency/timing → `lower`; throughput → `higher`.
R2. **`history.schema.json`**: validates the collector output before write.
R3. **Observatory trends section**: renders the history table (rows = benchmarks, columns = releases) with delta arrows (↓/↑) colored by whether the change is good; a note explains the `better` direction.
R4. **Serving**: a static `docs/results/history.json` on the site (like `results.json`), refreshed by the collector when new releases publish.
R5. Offline-testable: the collector's fetch is injectable; tests use fixture JSON, no network.

## Acceptance Criteria

- [ ] Collector produces schema-validated `history.json` from fixture releases
- [ ] Delta math correct: `better: lower` shows ↓ as good, `higher` shows ↑ as good
- [ ] Trend table renders on the observatory with per-release columns
- [ ] `docs/results/history.json` served and consumed
- [ ] Full suite passes offline; CI green
