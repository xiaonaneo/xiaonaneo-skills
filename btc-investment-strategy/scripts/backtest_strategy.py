#!/usr/bin/env python3
"""Backtest the BTC spot state machine on a normalized, availability-aware CSV."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timedelta, timezone
import json
import math
from pathlib import Path
from typing import Any, Iterable

from evaluate_signal import evaluate_snapshot
from risk_model import ENTRY_SIGNALS, RiskConfigError, calculate_position_size, validate_risk_config


REQUIRED_COLUMNS = (
    "observed_at",
    "available_at",
    "as_of",
    "execution_at",
    "execution_price",
    "benchmark",
    "derivatives_benchmark",
    "data_status",
    "spot_price",
    "weekly_ma200",
    "weekly_ma300",
    "etf_flow_5d",
    "etf_flow_20d",
    "oi_7d_change",
    "oi_7d_percentile",
    "funding_8h",
    "funding_7d_percentile",
    "financial_stress_level",
    "financial_stress_direction",
    "mvrv",
    "mvrv_percentile",
    "halving_cycle_state",
    "liquidation_cascade",
)
FLOAT_COLUMNS = (
    "execution_price",
    "spot_price",
    "weekly_ma200",
    "weekly_ma300",
    "etf_flow_5d",
    "etf_flow_20d",
    "oi_7d_change",
    "oi_7d_percentile",
    "funding_8h",
    "funding_7d_percentile",
    "mvrv",
    "mvrv_percentile",
)


class BacktestError(ValueError):
    """Raised when the backtest input would permit an invalid comparison."""


def parse_time(value: str, field: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise BacktestError(f"{field} is not a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise BacktestError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def parse_bool(value: str, field: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise BacktestError(f"{field} must be true or false")


def normalize_row(row: dict[str, str], index: int) -> dict[str, Any]:
    missing = [column for column in REQUIRED_COLUMNS if not row.get(column)]
    if missing:
        raise BacktestError(f"row {index} missing columns or values: {', '.join(missing)}")
    normalized: dict[str, Any] = dict(row)
    for column in FLOAT_COLUMNS:
        try:
            normalized[column] = float(row[column])
        except ValueError as exc:
            raise BacktestError(f"row {index} {column} must be numeric") from exc
        if not math.isfinite(normalized[column]):
            raise BacktestError(f"row {index} {column} must be finite")
    for column in ("observed_at", "available_at", "as_of", "execution_at"):
        normalized[column] = parse_time(row[column], f"row {index} {column}")
    normalized["liquidation_cascade"] = parse_bool(row["liquidation_cascade"], f"row {index} liquidation_cascade")
    if not normalized["execution_price"] > 0:
        raise BacktestError(f"row {index} execution_price must be greater than zero")
    if not normalized["observed_at"] <= normalized["available_at"] <= normalized["as_of"] < normalized["execution_at"]:
        raise BacktestError(f"row {index} requires observed_at <= available_at <= as_of < execution_at")
    return normalized


def row_to_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    def field(metric: str, value: Any, status: str = "final", **extra: Any) -> dict[str, Any]:
        return {
            "metric": metric,
            "value": value,
            "unit": "backtest-input",
            "source": "normalized-backtest-input",
            "venue_or_series": "Binance BTCUSDT or documented input series",
            "observed_at": row["observed_at"].isoformat().replace("+00:00", "Z"),
            "available_at": row["available_at"].isoformat().replace("+00:00", "Z"),
            "status": status,
            "methodology": "backtest input contract",
            **extra,
        }

    return {
        "as_of": row["as_of"].isoformat().replace("+00:00", "Z"),
        "benchmark": row["benchmark"],
        "derivatives_benchmark": row["derivatives_benchmark"],
        "fields": [
            field("spot_price", row["spot_price"], status=row["data_status"]),
            field("weekly_ma200", row["weekly_ma200"], status=row["data_status"]),
            field("weekly_ma300", row["weekly_ma300"], status=row["data_status"]),
            field("etf_flow_5d", row["etf_flow_5d"], status=row["data_status"]),
            field("etf_flow_20d", row["etf_flow_20d"], status=row["data_status"]),
            field("oi_7d_change", row["oi_7d_change"], status=row["data_status"], percentile=row["oi_7d_percentile"]),
            field("funding_8h", row["funding_8h"], status=row["data_status"]),
            field("funding_7d", row["funding_8h"], status=row["data_status"], percentile=row["funding_7d_percentile"]),
            field(
                "financial_stress",
                {"level": row["financial_stress_level"], "direction": row["financial_stress_direction"]},
                status=row["data_status"],
            ),
            field("mvrv", row["mvrv"], status=row["data_status"], percentile=row["mvrv_percentile"]),
            field("halving_timeline", {"cycle_state": row["halving_cycle_state"]}, status="estimated"),
            field("liquidation_cascade", row["liquidation_cascade"]),
        ],
    }


def load_rows(path: Path) -> list[dict[str, Any]]:
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise BacktestError("CSV has no header")
            missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
            if missing:
                raise BacktestError(f"CSV missing required columns: {', '.join(missing)}")
            rows = [normalize_row(row, index) for index, row in enumerate(reader, start=2)]
    except OSError as exc:
        raise BacktestError(str(exc)) from exc
    rows.sort(key=lambda row: row["as_of"])
    if not rows:
        raise BacktestError("CSV contains no data rows")
    for previous, current in zip(rows, rows[1:]):
        if current["as_of"] <= previous["as_of"]:
            raise BacktestError("as_of timestamps must be strictly increasing")
    return rows


def _equity(cash: float, btc_quantity: float, price: float) -> float:
    return cash + btc_quantity * price


def _net_sell_value(quantity: float, price: float, fee_bps: float, slippage_bps: float) -> float:
    return quantity * price * (1 - slippage_bps / 10000) * (1 - fee_bps / 10000)


def run_backtest(rows: Iterable[dict[str, Any]], risk_config: dict[str, Any]) -> dict[str, Any]:
    validate_risk_config(risk_config)
    ordered = list(rows)
    if not ordered:
        raise BacktestError("no rows to backtest")
    if risk_config["current_btc_exposure_usdt"] != 0:
        raise BacktestError("backtest must start with current_btc_exposure_usdt equal to zero")
    if risk_config["available_cash_usdt"] != risk_config["portfolio_value_usdt"]:
        raise BacktestError("backtest must start with available_cash_usdt equal to portfolio_value_usdt")
    initial_cash = float(risk_config["portfolio_value_usdt"])
    cash = initial_cash
    btc_quantity = 0.0
    peak_equity = initial_cash
    max_drawdown = 0.0
    trades = 0
    action_counts: dict[str, int] = {}
    cooldown_until: datetime | None = None
    fee_rate = float(risk_config["fee_bps"]) / 10000
    slip_rate = float(risk_config["slippage_bps"]) / 10000

    for row in ordered:
        snapshot = row_to_snapshot(row)
        signal = evaluate_snapshot(snapshot, "invested" if btc_quantity else "flat")
        action = signal["action"]
        action_counts[action] = action_counts.get(action, 0) + 1
        price = row["execution_price"]
        if action in {"reduce", "reduce_or_avoid"} and btc_quantity > 0:
            cash += _net_sell_value(btc_quantity, price, risk_config["fee_bps"], risk_config["slippage_bps"])
            btc_quantity = 0.0
            trades += 1
            cooldown_until = row["execution_at"] + timedelta(weeks=risk_config["cooldown_weeks"])
        elif action in ENTRY_SIGNALS and btc_quantity == 0 and (cooldown_until is None or row["as_of"] >= cooldown_until):
            current_equity = cash
            dynamic_config = dict(risk_config)
            dynamic_config["portfolio_value_usdt"] = current_equity
            dynamic_config["current_btc_exposure_usdt"] = 0.0
            dynamic_config["available_cash_usdt"] = cash
            sized = calculate_position_size(dynamic_config, action, price)
            notional = float(sized["trade_notional_usdt"])
            quantity = notional / (price * (1 + slip_rate))
            total_cost = quantity * price * (1 + slip_rate) * (1 + fee_rate)
            if total_cost > cash and total_cost > 0:
                quantity *= cash / total_cost
                total_cost = cash
            cash -= total_cost
            btc_quantity = quantity
            if quantity > 0:
                trades += 1

        equity = _equity(cash, btc_quantity, price)
        peak_equity = max(peak_equity, equity)
        max_drawdown = max(max_drawdown, 1 - equity / peak_equity)

    final_price = ordered[-1]["execution_price"]
    final_equity = _equity(cash, btc_quantity, final_price)
    first_price = ordered[0]["execution_price"]
    benchmark_quantity = initial_cash / (first_price * (1 + slip_rate) * (1 + fee_rate))
    benchmark_final = _net_sell_value(benchmark_quantity, final_price, risk_config["fee_bps"], risk_config["slippage_bps"])
    period_days = (ordered[-1]["as_of"] - ordered[0]["as_of"]).total_seconds() / 86400
    cagr = None if period_days <= 0 else (final_equity / initial_cash) ** (365 / period_days) - 1
    return {
        "rows": len(ordered),
        "start_as_of": ordered[0]["as_of"].isoformat().replace("+00:00", "Z"),
        "end_as_of": ordered[-1]["as_of"].isoformat().replace("+00:00", "Z"),
        "trades": trades,
        "action_counts": action_counts,
        "final_equity_usdt": round(final_equity, 8),
        "total_return": round(final_equity / initial_cash - 1, 8),
        "annualized_return": None if cagr is None else round(cagr, 8),
        "max_drawdown": round(max_drawdown, 8),
        "buy_and_hold_final_equity_usdt": round(benchmark_final, 8),
        "buy_and_hold_total_return": round(benchmark_final / initial_cash - 1, 8),
        "open_btc_quantity": round(btc_quantity, 8),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("risk_config", type=Path)
    args = parser.parse_args()
    try:
        rows = load_rows(args.csv_path)
        config = json.loads(args.risk_config.read_text(encoding="utf-8"))
        result = run_backtest(rows, config)
    except (OSError, json.JSONDecodeError, BacktestError, RiskConfigError) as exc:
        print(json.dumps({"status": "invalid", "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    result["status"] = "ok"
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
