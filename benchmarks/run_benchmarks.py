#!/usr/bin/env python3
"""AgentForge offline benchmark harness (ADR-0030).

Runs deterministic, offline suites against the gateway (mock provider,
in-process), the CLI, and AICS validation; validates the output against
benchmarks/results.schema.json; writes benchmarks/results.json.

Usage: python benchmarks/run_benchmarks.py [--samples N] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import platform
import statistics
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "gateway" / "src"))
sys.path.insert(0, str(ROOT / "apps" / "cli" / "src"))

SCHEMA_VERSION = "0.1"


def _median(samples: list[float]) -> float:
    return statistics.median(samples)


def _time_once(fn: Any) -> float:
    start = time.perf_counter()
    fn()
    return (time.perf_counter() - start) * 1000.0  # ms


def bench_gateway(samples: int) -> list[dict[str, Any]]:
    """In-process gateway chat completions against the mock provider."""
    from agentforge_gateway.app import GatewayApp
    from agentforge_gateway.config import DEFAULT_CONFIG

    app = GatewayApp(DEFAULT_CONFIG)
    body = {
        "model": "mock-coder",
        "messages": [{"role": "user", "content": "Benchmark the gateway deterministically."}],
        "stream": False,
    }

    latencies: list[float] = []
    for _ in range(samples):
        start = time.perf_counter()
        app.chat_completions(body)
        latencies.append((time.perf_counter() - start) * 1000.0)

    median_ms = _median(latencies)
    tps = 1000.0 / median_ms if median_ms > 0 else 0.0
    return [
        {
            "name": "gateway.chat_completion.median_latency_ms",
            "unit": "ms",
            "value": round(median_ms, 2),
            "samples": [round(s, 2) for s in latencies],
        },
        {
            "name": "gateway.chat_completion.throughput_per_sec",
            "unit": "completions/s",
            "value": round(tps, 2),
            "samples": [],
        },
    ]


def bench_cli(samples: int) -> list[dict[str, Any]]:
    """CLI command wall-clock timing on a temp scaffolded project."""
    from agentforge_cli.cli import main as cli_main
    from agentforge_cli.scaffolding import init_context

    validate_times: list[float] = []
    twin_times: list[float] = []

    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "bench-project"
        init_context(project)

        def run_validate() -> None:
            cli_main(["validate-context", str(project)])

        def run_twin() -> None:
            cli_main(["build-twin", str(project)])

        for _ in range(samples):
            validate_times.append(_time_once(run_validate))
        for _ in range(samples):
            twin_times.append(_time_once(run_twin))

    return [
        {
            "name": "cli.validate_context.median_ms",
            "unit": "ms",
            "value": round(_median(validate_times), 2),
            "samples": [round(s, 2) for s in validate_times],
        },
        {
            "name": "cli.build_twin.median_ms",
            "unit": "ms",
            "value": round(_median(twin_times), 2),
            "samples": [round(s, 2) for s in twin_times],
        },
    ]


def bench_aics(samples: int) -> list[dict[str, Any]]:
    """AICS validation timing on a scaffolded project."""
    from agentforge_cli.validation import validate_context

    times: list[float] = []
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "aics-bench"
        init_project(project)
        for _ in range(samples):
            times.append(_time_once(lambda: validate_context(project)))
    return [
        {
            "name": "aics.validate.median_ms",
            "unit": "ms",
            "value": round(_median(times), 2),
            "samples": [round(s, 2) for s in times],
        }
    ]


def init_project(project: Path) -> None:
    from agentforge_cli.scaffolding import init_context

    init_context(project)


def validate_against_schema(results: dict[str, Any]) -> None:
    """Minimal structural validation (stdlib only, no jsonschema dep)."""
    if results.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("schema_version mismatch")
    for required in ("suite", "environment", "timestamp", "benchmarks"):
        if required not in results:
            raise ValueError(f"missing field: {required}")
    if not isinstance(results["benchmarks"], list) or not results["benchmarks"]:
        raise ValueError("benchmarks must be a non-empty list")
    for bench in results["benchmarks"]:
        for field in ("name", "unit", "value", "samples"):
            if field not in bench:
                raise ValueError(f"benchmark missing {field}: {bench}")


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentForge offline benchmark harness")
    parser.add_argument("--samples", type=int, default=5, help="samples per benchmark (default 5)")
    parser.add_argument("--out", type=Path, default=ROOT / "benchmarks" / "results.json")
    args = parser.parse_args()

    results: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "suite": "offline",
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
        },
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "benchmarks": [],
    }

    for suite_fn in (bench_gateway, bench_cli, bench_aics):
        results["benchmarks"].extend(suite_fn(args.samples))

    validate_against_schema(results)
    args.out.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"benchmarks written to {args.out} ({len(results['benchmarks'])} benchmarks)")
    for bench in results["benchmarks"]:
        print(f"  {bench['name']}: {bench['value']} {bench['unit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
