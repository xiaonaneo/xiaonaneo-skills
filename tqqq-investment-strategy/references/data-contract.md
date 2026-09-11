# TQQQ 数据契约

本文件把冻结策略中的数据口径变成可复算规则。它服务于当前分析；任何更新后的用户策略文件优先于本文件。

## 时间与完整性

- 市场数据以 America/New_York 对齐；用户输出同时标注 Asia/Shanghai 的分析时间。
- 完整周线是交易周结束后的最后一个交易日收盘。周五休市时使用该交易周最后一个交易日，并记录实际 observation_date 与 week_ending。
- 当前周没有结束时，不纳入周线均线、P90、TrendRecovery、TD₁、TD₂ 或 TD₃。盘中值只能放在背景或当前价格栏。
- 估值比较使用最新已发布的完整月末和三个月前对应月末。月末是周末或假日时，使用该月最后一个交易日；两个日期都必须写出。
- 每个数据点保存 observation_date、available_at、retrieved_at、source_id、source_version、unit 和 method。available_at 晚于分析截止时间的数据不得使用。

## 价格、WMA 与偏离度

QQQ 的价格与均线使用同一来源、同一复权口径的周收盘序列。默认使用 adjusted close；若供应商只提供未复权收盘，必须明确标注并保持整段序列一致。TQQQ 当前价格可以单独报告，但不参与底层 Price Gate。

对最近 n 个完整周收盘 C，按最新值权重最高的线性加权移动平均定义：

```
WeeklyWMA_n(t) = [1×C_(t-n+1) + 2×C_(t-n+2) + ... + n×C_t] / [n×(n+1)/2]
```

策略固定使用 WeeklyWMA50 与 WeeklyWMA200。斜率为本周 WMA 减上周 WMA；大于 0 才算上升，小于 0 才算下降，等于 0 不满足任一方向。

价格偏离度：

```
D_t = QQQ_Close_t / WeeklyWMA200_t - 1
PriceGate = QQQ_Close_t <= 1.05 × WeeklyWMA200_t
```

## P90

P90 使用扩展历史样本，不使用滚动窗口或事后挑选的窗口。每个完整周的阈值只使用此前已经完成的有效 D 值，排除当前 D，避免当前值参与自己的阈值：

```
P90_t = nearest_rank_percentile(D_1, ..., D_(t-1), 90)
```

nearest-rank 的位置为 ceil(0.90×N)，按升序排列后使用第该位置个值。至少需要 260 个此前有效完整周观测；不足时只报告 D，不触发 O_high、WATCH 或相关顶部动作。D 与 P90 必须使用相同的百分比/小数单位。

## Forward PE 与 E

Forward PE 必须是 Nasdaq-100 的同口径 Forward PE。一次分析只固定一个来源和一个版本。数据优先级：

1. LSEG I/B/E/S Global Aggregates 直接提供的 NDX NTM blended Forward EPS；
2. Bloomberg 或 FactSet 直接提供的同口径 NDX NTM blended Forward EPS；
3. 公开来源的 NDX 与 NDX Forward PE 同期配对，反推 Implied NDX NTM Forward EPS；
4. 无法满足以上条件时为 NA。

反推方法：

```
ImpliedEPS_t = NDX_Close_t / ForwardPE_t
E = 1(ImpliedEPS_t < ImpliedEPS_(t-3m))
```

当前期与比较期必须是同一来源、同一观察日规则、同一指数版本和同一 PE 定义。不能把当前 NDX 除以旧日期 PE，也不能混用季度财年 EPS、简单 FY1 EPS、S&P 500 EPS 或 Nasdaq Inc. 公司 EPS。

如果直接 EPS 或反推值可用，记录两期的 NDX、Forward PE、Implied EPS、日期和百分比变化。若当前月份尚未结束，不能用不完整月份替代最新完整月末。百分比变化大于或等于 0 时，按公式 E=0；只有严格下降才是 E=1。

## C/L/E 与缺失值

```
C = 1(HY_OAS_t > HY_OAS_(t-13w))
L = 1(NFCI_t > NFCI_(t-13w))
```

比较值取同一序列中目标日期当日或此前最近一个已发布观测，并记录日期差异。C、L、E 全部为 0/1 时：

- RiskCount 0 或 1：Stable；
- RiskCount 2：Deteriorating；
- RiskCount 3：Severe。

如果有缺失通道，不为缺失值赋 0 或 1。可报告 known_count 和 possible_range=[known_count, known_count+missing_count]；只有整个可能范围落入同一状态时才确定 Risk State，否则为 NA。Risk State 为 NA 时，R_high 不得计为已成立。
