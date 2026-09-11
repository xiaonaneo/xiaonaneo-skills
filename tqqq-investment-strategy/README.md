# TQQQ投资策略

这是一个用于分析 QQQ/TQQQ 行情的 Codex Skill，依据《TQQQ 完整交易策略 v2026.09》冻结版执行。它把底层趋势、估值、盈利预期和金融风险转换为可复核的状态机判断，输出买入、持有、观察或分级兑现结论。

## 适用场景

当用户要求分析当前 TQQQ 行情、判断是否买入或加仓、评估已有仓位，或解释策略信号时使用：

```text
使用 $tqqq-investment-strategy 分析当前 TQQQ 行情。
```

Skill 只提供决策支持，不自动下单、不修改投资账户。当前用户提供的新策略文件、阈值或明确修改优先于本 Skill。

## 核心规则

### 买入

底层资产使用 QQQ 判断价格位置：

```text
PriceGate = QQQ <= 1.05 × WeeklySMA200
BuyGate = StructuralCheck=PASS AND PriceGate AND Forward PE<=25
```

只有 BuyGate 打开时，才允许 `WAIT → ACCUMULATE`。Forward PE 的风险预算分档为：20–25 正常，低于 20 更积极，高于 25 禁止新增。初始 TQQQ 风险资本上限为 `min(30% × NAV, AbsoluteCap)`。

风险状态只决定买入速度，不覆盖 BuyGate：Stable 正常或较快，Deteriorating 放慢，Severe 只进行基础仓和小规模分批。

### 风险投票

```text
C = 1(HY_OAS_t > HY_OAS_t-13w)
L = 1(NFCI_t > NFCI_t-13w)
E = 1(Implied_NDX_NTM_Forward_EPS_t < Implied_NDX_NTM_Forward_EPS_t-3m)
RiskCount = C + L + E
```

完整数据下，RiskCount 0–1 为 Stable，2 为 Deteriorating，3 为 Severe。E 优先使用 NDX NTM blended Forward EPS；不可得时，使用同一来源、同一观察日期的 `NDX ÷ Forward PE` 反推。缺失数据不能被填成 0 或 1。

### 持有与卖出

QQQ 高于 WeeklySMA200 连续两个完整周线收盘后，`ACCUMULATE → HOLD`。HOLD 默认无限期持有，HOLD 不自动加仓。

顶部预警使用三项：

```text
O_high = QQQ / WeeklySMA200 - 1 >= P90
V_high = Forward PE >= 30
R_high = Risk State >= Deteriorating
```

HOLD 中 O/V/R 任意两项成立才进入 WATCH。WATCH 保持 100% 战略仓位，预警本身不直接卖出。

只有趋势破坏才分级兑现：

- `TD₁`：QQQ 跌破 WeeklySMA50 且 WeeklySMA50 斜率转负，100% → 70%。
- `TD₂`：TD₁ 仍成立且 QQQ 跌破 WeeklySMA200，70% → 40%。
- `TD₃`：QQQ 跌破 WeeklySMA200 且 WeeklySMA200 斜率转负，40% → 20%。

每个完整周线最多下降一级。Structural Failure 拥有最高优先级，可将仓位降至 0–10%。

每个完整周的迁移优先级为：

```text
Structural Failure > 已有状态的卖出迁移 > WATCH/恢复判断 > WAIT/ACCUMULATE 买入判断
```

发生过 REALIZE 周期并满足新的 BuyGate 后，先进入 WAIT，该周不买入；下一完整周 BuyGate 仍成立才进入 ACCUMULATE。已兑现 TQQQ 不自动买回。

## 数据口径

- 周线只使用最近一个完整交易周的收盘，当前周的盘中值不触发周线迁移。
- WeeklySMA50 和 WeeklySMA200 使用同一复权周收盘序列的简单算术平均。
- D 的 P90 使用排除当前周的扩展历史样本，nearest-rank 90 分位，至少需要 260 个有效完整周观测。
- Forward PE 和 EPS 必须保持同一指数、同一财年定义、同一观察日期和同一数据版本。
- 每个数据点记录 `observation_date`、`available_at`、`retrieved_at`、`source_id`、`source_version`、`unit` 和 `method`。
- DXY、美国 10Y、原油、通胀预期和 VIX 只解释背景，不单独改变状态。

## 状态记录

持续跟踪时，状态记录至少保存：

```text
strategy_version
state
actual_state
top_candidate
reentry_eligible
target_position_pct
actual_position_pct
baseline_position_units
execution_status
last_complete_week
last_transition_week
last_transition
trend_recovery_weeks
warning_count
td_stage
provenance
```

`last_transition_week` 防止同一周重复跨级兑现；`reentry_eligible` 表示发生过 REALIZE 周期，但不表示立即买回。没有状态记录时，应输出 `state=unknown`，分别说明 WAIT、HOLD 和 WATCH 下的条件式结论。

`state` 表示策略根据指标产生的目标状态；`actual_state`、`actual_position_pct` 和 `execution_status` 只根据用户确认或成交记录更新。建议仓位变化不能自动写成已成交。

## 固定输出格式

每次分析严格使用以下五个标题，顺序不可改变：

1. 核心结论
2. 均线位置
3. 估值水平
4. 金融风险
5. 交易决策

输出必须标明分析时间、美国市场最新收盘日、盘中或收盘口径、最近完整周线日期、数据缺口和会改变结论的后续条件。

## 文件

- [SKILL.md](SKILL.md)：Codex 加载的活动规则。
- [data-contract.md](references/data-contract.md)：价格、SMA、P90、Forward PE、E 和 C/L/E 数据契约。
- [state-schema.md](references/state-schema.md)：状态记录字段和迁移流程。

旧版引用文件保留在 `references/legacy/`，仅作历史留档，不属于活动规则。
