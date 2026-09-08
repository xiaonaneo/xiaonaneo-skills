#!/usr/bin/env python3

import unittest

from evaluate_signal import evaluate_snapshot


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


def field(metric: str, value: object = 1.0, status: str = "final", **extra: object) -> dict[str, object]:
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
        **extra,
    }


class SignalTests(unittest.TestCase):
    def complete(self) -> dict[str, object]:
        return {
            "as_of": "2026-09-07T02:00:00Z",
            "benchmark": "Binance spot BTCUSDT",
            "derivatives_benchmark": "Binance USDⓈ-M BTCUSDT perpetual",
            "fields": [field(metric) for metric in REQUIRED],
        }

    def test_add_candidate_requires_all_positive_gates(self) -> None:
        snapshot = self.complete()
        values = {item["metric"]: item for item in snapshot["fields"]}  # type: ignore[index]
        values["spot_price"]["value"] = 70000
        values["weekly_ma200"]["value"] = 65000
        values["weekly_ma300"]["value"] = 55000
        values["etf_flow_5d"]["value"] = 100
        values["etf_flow_20d"]["value"] = 200
        values["financial_stress"]["value"] = {"level": "low", "direction": "easing"}
        values["mvrv"]["percentile"] = 50
        values["oi_7d_change"]["percentile"] = 30
        snapshot["fields"].append(field("funding_7d", 1, percentile=30))  # type: ignore[union-attr]
        result = evaluate_snapshot(snapshot, "flat")
        self.assertEqual(result["action"], "add_candidate")

    def test_high_leverage_blocks_add_candidate(self) -> None:
        snapshot = self.complete()
        values = {item["metric"]: item for item in snapshot["fields"]}  # type: ignore[index]
        values["spot_price"]["value"] = 70000
        values["weekly_ma200"]["value"] = 65000
        values["weekly_ma300"]["value"] = 55000
        values["etf_flow_5d"]["value"] = 100
        values["etf_flow_20d"]["value"] = 200
        values["financial_stress"]["value"] = {"level": "low", "direction": "stable"}
        values["mvrv"]["percentile"] = 50
        values["oi_7d_change"]["percentile"] = 95
        snapshot["fields"].append(field("funding_7d", 1, percentile=95))  # type: ignore[union-attr]
        result = evaluate_snapshot(snapshot)
        self.assertEqual(result["factors"]["leverage"], "high")
        self.assertEqual(result["action"], "hold_or_wait")

    def test_unknown_leverage_or_stress_blocks_add_candidate(self) -> None:
        snapshot = self.complete()
        values = {item["metric"]: item for item in snapshot["fields"]}  # type: ignore[index]
        values["spot_price"]["value"] = 70000
        values["weekly_ma200"]["value"] = 65000
        values["weekly_ma300"]["value"] = 55000
        values["etf_flow_5d"]["value"] = 100
        values["etf_flow_20d"]["value"] = 200
        values["mvrv"]["percentile"] = 50
        result = evaluate_snapshot(snapshot)
        self.assertEqual(result["factors"]["leverage"], "unknown")
        self.assertEqual(result["action"], "hold_or_wait")

    def test_bearish_price_reduces_or_avoids(self) -> None:
        snapshot = self.complete()
        values = {item["metric"]: item for item in snapshot["fields"]}  # type: ignore[index]
        values["spot_price"]["value"] = 40000
        values["weekly_ma200"]["value"] = 65000
        values["weekly_ma300"]["value"] = 55000
        result = evaluate_snapshot(snapshot, "invested")
        self.assertEqual(result["action"], "reduce_or_avoid")

    def test_below_ma300_is_a_large_position_candidate_when_other_gates_are_known(self) -> None:
        snapshot = self.complete()
        values = {item["metric"]: item for item in snapshot["fields"]}  # type: ignore[index]
        values["spot_price"]["value"] = 40000
        values["weekly_ma200"]["value"] = 65000
        values["weekly_ma300"]["value"] = 55000
        values["etf_flow_5d"]["value"] = 100
        values["etf_flow_20d"]["value"] = 200
        values["financial_stress"]["value"] = {"level": "low", "direction": "easing"}
        values["mvrv"]["percentile"] = 20
        values["oi_7d_change"]["percentile"] = 30
        snapshot["fields"].append(field("funding_7d", 1, percentile=30))  # type: ignore[union-attr]
        result = evaluate_snapshot(snapshot, "flat")
        self.assertEqual(result["factors"]["price_zone"], "large_position_zone")
        self.assertEqual(result["action"], "large_position_candidate")

    def test_data_gap_does_not_become_a_buy_signal(self) -> None:
        snapshot = self.complete()
        snapshot["fields"] = snapshot["fields"][:-1]  # type: ignore[index]
        result = evaluate_snapshot(snapshot)
        self.assertEqual(result["action"], "data_gap")
        self.assertFalse(result["gate"]["new_exposure_allowed"])

    def test_inverted_mas_are_reported_explicitly(self) -> None:
        snapshot = self.complete()
        values = {item["metric"]: item for item in snapshot["fields"]}  # type: ignore[index]
        values["spot_price"]["value"] = 60000
        values["weekly_ma200"]["value"] = 50000
        values["weekly_ma300"]["value"] = 55000
        result = evaluate_snapshot(snapshot)
        self.assertEqual(result["factors"]["price"], "inverted")
        self.assertEqual(result["action"], "hold_or_wait")

    def test_halving_window_is_context_not_a_standalone_signal(self) -> None:
        snapshot = self.complete()
        values = {item["metric"]: item for item in snapshot["fields"]}  # type: ignore[index]
        values["halving_timeline"]["value"] = {
            "cycle_state": "supportive",
            "cycle_window": "pre_halving_500d_window",
        }
        result = evaluate_snapshot(snapshot)
        self.assertEqual(result["factors"]["cycle_window"], "pre_halving_500d_window")
        self.assertEqual(result["action"], "hold_or_wait")


if __name__ == "__main__":
    unittest.main()
