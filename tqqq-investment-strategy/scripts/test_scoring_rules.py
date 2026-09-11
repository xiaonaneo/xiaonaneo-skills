import unittest
from calendar import monthrange
from datetime import datetime, timezone
from pathlib import Path

from scoring_rules import (
    buy_gate,
    buy_value_score,
    action_for_score,
    empirical_percentile,
    executable_action,
    macro_group_score,
    m_hot_score,
    m_low_score,
    score_band,
    sell_value_score,
    sell_valuation_confirmed,
    stress_composite,
    stress_factor_scores,
    stress_group_score,
    stress_trend,
    validate_forward_pe_records,
    weighted_score,
)


class ScoringRulesTest(unittest.TestCase):
    def test_score_band_boundaries(self):
        self.assertEqual(score_band(39.99), "<40")
        self.assertEqual(score_band(40), "40-54")
        self.assertEqual(score_band(54.99), "40-54")
        self.assertEqual(score_band(55), "55-69")
        self.assertEqual(score_band(69.99), "55-69")
        self.assertEqual(score_band(70), "70-84")
        self.assertEqual(score_band(84.99), "70-84")
        self.assertEqual(score_band(85), "85-100")

    def test_buy_gate_boundaries(self):
        self.assertTrue(buy_gate(0.05, -0.01, 25))
        self.assertFalse(buy_gate(0.0501, -0.01, 25))
        self.assertFalse(buy_gate(0.05, 0, 25))
        self.assertFalse(buy_gate(0.05, -0.01, 25.01))
        with self.assertRaises(ValueError):
            buy_gate(0.05, -0.01, 0)
        with self.assertRaises(ValueError):
            buy_gate(-1, -0.01, 20)

    def test_position_score(self):
        self.assertEqual(m_low_score(0.05, -0.10), 74)
        self.assertEqual(m_low_score(-0.10, -0.20), 92)

    def test_valuation_boundaries(self):
        self.assertEqual(buy_value_score(20, 50), 78)
        self.assertEqual(buy_value_score(20.01, 50), 52)
        self.assertEqual(sell_value_score(30, 75, 1), 72)
        self.assertEqual(sell_value_score(30, 75, 2), 90)
        self.assertEqual(sell_value_score(30, 75, 2, True), 100)
        with self.assertRaises(ValueError):
            buy_value_score(20, -1)
        with self.assertRaises(ValueError):
            sell_value_score(30, 75, float("inf"))
        self.assertFalse(sell_valuation_confirmed(30, 75, 1))
        self.assertTrue(sell_valuation_confirmed(30, 75, 2))
        self.assertTrue(sell_valuation_confirmed(25, 91))

    def test_stress_composite_requires_core_group(self):
        self.assertEqual(
            stress_composite({"credit": 70, "macro": 40}),
            55,
        )
        with self.assertRaises(ValueError):
            stress_composite({"volatility": 80, "macro": 60})
        with self.assertRaises(ValueError):
            stress_composite({"credit": 80, "unknown": 60})

    def test_stress_group_components_and_percentile_history(self):
        self.assertEqual(stress_group_score("credit", [80, 60]), 70)
        self.assertEqual(stress_group_score("liquidity", [40, 60, 80]), 60)
        with self.assertRaises(ValueError):
            stress_group_score("credit", [80])
        self.assertEqual(empirical_percentile(3, [1, 2, 3, 4], minimum_observations=4), 75)
        with self.assertRaises(ValueError):
            empirical_percentile(3, [1, 2, 3], minimum_observations=4)

    def test_forward_pe_records_require_versioned_contiguous_months(self):
        records = []
        year, month = 2021, 1
        for _ in range(60):
            last_day = monthrange(year, month)[1]
            records.append(
                {
                    "period_end": f"{year:04d}-{month:02d}-{last_day:02d}",
                    "value": 20,
                    "available_at": "2026-01-01T00:00:00+00:00",
                    "source_id": "vendor:ndx-forward-pe",
                    "source_url": "https://example.com/export/2026-01",
                    "retrieved_at": "2026-01-01T00:01:00+00:00",
                }
            )
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)
        analysis_at = datetime(2026, 1, 2, tzinfo=timezone.utc)
        self.assertEqual(len(validate_forward_pe_records(records, analysis_at=analysis_at)), 60)
        with self.assertRaises(ValueError):
            validate_forward_pe_records(records[:-1], analysis_at=analysis_at)
        records[1]["period_end"] = records[0]["period_end"]
        with self.assertRaises(ValueError):
            validate_forward_pe_records(records, analysis_at=analysis_at)

    def test_stress_trend_requires_identical_coverage(self):
        current = {"credit": 20, "liquidity": 40, "volatility": 80}
        previous = {"credit": 20, "liquidity": 40, "volatility": 80}
        two_weeks_ago = {"credit": 20, "liquidity": 40, "volatility": 80}
        self.assertEqual(stress_trend(current, previous, two_weeks_ago), (40, 0, 0))
        with self.assertRaises(ValueError):
            stress_trend({**current, "macro": 0}, previous, two_weeks_ago)

    def test_macro_group_uses_four_required_inputs(self):
        self.assertEqual(macro_group_score(80, 60, 40, 50), 55)
        with self.assertRaises(ValueError):
            macro_group_score(101, 60, 40, 50)

    def test_hot_position_boundaries(self):
        self.assertEqual(m_hot_score(49.99), 10)
        self.assertEqual(m_hot_score(50), 30)
        self.assertEqual(m_hot_score(75), 55)
        self.assertEqual(m_hot_score(90), 80)
        self.assertEqual(m_hot_score(95), 95)

    def test_stress_factor_scores(self):
        self.assertEqual(stress_factor_scores(95, 5, 5), (15, 95))
        self.assertEqual(stress_factor_scores(80, -5, -5), (70, 10))
        self.assertEqual(stress_factor_scores(50, 0, 0), (70, 20))
        self.assertEqual(
            stress_factor_scores(95, -5, -5, credit_or_liquidity_tightening=True),
            (30, 78),
        )

    def test_action_mapping(self):
        self.assertEqual(action_for_score(70, "buy"), "提高部署力度")
        self.assertEqual(action_for_score(85, "sell"), "高强度降低仓位")
        with self.assertRaises(ValueError):
            action_for_score(70, "hold")

    def test_executable_action_applies_gates_and_confirmation(self):
        self.assertEqual(executable_action("buy", 3, hard_gate_passed=False, score=90), "不买")
        self.assertEqual(executable_action("sell", 1, score=90), "观察/准备兑现")
        self.assertEqual(executable_action("buy", 2, score=90), "正常分批部署")
        self.assertEqual(executable_action("sell", 2, score=90), "正常分批兑现")
        self.assertEqual(executable_action("sell", 3, two_week_confirmed=False, score=90), "观察/准备兑现")
        self.assertEqual(executable_action("sell", 3, score=90), "高强度降低仓位")

    def test_weighted_score(self):
        self.assertEqual(weighted_score(70, 60, 50), 58)

    def test_default_output_template(self):
        skill = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")
        fixed = skill.split("## 固定输出结构", 1)[1]
        self.assertIn("**核心结论**", fixed)
        self.assertIn("**均线位置**", fixed)
        self.assertIn("**估值水平**", fixed)
        self.assertIn("**金融压力**", fixed)
        self.assertIn("**交易评分**", fixed)
        self.assertNotIn("|", fixed)
        self.assertIn("评分：", fixed)
        self.assertIn("结论：**（行动映射）**", fixed)
        self.assertIn("不得在结果中写入该文件未列出的估值或原油来源", fixed)
        self.assertIn("已授权 NDX `pe-forward` 版本化导出不可用", fixed)
        self.assertTrue(
            "当前、前一周、前两周的有效组集合" in fixed
            or "各板块的“数据：”行只写最终数据" in fixed
        )

    def test_missing_score_component_does_not_block_two_factor_sell(self):
        skill = (Path(__file__).parents[1] / "SKILL.md").read_text(encoding="utf-8")
        scoring = (Path(__file__).parents[1] / "references" / "scoring-system.md").read_text(encoding="utf-8")
        self.assertIn("数值总分 N/A 与定性行动不可用是两个不同结论", skill)
        self.assertIn("D≥P90` 与有效压力恶化加速", skill)
        self.assertIn("不得以等待估值或宏观组数据为由跳过分批减仓", skill)
        self.assertIn("宏观组 N/A 仅表示该组不参与本周复合值", scoring)
        self.assertIn("不得等待估值或宏观组补齐", scoring)

    def test_sources_cover_forward_pe_history_and_direct_ice_dxy(self):
        sources = (Path(__file__).parents[1] / "references" / "sources-and-metrics.md").read_text(encoding="utf-8")
        self.assertIn("Trendonify Nasdaq-100 Forward P/E", sources)
        self.assertIn("60 个连续月末观测", sources)
        self.assertIn("Yahoo `DX-Y.NYB`", sources)
        self.assertIn("ICE Futures 的 U.S. Dollar Index", sources)
        self.assertIn("美元期货连续合约", sources)
        self.assertNotIn("NYMEX:CL1!", sources)
        self.assertNotIn("WTI", sources)


if __name__ == "__main__":
    unittest.main()
