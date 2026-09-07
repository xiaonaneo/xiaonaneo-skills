# BTC Decision Rules

This is a deterministic signal state machine, not a promise of predictive performance. Thresholds are research defaults and must be validated against historical data before being used as an order system.

## Factor states

Use the normalized snapshot contract and compute these states:

- **Price:** when weekly MA200 is at least weekly MA300, price above MA200 is `bullish`, below MA300 is `bearish`, and the interval between them is `neutral`. If the averages are inverted, use `inverted` and report both relations.
- **Spot:** both 5-day and 20-day ETF net flows positive is `positive`; both negative is `negative`; otherwise `mixed`.
- **Leverage:** use one-year percentile fields for 7-day OI change and 7-day average Funding. Both at or above the 80th percentile is `high`; both at or below the 50th percentile is `low`; otherwise `medium`. A confirmed liquidation cascade is `high`. Missing percentiles are `unknown` and cannot support an add.
- **Financial stress:** use `low`, `medium`, `high`, or `unknown`, plus `easing`, `stable`, or `worsening`. Do not infer `low` from missing data.
- **Valuation:** use the MVRV percentile over the same provider's available history. At or below the 20th percentile is `low`, at or above the 80th percentile is `high`, otherwise `neutral`. If a comparable percentile is unavailable, use `unknown`.
- **Cycle:** `supportive`, `neutral`, or `unknown`; the halving date and 500-day window never trigger a trade by themselves.

The 20th/80th percentile boundaries are explicit to make the rule reproducible, not because they are known optimal values. Recalibrate only through an out-of-sample process.

## Action state machine

Evaluate rules from top to bottom:

1. `data_gap`: the snapshot validator returns invalid or blocked. Do not add exposure. If a final spot price supports a previously defined hard risk limit, a protective reduction may still be considered.
2. `reduce_or_avoid`: Price is `bearish`.
3. `reduce`: Financial stress is `high` and `worsening`, and either Leverage is `high` or Spot is `negative`.
4. `add_candidate`: Price is `bullish`, Spot is `positive`, Leverage is `low` or `medium`, Financial stress is `low` or `medium` with direction `easing` or `stable`, and Valuation is `low` or `neutral`.
5. `hold_or_wait`: all other complete snapshots.

If a bullish price state conflicts with negative Spot or high Leverage, keep the state at `hold_or_wait` or `reduce` according to the rules above; do not average the conflict into a bullish score. `add_candidate` does not authorize an amount, leverage, or order. The risk configuration and execution contract must approve those separately.

## Required decision record

Store the snapshot, factor states, gate result, matched rule, position context, and action state. The record must be sufficient to reproduce why the action state was emitted without relying on prose written after the fact.
