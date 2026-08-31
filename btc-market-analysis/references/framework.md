# BTC Six-Layer Framework

Use this reference for every current BTC market analysis.

## 1. Establish the evidence window

Define three horizons before interpreting data:

| Horizon | Typical window | Main question |
|---|---|---|
| Short term | Hours to days | Is momentum or positioning becoming crowded? |
| Medium term | Weeks to months | Is a higher-high/higher-low or lower-high/lower-low structure forming? |
| Cycle | Months to years | Is valuation and time offering an asymmetric opportunity? |

Build a small data ledger with `metric`, `value`, `as-of`, `unit/basis`, and `source`. A precise number without a timestamp and methodology is not decision-grade evidence.

Source order:

1. Primary and official: Intercontinental Exchange (ICE), Federal Reserve/FRED, U.S. Treasury, SEC, CFTC, CME, ETF issuers, and exchange market data or APIs.
2. Established international research/data: Coin Metrics, Glassnode, CryptoQuant, Kaiko, K33, Farside Investors, and comparable non-Chinese providers.
3. International reporting such as Reuters, Bloomberg, or the Financial Times for context and attributed expert claims.

Do not use Chinese websites or Chinese-language sources. A secondary article may help discover a fact, but verify consequential numbers against primary data where practical.

## 2. Analyze the six layers

### Macro: liquidity regime

Question: Is BTC running with a liquidity tailwind or headwind?

Use the ICE U.S. Dollar Index (DXY) as the dollar-strength measure. Do not substitute a broad trade-weighted dollar index, another dollar index, or a dollar ETF. Check DXY, U.S. 2-year and 10-year yields, current Fed stance and market-implied path, and a clearly defined liquidity proxy. Compare direction over a stated window rather than one daily move.

Interpretation heuristic:

- DXY declining, lower real or nominal yields, and improving liquidity usually form a tailwind.
- DXY rising, higher yields, and contracting liquidity usually form a headwind.

Do not use macro variables to predict an exact BTC price. Identify competing explanations: risk appetite, fiscal expectations, regulation, ETF demand, or crypto-specific deleveraging may dominate temporarily.

### Spot: real-money demand

Question: Is cash demand absorbing supply?

Check U.S. spot BTC ETF net flows, preferably latest completed day plus 5-day and 20-day sums; spot volume on a defined venue set; and, when reliable, spot premium or basis indicators.

Distinguish:

- `Price up + sustained ETF/spot demand + OI stable or moderate + Funding near neutral` suggests a spot-led advance.
- `Price up + weak spot demand + OI accelerating + Funding rising` suggests a leverage-led advance.

ETF flows are a proxy, not a complete map of spot demand. Note reporting lags, preliminary values, creation/redemption mechanics, and the fact that flow does not prove same-day open-market BTC purchases.

### Price: market structure

Question: What has price actually confirmed?

Use a stated benchmark and inspect:

- Current price, weekly close, and recent swing highs/lows.
- Higher high/higher low versus lower high/lower low.
- Key support, resistance, reclaim, breakdown, and invalidation zones.
- Weekly 200- and 300-period moving averages when the benchmark has adequate history.

Do not confuse daily MA200 with 200-week MA. A wick above resistance is weaker evidence than acceptance above it; define acceptance using closes, retests, or time spent above the level. Price is the final confirmation layer, but rising price alone does not identify the quality of the move.

### Leverage: internal fragility

Question: How much forced buying or selling could amplify the next move?

Analyze OI, Funding, futures basis when available, and liquidations together:

| Price | OI | Default reading; verify with Funding and spot flow |
|---|---|---|
| Up | Up | New leverage is entering; trend may strengthen while fragility rises. |
| Up | Down | Short covering, short squeeze, or deleveraging advance. |
| Down | Up | New shorts or leveraged dip-buyers are entering; direction is ambiguous. |
| Down | Down | Long closing or liquidation-driven deleveraging. |

OI is not directional because every contract has two sides. Dollar-denominated OI can rise mechanically with BTC price; use BTC-denominated OI or discuss this distortion when possible. Funding must state venue coverage, interval, and whether it is raw per-period or annualized. Liquidation feeds are incomplete estimates and must not be treated as market-wide ground truth.

High-risk combination:

`Price up + OI accelerating + Funding elevated + ETF/spot demand fading`.

Healthier combination:

`Price up or consolidating + ETF/spot demand sustained + OI stable/down + Funding near neutral`.

### Valuation: price relative to holder cost

Question: Is the market paying a historically demanding or discounted price relative to aggregate cost?

Prioritize MVRV, realized price, short-term-holder and long-term-holder cost basis, and price relative to the 200-week moving average. Keep provider methodology consistent across comparisons.

Use valuation to classify zones, not to time exact reversals. On-chain metrics may be revised, provider-specific, delayed, or distorted by lost coins, exchange custody, and ETF-era market structure. RSI or sentiment can supplement this layer but cannot substitute for cost-basis evidence.

### Cycle: time and regime

Question: Where might BTC sit in its lifecycle, and how weak is that inference?

Calculate days before or after the most recent halving and, if relevant, days until the projected next halving. Label the next date as an estimate because block production determines it.

The prior framework observed mature-cycle lows clustering roughly 500-540 days before a subsequent halving, with sample observations around 542, 513, and 515 days. Treat this as a hypothesis with a small sample, selection risk, and regime-change risk—not a trading rule. Test it jointly:

`Time x Valuation x Price structure x Capitulation`.

Do not infer that a projected calendar date must contain the absolute price low. A later cycle low may be a higher low, while the absolute price low occurred earlier.

## 3. Synthesize, do not count votes

The six layers are not equal, independent votes. Avoid a mechanical score unless the user supplied weights and thresholds.

Use this causal sequence as a diagnostic map:

`Macro environment -> Spot demand -> Price structure -> Leverage amplification -> Valuation -> Cycle context`.

Price and flows can dominate in the short term; valuation and cycle matter more for long-horizon risk-reward. Contradictions are information. Examples:

- Strong price plus deteriorating spot demand and rising leverage means confirmation is increasing while safety margin is shrinking.
- Weak price plus negative Funding and falling OI may indicate capitulation, but it is not a bottom until spot demand or price structure confirms.
- Strong ETF inflows with no price response may reveal hidden supply rather than failed data.

For bottom-like conditions, look for convergence among improving macro, price near long-term cost/MA zones, depressed valuation, returning spot demand, falling OI, neutral or negative Funding, liquidation/capitulation, and a plausible cycle window.

For top-risk conditions, look for price far above long-term anchors, elevated valuation, fading marginal spot demand, rapidly rising OI, elevated Funding, broad FOMO, and failed price acceptance.

## 4. Challenge the thesis

Before concluding, expose at least two hidden assumptions. Common examples:

- ETF inflows are incremental and persistent rather than rotations, hedged basis trades, or delayed reporting.
- Aggregate OI is comparable across dates despite venue mix and price-denomination effects.
- Historical halving behavior survives maturation, derivatives growth, ETFs, regulation, and monetary-regime changes.
- A support zone is causal rather than a hindsight label.
- A macro move caused BTC rather than merely occurring at the same time.

State the strongest disconfirming evidence and what observation would force a view change.

## 5. Output contract

Lead with a one-paragraph state assessment and its as-of time. Then use this order:

1. Data basis and freshness.
2. Macro.
3. Spot/ETF.
4. Price structure and key levels.
5. Leverage.
6. Valuation.
7. Cycle.
8. Hidden assumptions and contrary evidence.
9. Base, upside, and downside paths, each with observable triggers.
10. Final dashboard: Trend, Fragility, Risk-reward, Driver, Action bias, and Invalidation.

Use concise tables when they improve comparison. Cite all current facts and numerical claims. Distinguish:

- **Observed:** directly supported data.
- **Inferred:** interpretation derived from multiple observations.
- **Unknown:** data unavailable, stale, or methodologically inconsistent.

Never imply certainty from a single indicator or a small historical sample. When the user asks whether to buy or sell, connect the answer to horizon, position size, cash reserve, and invalidation; if those are absent, give conditional bands rather than personalized certainty.
