#!/usr/bin/env python3

from datetime import datetime, timezone
import unittest

from validate_snapshot import SnapshotError, validate_snapshot


def field(metric: str, value: object = 1.0, status: str = "final") -> dict[str, object]:
    return {
        "metric": metric,
        "value": value,
        "unit": "test",
        "source": "test-source",
        "venue_or_series": "test-venue",
        "observed_at": "2026-09-07T00:00:00Z",
        "available_at": "2026-09-07T01:00:00Z",
        "status": status,
        "methodology": "test-methodology",
    }


REQUIRED = [
    "spot_price",
    "weekly_ma200",
    "weekly_ma300",
    "etf_flow_5d",
    "etf_flow_20d",
    "oi_7d_change",
    "funding_8h",
    "financial_stress",
    "mvrv",
    "halving_timeline",
]


class SnapshotTests(unittest.TestCase):
    def complete(self) -> dict[str, object]:
        return {
            "as_of": "2026-09-07T02:00:00Z",
            "benchmark": "Binance spot BTCUSDT",
            "derivatives_benchmark": "Binance USDⓈ-M BTCUSDT perpetual",
            "fields": [field(metric) for metric in REQUIRED],
        }

    def test_complete_snapshot_allows_new_exposure(self) -> None:
        result = validate_snapshot(self.complete())
        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["new_exposure_allowed"])

    def test_missing_critical_metric_blocks_new_exposure(self) -> None:
        snapshot = self.complete()
        snapshot["fields"] = snapshot["fields"][:-1]  # type: ignore[index]
        result = validate_snapshot(snapshot)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["new_exposure_allowed"])
        self.assertIn("halving_timeline", " ".join(result["blockers"]))

    def test_stale_data_blocks_but_price_basis_remains_visible(self) -> None:
        snapshot = self.complete()
        snapshot["fields"][7]["status"] = "stale"  # type: ignore[index]
        result = validate_snapshot(snapshot)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["new_exposure_allowed"])
        self.assertTrue(result["protective_reduction_basis_available"])

    def test_future_observation_is_invalid(self) -> None:
        snapshot = self.complete()
        snapshot["fields"][0]["observed_at"] = "2026-09-08T00:00:00Z"  # type: ignore[index]
        result = validate_snapshot(snapshot)
        self.assertEqual(result["status"], "invalid")
        self.assertFalse(result["new_exposure_allowed"])

    def test_timezone_is_required(self) -> None:
        snapshot = self.complete()
        snapshot["as_of"] = "2026-09-07T02:00:00"  # type: ignore[assignment]
        with self.assertRaisesRegex(SnapshotError, "timezone"):
            validate_snapshot(snapshot)

    def test_available_time_cannot_precede_observation(self) -> None:
        snapshot = self.complete()
        snapshot["fields"][0]["available_at"] = "2026-09-06T23:00:00Z"  # type: ignore[index]
        result = validate_snapshot(snapshot)
        self.assertEqual(result["status"], "invalid")

    def test_noncanonical_benchmark_blocks_without_explicit_override(self) -> None:
        snapshot = self.complete()
        snapshot["benchmark"] = "Kraken BTCUSD"
        result = validate_snapshot(snapshot)
        self.assertEqual(result["status"], "blocked")
        self.assertFalse(result["new_exposure_allowed"])

    def test_benchmark_override_requires_reason(self) -> None:
        snapshot = self.complete()
        snapshot["benchmark"] = "Kraken BTCUSD"
        snapshot["benchmark_override"] = True
        result = validate_snapshot(snapshot)
        self.assertEqual(result["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
