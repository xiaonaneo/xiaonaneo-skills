"""Deterministic helpers for the TQQQ scoring reference."""

from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime
from math import isfinite
from statistics import median
from typing import Iterable, Mapping


VALID_STRESS_GROUPS = {"credit", "liquidity", "volatility", "macro"}
REQUIRED_GROUP_COMPONENTS = {
    "credit": 2,
    "liquidity": 3,
    "volatility": 1,
    "macro": 4,
}


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


def _deviation(value: float) -> float:
    value = _number(value)
    if value <= -1:
        raise ValueError("deviation requires a positive price and moving average")
    return value


def _whole_months(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("sustained_months must be a non-negative integer")
    return value


def empirical_percentile(value: float, history: Iterable[float], *, minimum_observations: int = 104) -> float:
    """Return the inclusive empirical percentile for a frozen history window."""
    if isinstance(minimum_observations, bool) or not isinstance(minimum_observations, int) or minimum_observations < 1:
        raise ValueError("minimum_observations must be a positive integer")
    values = [_number(item) for item in history]
    if len(values) < minimum_observations:
        raise ValueError("insufficient history for percentile")
    current = _number(value)
    return round(100 * sum(item <= current for item in values) / len(values), 4)


def validate_forward_pe_records(
    records: Iterable[Mapping[str, object]],
    *,
    analysis_at: datetime,
    minimum_months: int = 60,
) -> tuple[tuple[date, float], ...]:
    """Validate the versioned month-end records required for forward P/E scoring."""
    if analysis_at.tzinfo is None:
        raise ValueError("analysis_at must include a timezone")
    if isinstance(minimum_months, bool) or not isinstance(minimum_months, int) or minimum_months < 1:
        raise ValueError("minimum_months must be a positive integer")

    required = {"period_end", "value", "available_at", "source_id", "source_url", "retrieved_at"}
    validated: list[tuple[date, float]] = []
    source_id: str | None = None
    for record in records:
        if set(record) != required:
            raise ValueError("forward P/E record fields do not match the data contract")
        try:
            period_end = date.fromisoformat(str(record["period_end"]))
            available_at = datetime.fromisoformat(str(record["available_at"]).replace("Z", "+00:00"))
            retrieved_at = datetime.fromisoformat(str(record["retrieved_at"]).replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("forward P/E record has an invalid date or timestamp") from error
        if period_end.day != monthrange(period_end.year, period_end.month)[1]:
            raise ValueError("period_end must be a month-end date")
        if available_at.tzinfo is None or retrieved_at.tzinfo is None:
            raise ValueError("forward P/E timestamps must include timezones")
        if available_at > analysis_at or retrieved_at < available_at:
            raise ValueError("forward P/E record is not point-in-time visible")
        identifier = record["source_id"]
        url = record["source_url"]
        if not isinstance(identifier, str) or not identifier or not isinstance(url, str) or not url:
            raise ValueError("forward P/E record requires a source id and URL")
        if source_id is None:
            source_id = identifier
        elif identifier != source_id:
            raise ValueError("forward P/E records must use one source")
        validated.append((period_end, _positive(record["value"])))

    if len(validated) < minimum_months:
        raise ValueError("insufficient forward P/E month-end records")
    validated.sort()
    for index, (period_end, _) in enumerate(validated):
        if index and period_end == validated[index - 1][0]:
            raise ValueError("duplicate forward P/E month")
        if index:
            prior = validated[index - 1][0]
            expected_year = prior.year + (prior.month == 12)
            expected_month = 1 if prior.month == 12 else prior.month + 1
            if (period_end.year, period_end.month) != (expected_year, expected_month):
                raise ValueError("forward P/E months must be contiguous")
    return tuple(validated)


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
    d = _deviation(deviation)
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
    t = _deviation(deviation)
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
    return _deviation(qqq_deviation) <= 0.05 and _deviation(tqqq_deviation) < 0 and _positive(forward_pe) <= 25


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
    sustained_months = _whole_months(sustained_months)
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
        absolute = 72

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


def sell_valuation_confirmed(forward_pe: float, pe_percentile: float, sustained_months: int = 0) -> bool:
    """Return whether valuation can count as a sell-side confirmation factor."""
    pe = _positive(forward_pe)
    percentile = _percentile(pe_percentile)
    months = _whole_months(sustained_months)
    return percentile > 90 or (pe >= 30 and months >= 2)


def stress_group_score(name: str, component_percentiles: Iterable[float]) -> float:
    """Return a group score only when every documented component is present."""
    if name not in VALID_STRESS_GROUPS:
        raise ValueError(f"unknown stress group: {name}")
    values = [_percentile(value) for value in component_percentiles]
    expected = REQUIRED_GROUP_COMPONENTS[name]
    if len(values) != expected:
        raise ValueError(f"{name} requires exactly {expected} component values")
    return median(values)


def _normalized_stress_groups(groups: Mapping[str, float]) -> dict[str, float]:
    normalized = {}
    for name, value in groups.items():
        if name not in VALID_STRESS_GROUPS:
            raise ValueError(f"unknown stress group: {name}")
        normalized[name] = _percentile(value)
    if len(normalized) < 2 or not ({"credit", "liquidity"} & normalized.keys()):
        raise ValueError("at least two groups including credit or liquidity are required")
    return normalized


def stress_composite(groups: Mapping[str, float]) -> float:
    return median(_normalized_stress_groups(groups).values())


def stress_trend(
    current: Mapping[str, float],
    previous: Mapping[str, float],
    two_weeks_ago: Mapping[str, float],
) -> tuple[float, float, float]:
    """Return comparable weekly ``(Stress_t, ΔStress, Δ²Stress)`` values."""
    current_groups = _normalized_stress_groups(current)
    previous_groups = _normalized_stress_groups(previous)
    two_weeks_ago_groups = _normalized_stress_groups(two_weeks_ago)
    coverage = frozenset(current_groups)
    if coverage != frozenset(previous_groups) or coverage != frozenset(two_weeks_ago_groups):
        raise ValueError("stress groups must match across all three weeks")
    current_value = median(current_groups.values())
    previous_value = median(previous_groups.values())
    two_weeks_ago_value = median(two_weeks_ago_groups.values())
    delta = current_value - previous_value
    return current_value, delta, delta - (previous_value - two_weeks_ago_value)


def macro_group_score(
    ten_year_treasury: float,
    dxy: float,
    cpi: float,
    pce: float,
) -> float:
    """Return the macro group's median stress percentile.

    Inputs are sign-aligned historical percentiles; DXY means ICE DXY,
    not a broad trade-weighted dollar index.
    """
    return stress_group_score("macro", (ten_year_treasury, dxy, cpi, pce))


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
    elif delta >= 5:
        improve = 15 if level > 50 else 30
        worsen = 40
    elif delta <= -5:
        improve = 90 if level > 90 and delta2 <= -5 else 70 if level > 75 else 80
        worsen = 10
    else:
        if level <= 50:
            improve, worsen = 70, 20
        elif level <= 75:
            improve, worsen = 55, 30
        else:
            improve, worsen = 40, 50

    if multiple_deteriorating:
        improve, worsen = min(improve, 40), max(worsen, 60)
    if credit_or_liquidity_tightening:
        improve, worsen = min(improve, 30), max(worsen, 78)
    return improve, worsen


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


def executable_action(
    side: str,
    confirmed_factors: int,
    *,
    hard_gate_passed: bool = True,
    two_week_confirmed: bool = True,
    score: float | None = None,
) -> str:
    """Return the action allowed by gates, confirmation count, and score."""
    if side not in {"buy", "sell"}:
        raise ValueError("side must be 'buy' or 'sell'")
    if isinstance(confirmed_factors, bool) or not isinstance(confirmed_factors, int) or not 0 <= confirmed_factors <= 3:
        raise ValueError("confirmed_factors must be an integer from 0 to 3")
    if side == "buy" and not hard_gate_passed:
        return "不买"
    if confirmed_factors < 2 or not two_week_confirmed:
        return "观察/不买" if side == "buy" else "观察/准备兑现"
    if confirmed_factors == 2:
        return "正常分批部署" if side == "buy" else "正常分批兑现"
    if score is None:
        return "观察/不买" if side == "buy" else "观察/准备兑现"
    return action_for_score(score, side)
