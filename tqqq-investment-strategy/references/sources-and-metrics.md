# QQQ/TQQQ 数据源与口径

本文件用于执行实时行情分析时路由数据源。所有链接均为英文或国际来源；若某数据暂时不可得，要报告缺口，不用中文二手网站补齐。

## 优先来源

| 用途 | 优先来源 | 口径要求 |
|---|---|---|
| QQQ 产品信息与持仓/估值 | [Invesco QQQ](https://www.invesco.com/qqq-etf/en/home.html) | 说明是基金页面披露的 weighted harmonic P/E，还是指数 P/E；不要与 forward P/E 混写 |
| Nasdaq-100 指数资料 | [Nasdaq Index Research](https://www.nasdaq.com/solutions/global-indexes) | 用于指数方法、历史资料和成分股背景；记录发布日期 |
| QQQ/TQQQ 官方产品信息 | [ProShares UltraPro QQQ](https://www.proshares.com/our-etfs/leveraged-and-inverse/tqqq) | TQQQ 的目标是单日 3×，不能据此推导长期 3× |
| VIX | [Cboe VIX](https://www.cboe.com/tradable_products/vix/) | 标注收盘还是盘中；VIX 是隐含波动率，不是金融危机计量器 |
| 利率与宏观时间序列 | [Federal Reserve FRED](https://fred.stlouisfed.org/) | 记录 series ID、观察日和发布日期；10Y 等利率不能与不同日期的收盘价静默合并 |
| 金融压力 | [Chicago Fed NFCI](https://www.chicagofed.org/research/data/nfci/current-data)、[St. Louis Fed STLFSI](https://fred.stlouisfed.org/series/STLFSI4) | 记录指数定义、频率、水平、方向和变化速度；注意周频滞后 |
| 信用利差 | [FRED ICE BofA indices](https://fred.stlouisfed.org/categories/32345) | 优先使用同一数据体系的 HY OAS 与 IG OAS；注明 series ID 和观察日 |
| 企业盈利水平与盈利预期 | [FactSet Earnings Insight](https://insight.factset.com/) 或 Nasdaq 的英文盈利资料 | 优先使用 Nasdaq-100 聚合 EPS、同比增长、forward EPS 与分析师修正；S&P 500 只能作为背景，不能替代指数证据 |

这些是路由建议，不是保证每个页面都提供当天数据。当前值、历史百分位和均线必须在实际查询后再写入结论。

## 计算口径

- 周线：同一交易周取最后一个交易日收盘，QQQ 周 MA200 与 TQQQ 周 MA300 使用一致周边界；QQQ 不足 200 周可用 Nasdaq-100 代理并标注，TQQQ 不足 300 周则 MA300 无效。
- 价格：明确 split/dividend 调整方式，趋势比较不得混用 adjusted close 与未调整 close。
- 数据截止：统一使用 America/New_York；只纳入周五收盘前已发布的数据。日频指标取周五收盘或此前最后观测，周频取最新已发布观测，月频估值使用发布日期可见的 vintage。
- 历史分位：D 至少需要 260 个完整周观测，forward P/E 至少需要 60 个可比月度 vintage；样本不足只报告当前值，不触发历史分位动作。窗口（扩展或冻结）须在回测前确定。
- Forward P/E、EPS 和分析师修正必须保存发布日期/时间戳与当时可见版本；无法验证 vintage 时，历史评分和回测仅作非严格研究或 N/A。Trailing/harmonic P/E 不能替代 forward P/E。
- 金融压力：按信用、流动性、波动三组统一为“越高越危险”的百分位，组内取中位数，至少两个组可用才计算 `Stress_t`；按同频周序列计算 `ΔStress`、`Δ²Stress`，默认稳定带为 ±5 个百分点，恶化加速为 `ΔStress ≥ 5` 且 `Δ²Stress ≥ 5`。

## 来源纪律

来源只负责提供可追溯数据，不直接提供交易结论。新闻和技术分析仅解释背景；信号必须回到价格、估值和压力指标。来源冲突时保留差异并说明口径，不挑选最支持既有观点的数字。
