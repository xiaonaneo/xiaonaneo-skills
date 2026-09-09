# BTC Backtest Contract

Use `scripts/backtest_strategy.py` for historical validation. It consumes normalized CSV rows and does not download or infer missing market data.

## Required CSV columns

```text
observed_at,available_at,as_of,execution_at,execution_price,
benchmark,derivatives_benchmark,data_status,
spot_price,weekly_ma200,weekly_ma300,etf_flow_5d,etf_flow_20d,
weekly_sma50,
oi_7d_change,oi_7d_percentile,funding_8h,funding_7d_percentile,
financial_stress_level,financial_stress_direction,mvrv,mvrv_percentile,
halving_cycle_state,liquidation_cascade
```

Each row represents a decision snapshot. `available_at <= as_of < execution_at` is mandatory. `execution_price` must be the next available Binance spot `BTCUSDT` price after the signal, not the signal candle close. The input must use completed weekly bars for the moving averages and must not include future information in any feature column. `benchmark` and `derivatives_benchmark` must declare the canonical Binance venues; `data_status` must preserve `final`, `preliminary`, `stale`, or `unknown` status rather than silently treating every row as final.

Use a separate risk configuration JSON accepted by `calculate_position_size.py`. The backtest defaults to spot-only, applies fee and slippage, enforces the maximum exposure and risk budget, and observes the configured cooldown after a reduction. A `data_gap` cannot create a new position; no protective reduction is simulated unless the input includes an explicit hard risk-limit event.

## Reported metrics

The script reports data coverage, action states, trade count, final equity, total return, annualized return when the period permits it, maximum drawdown, and a net Buy-and-hold benchmark using the same fee/slippage assumptions. It does not claim statistical significance, robustness, or production readiness.

Run at least an in-sample calibration and a chronological out-of-sample test. Do not tune percentile boundaries, cooldown, or risk parameters on the same period used for the final performance claim. Compare against a simple baseline and disclose omitted costs, taxes, custody, funding, and execution gaps.
