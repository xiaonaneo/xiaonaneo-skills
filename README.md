# xiaonaneo-skills

这里分享我制作的实用 skills，帮助 Codex 在具体工作中遵循稳定、可复用的处理方式。

每个 skill 都以独立目录保存，核心说明和行为约束写在目录中的 `SKILL.md` 文件里。

## Skills

### [ai-native-software-engineering](ai-native-software-engineering/SKILL.md)

把 AI 编程纳入可审查、可验证、可回滚的软件工程闭环。

### [tqqq-investment-strategy](tqqq-investment-strategy/SKILL.md)

只分析当前 TQQQ/QQQ 的市场状态，不输出交易或仓位建议，固定覆盖：

- QQQ 距离周 SMA200 的水平与历史百分位、是否低于周 SMA200；
- QQQ 相对周 SMA50 的位置，以及周 SMA50 斜率是否向上；
- QQQ 估值代理 Nasdaq-100 Forward PE 及历史百分位；
- HY OAS、NFCI、VIX 的当前水平、历史百分位、变化方向和近四周平均变化。

输出使用简体中文，只显示精简数据和结论，不列计算过程或内部流程。

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
