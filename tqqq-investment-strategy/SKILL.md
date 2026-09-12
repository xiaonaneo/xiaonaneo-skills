---
name: tqqq-investment-strategy
description: "只分析当前 TQQQ/QQQ 的市场结构、均线、估值、盈利预期和金融风险，不输出交易或仓位建议。"
---

# TQQQ投资策略

## 范围

本 Skill 只输出 QQQ/TQQQ 市场分析：价格、周线均线、P90、Forward PE、NDX NTM blended Forward EPS、C/L/E 风险、水平诊断和市场状态。不得输出买入、卖出、持有、加仓、减仓、建仓、清仓、仓位、目标资金或成交建议。

用户提供的新策略文件、数据口径和明确修改优先于本 Skill。交易规则只作为背景，不能转换为交易动作。

## 分析纪律

- 当前数据必须重新核验，并标明 Asia/Shanghai 分析时间、美国最新收盘日、收盘/盘中口径和最近完整周线日期。
- 周线指标只使用最近一个完整交易周的收盘；当前周未结束时，盘中值只能作为背景。
- QQQ 是底层结构的主要对象；TQQQ 只报告价格表现和产品波动。
- 价格、SMA、D 和 P90 使用同一来源、同一复权口径和同一周边界。
- 每个数据点记录 observation_date、available_at、retrieved_at、source_id、source_version、unit 和 method。

详细计算口径见 [references/data-contract.md](references/data-contract.md)，市场状态字段见 [references/state-schema.md](references/state-schema.md)。

## 核心指标

### 均线与位置

WeeklySMA50 和 WeeklySMA200 是完整周收盘的简单算术平均：

```text
WeeklySMA_n(t) = [C_(t-n+1) + ... + C_t] / n
D_t = QQQ_Close_t / WeeklySMA200_t - 1
PriceCondition = QQQ_Close_t <= 1.05 × WeeklySMA200_t
```

均线斜率是本周 SMA 减上周 SMA；大于 0 为上升，小于 0 为下降，等于 0 为平坦。

P90 是排除当前完整周的扩展历史 D 样本 nearest-rank 90 分位，至少需要 260 个此前有效周。样本不足时 O_high=NA，不影响其他风险标记。

```text
O_high = D >= P90
V_high = Forward PE >= 30
R_high = Risk State >= Deteriorating
```

O/V/R 使用 TRUE、FALSE、NA 三值逻辑。至少两项确认 TRUE 时，TopRiskCandidate=TRUE；最多一项可能为 TRUE 时为 FALSE；其余为 NA。

### C/L/E 风险

```text
C = 1(HY_OAS_t > HY_OAS_t-13w)
L = 1(NFCI_t > NFCI_t-13w)
E = 1(Implied_NDX_NTM_Forward_EPS_t < Implied_NDX_NTM_Forward_EPS_t-3m)
```

只有 C/L/E 方向值进入 RiskCount：0–1 为 Stable，2 为 Deteriorating，3 为 Severe。缺失值不填补；报告 known_count 和 possible_range，只有可能范围落在同一状态时才确定 Risk State。

E 优先使用直接 NDX NTM blended Forward EPS；不可得时，使用同一观察日期的 NDX ÷ Forward PE 反推。记录 e_method、e_confidence、e_date_match、source_id 和 source_version。

### 水平诊断

HY OAS、NFCI 和 ANFCI 记录当前值、单位、历史分位和 sample_n；VIX、DXY、Funding Stress 和美国 10Y 只作背景。水平诊断不计入 RiskCount，不增加投票，不单独改变市场状态。

### 趋势状态

仅把以下条件作为市场趋势标记：

- TrendRecovery：QQQ Close>WeeklySMA50 且 WeeklySMA50_t>WeeklySMA50_t-1。
- TD1：QQQ Close<WeeklySMA50 且 WeeklySMA50_t<WeeklySMA50_t-1。
- TD2：TD1 且 QQQ Close<WeeklySMA200。
- TD3：QQQ Close<WeeklySMA200 且 WeeklySMA200_t<WeeklySMA200_t-1。

趋势标记描述中期和长期趋势，不转换成交易指令。

## 市场状态

market_state 按以下顺序描述当前市场，所有原始 flags 仍须同时输出：

```text
DATA_INSUFFICIENT  核心数据不足
STRUCTURE_FAILURE  结构性检查失败
LONG_TREND_DAMAGE  TD3 成立
MID_TREND_DAMAGE   TD1 或 TD2 成立
TOP_RISK_CANDIDATE O/V/R 至少两项成立
STRUCTURE_STABLE   以上条件均未成立且结构正常
UNKNOWN            没有历史状态或无法初始化
```

状态优先级只用于生成一个 market_state，不覆盖原始风险和趋势 flags。

## 状态记录

状态记录只保存市场状态、风险/趋势 flags、水平诊断、数据质量和 provenance。同一完整周重复分析必须幂等，不重复生成事件。只有用户明确要求持续保存且提供路径时才写入状态。

状态字段见 [references/state-schema.md](references/state-schema.md)。

## 固定输出

面向用户的所有可见标题、叙述、数据标签和结论都使用简体中文。股票代码、公式和必要的机器字段可以保留原样。严格使用以下五个标题，顺序不可变；只显示精简数据和结论，不列公式、计算过程、数据抓取流程、来源优先级、状态更新流程或字段解释。

**核心结论**
日期：YYYY-MM-DD HH:mm（Asia/Shanghai；美国收盘/盘中）
结论：用中文一句话概括市场状态。

**均线位置**
数据：QQQ、TQQQ、最近完整周线、50周简单均线、200周简单均线、偏离度、90分位和趋势标记。
结论：用中文一句话说明均线位置。

**估值水平**
数据：Nasdaq-100 预期市盈率、估值区间、未来十二个月混合预期每股收益状态和数据可信度。
结论：用中文一句话说明估值状态。

**金融风险**
数据：信用风险（C）、流动性风险（L）、盈利风险（E）、风险计数或可能范围、风险状态、HY OAS/NFCI 水平诊断。
结论：用中文一句话说明金融风险状态。

**市场状态**
数据：结构检查、顶部风险候选、中期趋势恢复、一级/二级/三级趋势破坏和市场状态。
结论：用中文一句话说明已确认状态和关键数据缺口。
