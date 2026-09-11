---
name: tqqq-investment-strategy
description: "按 TQQQ 完整交易策略 v2026.09 冻结版，核验 QQQ/TQQQ 行情、均线、估值、C/L/E 风险和状态机决策。适用于当前 TQQQ 投资策略分析，不适用于普通个股评论。"
---

# TQQQ投资策略

## 目的与规则来源

本 Skill 把《TQQQ 完整交易策略 v2026.09》（版本日期 2026-09-11，新版冻结版）落实为可复核的当前行情分析。它只提供决策支持，不自动下单，不修改账户，不把历史示例当作当前数据。

该版本是唯一活动规则源。用户后来提供的新版本、明确阈值或修改优先于本 Skill。旧版的 TQQQ 自身 MA300 买入门、P95、极端估值直接卖出、T0、持有天数止盈、连续 N 周规则和额外评分均已删除；PE≥30 现作为顶部估值预警使用，不得误列为已删除规则。

数据契约见 [references/data-contract.md](references/data-contract.md)。需要跨次分析保持状态时，读取 [references/state-schema.md](references/state-schema.md) 和用户指定的状态记录；没有状态记录时，不凭当天指标伪造账户所处状态。

## 数据截止与来源

当前行情必须重新核验。输出核心结论中标明北京时间、美国市场最新收盘日、盘中/收盘状态和最近一个完整周线日期。

- 周线信号只使用最近一个完整交易周的收盘；当前周未结束时，盘中价格和部分周线只能作为背景。
- 价格、SMA200、SMA50、偏离度和 P90 使用同一来源、同一复权口径、同一周边界。历史数据不足时报告缺口，不用日线均线或另一只 ETF 替代。
- QQQ 是底层趋势和 Price Gate 对象。TQQQ 价格用于行情表现与风险说明，不作为底层趋势门槛。
- Forward PE 只使用一个可验证口径。NTM blended Forward EPS 优先使用 LSEG I/B/E/S Global Aggregates，其次 Bloomberg/FactSet；如果直接 EPS 不可得，才使用同一观察日的 NDX ÷ Forward PE 反推。
- E 的比较使用最新可用完整月末与三个月前的对应月末。周末/节假日使用月末最后一个交易日，并同时记录数据的 observation date、available_at 和 retrieved_at。
- 直接 EPS 和合规反推均不可得时，E=NA。未知值不能当作 0、1、改善、恶化或有利证据。
- C 使用 HY OAS，L 使用 NFCI，E 使用 Nasdaq-100 NTM blended Forward EPS 三个月方向。DXY、美国 10Y、原油、通胀预期和 VIX 只作背景，不单独改变状态。

## 冻结决策规则

### Structural Check 与 Buy Gate

StructuralCheck 观察 Nasdaq-100 的盈利与创新驱动、指数优胜劣汰、TQQQ 日常实现机制、基金结构、流动性和美国资本市场制度。普通衰退、战争、疫情、金融危机或 VIX 暴涨不自动等于结构性失效；根本性制度或产品失效才是 FAIL。

价格硬门只使用 QQQ：

PriceGate = QQQ <= 1.05 × WeeklySMA200

估值硬门为 Forward PE <= 25。PE>25 禁止新增；20–25 为正常风险预算；<20 为高风险预算。Forward EPS 可靠性下降只降低 TargetCapital，不建立额外评分。

只有 StructuralCheck=PASS、PriceGate=OPEN 和 Forward PE<=25 同时满足，才允许 WAIT→ACCUMULATE。初始 TQQQ 风险资本上限为 min(30%×NAV, AbsoluteCap)；这是初始投入上限，不是永久组合权重上限。

Risk State 只决定买入速度：Stable 正常或较快，Deteriorating 放慢，Severe 只保留基础仓和小规模分批。风险压力不替代 Buy Gate。

每个完整周的状态迁移优先级固定为：Structural Failure > 已有状态的卖出迁移 > WATCH/恢复判断 > WAIT/ACCUMULATE 买入判断。同一完整周只执行一个状态迁移；低优先级买入判断不能覆盖当前状态的卖出或恢复判断。

### C/L/E Risk State

```text
C = 1(HY_OAS_t > HY_OAS_t-13w)
L = 1(NFCI_t > NFCI_t-13w)
E = 1(Implied_NDX_NTM_Forward_EPS_t < Implied_NDX_NTM_Forward_EPS_t-3m)
RiskCount = C + L + E
```

完整数据下，RiskCount=0或1 为 Stable，=2 为 Deteriorating，=3 为 Severe。任一通道缺失时不填补该通道；报告 known_count 和 possible_range。只有可能范围完全落在同一状态时，才可确定该状态，否则 Risk State=NA。R_high 只有在 known_count≥2 时才确认成立；区间跨越 1/2 时保持 NA。

### ACCUMULATE 与 HOLD

QQQ 高于 WeeklySMA200 连续两个完整周线收盘，才允许 ACCUMULATE→HOLD。HOLD 默认无限期持有，不因涨幅、持有时间、TQQQ 占 NAV 比例或一次普通风险事件自动卖出。

HOLD 不自动加仓。即使 Buy Gate 打开，HOLD 也只按重新进入 WAIT 的规则等待新一轮完整周确认，不在 HOLD 状态直接新增 TQQQ。

### WATCH、Trend Recovery 与 Trend Damage

定义：

```text
D = QQQ / WeeklySMA200 - 1
O_high = D >= P90
V_high = Forward PE >= 30
R_high = Risk State >= Deteriorating
```

HOLD 中 O、V、R 任意两项成立才进入 WATCH，并设置 TopCandidate=TRUE。WATCH 保持 100% 战略仓位；O/V/R 只负责预警，不直接卖出。进入 WATCH 后保留状态记忆，即使最初两项后来消退，也不自动清除候选顶部。

WarningCount = O_high + V_high + R_high。R 未知时不能按 0 计入；应保留已知计数和可能范围，只有确定达到两项时才进入 WATCH。

TrendRecovery = QQQ Close > WeeklySMA50 且 WeeklySMA50_t > WeeklySMA50_t-1。只有 WarningCount≤1 且 TrendRecovery 成立，才允许 WATCH→HOLD，并清除 TopCandidate。

首次卖出权限只在 WATCH 且 TD₁ 成立时产生：

- TD₁：QQQ Close<WeeklySMA50 且 WeeklySMA50_t<WeeklySMA50_t-1，100%→70%。
- TD₂：TD₁ 且 QQQ Close<WeeklySMA200，70%→40%。
- TD₃：QQQ Close<WeeklySMA200 且 WeeklySMA200_t<WeeklySMA200_t-1，40%→20%。

每个完整周线最多下降一级，即使 TD₁、TD₂、TD₃ 同周成立也只能执行一级。兑现比例相对于卖出阶段开始时的 TQQQ 战略仓位，不是 NAV 权重。REALIZE 后恢复只停止继续卖出，不自动买回；重新增加 TQQQ 必须等待未来 Buy Gate。StructuralCheck=FAIL 优先，将仓位降至 0–10%。

### REALIZE 后重新进入 WAIT

发生过一次 REALIZE₁、REALIZE₂ 或 DE-RISK 迁移后，设置 reentry_eligible=TRUE。若顶部候选已经通过 TrendRecovery 清除并回到 HOLD，HOLD 仍不直接买入。只有之后某个新的完整周同时满足 StructuralCheck=PASS、PriceGate=OPEN、Forward PE≤25，且本周没有更高优先级的卖出迁移，才允许 HOLD/REALIZE/DE-RISK→WAIT；该迁移周不买入。下一完整周 Buy Gate 仍成立时，才允许 WAIT→ACCUMULATE。没有发生过 REALIZE 周期的普通 HOLD，不因 Buy Gate 打开而转入 WAIT。

## 状态记录要求

状态记录至少保存：strategy_version、state、actual_state、top_candidate、reentry_eligible、target_position_pct、actual_position_pct、baseline_position_units、execution_status、last_complete_week、last_transition_week、last_transition、trend_recovery_weeks、warning_count、td_stage 和本次各指标的 provenance。

state、target_position_pct 和 last_transition 表示策略信号；actual_state、actual_position_pct 和 execution_status 表示用户确认或成交后的实际执行结果。产生卖出或买入建议时，只更新目标字段，不把建议当作成交；execution_status 为 pending、partially_filled、filled、rejected 或 unknown 时，下一次分析必须同时展示目标与实际状态。

每次运行先读取上一状态，再按最新完整周线计算候选迁移。last_transition_week 用于阻止同一完整周重复执行多个兑现级别；trend_recovery_weeks 用于确认 ACCUMULATE→HOLD 的两个完整周。没有状态记录时，输出 state unknown，并分别给出若当前为 WAIT、HOLD 或 WATCH 时的条件式结论；不要把未知账户状态写成已确认状态。

只有用户要求持续保存状态，或已提供明确状态文件路径时，才写回状态。写回时保留旧记录或追加历史事件，不覆盖无法确认归属的文件。

## 输出格式

面向用户使用简体中文，严格只使用以下五个固定标题，顺序不可变，不增加其他顶级标题：

**核心结论**
日期：YYYY-MM-DD HH:mm（Asia/Shanghai；美国收盘/盘中）
结论：[行动状态]。概括均线、估值、金融风险和状态机判断。

**均线位置**
数据：QQQ/TQQQ 价格、最近完整周线、WeeklySMA200、WeeklySMA50、D、P90 和数据口径。
结论：说明 PriceGate、TrendRecovery 或 TD₁/TD₂/TD₃ 是否满足。

**估值水平**
数据：Nasdaq-100 Forward PE、观察日、估值档位，以及直接 NTM blended Forward EPS 或同日期反推过程。
结论：说明估值对 Buy Gate、TargetCapital 和顶部预警的影响。

**金融风险**
数据：C、L、E、比较窗口、RiskCount 或可能范围、Risk State 及每个数据的发布日期。
结论：说明风险对买入速度、WATCH 和状态迁移的影响；缺失值保留 NA。

**交易决策**
新资金：[不新增/正常部署/放慢/分批等]。
已有仓位：[状态未知时给条件式结论；否则持有/进入 WATCH/按 TD₁、TD₂ 或 TD₃ 兑现]。同时区分 target 与 actual 的执行状态。
说明未触发迁移的具体原因和会改变结论的最小后续条件。
