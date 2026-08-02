#!/usr/bin/env python3
"""AgentForge benchmark history collector (ADR-0033).

Fetches each release's results.json asset (GitHub public API + download
URLs, stdlib only) and merges them into benchmarks/history.json with
per-benchmark series and release-to-release deltas.

Usage: python benchmarks/collect_history.py [--repo AgentForgiT/agentforge] [--tags 0.3.0 0.4.0 ...] [--out PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = "0.1"

# benchmark name -> direction: lower is better (latency/timing) vs higher (throughput)
LOWER_BETTER_MARKERS = ("latency", "median_ms", "throughput_per_sec")
HIGHER_BETTER_MARKERS = ("throughput", "per_sec")


def _better_direction(name: str) -> str:
    lowered = name.lower()
    if "throughput" in lowered or "per_sec" in lowered:
        return "higher"
    return "lower"


def collect_history(
    repo: str,
    tags: list[str],
    fetch_json: Callable[[str], dict[str, Any]],
) -> dict[str, Any]:
    """Build history.json from per-release results fetch functions.

    fetch_json(url) -> parsed results.json dict (injectable for tests).
    """
    releases: list[dict[str, Any]] = []
    benchmark_units: dict[str, str] = {}

    for tag in tags:
        url = f"https://github.com/{repo}/releases/download/{tag}/results.json"
        try:
            results = fetch_json(url)
        except Exception:
            continue  # release without results (e.g. pre-0.3.0) is skipped
        benchmarks: dict[str, float] = {}
        for bench in results.get("benchmarks", []):
            name = bench.get("name")
            value = bench.get("value")
            if isinstance(name, str) and isinstance(value, (int, float)):
                benchmarks[name] = float(value)
                benchmark_units.setdefault(name, bench.get("unit", ""))
        if benchmarks:
            releases.append(
                {
                    "tag": tag,
                    "timestamp": results.get("timestamp", ""),
                    "benchmarks": benchmarks,
                }
            )

    trends: list[dict[str, Any]] = []
    for name, unit in sorted(benchmark_units.items()):
        values = [
            {"tag": release["tag"], "value": release["benchmarks"].get(name)}
            for release in releases
            if name in release["benchmarks"]
        ]
        trends.append(
            {
                "name": name,
                "unit": unit,
                "better": _better_direction(name),
                "values": values,
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "releases": releases,
        "trends": trends,
    }


def validate_history(history: dict[str, Any]) -> None:
    """Minimal structural validation (stdlib only)."""
    if history.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("schema_version mismatch")
    for field in ("releases", "trends"):
        if field not in history:
            raise ValueError(f"missing field: {field}")
    if not isinstance(history["releases"], list):
        raise ValueError("releases must be a list")
    for trend in history["trends"]:
        for field in ("name", "unit", "better", "values"):
            if field not in trend:
                raise ValueError(f"trend missing {field}: {trend}")
        if trend["better"] not in ("lower", "higher"):
            raise ValueError(f"trend better must be lower|higher: {trend['name']}")


def _fetch_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310
        body = json.loads(response.read().decode("utf-8"))
    if not isinstance(body, dict):
        raise ValueError("non-object response")
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentForge benchmark history collector")
    parser.add_argument("--repo", default="AgentForgiT/agentforge")
    parser.add_argument("--tags", nargs="+", default=["0.5.0", "0.4.0", "0.3.0"])
    parser.add_argument("--out", type=Path, default=ROOT / "benchmarks" / "history.json")
    args = parser.parse_args()

    history = collect_history(args.repo, args.tags, _fetch_json)
    validate_history(history)
    args.out.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")
    print(f"history written to {args.out} ({len(history['releases'])} releases, {len(history['trends'])} trends)")
    for trend in history["trends"]:
        series = ", ".join(f"{v['tag']}:{v['value']}" for v in trend["values"])
        print(f"  {trend['name']} ({trend['better']}): {series}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
