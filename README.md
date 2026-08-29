# xiaonaneo-skills

这里分享我制作的实用 skills，帮助 Codex 在具体工作中遵循一套稳定、可复用的处理流程。

每个 skill 都以独立目录保存，核心说明和行为约束写在目录中的 `SKILL.md` 文件里。仓库会持续更新。

## Skills

### [deep-book-deconstruction](deep-book-deconstruction/SKILL.md)

把一本完整书籍转化为结构化、可阅读的中文拆书稿。

它会：

- 以用户提供的书籍 PDF 作为主要证据来源；
- 按阅读顺序逐章梳理观点、证据、案例和推理链；
- 用日常语言解释抽象概念，并区分书中观点与解释性类比；
- 输出 `核心观点`、`逐章解读`、`适用范围` 三个部分；
- 提取 10 条有来源、简短的精彩原句；
- 将生成的 Markdown 文件保存并复制到 Obsidian 的 `拆书` 文件夹。

适合在需要快速理解一本书、整理阅读笔记，或把书中的论证转化为可复习材料时使用。触发方式包括 `深度拆书`、`gg`、`拆书`，或直接提供一本书籍 PDF。

### [qqq-market-analysis](qqq-market-analysis/SKILL.md)

按照长期趋势、估值和金融压力分析 QQQ/TQQQ，并将证据映射为明确的交易信号。

它会：

- 比较 QQQ 周 MA200、TQQQ 周 MA300 及长期乖离；
- 区分 trailing、forward 和 harmonic P/E，判断估值水平与历史位置；
- 跟踪信用利差、流动性、波动率、盈利预期和综合金融条件；
- 输出观察、买入、加仓、持有、卖出观察或分批卖出信号；
- 执行 TQQQ 买入本金不超过总资产 30% 和绝对金额上限的仓位规则；
- 检查日杠杆的路径依赖、数据口径和策略中的隐藏假设。

适合在分析当前 QQQ/TQQQ 行情、执行个人 TQQQ 策略，或研究历史行情与回测条件时使用。实时分析只使用英文或国际来源，并标注数据时间与口径。

## 使用方式

选择需要的 skill，阅读对应目录中的 `SKILL.md`，再将该目录放入 Codex 的 skills 目录中使用。不同运行环境的 skills 目录位置可能不同，请以本机 Codex 配置为准。

## 项目结构

```text
.
├── qqq-market-analysis/
│   ├── agents/
│   │   └── openai.yaml
│   ├── references/
│   │   └── sources-and-metrics.md
│   └── SKILL.md
├── deep-book-deconstruction/
│   └── SKILL.md
├── LICENSE
└── README.md
```

## 说明

这些 skills 面向实际工作流设计，重点是明确输入、处理边界、输出结构和验证要求。使用时请结合自己的文件路径、工具权限和隐私需求进行配置。
