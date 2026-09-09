# BTC Data Contract

Use this contract unless the user explicitly supplies a different benchmark. A source change is a methodology change and must be disclosed; do not silently fall back to another venue.

## Canonical sources and fields

| Domain | Canonical source and series | Required basis |
|---|---|---|
| Spot price | Binance spot `BTCUSDT` | USDT quote; state live, intraday, or completed-session basis. |
| Weekly price and MAs | Binance spot `BTCUSDT` 1-week klines | Simple SMA50/MA200/MA300 of completed UTC weekly closes; exclude the partial week. |
| Perpetual OI | Binance USDⓈ-M `BTCUSDT` perpetual | Report USDT notional and, when available, BTC-denominated OI; include venue and observation time. |
| Funding | Binance USDⓈ-M `BTCUSDT` perpetual | Report raw 8-hour rate and annualized equivalent separately; do not mix them. |
| ETF flow | Farside Investors U.S. spot BTC ETF table, cross-checked with issuer data when available | Latest completed U.S. trading session; report preliminary/final status and 5-day/20-day sums. |
| Dollar index | ICE U.S. Dollar Index (DXY) | Use DXY itself; do not substitute a broad trade-weighted index, another dollar index, or a dollar ETF. |
| Rates and financial stress | FRED/Federal Reserve, New York Fed, Chicago Fed, and Cboe series specified in the framework | Preserve series ID, unit, observation date, release/availability date, and vintage when relevant. |
| MVRV | Coin Metrics Community API `CapMVRVCur` | Dimensionless ratio; retain provider, methodology URL, UTC observation time, and retrieval time. |
| Halving | Bitcoin block height/date from a cited international block-data source | Record actual block height and UTC timestamp for completed halvings; label the next date as projected; derive the 500-day window state with its tolerance. |

## Required data record

Each normalized snapshot must declare `benchmark` and `derivatives_benchmark`. The defaults are exactly `Binance spot BTCUSDT` and `Binance USDⓈ-M BTCUSDT perpetual`. A different venue requires `benchmark_override: true`, a non-empty `override_reason`, and a methodology note; otherwise the action gate remains closed.

Every value used in a current report should be representable as:

```text
metric
value
unit
source
venue_or_series
observed_at
available_at
status            # final, preliminary, estimated, stale, or unknown
methodology
```

`observed_at` is when the market or series refers to the value. `available_at` is when the value could first have been known to the analyst. A backtest must use `available_at`, not merely `observed_at`, to avoid look-ahead bias.

The `halving_timeline` value should include `cycle_state` and, when calculable, `cycle_window`: `pre_halving_500d_window`, `post_halving_500d_window`, `other`, or `unknown`. Use the actual or projected UTC date and preserve whether it is `Actual` or `Estimate`.

## Freshness and fallback rules

- Price and perpetual data: use the stated retrieval time and report outages or gaps; do not replace Binance with another venue silently.
- Weekly MAs: calculate only after the Binance UTC weekly candle is complete. A live price may be compared with completed-week MAs, but the distinction must be stated.
- ETF flows: a missing issuer or venue row is unknown, not zero. Preliminary rows remain preliminary until the source marks them final.
- FRED and other macro series: use the latest available release and retain its release date; an old observation is not necessarily stale if it is the latest published value.
- MVRV: use the helper's 72-hour freshness rule and reject future observations.
- If a critical field is missing, stale, benchmark-mismatched, or lacks an availability time, block new exposure. A hard price risk limit may still permit a protective reduction.

The critical snapshot fields are `spot_price`, `weekly_sma50`, `weekly_ma200`, `weekly_ma300`, `etf_flow_5d`, `etf_flow_20d`, `oi_7d_change`, `funding_8h`, `financial_stress`, `mvrv`, and `halving_timeline`. Use `scripts/validate_snapshot.py` to apply this gate consistently. Derived fields such as `oi_7d_change.percentile`, `funding_7d.percentile`, and `mvrv.percentile` are required by the decision state machine for a non-unknown factor state.
