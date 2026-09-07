#!/usr/bin/env python3
"""Fetch validated daily BTC MVRV from the Coin Metrics Community API."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import json
import re
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_ENDPOINT = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
METHODOLOGY_URL = "https://docs.coinmetrics.io/asset-metrics/market/capmvrvcur"


class MVRVError(ValueError):
    """Raised when the response cannot provide a trustworthy MVRV value."""


def build_url(page_size: int = 5) -> str:
    query = urlencode(
        {
            "assets": "btc",
            "metrics": "CapMVRVCur",
            "frequency": "1d",
            "page_size": page_size,
            "paging_from": "end",
        }
    )
    return f"{API_ENDPOINT}?{query}"


def parse_time(value: str) -> datetime:
    if not isinstance(value, str):
        raise MVRVError(f"invalid observation timestamp: {value!r}")
    match = re.fullmatch(
        r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d+))?(Z|[+-]\d{2}:\d{2})",
        value,
    )
    if not match:
        raise MVRVError(f"invalid observation timestamp: {value!r}")
    base, fraction, zone = match.groups()
    fractional_part = f".{fraction[:6]}" if fraction else ""
    normalized_zone = "+00:00" if zone == "Z" else zone
    try:
        parsed = datetime.fromisoformat(f"{base}{fractional_part}{normalized_zone}")
    except ValueError as exc:
        raise MVRVError(f"invalid observation timestamp: {value!r}") from exc
    if parsed.tzinfo is None:
        raise MVRVError(f"observation timestamp lacks timezone: {value!r}")
    return parsed.astimezone(timezone.utc)


def parse_observations(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("data")
    if not isinstance(rows, list) or not rows:
        raise MVRVError("response contains no observations")

    observations: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict) or row.get("asset") != "btc":
            continue
        raw_value = row.get("CapMVRVCur")
        try:
            value = Decimal(str(raw_value))
        except (InvalidOperation, ValueError) as exc:
            raise MVRVError(f"MVRV is not a dimensionless number: {raw_value!r}") from exc
        if not value.is_finite() or value <= 0 or value >= 100:
            raise MVRVError(f"MVRV is outside the validation range: {raw_value!r}")
        observed_at = parse_time(row.get("time"))
        observations.append(
            {
                "as_of": observed_at.isoformat().replace("+00:00", "Z"),
                "value": float(value),
                "_time": observed_at,
            }
        )

    if not observations:
        raise MVRVError("response contains no BTC MVRV observations")
    observations.sort(key=lambda item: item["_time"])
    return observations


def build_result(
    payload: dict[str, Any],
    *,
    retrieved_at: datetime | None = None,
    max_staleness_hours: float = 72,
    source_url: str | None = None,
) -> dict[str, Any]:
    retrieved_at = (retrieved_at or datetime.now(timezone.utc)).astimezone(timezone.utc)
    observations = parse_observations(payload)
    latest = observations[-1]
    age_hours = (retrieved_at - latest["_time"]).total_seconds() / 3600
    if age_hours < 0:
        raise MVRVError("latest MVRV observation is in the future")
    status = "stale" if age_hours > max_staleness_hours else "ok"
    public_observations = [
        {"as_of": item["as_of"], "value": item["value"]} for item in observations
    ]
    return {
        "status": status,
        "asset": "btc",
        "metric": "CapMVRVCur",
        "display_name": "MVRV",
        "unit": "dimensionless",
        "frequency": "1d",
        "value": latest["value"],
        "as_of": latest["as_of"],
        "retrieved_at": retrieved_at.isoformat().replace("+00:00", "Z"),
        "age_hours": round(age_hours, 2),
        "provider": "Coin Metrics Community API",
        "source_url": source_url or build_url(len(observations)),
        "methodology_url": METHODOLOGY_URL,
        "observations": public_observations,
    }


def fetch_payload(url: str, timeout: float) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": "btc-investment-strategy/1.0"})
    with urlopen(request, timeout=timeout) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise MVRVError("API response is not a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page-size", type=int, default=5, choices=range(1, 31))
    parser.add_argument("--timeout", type=float, default=15)
    parser.add_argument("--max-staleness-hours", type=float, default=72)
    args = parser.parse_args()

    url = build_url(args.page_size)
    try:
        result = build_result(
            fetch_payload(url, args.timeout),
            max_staleness_hours=args.max_staleness_hours,
            source_url=url,
        )
    except (HTTPError, URLError, TimeoutError, OSError, MVRVError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc), "source_url": url}))
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 2


if __name__ == "__main__":
    sys.exit(main())
