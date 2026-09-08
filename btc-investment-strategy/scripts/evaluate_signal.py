#!/usr/bin/env python3
"""Evaluate the deterministic BTC signal state machine for a normalized snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

from validate_snapshot import validate_snapshot


def field_map(snapshot: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {field["metric"]: field for field in snapshot.get("fields", []) if isinstance(field, dict) and isinstance(field.get("metric"), str)}


def numeric(fields: dict[str, dict[str, Any]], metric: str) -> float | None:
    value = fields.get(metric, {}).get("value")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def percentile(fields: dict[str, dict[str, Any]], metric: str) -> float | None:
    value = fields.get(metric, {}).get("percentile")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def financial_state(fields: dict[str, dict[str, Any]]) -> tuple[str, str]:
    value = fields.get("financial_stress", {}).get("value")
    if isinstance(value, dict):
        level = value.get("level", "unknown")
        direction = value.get("direction", "unknown")
    else:
        level = value if isinstance(value, str) else "unknown"
        direction = fields.get("financial_stress", {}).get("direction", "unknown")
    if level not in {"low", "medium", "high", "unknown"}:
        level = "unknown"
    if direction not in {"easing", "stable", "worsening", "unknown"}:
        direction = "unknown"
    return level, direction


def cycle_state(fields: dict[str, dict[str, Any]]) -> str:
    value = fields.get("halving_timeline", {}).get("value")
    if isinstance(value, dict):
        value = value.get("cycle_state", "unknown")
    return value if value in {"supportive", "neutral", "unknown"} else "unknown"


def factor_states(fields: dict[str, dict[str, Any]]) -> dict[str, Any]:
    price = numeric(fields, "spot_price")
    ma200 = numeric(fields, "weekly_ma200")
    ma300 = numeric(fields, "weekly_ma300")
    if price is None or ma200 is None or ma300 is None:
        price_state = "unknown"
        ma_band = "unknown"
        price_zone = "unknown"
    elif ma200 < ma300:
        price_state = "inverted"
        ma_band = "inverted; report relation to both averages"
        price_zone = "inverted"
    elif price > ma200:
        price_state = "bullish"
        ma_band = "above weekly MA200"
        price_zone = "above_ma200"
    elif price < ma300:
        price_state = "bearish"
        ma_band = "below weekly MA300"
        price_zone = "large_position_zone"
    else:
        price_state = "neutral"
        ma_band = "between weekly MA200 and weekly MA300"
        price_zone = "bottom_fishing_zone"

    flow_5d = numeric(fields, "etf_flow_5d")
    flow_20d = numeric(fields, "etf_flow_20d")
    if flow_5d is None or flow_20d is None:
        spot_state = "unknown"
    elif flow_5d > 0 and flow_20d > 0:
        spot_state = "positive"
    elif flow_5d < 0 and flow_20d < 0:
        spot_state = "negative"
    else:
        spot_state = "mixed"

    oi_pctile = percentile(fields, "oi_7d_change")
    funding_pctile = percentile(fields, "funding_7d")
    liquidation = fields.get("liquidation_cascade", {}).get("value") is True
    if liquidation:
        leverage_state = "high"
    elif oi_pctile is None or funding_pctile is None:
        leverage_state = "unknown"
    elif oi_pctile >= 80 and funding_pctile >= 80:
        leverage_state = "high"
    elif oi_pctile <= 50 and funding_pctile <= 50:
        leverage_state = "low"
    else:
        leverage_state = "medium"

    mvrv_pctile = percentile(fields, "mvrv")
    if mvrv_pctile is None:
        valuation_state = "unknown"
    elif mvrv_pctile <= 20:
        valuation_state = "low"
    elif mvrv_pctile >= 80:
        valuation_state = "high"
    else:
        valuation_state = "neutral"

    stress_level, stress_direction = financial_state(fields)
    cycle_value = fields.get("halving_timeline", {}).get("value")
    cycle_window = cycle_value.get("cycle_window", "unknown") if isinstance(cycle_value, dict) else "unknown"
    if cycle_window not in {"pre_halving_500d_window", "post_halving_500d_window", "other", "unknown"}:
        cycle_window = "unknown"
    return {
        "price": price_state,
        "price_zone": price_zone,
        "weekly_ma_band": ma_band,
        "spot": spot_state,
        "leverage": leverage_state,
        "financial_stress": stress_level,
        "financial_stress_direction": stress_direction,
        "valuation": valuation_state,
        "cycle": cycle_state(fields),
        "cycle_window": cycle_window,
    }


def evaluate_snapshot(snapshot: dict[str, Any], position: str = "unknown") -> dict[str, Any]:
    gate = validate_snapshot(snapshot)
    fields = field_map(snapshot)
    factors = factor_states(fields)
    if gate["status"] != "ok":
        entry_action = "data_gap"
        position_action = "data_gap"
        matched_rule = "data gate is not open"
    elif (
        factors["financial_stress"] == "high"
        and factors["financial_stress_direction"] == "worsening"
        and (factors["leverage"] == "high" or factors["spot"] == "negative")
    ):
        entry_action = "hold_or_wait"
        position_action = "reduce"
        matched_rule = "high worsening financial stress conflicts with leverage or spot demand"
    else:
        conditions_known = (
            factors["leverage"] in {"low", "medium"}
            and factors["financial_stress"] in {"low", "medium"}
            and factors["financial_stress_direction"] in {"easing", "stable"}
            and factors["valuation"] in {"low", "neutral"}
            and factors["spot"] != "negative"
        )
        if conditions_known and factors["price_zone"] == "large_position_zone":
            entry_action = "large_position_candidate"
            matched_rule = "price below weekly MA300 with known non-high valuation, leverage, stress, and non-negative spot"
        elif conditions_known and factors["price_zone"] == "bottom_fishing_zone":
            entry_action = "bottom_fishing_candidate"
            matched_rule = "price below weekly MA200 with known non-high valuation, leverage, stress, and non-negative spot"
        elif conditions_known and factors["price"] == "bullish" and factors["spot"] == "positive":
            entry_action = "add_candidate"
            matched_rule = "bullish price, positive spot, known non-high leverage, stress, and valuation"
        else:
            entry_action = "hold_or_wait"
            matched_rule = "no higher-priority entry rule matched"
        position_action = "reduce_or_avoid" if factors["price"] == "bearish" and position == "invested" else "hold_or_wait"
    action = position_action if position == "invested" else entry_action
    return {
        "position": position,
        "gate": gate,
        "factors": factors,
        "entry_action": entry_action,
        "position_action": position_action,
        "action": action,
        "matched_rule": matched_rule,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    parser.add_argument("--position", choices=("flat", "invested", "unknown"), default="unknown")
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = evaluate_snapshot(snapshot, args.position)
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        print(json.dumps({"status": "invalid", "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
