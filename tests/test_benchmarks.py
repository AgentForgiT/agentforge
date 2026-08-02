from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

from run_benchmarks import (
    bench_aics,
    bench_cli,
    bench_gateway,
    validate_against_schema,
)


class BenchmarkHarnessTests(unittest.TestCase):
    def test_gateway_suite_returns_benchmarks(self) -> None:
        results = bench_gateway(samples=3)
        names = [r["name"] for r in results]
        self.assertIn("gateway.chat_completion.median_latency_ms", names)
        self.assertIn("gateway.chat_completion.throughput_per_sec", names)
        for r in results:
            self.assertGreater(r["value"], 0)

    def test_cli_suite_returns_benchmarks(self) -> None:
        results = bench_cli(samples=2)
        names = [r["name"] for r in results]
        self.assertIn("cli.validate_context.median_ms", names)
        self.assertIn("cli.build_twin.median_ms", names)

    def test_aics_suite_returns_benchmark(self) -> None:
        results = bench_aics(samples=2)
        self.assertEqual(results[0]["name"], "aics.validate.median_ms")
        self.assertGreater(results[0]["value"], 0)

    def test_schema_validation_passes_on_wellformed(self) -> None:
        results = {
            "schema_version": "0.1",
            "suite": "offline",
            "environment": {"python": "3.11", "platform": "test"},
            "timestamp": "2026-08-01T00:00:00Z",
            "benchmarks": [{"name": "x", "unit": "ms", "value": 1.0, "samples": [1.0]}],
        }
        validate_against_schema(results)  # should not raise

    def test_schema_validation_rejects_missing_field(self) -> None:
        results = {
            "schema_version": "0.1",
            "suite": "offline",
            "environment": {},
            "timestamp": "x",
            "benchmarks": [],
        }
        with self.assertRaises(ValueError):
            validate_against_schema(results)

    def test_schema_validation_rejects_bad_benchmark(self) -> None:
        results = {
            "schema_version": "0.1",
            "suite": "offline",
            "environment": {},
            "timestamp": "x",
            "benchmarks": [{"name": "y"}],  # missing unit/value/samples
        }
        with self.assertRaises(ValueError):
            validate_against_schema(results)


class BenchmarkRunnerCliTests(unittest.TestCase):
    def test_runner_writes_valid_results_file(self) -> None:
        out = ROOT / "benchmarks" / "results.json"
        proc = subprocess.run(
            [sys.executable, str(ROOT / "benchmarks" / "run_benchmarks.py"), "--samples", "2"],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertTrue(out.is_file())
        results = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(results["schema_version"], "0.1")
        self.assertGreaterEqual(len(results["benchmarks"]), 5)


if __name__ == "__main__":
    unittest.main()
