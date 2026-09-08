# BTC Risk and Execution Contract

The strategy can emit a signal without authorizing a trade. Position sizing requires an explicit risk configuration; if it is absent or invalid, the result is research-only and no amount may be suggested.

## Required risk configuration

Provide these fields in a separate JSON object:

```json
{
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
  "cooldown_weeks": 1
}
```

The example is a schema example, not a default allocation. All percentages are decimals between 0 and 1. `invalidation_distance_pct` must come from a defined price invalidation, not from an arbitrary desired loss.

## Sizing formula

For an `add_candidate`, `bottom_fishing_candidate`, or `large_position_candidate` signal only:

```text
remaining_exposure = max(0, portfolio_value * max_btc_exposure_pct - current_btc_exposure)
cash_limited = max(0, available_cash_usdt - portfolio_value * cash_reserve_floor_pct)
single_trade_cap = portfolio_value * single_trade_cap_pct
large_trade_cap = portfolio_value * large_trade_cap_pct
round_trip_cost = 2 * (fee_bps + slippage_bps) / 10000
effective_loss = invalidation_distance_pct + round_trip_cost
risk_limited = portfolio_value * risk_budget_pct / effective_loss
trade_cap = large_trade_cap for `large_position_candidate`, otherwise single_trade_cap
trade_notional = min(remaining_exposure, cash_limited, trade_cap, risk_limited)
BTC quantity = trade_notional / execution price
```

The available-cash field is required because total portfolio value may include non-BTC assets, liabilities, or locked funds; total portfolio value alone is not a cash balance. `large_trade_cap_pct` must be at least `single_trade_cap_pct`; it increases only the single-trade ceiling, not the maximum BTC exposure or risk budget.

If `trade_notional` is zero, do not create an order. The calculation is a cap, not a guarantee that an order should be placed. Use `scripts/calculate_position_size.py` to reproduce it.

## Execution and de-risking

- Default execution is Binance spot `BTCUSDT`, without leverage. A different venue or a perpetual contract requires an explicit user override and a new risk calculation.
- A backtest starts flat with `current_btc_exposure_usdt = 0` and `available_cash_usdt = portfolio_value_usdt`; use a separate configuration if the live portfolio contains other assets.
- Evaluate a weekly-MA signal only after the UTC weekly candle is complete. In a backtest, fill at the next available bar open and apply the configured fee and slippage; never fill on the signal candle close unless the data proves that close was tradable.
- A `data_gap` blocks new exposure. A valid final spot price may still trigger a protective reduction against a previously defined hard risk limit.
- After a `reduce` or `reduce_or_avoid` state, require at least `cooldown_weeks` completed weekly bars and a fresh data gate before a new add candidate can be acted upon.
- No rule may increase exposure solely because the halving date, the 500-day window, MVRV, or one moving-average crossing occurred.
- Taxes, custody, counterparty, stablecoin, and transfer risks are outside this sizing formula and must be disclosed if they affect the decision.
