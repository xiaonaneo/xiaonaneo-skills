# TQQQ 市场分析快照 schema

状态记录只保存市场分析快照，不保存交易目标、仓位、成交、买卖迁移或账户状态。

没有用户明确的持续保存要求时，只输出结果，不创建或覆盖状态文件。用户授权保存时，使用明确指定的路径，并保留已有记录。

## 最小字段

```json
{
  "analysis_version": "2026.09",
  "as_of": "YYYY-MM-DDTHH:mm:ss+08:00",
  "market_state": "MIXED",
  "last_complete_week": "YYYY-MM-DD",
  "ma_position": {
    "qqq_close": null,
    "sma50": null,
    "sma200": null,
    "distance_sma200": null,
    "distance_percentile": null,
    "below_sma200": null,
    "sma50_relation": null,
    "sma50_slope": null
  },
  "valuation": {
    "forward_pe": null,
    "historical_percentile": null,
    "observation_date": null
  },
  "financial_pressure": {
    "hy_oas": {"value": null, "percentile": null, "direction_13w": null, "speed_4w": null, "speed_change": null},
    "nfci": {"value": null, "percentile": null, "direction_13w": null, "speed_4w": null, "speed_change": null},
    "vix": {"value": null, "percentile": null, "direction_13w": null, "speed_4w": null, "speed_change": null}
  },
  "data_quality": {"missing_fields": []},
  "provenance": {"price": [], "valuation": [], "risk": []}
}
```

允许的 `market_state` 为 `DATA_INSUFFICIENT`、`LONG_TERM_WEAK`、`MID_TERM_WEAK`、`MID_TERM_STRONG` 和 `MIXED`。均线关系、斜率、百分位、方向和速度缺失时使用 `null`，不得写成 FALSE、0 或中性。

`direction_13w` 只能是 `worsening`、`easing`、`flat` 或 `unknown`。`speed_4w` 保存近四周平均每周变化，`speed_change` 保存该速度相对前一四周窗口的变化；两者均使用对应指标原始单位。每个指标的单位必须在 provenance 中记录。

同一完整周重复分析应保持幂等：不得因重复运行生成重复事件。快照更新只替换已明确授权的目标文件，不覆盖无法确认归属的文件。
