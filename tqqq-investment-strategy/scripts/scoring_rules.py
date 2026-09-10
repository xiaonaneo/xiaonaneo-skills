"""Deterministic helpers for the TQQQ scoring reference."""

from __future__ import annotations

from math import isfinite
from statistics import median
from typing import Iterable, Mapping


VALID_STRESS_GROUPS = {"credit", "liquidity", "volatility", "macro"}


def _number(value: float) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError("value must be finite")
    return value


def _percentile(value: float) -> float:
    value = _number(value)
    if not 0 <= value <= 100:
        raise ValueError("percentile must be between 0 and 100")
    return value


def _positive(value: float) -> float:
    value = _number(value)
    if value <= 0:
        raise ValueError("value must be positive")
    return value


def score_band(score: float) -> str:
    score = _number(score)
    if not 0 <= score <= 100:
        raise ValueError("score must be between 0 and 100")
    if score < 40:
        return "<40"
    if score < 55:
        return "40-54"
    if score < 70:
        return "55-69"
    if score < 85:
        return "70-84"
    return "85-100"


def qqq_position_score(deviation: float) -> int:
    d = _number(deviation)
    if d > 0.20:
        return 10
    if d > 0.10:
        return 30
    if d > 0.05:
        return 50
    if d > 0:
        return 70
    if d > -0.10:
        return 90
    return 100


def tqqq_position_score(deviation: float) -> int:
    t = _number(deviation)
    if t >= 0:
        return 0
    if t > -0.10:
        return 60
    if t >= -0.20:
        return 80
    return 100


def m_low_score(qqq_deviation: float, tqqq_deviation: float) -> float:
    return round(0.6 * qqq_position_score(qqq_deviation) + 0.4 * tqqq_position_score(tqqq_deviation), 2)


def buy_gate(qqq_deviation: float, tqqq_deviation: float, forward_pe: float) -> bool:
    return _number(qqq_deviation) <= 0.05 and _number(tqqq_deviation) < 0 and _positive(forward_pe) <= 25


def buy_value_score(forward_pe: float, pe_percentile: float) -> float:
    pe = _positive(forward_pe)
    percentile = _percentile(pe_percentile)
    if pe > 30:
        absolute = 5
    elif pe > 25:
        absolute = 20
    elif pe > 20:
        absolute = 52
    elif pe >= 18:
        absolute = 78
    else:
        absolute = 92

    if percentile <= 25:
        historical = 95
    elif percentile <= 50:
        historical = 80
    elif percentile <= 75:
        historical = 60
    elif percentile <= 90:
        historical = 30
    else:
        historical = 10
    return min(absolute, historical)


def sell_value_score(
    forward_pe: float,
    pe_percentile: float,
    sustained_months: int = 0,
    earnings_deteriorating: bool = False,
) -> float:
    pe = _positive(forward_pe)
    percentile = _percentile(pe_percentile)
    if sustained_months < 0:
        raise ValueError("sustained_months cannot be negative")
    if pe < 20:
        absolute = 10
    elif pe < 25:
        absolute = 30
    elif pe < 28:
        absolute = 52
    elif pe < 30:
        absolute = 72
    elif sustained_months >= 2 and earnings_deteriorating:
        absolute = 100
    elif sustained_months >= 2:
        absolute = 90
    else:
        absolute = 40

    if percentile <= 25:
        historical = 10
    elif percentile <= 50:
        historical = 25
    elif percentile <= 75:
        historical = 50
    elif percentile <= 90:
        historical = 75
    else:
        historical = 95
    return max(absolute, historical)


def stress_composite(groups: Mapping[str, Iterable[float] | float]) -> float:
    normalized = {}
    for name, values in groups.items():
        if name not in VALID_STRESS_GROUPS:
            raise ValueError(f"unknown stress group: {name}")
        if isinstance(values, (int, float)):
            normalized[name] = _percentile(values)
        else:
            series = [_percentile(value) for value in values]
            if not series:
                continue
            normalized[name] = median(series)
    if len(normalized) < 2 or not ({"credit", "liquidity"} & normalized.keys()):
        raise ValueError("at least two groups including credit or liquidity are required")
    return median(normalized.values())


def macro_group_score(
    ten_year_treasury: float,
    dxy: float,
    cpi: float,
    pce: float,
    cl1: float,
) -> float:
    """Return the macro group's median stress percentile.

    Inputs are sign-aligned historical percentiles; DXY means ICE DXY,
    not a broad trade-weighted dollar index.
    """
    return median(_percentile(value) for value in (ten_year_treasury, dxy, cpi, pce, cl1))


def m_hot_score(deviation_percentile: float) -> int:
    percentile = _percentile(deviation_percentile)
    if percentile < 50:
        return 10
    if percentile < 75:
        return 30
    if percentile < 90:
        return 55
    if percentile < 95:
        return 80
    return 95


def stress_factor_scores(
    stress_level: float,
    delta_stress: float,
    delta2_stress: float,
    *,
    credit_or_liquidity_tightening: bool = False,
    multiple_deteriorating: bool = False,
) -> tuple[int, int]:
    """Return deterministic (F_improve, F_worsening) scores.

    ``stress_level`` is the composite stress percentile. Positive deltas mean
    worsening. The thresholds match the scoring reference's weekly rules.
    """
    level = _percentile(stress_level)
    delta = _number(delta_stress)
    delta2 = _number(delta2_stress)

    if delta >= 5 and delta2 >= 5:
        improve = 15 if level > 50 else 30
        if level > 90:
            worsen = 95
        elif credit_or_liquidity_tightening:
            worsen = 78
        elif multiple_deteriorating:
            worsen = 60
        else:
            worsen = 40
        return improve, worsen

    if delta >= 5:
        return (15 if level > 50 else 30), (78 if credit_or_liquidity_tightening else 60 if multiple_deteriorating else 40)

    if delta <= -5:
        improve = 90 if level > 90 and delta2 <= -5 else 70 if level > 75 else 80
        return improve, 10

    if -5 < delta < 5:
        if level <= 50:
            return 70, 20
        if level <= 75:
            return 55, 30
        return 40, 50

    return 50, 50


def weighted_score(position: float, valuation: float, financial_stress: float) -> float:
    values = [_number(position), _number(valuation), _number(financial_stress)]
    if any(value < 0 or value > 100 for value in values):
        raise ValueError("component scores must be between 0 and 100")
    return round(0.2 * values[0] + 0.4 * values[1] + 0.4 * values[2], 2)


def action_for_score(score: float, side: str) -> str:
    band = score_band(score)
    actions = {
        "buy": {
            "<40": "不买",
            "40-54": "观察或试探",
            "55-69": "正常分批部署",
            "70-84": "提高部署力度",
            "85-100": "接近既定本金上限",
        },
        "sell": {
            "<40": "持有/观察",
            "40-54": "提高警戒、少量兑现",
            "55-69": "正常分批兑现",
            "70-84": "积极分批减仓",
            "85-100": "高强度降低仓位",
        },
    }
    if side not in actions:
        raise ValueError("side must be 'buy' or 'sell'")
    return actions[side][band]
