#!/usr/bin/env python3
"""Pure validation and position-sizing functions for BTC spot research signals."""

from __future__ import annotations

import math
from typing import Any


REQUIRED_CONFIG = (
    "portfolio_value_usdt",
    "current_btc_exposure_usdt",
    "available_cash_usdt",
    "max_btc_exposure_pct",
    "cash_reserve_floor_pct",
    "single_trade_cap_pct",
    "large_trade_cap_pct",
    "risk_budget_pct",
    "invalidation_distance_pct",
    "fee_bps",
    "slippage_bps",
    "cooldown_weeks",
)
PERCENT_FIELDS = (
    "max_btc_exposure_pct",
    "cash_reserve_floor_pct",
    "single_trade_cap_pct",
    "risk_budget_pct",
    "invalidation_distance_pct",
)
ENTRY_SIGNALS = {"add_candidate", "bottom_fishing_candidate", "large_position_candidate"}
NON_NEGATIVE_FIELDS = ("current_btc_exposure_usdt", "available_cash_usdt", "fee_bps", "slippage_bps")


class RiskConfigError(ValueError):
    """Raised when sizing inputs are absent or unsafe."""


def _number(config: dict[str, Any], key: str) -> float:
    value = config.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise RiskConfigError(f"{key} must be a finite number")
    return float(value)


def validate_risk_config(config: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(config, dict):
        raise RiskConfigError("risk config must be a JSON object")
    missing = [key for key in REQUIRED_CONFIG if key not in config]
    if missing:
        raise RiskConfigError(f"missing risk config fields: {', '.join(missing)}")
    portfolio = _number(config, "portfolio_value_usdt")
    if portfolio <= 0:
        raise RiskConfigError("portfolio_value_usdt must be greater than zero")
    for key in NON_NEGATIVE_FIELDS:
        if _number(config, key) < 0:
            raise RiskConfigError(f"{key} must not be negative")
    for key in PERCENT_FIELDS:
        value = _number(config, key)
        if not 0 <= value <= 1 or (key != "cash_reserve_floor_pct" and value == 0):
            raise RiskConfigError(f"{key} must be in the valid range from zero to one")
    if _number(config, "available_cash_usdt") > portfolio:
        raise RiskConfigError("available_cash_usdt cannot exceed portfolio_value_usdt")
    if _number(config, "large_trade_cap_pct") < _number(config, "single_trade_cap_pct"):
        raise RiskConfigError("large_trade_cap_pct cannot be below single_trade_cap_pct")
    cooldown = config.get("cooldown_weeks")
    if isinstance(cooldown, bool) or not isinstance(cooldown, int) or cooldown < 0:
        raise RiskConfigError("cooldown_weeks must be a non-negative integer")
    return config


def calculate_position_size(config: dict[str, Any], signal: str, execution_price: float) -> dict[str, float | str]:
    if signal not in ENTRY_SIGNALS:
        return {"signal": signal, "trade_notional_usdt": 0.0, "btc_quantity": 0.0}
    validate_risk_config(config)
    if not math.isfinite(execution_price) or execution_price <= 0:
        raise RiskConfigError("execution_price must be a finite number greater than zero")

    portfolio = _number(config, "portfolio_value_usdt")
    current = _number(config, "current_btc_exposure_usdt")
    remaining_exposure = max(0.0, portfolio * _number(config, "max_btc_exposure_pct") - current)
    cash_limited = max(0.0, _number(config, "available_cash_usdt") - portfolio * _number(config, "cash_reserve_floor_pct"))
    cap_key = "large_trade_cap_pct" if signal == "large_position_candidate" else "single_trade_cap_pct"
    single_trade_cap = portfolio * _number(config, cap_key)
    round_trip_cost = 2 * (_number(config, "fee_bps") + _number(config, "slippage_bps")) / 10000
    effective_loss = _number(config, "invalidation_distance_pct") + round_trip_cost
    risk_limited = portfolio * _number(config, "risk_budget_pct") / effective_loss
    trade_notional = min(remaining_exposure, cash_limited, single_trade_cap, risk_limited)
    return {
        "signal": signal,
        "trade_notional_usdt": round(trade_notional, 8),
        "btc_quantity": round(trade_notional / execution_price, 8),
        "remaining_exposure_usdt": round(remaining_exposure, 8),
        "cash_limited_usdt": round(cash_limited, 8),
        "trade_cap_type": cap_key,
        "trade_cap_usdt": round(single_trade_cap, 8),
        "risk_limited_usdt": round(risk_limited, 8),
        "effective_loss_pct": round(effective_loss, 8),
    }
