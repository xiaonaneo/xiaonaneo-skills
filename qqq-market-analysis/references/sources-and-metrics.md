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
| 盈利预期与指数盈利 | [FactSet Earnings Insight](https://insight.factset.com/) 或 Nasdaq 的英文盈利资料 | 区分 reported earnings、forward EPS、分析师修正和实际盈利；写明覆盖范围与截止日 |

这些是路由建议，不是保证每个页面都提供当天数据。当前值、历史百分位和均线必须在实际查询后再写入结论。

## 计算口径

- 周线：把同一交易周最后一个交易日作为周收盘；QQQ 的周 MA200 和 TQQQ 的周 MA300 使用一致的周线构造。若数据供应商直接提供周线，核对其周边界和时区。
- 价格：对 split/dividend 调整方式保持一致并写明。用于趋势比较时不能把 adjusted close 与未调整 close 混用。
- 乖离：`(价格 - 周MA200) / 周MA200`。与历史乖离比较时使用同口径历史序列；没有足够历史样本时只报告当前百分比，不声称处于“历史极端”。
- 估值：每次同时写出 P/E 类型、数值、日期、来源和历史基准。`PE < 20`、`PE > 25`、`PE 接近/超过 30` 是用户策略阈值，但不把不同 P/E 类型的数值互相替代。
- 压力速度：至少比较最近一次与此前同频观察值；“正在改善/恶化”需要方向证据，“变化很快”需要时间间隔和幅度证据。

## 来源纪律

不要把新闻标题、技术分析者的判断或模型生成的估值摘要当成原始数据。新闻只用于解释事件背景，交易信号必须回到价格、估值和压力指标。发现来源之间不一致时，保留差异并解释口径，不选择看起来最支持结论的数字。
