#!/usr/bin/env python3

from __future__ import annotations

from datetime import datetime, timezone
import unittest

from backtest_strategy import BacktestError, normalize_row, run_backtest, row_to_snapshot


CONFIG = {
    "portfolio_value_usdt": 100000,
    "current_btc_exposure_usdt": 0,
    "available_cash_usdt": 100000,
    "max_btc_exposure_pct": 0.30,
    "cash_reserve_floor_pct": 0.20,
    "single_trade_cap_pct": 0.05,
    "large_trade_cap_pct": 0.15,
    "risk_budget_pct": 0.01,
    "invalidation_distance_pct": 0.10,
    "fee_bps": 10,
    "slippage_bps": 10,
    "cooldown_weeks": 1,
}


def row(as_of: str, price: float, *, bearish: bool = False, available_at: str | None = None, data_status: str = "final") -> dict[str, object]:
    as_of_dt = datetime.fromisoformat(as_of.replace("Z", "+00:00"))
    observed = as_of_dt.replace(hour=0)
    available = available_at or as_of
    return {
        "observed_at": observed.isoformat().replace("+00:00", "Z"),
        "available_at": available,
        "as_of": as_of,
        "execution_at": (as_of_dt.replace(hour=12)).isoformat().replace("+00:00", "Z"),
        "execution_price": str(price),
        "benchmark": "Binance spot BTCUSDT",
        "derivatives_benchmark": "Binance USDⓈ-M BTCUSDT perpetual",
        "data_status": data_status,
        "spot_price": str(price),
        "weekly_sma50": "105" if bearish else "85",
        "weekly_ma200": "110" if bearish else "90",
        "weekly_ma300": "100" if bearish else "80",
        "etf_flow_5d": "100",
        "etf_flow_20d": "200",
        "oi_7d_change": "1",
        "oi_7d_percentile": "30",
        "funding_8h": "0.01",
        "funding_7d_percentile": "30",
        "financial_stress_level": "low",
        "financial_stress_direction": "stable",
        "mvrv": "1.5",
        "mvrv_percentile": "50",
        "halving_cycle_state": "supportive",
        "liquidation_cascade": "false",
    }


def normalized(raw: dict[str, object], index: int = 2) -> dict[str, object]:
    return normalize_row({key: str(value) for key, value in raw.items()}, index)


class BacktestTests(unittest.TestCase):
    def test_availability_lag_is_required(self) -> None:
        invalid = row("2026-01-04T00:00:00Z", 100, available_at="2026-01-05T00:00:00Z")
        with self.assertRaises(BacktestError):
            run_backtest([normalized(invalid)], CONFIG)

    def test_bullish_entry_and_bearish_exit_are_counted(self) -> None:
        rows = [
            row("2026-01-04T00:00:00Z", 100),
            row("2026-01-11T00:00:00Z", 110),
            row("2026-01-18T00:00:00Z", 90, bearish=True),
        ]
        result = run_backtest([normalized(item, index) for index, item in enumerate(rows, start=2)], CONFIG)
        self.assertEqual(result["trades"], 2)
        self.assertGreater(result["action_counts"]["add_candidate"], 0)
        self.assertGreater(result["action_counts"]["reduce_or_avoid"], 0)
        self.assertEqual(result["open_btc_quantity"], 0.0)

    def test_snapshot_uses_next_execution_time_as_of_boundary(self) -> None:
        raw = row("2026-01-04T00:00:00Z", 100)
        raw["observed_at"] = "2026-01-03T00:00:00Z"
        raw["available_at"] = "2026-01-04T00:00:00Z"
        snapshot = row_to_snapshot(normalized({**raw, "execution_at": datetime(2026, 1, 4, 12, tzinfo=timezone.utc)}))
        self.assertEqual(snapshot["as_of"], "2026-01-04T00:00:00Z")

    def test_noncanonical_benchmark_becomes_data_gap(self) -> None:
        raw = row("2026-01-04T00:00:00Z", 100)
        raw["benchmark"] = "Kraken BTCUSD"
        result = run_backtest([normalized(raw)], CONFIG)
        self.assertEqual(result["action_counts"]["data_gap"], 1)
        self.assertEqual(result["trades"], 0)

    def test_preliminary_data_cannot_open_a_position(self) -> None:
        raw = row("2026-01-04T00:00:00Z", 100, data_status="preliminary")
        result = run_backtest([normalized(raw)], CONFIG)
        self.assertEqual(result["action_counts"]["data_gap"], 1)
        self.assertEqual(result["trades"], 0)


if __name__ == "__main__":
    unittest.main()
