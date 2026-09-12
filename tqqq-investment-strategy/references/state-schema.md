# TQQQ 市场状态 schema

状态记录只保存市场分析结果，不保存交易目标、仓位或成交信息。没有用户明确的持续保存要求时，只输出结果，不写入文件。

```json
{
  "analysis_version": "2026.09",
  "market_state": "UNKNOWN",
  "structural_check": "UNKNOWN",
  "top_risk_candidate": null,
  "risk_state": "UNKNOWN",
  "risk_flags": {
    "c": null,
    "l": null,
    "e": null,
    "o_high": null,
    "v_high": null,
    "r_high": null
  },
  "trend_flags": {
    "trend_recovery": null,
    "td1": null,
    "td2": null,
    "td3": null
  },
  "level_diagnostics": {},
  "earnings_quality": {},
  "last_complete_week": null,
  "last_evaluation_at": null,
  "data_quality": {
    "missing_fields": [],
    "known_count": null,
    "possible_range": null
  },
  "provenance": {
    "price": [],
    "valuation": [],
    "risk": []
  }
}
```

market_state 只能是 UNKNOWN、STRUCTURE_STABLE、TOP_RISK_CANDIDATE、MID_TREND_DAMAGE、LONG_TREND_DAMAGE、STRUCTURE_FAILURE 或 DATA_INSUFFICIENT。所有 flags 可为 TRUE、FALSE 或 NA。

市场状态优先级为 DATA_INSUFFICIENT > STRUCTURE_FAILURE > LONG_TREND_DAMAGE > MID_TREND_DAMAGE > TOP_RISK_CANDIDATE > STRUCTURE_STABLE；原始 flags 必须同时保留。

每次分析读取上一条市场状态，使用最新可见的完整周线更新。同一完整周已处理过时保持幂等，不重复生成事件。事件 reason 只能描述市场结构、顶部风险、趋势恢复、趋势破坏或数据不足。
