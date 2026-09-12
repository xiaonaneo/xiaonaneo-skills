# TQQQ 市场数据契约

## 时间

- 市场数据按 America/New_York 对齐；输出同时标明 Asia/Shanghai 分析时间。
- 完整周线取交易周最后一个交易日收盘；当前周未结束时不计算周线状态。
- 估值使用最新可用完整月末和三个月前对应月末；周末/假日使用最后一个交易日。
- 每条数据记录 observation_date、available_at、retrieved_at、source_id、source_version、unit 和 method。

## 价格与均线

QQQ 使用同一来源、同一复权口径的周收盘序列，计算简单算术平均：

```
WeeklySMA_n(t) = [C_(t-n+1) + ... + C_t] / n
D_t = QQQ_Close_t / WeeklySMA200_t - 1
PriceCondition = QQQ_Close_t <= 1.05 × WeeklySMA200_t
```

P90 使用排除当前完整周的扩展历史 D 样本 nearest-rank 90 分位，位置为 ceil(0.90×N)，至少需要 260 个此前有效周；不足时 O_high=NA。

## 估值与 E

Forward PE 必须是 Nasdaq-100 同口径数据，一次分析固定一个来源和版本。直接 NDX NTM blended Forward EPS 优先；不可得时，使用同一来源、同一观察日期规则的 NDX ÷ Forward PE 反推。

```
ImpliedEPS_t = NDX_Close_t / ForwardPE_t
E = 1(ImpliedEPS_t < ImpliedEPS_(t-3m))
```

当前期与比较期必须匹配指数版本、Forward PE 定义和观察日期。记录 e_method、e_confidence、e_date_match、source_id、source_version 和 available_at。

## C/L/E

```
C = 1(HY_OAS_t > HY_OAS_(t-13w))
L = 1(NFCI_t > NFCI_(t-13w))
E = 1(ImpliedEPS_t < ImpliedEPS_(t-3m))
```

只有 C/L/E 的方向值进入 RiskCount：0–1=Stable，2=Deteriorating，3=Severe。缺失通道不填补，报告 known_count 和 possible_range；可能范围跨越状态时 Risk State=NA。

R_high：known_count≥2 为 TRUE，known_count+missing_count≤1 为 FALSE，其余为 NA。O_high 或 V_high 为 NA 时不当作 FALSE。至少两项 TRUE 才确认 TopRiskCandidate；最多一项可能 TRUE 才确认不成立。

## 水平诊断

HY OAS、NFCI、ANFCI 记录值、单位、历史分位和 sample_n；VIX、DXY、Funding Stress 和美国 10Y 只作背景。水平诊断不计入 RiskCount，不单独改变市场状态。
