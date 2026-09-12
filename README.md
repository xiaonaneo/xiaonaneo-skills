# xiaonaneo-skills

这里分享我制作的实用 skills，帮助 Codex 在具体工作中遵循一套稳定、可复用的处理流程。

每个 skill 都以独立目录保存，核心说明和行为约束写在目录中的 `SKILL.md` 文件里。仓库会持续更新。

## Skills

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

### [tqqq-investment-strategy](tqqq-investment-strategy/SKILL.md)

按 `TQQQ 完整交易策略 v2026.09` 冻结版分析 QQQ/TQQQ 市场状态，覆盖均线位置、Forward PE、NDX NTM blended Forward EPS、C/L/E 金融风险投票和趋势标记。

它会：

- 使用 QQQ 的 WeeklySMA50/200、PriceCondition 和扩展历史 P90 判断位置；
- 通过直接数据或同日期 NDX ÷ Forward PE 反推验证 E 通道，并保留数据 provenance；
- 按 UNKNOWN、STRUCTURE_STABLE、TOP_RISK_CANDIDATE、MID_TREND_DAMAGE、LONG_TREND_DAMAGE 和 STRUCTURE_FAILURE 标记市场状态；
- 只保存市场状态、数据质量和 provenance，不输出交易决策或仓位建议；
- 严格区分完整周线、未完成周线、数据缺失和三值风险投票。

适合需要按固定规则分析当前 TQQQ 行情和市场阶段的场景；不输出交易决策，也不适用于普通个股评论。

## 使用方式

选择需要的 skill，阅读对应目录中的 `SKILL.md`，再将该目录放入 Codex 的 skills 目录中使用。不同运行环境的 skills 目录位置可能不同，请以本机 Codex 配置为准。

## 项目结构

```text
.
├── ai-native-software-engineering/
│   ├── agents/
│   │   └── openai.yaml
│   └── SKILL.md
├── tqqq-investment-strategy/
│   ├── agents/
│   │   └── openai.yaml
│   ├── references/
│   │   ├── data-contract.md
│   │   └── state-schema.md
│   └── SKILL.md
├── LICENSE
└── README.md
```

## 说明

这些 skills 面向实际工作流设计，重点是明确输入、处理边界、输出结构和验证要求。使用时请结合自己的文件路径、工具权限和隐私需求进行配置。
