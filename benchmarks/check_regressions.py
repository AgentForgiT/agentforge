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


def load_thresholds(path: Path | None) -> tuple[float, dict[str, float]]:
    """Load thresholds config (ADR-0035): returns (default, per-name overrides).

    Resolution order: per-benchmark name > config default > 10.
    Raises ValueError with a clear message on invalid config.
    """
    if path is None:
        return 10.0, {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"thresholds config is not valid JSON: {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("thresholds config must be an object")
    default = data.get("default", 10.0)
    if not isinstance(default, (int, float)) or isinstance(default, bool) or default <= 0:
        raise ValueError("thresholds.default must be a positive number")
    overrides: dict[str, float] = {}
    benchmarks = data.get("benchmarks", {})
    if not isinstance(benchmarks, dict):
        raise ValueError("thresholds.benchmarks must be an object")
    for name, value in benchmarks.items():
        if not isinstance(value, (int, float)) or isinstance(value, bool) or value <= 0:
            raise ValueError(f"threshold for '{name}' must be a positive number")
        overrides[name] = float(value)
    return float(default), overrides


def _threshold_for(name: str, default: float, overrides: dict[str, float]) -> float:
    return overrides.get(name, default)


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
    overrides: dict[str, float] | None = None,
) -> tuple[list[_Verdict], bool]:
    """Compare two results documents; returns (verdicts, has_regression).

    threshold_pct is the fallback default; overrides map benchmark names
    to their own thresholds (ADR-0035: per-name > default > 10).
    """
    overrides = overrides or {}
    prev_values, prev_units = _benchmarks_map(previous)
    curr_values, _ = _benchmarks_map(current)

    verdicts: list[_Verdict] = []
    has_regression = False

    for name in sorted(prev_values.keys() & curr_values.keys()):
        pv = prev_values[name]
        cv = curr_values[name]
        better = _better_direction(name)
        threshold = _threshold_for(name, threshold_pct, overrides)
        if pv == 0:
            delta_pct = 0.0
        else:
            delta_pct = ((cv - pv) / pv) * 100.0

        regressed = False
        if better == "lower":
            regressed = cv > pv * (1 + threshold / 100.0)
        else:
            regressed = cv < pv * (1 - threshold / 100.0)

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
    parser.add_argument("--threshold", type=float, default=None, help="fallback regression threshold in percent (default 10)")
    parser.add_argument("--thresholds", type=Path, default=None, help="thresholds config JSON (ADR-0035)")
    args = parser.parse_args()

    try:
        config_default, overrides = load_thresholds(args.thresholds)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    fallback = args.threshold if args.threshold is not None else config_default

    previous = json.loads(args.previous.read_text(encoding="utf-8"))
    current = json.loads(args.current.read_text(encoding="utf-8"))
    verdicts, has_regression = check_regressions(previous, current, fallback, overrides)

    prev_names = set(b.get("name") for b in previous.get("benchmarks", []))
    curr_names = set(b.get("name") for b in current.get("benchmarks", []))
    skipped = sorted(s for s in prev_names.symmetric_difference(curr_names) if isinstance(s, str))

    print(render(verdicts, skipped))
    return 1 if has_regression else 0


if __name__ == "__main__":
    raise SystemExit(main())
