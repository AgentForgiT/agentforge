#!/usr/bin/env python3
"""AgentForge benchmark regression gate (ADR-0034).

Compares the current release's results.json against the previous
release's and fails (exit 1) when a benchmark regressed beyond the
threshold. lower-better increases and higher-better decreases fail;
improvements and within-threshold changes never fail.

Usage: python benchmarks/check_regressions.py --previous prev.json --current cur.json [--threshold 10]
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

from collect_history import _better_direction  # noqa: E402


@dataclass(frozen=True)
class _Verdict:
    name: str
    unit: str
    better: str
    previous: float | None
    current: float | None
    delta_pct: float | None
    regressed: bool


def _benchmarks_map(results: dict[str, Any]) -> tuple[dict[str, float], dict[str, str]]:
    values: dict[str, float] = {}
    units: dict[str, str] = {}
    for bench in results.get("benchmarks", []):
        name = bench.get("name")
        value = bench.get("value")
        if isinstance(name, str) and isinstance(value, (int, float)):
            values[name] = float(value)
            units[name] = bench.get("unit", "")
    return values, units


def check_regressions(
    previous: dict[str, Any],
    current: dict[str, Any],
    threshold_pct: float = 10.0,
) -> tuple[list[_Verdict], bool]:
    """Compare two results documents; returns (verdicts, has_regression)."""
    prev_values, prev_units = _benchmarks_map(previous)
    curr_values, _ = _benchmarks_map(current)

    verdicts: list[_Verdict] = []
    has_regression = False

    for name in sorted(prev_values.keys() & curr_values.keys()):
        pv = prev_values[name]
        cv = curr_values[name]
        better = _better_direction(name)
        if pv == 0:
            delta_pct = 0.0
        else:
            delta_pct = ((cv - pv) / pv) * 100.0

        regressed = False
        if better == "lower":
            regressed = cv > pv * (1 + threshold_pct / 100.0)
        else:
            regressed = cv < pv * (1 - threshold_pct / 100.0)

        if regressed:
            has_regression = True
        verdicts.append(
            _Verdict(
                name=name,
                unit=prev_units.get(name, ""),
                better=better,
                previous=pv,
                current=cv,
                delta_pct=round(delta_pct, 2),
                regressed=regressed,
            )
        )
    return verdicts, has_regression


def render(verdicts: list[_Verdict], skipped: list[str]) -> str:
    lines = ["benchmark regression gate"]
    for v in verdicts:
        status = "REGRESSED" if v.regressed else "OK"
        lines.append(
            f"  [{status}] {v.name} ({v.better} better): {v.previous} -> {v.current} "
            f"({v.delta_pct:+.2f}%{(' ' + v.unit) if v.unit else ''})"
        )
    for name in skipped:
        lines.append(f"  [SKIP] {name}: missing from one side")
    lines.append(f"regressions: {sum(1 for v in verdicts if v.regressed)}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentForge benchmark regression gate")
    parser.add_argument("--previous", type=Path, required=True, help="previous release results.json")
    parser.add_argument("--current", type=Path, required=True, help="current release results.json")
    parser.add_argument("--threshold", type=float, default=10.0, help="regression threshold in percent (default 10)")
    args = parser.parse_args()

    previous = json.loads(args.previous.read_text(encoding="utf-8"))
    current = json.loads(args.current.read_text(encoding="utf-8"))
    verdicts, has_regression = check_regressions(previous, current, args.threshold)

    prev_names = set(b.get("name") for b in previous.get("benchmarks", []))
    curr_names = set(b.get("name") for b in current.get("benchmarks", []))
    skipped = sorted(prev_names.symmetric_difference(curr_names) - {None})  # type: ignore[arg-type]

    print(render(verdicts, sorted(s for s in skipped if isinstance(s, str))))
    return 1 if has_regression else 0


if __name__ == "__main__":
    raise SystemExit(main())
