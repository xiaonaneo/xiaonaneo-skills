import unittest
from pathlib import Path

from scoring_rules import (
    buy_gate,
    buy_value_score,
    action_for_score,
    macro_group_score,
    m_hot_score,
    m_low_score,
    score_band,
    sell_value_score,
    stress_composite,
    stress_factor_scores,
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

    def test_position_score(self):
        self.assertEqual(m_low_score(0.05, -0.10), 74)
        self.assertEqual(m_low_score(-0.10, -0.20), 92)

    def test_valuation_boundaries(self):
        self.assertEqual(buy_value_score(20, 50), 78)
        self.assertEqual(buy_value_score(20.01, 50), 52)
        self.assertEqual(sell_value_score(30, 75, 1), 50)
        self.assertEqual(sell_value_score(30, 75, 2), 90)
        self.assertEqual(sell_value_score(30, 75, 2, True), 100)
        with self.assertRaises(ValueError):
            buy_value_score(20, -1)

    def test_stress_composite_requires_core_group(self):
        self.assertEqual(
            stress_composite({"credit": [80, 60], "macro": 40}),
            55,
        )
        with self.assertRaises(ValueError):
            stress_composite({"volatility": 80, "macro": 60})
        with self.assertRaises(ValueError):
            stress_composite({"credit": 80, "unknown": 60})

    def test_macro_group_uses_five_required_inputs(self):
        self.assertEqual(macro_group_score(80, 60, 40, 50, 70), 60)
        with self.assertRaises(ValueError):
            macro_group_score(101, 60, 40, 50, 70)

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

    def test_action_mapping(self):
        self.assertEqual(action_for_score(70, "buy"), "提高部署力度")
        self.assertEqual(action_for_score(85, "sell"), "高强度降低仓位")
        with self.assertRaises(ValueError):
            action_for_score(70, "hold")

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
        self.assertIn("MacroMicro Nasdaq-100 Forward P/E", sources)
        self.assertIn("至少 60 个连续月度观测", sources)
        self.assertIn("Yahoo `DX-Y.NYB`", sources)
        self.assertIn("ICE Futures 的 U.S. Dollar Index", sources)
        self.assertIn("美元期货连续合约", sources)


if __name__ == "__main__":
    unittest.main()
