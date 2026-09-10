# QQQ/TQQQ 数据源与口径

本文件用于执行实时行情分析时路由数据源。所有链接均为英文或国际来源；若某数据暂时不可得，要报告缺口，不用中文二手网站补齐。

## 优先来源

| 用途 | 优先来源 | 口径要求 |
|---|---|---|
| 价格与均线 | [Yahoo Finance](https://finance.yahoo.com/) adjusted close | 只负责 QQQ/TQQQ 价格、周线和均线；不负责估值、盈利或金融压力 |
| Forward P/E | [FactSet Earnings Insight](https://insight.factset.com/)（默认唯一供应商） | 整次分析和回测使用同一供应商、同一口径、同一版本；若当前值或历史 vintage 无法验证，记为 N/A，不切换或拼接替代 |
| Nasdaq-100 指数资料与企业盈利 | [Nasdaq Index Research](https://www.nasdaq.com/solutions/global-indexes) 及 Nasdaq 官方盈利资料 | 盈利只使用 Nasdaq 官方资料；记录指数方法、EPS、预期修正、发布日期和覆盖范围 |
| 金融压力与信用利差 | [Federal Reserve FRED](https://fred.stlouisfed.org/)、[Chicago Fed NFCI](https://www.chicagofed.org/research/data/nfci/current-data)、[St. Louis Fed STLFSI](https://fred.stlouisfed.org/series/STLFSI4) | FRED 负责压力、流动性和利差；记录 series ID、频率、观察日和发布日期 |
| 美国 10 年期国债收益率 | [FRED DGS10](https://fred.stlouisfed.org/series/DGS10) | 只使用美国 10 年期国债名义收益率；标注观察日、收盘/日内口径和发布日期 |
| 美元指数 DXY | [ICE U.S. Dollar Index methodology](https://www.theice.com/publicdocs/data/ICE_FX_Indexes_Methodology.pdf) | 只使用 ICE DXY/USDX（NYICDX）；禁止广义贸易加权美元指数、美元 ETF 或其他美元篮子替代 |
| 通胀与油价 | [FRED CPIAUCSL](https://fred.stlouisfed.org/series/CPIAUCSL)、[FRED PCEPI](https://fred.stlouisfed.org/series/PCEPI)、[FRED DCOILWTICO](https://fred.stlouisfed.org/series/DCOILWTICO) | 通胀使用 CPI、PCE 和 WTI 油价；分别记录观察日、发布日期和水平/加速度 |
| 波动压力 | [Cboe VIX](https://www.cboe.com/tradable_products/vix/) | Cboe 负责 VIX 等波动数据；标注收盘/盘中，VIX 不能单独代表金融危机 |

这些是路由建议，不是保证每个页面都提供当天数据。当前值、历史百分位和均线必须在实际查询后再写入结论。

## 计算口径

- 周线：同一交易周取最后一个交易日收盘，QQQ 周 MA200 与 TQQQ 周 MA300 使用一致周边界；QQQ 不足 200 周可用 Nasdaq-100 代理并标注，TQQQ 不足 300 周则 MA300 无效。
- 价格：Yahoo adjusted close 只用于价格、周线和均线；明确 split/dividend 调整方式，趋势比较不得混用 adjusted close 与未调整 close。
- 数据截止：统一使用 America/New_York；只纳入周五收盘前已发布的数据。日频指标取周五收盘或此前最后观测，周频取最新已发布观测，月频估值使用发布日期可见的 vintage。
- 历史分位：D 至少需要 260 个完整周观测，forward P/E 至少需要 60 个可比月度 vintage；样本不足只报告当前值，不触发历史分位动作。窗口（扩展或冻结）须在回测前确定。
- Forward P/E：默认锁定 FactSet Earnings Insight，当前值、历史序列和 vintage 不得跨供应商拼接；保存发布日期/时间戳、口径和当时可见版本。FactSet 无法验证时，估值判定为 N/A，不切换供应商；Trailing/harmonic P/E 不能替代 forward P/E。
- 企业盈利：只使用 Nasdaq 官方资料；EPS、同比增速、forward EPS 和分析师修正分别记录发布日期、覆盖范围和口径，不用 Yahoo、FRED/Cboe 或 S&P 500 数据替代。
- 金融压力：按信用、流动性、波动、宏观四组统一为“越高越危险”的百分位，组内取中位数；至少两个组可用且至少包含信用或流动性组，才计算 `Stress_t = median(G_credit, G_liquidity, G_volatility, G_macro)`。按同频周序列计算 `ΔStress`、`Δ²Stress`，默认稳定带为 ±5 个百分点，恶化加速为 `ΔStress ≥ 5` 且 `Δ²Stress ≥ 5`。宏观组严格包含美国 10 年期国债名义收益率、ICE DXY、CPI、PCE 和 WTI 油价的水平/加速度；不得使用实际利率、广义贸易加权美元指数或油价 ETF 替代。

## 来源纪律

来源只负责提供可追溯数据，不直接提供交易结论。新闻和技术分析仅解释背景；信号必须回到价格、估值和压力指标。来源冲突时保留差异并说明口径，不挑选最支持既有观点的数字。
