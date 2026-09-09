---
name: btc-investment-strategy
description: Analyze current Bitcoin market conditions with a six-layer framework covering macro liquidity, spot and ETF flows, price structure, leverage, on-chain valuation, and cycle position. Use when the user asks for BTC market analysis, trend assessment, bottom or top evaluation, current risk-reward, or whether a BTC move is spot-driven or leverage-driven; do not use for unrelated crypto assets or purely technical execution questions.
---

# BTC投资策略

Produce an evidence-based BTC state assessment, not a point-price prediction. The analysis must answer:

1. Is the trend established?
2. Is the market internally fragile?
3. Is the current risk-reward worth taking?

For every current-market request, browse for fresh data. Use English-language or international sources only; do not use Chinese websites. Prefer primary data and cite each time-sensitive claim close to the claim.

Before analysis, read [references/framework.md](references/framework.md), [references/data-contract.md](references/data-contract.md), [references/decision-rules.md](references/decision-rules.md), [references/risk-and-execution.md](references/risk-and-execution.md), and [references/backtest.md](references/backtest.md). They define the six layers, canonical data sources, data conventions, decision state machine, risk and execution rules, backtest contract, synthesis rules, and output contract.

## Deterministic data helpers

- Retrieve current MVRV with `python3 scripts/fetch_mvrv.py`. The helper requests only Coin Metrics Community API metric `CapMVRVCur`, validates that the result is a dimensionless positive ratio, exposes the UTC observation time, and fails closed when the latest observation is stale.
- Validate a normalized snapshot with `python3 scripts/validate_snapshot.py snapshot.json` before assigning an action bias. A blocked or invalid snapshot forbids new exposure; a valid spot-price field may still support a protective reduction.
- Evaluate the normalized snapshot with `python3 scripts/evaluate_signal.py snapshot.json` after the data gate passes. Treat `add_candidate` as a conditional signal only; it does not specify position size or place an order.
- Calculate a position only with an explicit risk configuration using `python3 scripts/calculate_position_size.py risk_config.json --signal add_candidate --price <execution-price>`. Without a valid configuration, do not suggest an amount.
- Validate historical claims with `python3 scripts/backtest_strategy.py data.csv risk_config.json`. The CSV must include `available_at` and a next-bar `execution_at`; reject rows that contain information unavailable at the decision time.
- Do not scrape an unlabeled number from the Glassnode page as MVRV. In particular, reject currency-formatted values and page fields without an explicit MVRV label and timestamp. Follow the fallback contract in [references/framework.md](references/framework.md).

## Data failure recovery

When a public request fails with `Operation not permitted`, a connection to `127.0.0.1:12334`, DNS failure, or a timeout, treat it as an execution-environment/network failure first. Retry the same read-only request through the approved network execution path, preserving the canonical source and the original URL. Do not disable TLS verification, remove proxy settings, switch venues, or replace a failed primary value with an unlabeled secondary value. If the retry still fails, keep the field `unknown` or `stale` and let the data gate block new exposure.

For MVRV, rerun the installed `scripts/fetch_mvrv.py` from the active `btc-investment-strategy` directory. It must request only Coin Metrics `CapMVRVCur`; combined restricted metrics can produce HTTP 403. A successful result must be finite, positive, dimensionless, timestamped in UTC, and no older than 72 hours. A previous value may be carried forward only inside that window and must retain its original `as_of` and retrieval age. Do not turn a secondary chart into a final MVRV value merely because the helper is unavailable.

For Binance weekly averages, request at least 301 `BTCUSDT` 1-week klines, exclude the current partial UTC week, verify 300 contiguous completed weekly bars, and calculate SMA50, MA200, and MA300 from close prices. The current price may be intraday, but the averages must use completed weekly closes. If the official Binance response is unavailable or the continuity check fails, report the SMA regime as unknown and block new exposure.

The Binance open-interest statistics endpoint does not provide a full one-year history. To calculate the required one-year percentile, use Binance's official public daily USDⓈ-M metrics archives, verify each archive with its published SHA256 checksum, and extract the BTC-denominated `sum_open_interest` observation at a consistent UTC time. Require 372 consecutive daily observations to form 365 seven-day changes; never substitute USD-notional OI or shorten the sample.

For funding percentiles, paginate Binance BTCUSDT settled funding history. Build each daily seven-day mean from exactly 21 unique eight-hour settlements. Binance timestamps may differ from the scheduled settlement by milliseconds; normalize offsets below one second, reject larger offsets, and reject any window with missing or duplicate settlements. Use the same latest published date for OI and funding; if today's archive is not published, use the latest common completed date and disclose it.

Calculate both empirical percentiles as `100 * count(sample <= latest) / 365`, including the latest observation and ties. Do not forward-fill, interpolate, or use a shorter history. Save raw responses, observation dates, sample counts, checksums, and errors so the snapshot and signal can be reproduced. Any unresolved error, stale field, incomplete sample, or mismatched date keeps the signal at `data_gap` and forbids new exposure.

## Operating rules

- State the analysis timestamp and timezone, price venue or benchmark, and whether values are live, intraday, or based on the latest completed session.
- Separate observed facts, interpretation, and scenario assumptions. Never present a subjective scenario weight as a statistical probability.
- Analyze short-term, medium-term, and cycle horizons separately. Do not let a bullish cycle view erase poor short-term risk-reward.
- Judge interactions, not isolated indicators. In particular, combine Price, Spot/ETF flow, OI, Funding, and Liquidations before calling a move healthy or fragile.
- Treat macro and halving timing as context, not deterministic clocks. Correlation does not establish causation, and BTC has few independent historical cycles.
- Surface at least two hidden assumptions or plausible disconfirming signals. Explain what evidence would change the conclusion.
- If reliable current data is unavailable or methodologies conflict, say so. Do not fill gaps with unsourced numbers or silently combine mismatched timestamps.
- Keep language objective and direct. Give conditional conclusions and invalidation levels rather than certainty.

## Required output format

Use exactly this compact template and order. Do not add top-level sections or repeat a conclusion in multiple sections:

```markdown
## 核心结论
一句话判断：
状态：趋势 / 脆弱性 / 风险收益
数据状态：完整 / 有缺口；主要反证：

## 宏观数据
DXY、利率、流动性、金融压力、ETF/现货：值、方向、时间、来源
小结：顺风 / 逆风 / 中性

## 周期位置
减半时间表：实际/预计日期、前后 500 天日期、当前 cycle_window

## 价格结构
价格、周 SMA50、周 MA200、周 MA300、sma50_regime、price_zone
结构：HH/HL 或 LH/LL；关键位：

## 杠杆水平
OI、Funding、基差、清算；驱动：现货 / 杠杆 / 混合；脆弱性：

## 链上估值
MVRV、Realized Price、持有人成本、分位数；估值状态：

## 交易决策
动作：data_gap / hold_or_wait / add_candidate / bottom_fishing_candidate / large_position_candidate / reduce / reduce_or_avoid
已有仓位：；新资金：；风险配置：已配置 / 未配置
仓位金额：仅在风险配置有效时给出；失效条件：；执行：下一根可交易 K 线
```

事实、判断和未知信息分别标注；`交易决策` 是唯一输出行动状态、仓位、失效位和执行条件的部分。缺少关键数据时不得新增仓位，不能给出未经配置支持的金额或价格目标。
