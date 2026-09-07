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

Before analysis, read [references/framework.md](references/framework.md). It defines the six layers, data conventions, synthesis rules, and output contract.

## Deterministic data helpers

- Retrieve current MVRV with `python3 scripts/fetch_mvrv.py`. The helper requests only Coin Metrics Community API metric `CapMVRVCur`, validates that the result is a dimensionless positive ratio, exposes the UTC observation time, and fails closed when the latest observation is stale.
- Do not scrape an unlabeled number from the Glassnode page as MVRV. In particular, reject currency-formatted values and page fields without an explicit MVRV label and timestamp. Follow the fallback contract in [references/framework.md](references/framework.md).

## Operating rules

- State the analysis timestamp and timezone, price venue or benchmark, and whether values are live, intraday, or based on the latest completed session.
- Separate observed facts, interpretation, and scenario assumptions. Never present a subjective scenario weight as a statistical probability.
- Analyze short-term, medium-term, and cycle horizons separately. Do not let a bullish cycle view erase poor short-term risk-reward.
- Judge interactions, not isolated indicators. In particular, combine Price, Spot/ETF flow, OI, Funding, and Liquidations before calling a move healthy or fragile.
- Treat macro and halving timing as context, not deterministic clocks. Correlation does not establish causation, and BTC has few independent historical cycles.
- Surface at least two hidden assumptions or plausible disconfirming signals. Explain what evidence would change the conclusion.
- If reliable current data is unavailable or methodologies conflict, say so. Do not fill gaps with unsourced numbers or silently combine mismatched timestamps.
- Keep language objective and direct. Give conditional conclusions and invalidation levels rather than certainty.

## Required conclusion

End with a compact dashboard containing:

- Trend: bullish, neutral, or bearish, with horizon.
- Fragility: low, medium, or high.
- Financial stress: low, medium, high, or unknown, with easing/stable/worsening direction and implications for the action bias.
- Risk-reward: favorable, neutral, or unfavorable.
- Driver: spot-led, leverage-led, mixed, or unclear.
- Weekly MA band: above weekly MA200, between weekly MA200 and weekly MA300, or below weekly MA300; if the averages are inverted, report the actual relation to both instead of forcing a band.
- Halving timeline: the most recent actual and next projected halving dates, with the calendar dates 500 days before and 500 days after each relevant halving.
- Action bias: add, hold, wait, reduce, or avoid, expressed conditionally unless the user supplied a portfolio and explicit rules.
- Invalidation: the price, flow, leverage, or macro evidence that would overturn the view.

Include a base, upside, and downside path with triggers. Avoid unsupported price targets.
