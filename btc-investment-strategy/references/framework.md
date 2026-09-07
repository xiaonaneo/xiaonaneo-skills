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

#### Financial stress: credit, volatility, and dollar funding

Include financial stress as a fixed subsection within Macro in every report, not as a peer section. Keep it distinct from crypto derivatives fragility: rising yields alone do not establish systemic financial stress.

- Broad conditions: NFCI and, when available, STLFSI4. Compare levels and changes using the same latest data vintage; historical revisions are not new stress.
- Credit: ICE BofA US High Yield OAS and US Corporate OAS through FRED. Report units consistently (basis points or percent), latest available observations, and change over roughly one week and one month.
- Volatility: VIX; add Treasury volatility only when a reliable, dated series is available. Distinguish equity fear from credit or funding impairment.
- Dollar funding: SOFR minus IORB on matching observation dates, with repo or other funding evidence when available. A brief calendar-related spike is not sufficient to call a funding crisis.
- Prefer Chicago Fed, St. Louis Fed/FRED, New York Fed, Federal Reserve, and Cboe sources. Label missing or delayed data explicitly.

Conclude with Financial stress: low / medium / high (or unknown when evidence is insufficient), plus easing / stable / worsening and the observation window. This is an evidence-based assessment, not a calibrated probability or a vote count. Do not double-count correlated indicators or classify missing readings as low stress.

Explain the action implication: worsening credit and funding conditions weaken the case for adding even when BTC valuation improves; easing stress supports consideration of additions only alongside price, spot demand, and position-risk constraints. State which credit, funding, or volatility evidence would invalidate the assessment.

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
- Weekly 200- and 300-period simple moving averages when the benchmark has adequate history. Report the current BTC price and both moving-average values with their as-of times.

Do not confuse daily MA200 with 200-week MA. A wick above resistance is weaker evidence than acceptance above it; define acceptance using closes, retests, or time spent above the level. Price is the final confirmation layer, but rising price alone does not identify the quality of the move.

Calculate weekly MA200 and weekly MA300 from weekly closes on the same benchmark. Use completed weekly bars by default; if the current partial weekly bar is included, disclose that choice. Classify the current price as follows when `weekly MA200 >= weekly MA300`:

- `Price > weekly MA200`: **above weekly MA200**.
- `weekly MA300 <= Price <= weekly MA200`: **between weekly MA200 and weekly MA300**.
- `Price < weekly MA300`: **below weekly MA300**.

This classification assumes weekly MA200 is above weekly MA300. If `weekly MA200 < weekly MA300`, state that the averages are inverted and report price as above or below each average; do not force it into one of the three labels. Keep live/intraday price distinct from moving averages based on the latest completed weekly close.

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

#### MVRV retrieval contract

Use the deterministic helper before attempting webpage extraction:

```bash
python3 scripts/fetch_mvrv.py
```

The helper uses the no-key Coin Metrics Community API daily metric `CapMVRVCur`, defined as current market capitalization divided by realized capitalization. Treat its latest UTC date as the observation time and retain the provider label because Coin Metrics and Glassnode methodologies can differ.

- Request `CapMVRVCur` by itself. Combining it with metrics that are not available to Community credentials can make the whole request return HTTP 403.
- Accept only a finite, positive, dimensionless ratio with an ISO timestamp. Never interpret a currency-formatted field, chart price, or unrelated page value as MVRV.
- The helper marks data older than 72 hours as stale and exits nonzero. Report stale or failed retrieval as a data gap unless a fallback meets the same value, unit, and timestamp requirements.
- Glassnode is a cross-check or fallback only when its page exposes an explicitly labeled MVRV ratio and observation time. `fuckbtc.com` may supplement a gap only when it exposes a numeric value, visible update time, and usable methodology or upstream source; placeholders such as `--` are not data.
- Do not splice one provider's current value into another provider's historical thresholds without labeling the methodology change.

### Cycle: time and regime

Question: Where might BTC sit in its lifecycle, and how weak is that inference?

Report a halving timeline in `YYYY-MM-DD` using UTC dates. For a current-market analysis, include at minimum:

| Halving reference | Halving date | 500 days before | 500 days after | Status |
|---|---|---|---|---|
| Most recent halving | Actual date | `H - 500 calendar days` | `H + 500 calendar days` | Actual |
| Next halving | Projected date | `H - 500 calendar days` | `H + 500 calendar days` | Estimate |

Calculate and display the dates rather than leaving formulas in the final answer. Also report days before or after the relevant halving as of the analysis timestamp. Label the next halving and both dates derived from it as estimates because block production determines the event date. For historical analysis, use the halving or halvings that bracket the requested period.

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

Every execution must use exactly these six top-level sections and this order:

1. `## 核心结论`
2. `## 宏观数据`
3. `## 周期位置`
4. `## 价格结构`
5. `## 杠杆水平`
6. `## 链上估值`

Use `核心结论` for the one-paragraph state assessment and as-of time. Put the compact dashboard there: Trend, Fragility, Financial stress (level and direction), Risk-reward, Driver, Weekly MA band, Halving timeline, Action bias, and Invalidation. Put hidden assumptions, contrary evidence, and base/upside/downside paths with observable triggers there as well. Do not create additional top-level sections for these items.

Map the evidence into the remaining sections:

- `宏观数据`: DXY, yields, Fed stance, liquidity, financial stress, ETF/spot flow, and data freshness relevant to the macro and demand read.
- `周期位置`: actual and projected halving dates, each relevant `-500 days` and `+500 days` date, days before/after halving, and cycle interpretation.
- `价格结构`: current price, weekly MA200, weekly MA300, the required weekly MA band, swing structure, and key levels.
- `杠杆水平`: OI, Funding, futures basis, liquidations, and whether the move is spot-led or leverage-led.
- `链上估值`: MVRV, realized price, holder cost basis, and valuation interpretation.

Use concise tables when they improve comparison. Cite all current facts and numerical claims. Distinguish:

- **Observed:** directly supported data.
- **Inferred:** interpretation derived from multiple observations.
- **Unknown:** data unavailable, stale, or methodologically inconsistent.

Never imply certainty from a single indicator or a small historical sample. When the user asks whether to buy or sell, connect the answer to horizon, position size, cash reserve, and invalidation; if those are absent, give conditional bands rather than personalized certainty.
