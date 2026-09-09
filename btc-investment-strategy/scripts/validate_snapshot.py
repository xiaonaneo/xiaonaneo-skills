#!/usr/bin/env python3
"""Validate a normalized BTC analysis snapshot before producing an action bias."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_METRICS = (
    "spot_price",
    "weekly_sma50",
    "weekly_ma200",
    "weekly_ma300",
    "etf_flow_5d",
    "etf_flow_20d",
    "oi_7d_change",
    "funding_8h",
    "financial_stress",
    "mvrv",
    "halving_timeline",
)
ALLOWED_STATUSES = {"final", "preliminary", "estimated", "stale", "unknown"}
BLOCKING_STATUSES = {"preliminary", "stale", "unknown"}
REQUIRED_METADATA = (
    "unit",
    "source",
    "venue_or_series",
    "observed_at",
    "available_at",
    "status",
    "methodology",
)


class SnapshotError(ValueError):
    """Raised when the snapshot is malformed rather than merely incomplete."""


def parse_timestamp(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise SnapshotError(f"{field} must be an ISO-8601 timestamp")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise SnapshotError(f"{field} is not a valid ISO-8601 timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise SnapshotError(f"{field} must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(snapshot, dict):
        raise SnapshotError("snapshot must be a JSON object")
    as_of = parse_timestamp(snapshot.get("as_of"), "as_of")
    errors: list[str] = []
    blockers: list[str] = []
    benchmark = snapshot.get("benchmark")
    derivatives_benchmark = snapshot.get("derivatives_benchmark")
    override = snapshot.get("benchmark_override") is True
    if benchmark != "Binance spot BTCUSDT" or derivatives_benchmark != "Binance USDⓈ-M BTCUSDT perpetual":
        if not override:
            blockers.append("non-canonical benchmark without explicit override")
        elif not isinstance(snapshot.get("override_reason"), str) or not snapshot["override_reason"].strip():
            errors.append("benchmark_override requires a non-empty override_reason")
    fields = snapshot.get("fields")
    if not isinstance(fields, list):
        raise SnapshotError("fields must be a JSON array")

    by_metric: dict[str, dict[str, Any]] = {}
    for index, field in enumerate(fields):
        prefix = f"fields[{index}]"
        if not isinstance(field, dict):
            errors.append(f"{prefix} must be an object")
            continue
        metric = field.get("metric")
        if not isinstance(metric, str) or not metric:
            errors.append(f"{prefix}.metric must be a non-empty string")
            continue
        if metric in by_metric:
            errors.append(f"duplicate metric: {metric}")
            continue
        by_metric[metric] = field
        for key in REQUIRED_METADATA:
            if key not in field:
                errors.append(f"{metric} missing {key}")
        status = field.get("status")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{metric}.status is invalid: {status!r}")
        elif status == "estimated" and metric != "halving_timeline":
            blockers.append(f"{metric} cannot be estimated")
        try:
            observed_at = parse_timestamp(field.get("observed_at"), f"{metric}.observed_at")
            available_at = parse_timestamp(field.get("available_at"), f"{metric}.available_at")
            if observed_at > as_of:
                errors.append(f"{metric}.observed_at is after snapshot as_of")
            if available_at > as_of:
                errors.append(f"{metric}.available_at is after snapshot as_of")
            if available_at < observed_at:
                errors.append(f"{metric}.available_at is before observed_at")
        except SnapshotError as exc:
            errors.append(str(exc))
        for key in ("unit", "source"):
            if not isinstance(field.get(key), str) or not field[key].strip():
                errors.append(f"{metric}.{key} must be a non-empty string")
        if "value" not in field:
            errors.append(f"{metric} missing value")
        if status in BLOCKING_STATUSES:
            blockers.append(f"{metric} status={status}")

    for metric in REQUIRED_METRICS:
        if metric not in by_metric:
            blockers.append(f"missing critical metric: {metric}")

    spot_valid = (
        "spot_price" in by_metric
        and by_metric["spot_price"].get("status") == "final"
        and not any(error.startswith("spot_price") for error in errors)
    )
    result = {
        "status": "invalid" if errors else ("blocked" if blockers else "ok"),
        "as_of": as_of.isoformat().replace("+00:00", "Z"),
        "required_metrics": list(REQUIRED_METRICS),
        "errors": errors,
        "blockers": blockers,
        "new_exposure_allowed": not errors and not blockers,
        "protective_reduction_basis_available": spot_valid,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    try:
        snapshot = json.loads(args.snapshot.read_text(encoding="utf-8"))
        result = validate_snapshot(snapshot)
    except (OSError, json.JSONDecodeError, SnapshotError) as exc:
        print(json.dumps({"status": "invalid", "errors": [str(exc)]}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 2


if __name__ == "__main__":
    sys.exit(main())
