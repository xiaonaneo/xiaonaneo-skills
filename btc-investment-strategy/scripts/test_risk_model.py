#!/usr/bin/env python3

import unittest

from risk_model import RiskConfigError, calculate_position_size, validate_risk_config


VALID_CONFIG = {
    "portfolio_value_usdt": 100000,
    "current_btc_exposure_usdt": 10000,
    "available_cash_usdt": 90000,
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


class RiskModelTests(unittest.TestCase):
    def test_add_candidate_is_capped_by_single_trade_and_risk(self) -> None:
        result = calculate_position_size(VALID_CONFIG, "add_candidate", 50000)
        self.assertEqual(result["trade_notional_usdt"], 5000.0)
        self.assertEqual(result["btc_quantity"], 0.1)

    def test_large_position_candidate_uses_the_same_risk_caps(self) -> None:
        result = calculate_position_size(VALID_CONFIG, "large_position_candidate", 50000)
        self.assertEqual(result["trade_notional_usdt"], 9615.38461538)
        self.assertEqual(result["trade_cap_type"], "large_trade_cap_pct")

    def test_large_trade_cap_cannot_be_below_normal_cap(self) -> None:
        config = dict(VALID_CONFIG, large_trade_cap_pct=0.04)
        with self.assertRaisesRegex(RiskConfigError, "large_trade_cap_pct"):
            validate_risk_config(config)

    def test_non_add_signal_has_no_position_size(self) -> None:
        result = calculate_position_size({}, "hold_or_wait", 50000)
        self.assertEqual(result["trade_notional_usdt"], 0.0)

    def test_invalid_config_is_rejected(self) -> None:
        config = dict(VALID_CONFIG)
        del config["invalidation_distance_pct"]
        with self.assertRaisesRegex(RiskConfigError, "invalidation_distance_pct"):
            validate_risk_config(config)

    def test_exposure_cap_can_reduce_trade_to_zero(self) -> None:
        config = dict(VALID_CONFIG, current_btc_exposure_usdt=40000)
        result = calculate_position_size(config, "add_candidate", 50000)
        self.assertEqual(result["trade_notional_usdt"], 0.0)

    def test_zero_price_is_rejected(self) -> None:
        with self.assertRaisesRegex(RiskConfigError, "execution_price"):
            calculate_position_size(VALID_CONFIG, "add_candidate", 0)


if __name__ == "__main__":
    unittest.main()
