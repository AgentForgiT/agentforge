from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "benchmarks"))

from check_regressions import check_regressions, load_thresholds, welch_t_pvalue


def make_results(benchmarks: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema_version": "0.1",
        "suite": "offline",
        "environment": {"python": "3.11", "platform": "test"},
        "timestamp": "2026-08-01T00:00:00Z",
        "benchmarks": benchmarks,
    }


LATENCY = {"name": "gateway.chat_completion.median_latency_ms", "unit": "ms", "value": 0.05, "samples": []}
THROUGHPUT = {"name": "gateway.chat_completion.throughput_per_sec", "unit": "completions/s", "value": 20000.0, "samples": []}
VALIDATE = {"name": "cli.validate_context.median_ms", "unit": "ms", "value": 10.0, "samples": []}


class CheckRegressionsTests(unittest.TestCase):
    def test_lower_better_regression_fails(self) -> None:
        # latency 0.05 -> 0.06 = +20% > 10% threshold
        prev = make_results([dict(LATENCY)])
        curr = make_results([dict(LATENCY, value=0.06)])
        verdicts, has_regression = check_regressions(prev, curr, 10.0)
        self.assertTrue(has_regression)
        self.assertEqual(verdicts[0].regressed, True)
        self.assertEqual(verdicts[0].delta_pct, 20.0)

    def test_higher_better_regression_fails(self) -> None:
        # throughput 20000 -> 15000 = -25% > 10%
        prev = make_results([dict(THROUGHPUT)])
        curr = make_results([dict(THROUGHPUT, value=15000.0)])
        verdicts, has_regression = check_regressions(prev, curr, 10.0)
        self.assertTrue(has_regression)
        self.assertEqual(verdicts[0].regressed, True)

    def test_improvement_never_fails(self) -> None:
        # latency down 20% is good
        prev = make_results([dict(LATENCY)])
        curr = make_results([dict(LATENCY, value=0.04)])
        verdicts, has_regression = check_regressions(prev, curr, 10.0)
        self.assertFalse(has_regression)
        self.assertEqual(verdicts[0].regressed, False)

    def test_higher_better_improvement_never_fails(self) -> None:
        # throughput up 25% is good
        prev = make_results([dict(THROUGHPUT)])
        curr = make_results([dict(THROUGHPUT, value=25000.0)])
        verdicts, has_regression = check_regressions(prev, curr, 10.0)
        self.assertFalse(has_regression)

    def test_within_threshold_passes(self) -> None:
        # +5% latency < 10% threshold
        prev = make_results([dict(VALIDATE)])
        curr = make_results([dict(VALIDATE, value=10.5)])
        verdicts, has_regression = check_regressions(prev, curr, 10.0)
        self.assertFalse(has_regression)
        self.assertEqual(verdicts[0].regressed, False)

    def test_benchmark_only_in_one_side_is_skipped(self) -> None:
        prev = make_results([dict(LATENCY), dict(VALIDATE)])
        curr = make_results([dict(LATENCY)])
        verdicts, has_regression = check_regressions(prev, curr, 10.0)
        # only LATENCY is compared; VALIDATE is skipped, never fails
        self.assertEqual(len(verdicts), 1)
        self.assertFalse(has_regression)

    def test_empty_both_sides_no_regression(self) -> None:
        verdicts, has_regression = check_regressions(make_results([]), make_results([]), 10.0)
        self.assertEqual(verdicts, [])
        self.assertFalse(has_regression)

    def test_threshold_zero_is_strict(self) -> None:
        # any change at threshold 0 fails
        prev = make_results([dict(VALIDATE)])
        curr = make_results([dict(VALIDATE, value=10.1)])
        verdicts, has_regression = check_regressions(prev, curr, 0.0)
        self.assertTrue(has_regression)


class ThresholdConfigTests(unittest.TestCase):
    def test_no_config_defaults_to_10(self) -> None:
        default, overrides = load_thresholds(None)
        self.assertEqual(default, 10.0)
        self.assertEqual(overrides, {})

    def test_loads_default_and_overrides(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "thresholds.json"
            path.write_text(
                json.dumps({"default": 15, "benchmarks": {"gateway.latency": 5}}),
                encoding="utf-8",
            )
            default, overrides = load_thresholds(path)
            self.assertEqual(default, 15.0)
            self.assertEqual(overrides, {"gateway.latency": 5.0})

    def test_per_name_override_beats_default(self) -> None:
        prev = make_results([dict(VALIDATE)])  # 10.0
        curr = make_results([dict(VALIDATE, value=12.0)])  # +20%
        # default 10 would fail; per-name 30 passes
        verdicts, has_regression = check_regressions(prev, curr, 10.0, {"cli.validate_context.median_ms": 30.0})
        self.assertFalse(has_regression)

    def test_unlisted_name_uses_default(self) -> None:
        prev = make_results([dict(VALIDATE)])
        curr = make_results([dict(VALIDATE, value=12.0)])  # +20%
        # override only for a different name; default 10 applies -> regression
        verdicts, has_regression = check_regressions(prev, curr, 10.0, {"some.other.bench": 30.0})
        self.assertTrue(has_regression)

    def test_invalid_config_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"default": -5}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_thresholds(path)

    def test_invalid_benchmark_threshold_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text(json.dumps({"benchmarks": {"x": "high"}}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_thresholds(path)

    def test_cli_thresholds_flag_usage_error_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prev = Path(tmp) / "prev.json"
            curr = Path(tmp) / "curr.json"
            prev.write_text(json.dumps(make_results([dict(LATENCY)])), encoding="utf-8")
            curr.write_text(json.dumps(make_results([dict(LATENCY)])), encoding="utf-8")
            bad = Path(tmp) / "bad.json"
            bad.write_text("{oops", encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "benchmarks" / "check_regressions.py"),
                    "--previous", str(prev),
                    "--current", str(curr),
                    "--thresholds", str(bad),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 2)
            self.assertIn("error:", proc.stderr)


class WelchTPvalueTests(unittest.TestCase):
    def test_identical_samples_p_high(self) -> None:
        p = welch_t_pvalue([10.0] * 5, [10.0] * 5)
        self.assertIsNotNone(p)
        self.assertGreater(p, 0.05)

    def test_well_separated_samples_p_low(self) -> None:
        p = welch_t_pvalue([10.0] * 5, [12.0] * 5)
        self.assertIsNotNone(p)
        self.assertLess(p, 0.05)

    def test_noisy_overlap_p_high(self) -> None:
        # high variance, overlapping: not significant
        p = welch_t_pvalue([10.0, 10.5, 9.5, 10.2, 9.8], [10.6, 10.9, 9.9, 10.3, 10.1])
        self.assertIsNotNone(p)
        self.assertGreater(p, 0.05)

    def test_insufficient_samples_none(self) -> None:
        self.assertIsNone(welch_t_pvalue([10.0], [12.0]))  # 1 sample each
        self.assertIsNone(welch_t_pvalue([], [12.0, 13.0]))


class VarianceAwareGateTests(unittest.TestCase):
    def test_low_variance_regression_flags(self) -> None:
        # +25% with tight samples: significant -> REGRESSED
        prev = make_results([dict(VALIDATE, samples=[10.0] * 5)])
        curr = make_results([dict(VALIDATE, value=12.5, samples=[12.5] * 5)])
        verdicts, has_regression = check_regressions(prev, curr, 10.0, significance=0.05)
        self.assertTrue(has_regression)
        self.assertTrue(verdicts[0].regressed)
        self.assertTrue(verdicts[0].significant)
        self.assertLess(verdicts[0].p_value, 0.05)

    def test_high_variance_jitter_does_not_flag(self) -> None:
        # +25% median but samples overlap heavily (jittery): not significant -> OK
        prev = make_results([dict(VALIDATE, samples=[8.0, 13.0, 9.0, 12.0, 10.0, 8.5, 11.5])])
        curr = make_results([dict(VALIDATE, value=12.5, samples=[9.0, 14.0, 10.0, 13.0, 11.0, 9.5, 12.5])])
        verdicts, has_regression = check_regressions(prev, curr, 10.0, significance=0.05)
        self.assertFalse(has_regression)
        self.assertFalse(verdicts[0].regressed)
        self.assertIsNotNone(verdicts[0].p_value)
        self.assertFalse(verdicts[0].significant)

    def test_significance_disabled_flags_threshold_only(self) -> None:
        # significance=1.0 disables stats: jitter that crossed threshold flags
        prev = make_results([dict(VALIDATE, samples=[9.0, 11.0, 9.5, 10.5, 10.0])])
        curr = make_results([dict(VALIDATE, value=12.5, samples=[11.0, 13.5, 12.0, 12.8, 13.2])])
        verdicts, has_regression = check_regressions(prev, curr, 10.0, significance=1.0)
        self.assertTrue(has_regression)
        self.assertTrue(verdicts[0].regressed)

    def test_insufficient_samples_threshold_only_fallback(self) -> None:
        # no samples: falls back to threshold-only (still flags)
        prev = make_results([dict(VALIDATE, samples=[])])
        curr = make_results([dict(VALIDATE, value=12.0, samples=[])])
        verdicts, has_regression = check_regressions(prev, curr, 10.0, significance=0.05)
        self.assertTrue(has_regression)
        self.assertTrue(verdicts[0].regressed)
        self.assertIsNone(verdicts[0].p_value)
        self.assertIsNone(verdicts[0].significant)


class CheckRegressionsCliTests(unittest.TestCase):
    def test_cli_exit_codes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prev = Path(tmp) / "prev.json"
            curr = Path(tmp) / "curr.json"
            prev.write_text(json.dumps(make_results([dict(LATENCY)])), encoding="utf-8")
            # regression: +20%
            curr.write_text(json.dumps(make_results([dict(LATENCY, value=0.06)])), encoding="utf-8")

            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "benchmarks" / "check_regressions.py"),
                    "--previous",
                    str(prev),
                    "--current",
                    str(curr),
                    "--threshold",
                    "10",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 1, proc.stdout)
            self.assertIn("REGRESSED", proc.stdout)

            # fix: improvement exits 0
            curr.write_text(json.dumps(make_results([dict(LATENCY, value=0.04)])), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "benchmarks" / "check_regressions.py"),
                    "--previous",
                    str(prev),
                    "--current",
                    str(curr),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stdout)
            self.assertIn("OK", proc.stdout)


if __name__ == "__main__":
    unittest.main()
