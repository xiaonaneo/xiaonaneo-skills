# xiaonaneo-skills

这里分享我制作的实用 skills，帮助 Codex 在具体工作中遵循一套稳定、可复用的处理流程。

每个 skill 都以独立目录保存，核心说明和行为约束写在目录中的 `SKILL.md` 文件里。仓库会持续更新。

## Skills

### [TQQQ投资策略](tqqq-investment-strategy/SKILL.md)

以均线、估值和金融压力三因子交叉验证 QQQ/TQQQ，并将证据映射为明确的交易信号。

它会：

- 比较 QQQ 周 MA200、TQQQ 周 MA300 及长期乖离；
- 区分 trailing、forward 和 harmonic P/E，判断估值水平与历史位置；
- 跟踪信用利差、流动性、波动率、企业盈利水平、盈利预期和综合金融条件；
- 严格分离数据职责：Yahoo adjusted close 只用于 QQQ/TQQQ 价格和均线，Yahoo `DX-Y.NYB` 只用于直接 ICE DXY，FRED/Cboe 用于金融压力，Nasdaq 官方资料用于盈利，forward P/E 只使用 Trendonify 的已载入并通过连续性检查的月度序列；
- 按均线、估值和金融压力的定性一致性决定观察、分批行动或提高力度；
- 先按 `READY / PARTIAL / STALE / INVALID` 判断三因子资格，再将评分作为行动强度上限；
- 按统一买入分/卖出分表计算评分，并在“交易评分”中显示分数及行动映射；
- 按因子一致性控制仓位，并受硬门槛、总资产 30% 上限和绝对金额上限约束；
- 按“核心结论、均线位置、估值水平、金融压力、交易评分”五大板块输出执行结果；
- 输出观察、买入、加仓、持有、卖出观察或分批卖出信号；
- 执行 TQQQ 买入本金不超过总资产 30% 和绝对金额上限的仓位规则；
- 检查日杠杆的路径依赖、数据口径和策略中的隐藏假设。

适合在分析当前 QQQ/TQQQ 行情、执行个人 TQQQ 策略，或研究历史行情与回测条件时使用。实时分析只使用英文或国际来源，并标注数据时间与口径。

### [ai-native-software-engineering](ai-native-software-engineering/SKILL.md)

把 AI 编程纳入可审查、可验证、可回滚的软件工程闭环。

已针对 GPT-6 Astra 调整自主执行、验证范围和任务协作：常规选择直接推进，按风险验证，验证通过后及时交付；处理中途补充要求，并仅在工作可独立完成时委派。

它会：

- 按变化原因和业务领域划分模块，控制上下文半径与修改范围；
- 明确验收标准、数据 ownership、不变量以及 API、事件和 schema 契约；
- 优先选择最简单的正确实现，控制抽象、依赖、共享状态和长期复杂度；
- 覆盖边界、失败路径和回归测试，并自动执行适用的格式化、静态检查、构建和安全检查；
- 对生产数据、权限、secret、破坏性迁移和生产部署等不可逆操作保留人工确认；
- 删除功能时同步清理代码、配置、依赖、测试、文档、监控和兼容逻辑。

适合在使用 AI 规划、实现、审查或重构软件时使用；纯粹的代码风格改写不适用。

## 使用方式

选择需要的 skill，阅读对应目录中的 `SKILL.md`，再将该目录放入 Codex 的 skills 目录中使用。不同运行环境的 skills 目录位置可能不同，请以本机 Codex 配置为准。

## 项目结构

```text
.
├── tqqq-investment-strategy/
│   ├── agents/
│   │   └── openai.yaml
│   ├── references/
│   │   ├── scoring-system.md
│   │   └── sources-and-metrics.md
│   ├── scripts/
│   │   ├── scoring_rules.py
│   │   └── test_scoring_rules.py
│   └── SKILL.md
├── ai-native-software-engineering/
│   ├── agents/
│   │   └── openai.yaml
│   └── SKILL.md
├── LICENSE
└── README.md
```

## 说明

这些 skills 面向实际工作流设计，重点是明确输入、处理边界、输出结构和验证要求。使用时请结合自己的文件路径、工具权限和隐私需求进行配置。
