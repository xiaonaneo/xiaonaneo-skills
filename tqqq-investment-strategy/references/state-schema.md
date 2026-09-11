# TQQQ 状态记录契约

状态记录解决“指标变化”和“策略当前状态”不是同一件事的问题。指标只能产生候选迁移；上一状态、上一迁移周和当前战略仓位必须从记录读取。

## 存储边界

持续跟踪时，使用用户指定的状态文件。用户没有指定路径但明确要求持续保存时，可使用当前分析工作区下的 state/tqqq-state.json，并同时保留 state/tqqq-history.jsonl 作为追加历史。没有持续保存授权时只输出结果，不创建或覆盖状态文件。

## 最小字段

```json
{
  "strategy_version": "2026.09",
  "state": "WAIT",
  "actual_state": "WAIT",
  "top_candidate": false,
  "reentry_eligible": false,
  "target_position_pct": 0,
  "actual_position_pct": 0,
  "baseline_position_units": null,
  "execution_status": "not_requested",
  "td_stage": 0,
  "last_complete_week": "YYYY-MM-DD",
  "last_transition_week": null,
  "last_transition": null,
  "trend_recovery_weeks": 0,
  "warning_count": null,
  "last_evaluation_at": "YYYY-MM-DDTHH:mm:ssZ",
  "provenance": {
    "price": [],
    "valuation": [],
    "risk": []
  }
}
```

state 只能是 WAIT、ACCUMULATE、HOLD、WATCH、REALIZE1、REALIZE2 或 DE-RISK。StructuralCheck=FAIL 是覆盖条件，不另造一个与状态机并列的普通状态。

state 是基于信号的目标状态；actual_state 只根据用户确认或成交记录更新。target_position_pct 是相对于卖出阶段开始时战略仓位的目标剩余比例，只允许 100、70、40、20；StructuralCheck=FAIL 时可为 0–10。actual_position_pct 是同一基准下已确认的实际剩余比例；没有成交证据时保持 null。baseline_position_units 记录卖出阶段开始时的 TQQQ 数量，不能用 NAV 权重替代。

execution_status 取 not_requested、pending、partially_filled、filled、rejected 或 unknown。策略信号可以改变 state 和 target_position_pct，但不能自动改变 actual_state 或 actual_position_pct。

reentry_eligible 在发生过 REALIZE₁、REALIZE₂ 或 DE-RISK 迁移后设为 true。它只表示未来可以评估新一轮 Buy Gate，不表示立即买回或允许 HOLD 自动加仓。

last_complete_week 是最近已处理的完整周线。last_transition_week 防止同一周执行多次兑现。td_stage 取 0、1、2、3，分别对应未兑现、REALIZE1、REALIZE2、DE-RISK。

## 读取与迁移

每次运行按以下顺序处理：

1. 读取上一条状态和最近已处理周线；没有状态记录时，state=unknown。
2. 读取最新可见的日、周、月数据，剔除分析截止时间后才发布的数据。
3. 计算 Buy Gate、C/L/E、O/V/R、TrendRecovery 和 TD₁/TD₂/TD₃。
4. 按固定优先级处理：Structural Failure > 当前状态的卖出迁移 > WATCH/恢复判断 > WAIT/ACCUMULATE 买入判断。同一完整周最多执行一个信号迁移。
5. 如果 StructuralCheck=FAIL，优先把战略仓位设为 0–10%，记录迁移原因。
6. WATCH 若 TD₁ 成立且本周未产生过同级信号，进入 REALIZE1 并把 target_position_pct 设为 70%；REALIZE1 后续完整周 TD₂ 仍成立才设为 40%；REALIZE2 后续完整周 TD₃ 成立才设为 20%。同一完整周禁止跨越多个级别。
7. WATCH 若没有更高优先级的 TD₁，且 warning_count≤1、TrendRecovery 成立，回到 HOLD 并清除 top_candidate。REALIZE 状态若顶部警报消退且 TrendRecovery 成立，只回到 HOLD 并停止继续卖出；已经兑现的 TQQQ 不自动买回。
8. HOLD 不自动加仓。发生过 REALIZE 迁移且 reentry_eligible=true 后，只有新的完整周满足 StructuralCheck=PASS、PriceGate=OPEN、Forward PE≤25、top_candidate=false，且没有更高优先级卖出迁移，才从 HOLD/REALIZE/DE-RISK 转入 WAIT；该周不买入。若同周满足恢复条件，先执行恢复到 HOLD，下一完整周再评估重新进入 WAIT。
9. WAIT 只有 Buy Gate 全部打开才进入 ACCUMULATE；重新进入 WAIT 后必须再经过一个完整周确认。ACCUMULATE 需要 QQQ>SMA200 连续两个完整周线收盘，才进入 HOLD。
10. HOLD 只有 O、V、R 任意两项确认才进入 WATCH，并设置 top_candidate=true；普通 HOLD 即使 Buy Gate 打开也不转入 WAIT。
11. 写回时更新 last_complete_week、provenance、target 状态和迁移理由，并向 history.jsonl 追加事件；只有成交证据存在时才更新 actual_state、actual_position_pct 和 execution_status；保留旧状态。

没有状态记录时，不得把“当前指标满足某条件”写成“账户已经处于某状态”。输出应分别给出：若当前是 WAIT、若当前是 HOLD、若当前是 WATCH 时的行动分支。

## 事件记录

每个历史事件至少保存 event_at、decision_week、from_state、to_state、reason、target_position_pct、actual_position_pct、execution_status、signals 和 provenance。reason 必须能指出是 BuyGate、两票 WATCH、TD₁/TD₂/TD₃、TrendRecovery 还是 Structural Failure 导致迁移。
