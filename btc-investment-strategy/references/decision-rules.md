# BTC Decision Rules

This is a deterministic signal state machine, not a promise of predictive performance. Thresholds are research defaults and must be validated against historical data before being used as an order system.

## Factor states

Use the normalized snapshot contract and compute these states:

- **Price:** keep the structural state separate from the accumulation zone. When weekly MA200 is at least weekly MA300, price above MA200 is structurally `bullish` and `price_zone=above_ma200`; price between MA200 and MA300 is structurally `neutral` and `price_zone=bottom_fishing_zone`; price below MA300 is structurally `bearish` and `price_zone=large_position_zone`. The new zones describe where to investigate or stage new capital; they do not erase trend risk for an existing position. If the averages are inverted, use `inverted` and report both relations.
- **Spot:** both 5-day and 20-day ETF net flows positive is `positive`; both negative is `negative`; otherwise `mixed`.
- **Leverage:** use one-year percentile fields for 7-day OI change and 7-day average Funding. Both at or above the 80th percentile is `high`; both at or below the 50th percentile is `low`; otherwise `medium`. A confirmed liquidation cascade is `high`. Missing percentiles are `unknown` and cannot support an add.
- **Financial stress:** use `low`, `medium`, `high`, or `unknown`, plus `easing`, `stable`, or `worsening`. Do not infer `low` from missing data.
- **Valuation:** use the MVRV percentile over the same provider's available history. At or below the 20th percentile is `low`, at or above the 80th percentile is `high`, otherwise `neutral`. If a comparable percentile is unavailable, use `unknown`.
- **Cycle:** `supportive`, `neutral`, or `unknown`, plus `pre_halving_500d_window`, `post_halving_500d_window`, `other`, or `unknown`. Use a ±30-day tolerance around 500 days. These are cycle-extreme windows where the likelihood of a bottom or top may increase; time alone never identifies which one or triggers a trade.

The 20th/80th percentile boundaries are explicit to make the rule reproducible, not because they are known optimal values. Recalibrate only through an out-of-sample process.

## Action state machine

Evaluate rules from top to bottom:

1. `data_gap`: the snapshot validator returns invalid or blocked. Do not add exposure. If a final spot price supports a previously defined hard risk limit, a protective reduction may still be considered.
2. `reduce_or_avoid`: for an existing position, Price is structurally `bearish` and no separate hard-risk rule authorizes continued exposure. This is an existing-position state, not a prohibition on investigating a new entry zone.
3. `reduce`: Financial stress is `high` and `worsening`, and either Leverage is `high` or Spot is `negative`.
4. `large_position_candidate`: for new capital, `price_zone=large_position_zone`, Valuation is `low` or `neutral`, Leverage is `low` or `medium`, Financial stress is `low` or `medium` with direction `easing` or `stable`, and Spot is not `negative`. This is the user's large-position zone expressed as a capped candidate, not an automatic order.
5. `bottom_fishing_candidate`: for new capital, `price_zone=bottom_fishing_zone`, Valuation is `low` or `neutral`, Leverage is `low` or `medium`, Financial stress is `low` or `medium` with direction `easing` or `stable`, and Spot is not `negative`.
6. `add_candidate`: Price is structurally `bullish`, Spot is `positive`, Leverage is `low` or `medium`, Financial stress is `low` or `medium` with direction `easing` or `stable`, and Valuation is `low` or `neutral`.
7. `hold_or_wait`: all other complete snapshots.

If a bullish price state conflicts with negative Spot or high Leverage, keep the state at `hold_or_wait` or `reduce` according to the rules above; do not average the conflict into a bullish score. If price is below MA300 while stress or leverage is high, report `large_position_zone` but do not emit `large_position_candidate`. Any candidate does not authorize an amount, leverage, or order. The risk configuration and execution contract must approve those separately.

## Required decision record

Store the snapshot, factor states, gate result, matched rule, position context, and action state. The record must be sufficient to reproduce why the action state was emitted without relying on prose written after the fact.
