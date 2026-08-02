from __future__ import annotations

import json
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

from collect_history import _better_direction, collect_history, validate_history


def make_results(benchmarks: list[dict[str, object]], timestamp: str = "2026-08-01T00:00:00Z") -> dict[str, object]:
    return {
        "schema_version": "0.1",
        "suite": "offline",
        "environment": {"python": "3.11", "platform": "test"},
        "timestamp": timestamp,
        "benchmarks": benchmarks,
    }


class BetterDirectionTests(unittest.TestCase):
    def test_latency_is_lower_better(self) -> None:
        self.assertEqual(_better_direction("gateway.chat_completion.median_latency_ms"), "lower")

    def test_throughput_is_higher_better(self) -> None:
        self.assertEqual(_better_direction("gateway.chat_completion.throughput_per_sec"), "higher")

    def test_validate_median_is_lower_better(self) -> None:
        self.assertEqual(_better_direction("cli.validate_context.median_ms"), "lower")


class CollectHistoryTests(unittest.TestCase):
    def _fixture_fetch(self, fixtures: dict[str, dict[str, object]]):
        def fetch_json(url: str) -> dict[str, object]:
            tag = url.split("/")[-2]
            if tag not in fixtures:
                raise FileNotFoundError(tag)
            return fixtures[tag]

        return fetch_json

    def test_merges_releases_and_builds_trends(self) -> None:
        fixtures = {
            "0.3.0": make_results(
                [
                    {"name": "gateway.chat_completion.median_latency_ms", "unit": "ms", "value": 0.05, "samples": []},
                    {"name": "gateway.chat_completion.throughput_per_sec", "unit": "completions/s", "value": 20000.0, "samples": []},
                ]
            ),
            "0.4.0": make_results(
                [
                    {"name": "gateway.chat_completion.median_latency_ms", "unit": "ms", "value": 0.04, "samples": []},
                    {"name": "gateway.chat_completion.throughput_per_sec", "unit": "completions/s", "value": 25000.0, "samples": []},
                ]
            ),
        }
        history = collect_history("AgentForgiT/agentforge", ["0.3.0", "0.4.0"], self._fixture_fetch(fixtures))
        validate_history(history)
        self.assertEqual(len(history["releases"]), 2)
        trends = {t["name"]: t for t in history["trends"]}
        latency = trends["gateway.chat_completion.median_latency_ms"]
        self.assertEqual(latency["better"], "lower")
        self.assertEqual([v["value"] for v in latency["values"]], [0.05, 0.04])
        self.assertEqual(latency["values"][0]["tag"], "0.3.0")
        throughput = trends["gateway.chat_completion.throughput_per_sec"]
        self.assertEqual(throughput["better"], "higher")

    def test_skips_releases_without_results(self) -> None:
        fixtures = {"0.4.0": make_results([{"name": "x", "unit": "ms", "value": 1.0, "samples": []}])}
        history = collect_history("r", ["0.3.0", "0.4.0"], self._fixture_fetch(fixtures))
        self.assertEqual(len(history["releases"]), 1)
        self.assertEqual(history["releases"][0]["tag"], "0.4.0")

    def test_skips_releases_with_empty_benchmarks(self) -> None:
        fixtures = {"0.4.0": make_results([])}
        history = collect_history("r", ["0.4.0"], self._fixture_fetch(fixtures))
        self.assertEqual(history["releases"], [])
        self.assertEqual(history["trends"], [])


class ValidateHistoryTests(unittest.TestCase):
    def test_rejects_bad_better_direction(self) -> None:
        history = {
            "schema_version": "0.1",
            "releases": [],
            "trends": [{"name": "x", "unit": "ms", "better": "sideways", "values": []}],
        }
        with self.assertRaises(ValueError):
            validate_history(history)

    def test_rejects_missing_schema_version(self) -> None:
        with self.assertRaises(ValueError):
            validate_history({"releases": [], "trends": []})


if __name__ == "__main__":
    unittest.main()
