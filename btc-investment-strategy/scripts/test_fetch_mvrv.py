#!/usr/bin/env python3

from datetime import datetime, timezone
import unittest
from urllib.parse import parse_qs, urlparse

from fetch_mvrv import MVRVError, build_result, build_url, parse_observations


class FetchMVRVTests(unittest.TestCase):
    def test_build_url_requests_only_community_mvrv(self) -> None:
        query = parse_qs(urlparse(build_url()).query)
        self.assertEqual(query["assets"], ["btc"])
        self.assertEqual(query["metrics"], ["CapMVRVCur"])
        self.assertEqual(query["frequency"], ["1d"])

    def test_latest_observation_wins_even_when_input_is_unsorted(self) -> None:
        rows = parse_observations(
            {
                "data": [
                    {"asset": "btc", "time": "2026-09-03T00:00:00Z", "CapMVRVCur": "1.52"},
                    {"asset": "btc", "time": "2026-09-02T00:00:00Z", "CapMVRVCur": "1.45"},
                ]
            }
        )
        self.assertEqual(rows[-1]["value"], 1.52)

    def test_coin_metrics_nanosecond_timestamp_is_supported(self) -> None:
        rows = parse_observations(
            {
                "data": [
                    {
                        "asset": "btc",
                        "time": "2026-09-03T00:00:00.000000000Z",
                        "CapMVRVCur": "1.529084095903799471",
                    }
                ]
            }
        )
        self.assertEqual(rows[0]["as_of"], "2026-09-03T00:00:00Z")

    def test_currency_value_is_rejected(self) -> None:
        with self.assertRaisesRegex(MVRVError, "dimensionless"):
            parse_observations(
                {
                    "data": [
                        {
                            "asset": "btc",
                            "time": "2026-09-03T00:00:00Z",
                            "CapMVRVCur": "$420,690",
                        }
                    ]
                }
            )

    def test_stale_observation_fails_closed(self) -> None:
        result = build_result(
            {
                "data": [
                    {"asset": "btc", "time": "2026-09-01T00:00:00Z", "CapMVRVCur": "1.4"}
                ]
            },
            retrieved_at=datetime(2026, 9, 5, tzinfo=timezone.utc),
            max_staleness_hours=72,
        )
        self.assertEqual(result["status"], "stale")

    def test_current_observation_includes_unit_and_history(self) -> None:
        result = build_result(
            {
                "data": [
                    {"asset": "btc", "time": "2026-09-03T00:00:00Z", "CapMVRVCur": "1.529"}
                ]
            },
            retrieved_at=datetime(2026, 9, 4, tzinfo=timezone.utc),
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["unit"], "dimensionless")
        self.assertEqual(result["observations"][0]["value"], 1.529)


if __name__ == "__main__":
    unittest.main()
