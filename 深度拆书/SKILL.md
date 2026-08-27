---
name: deep-book-deconstruction
description: 使用用户上传的书籍 PDF 输出深度拆书稿。Use when the user invokes 深度拆书, gg, 拆书, or uploads a book PDF for deconstruction, writes a Chinese book deconstruction, and copies the generated Markdown file into the Obsidian 拆书 folder.
---

# 深度拆书

## Goal

If the user uploads a full book PDF, read the PDF as the primary source and write a sharp Chinese deconstruction of that book with exactly three sections: 核心观点, 逐章解读, 适用范围. If no full book source is provided, ask the user to provide one instead of selecting a book automatically. Save a real Markdown file named `书名.md`, and copy that file into the user's Obsidian notes `拆书` folder.

## Hard Rules

- If the user provides a book PDF in the current request, use the PDF as the primary evidence source.
- Do not select a book automatically when no full book source is provided; ask the user for a source.
- Do not fake evidence. If the available source is thin, say it is thin and reduce confidence.
- For copyrighted books, summarize and analyze in your own words. Use only short quotations when necessary, and do not reproduce long passages or create an output that substitutes for the original book.
- The output must contain exactly three top-level sections: 核心观点, 逐章解读, 适用范围. Do not add any other sections.
- The complete deconstruction must be between 8000 and 10000 Chinese characters, including headings, quotations, and every section, unless the user explicitly sets another limit in the current request.
- Write the output file first, verify it exists, copy it into the user's Obsidian notes `拆书` folder, verify the copied file exists, then report both paths.

## Default Parameters

- Output language: Chinese.
- Output length: 8000-10000 Chinese characters unless the user explicitly sets another limit in the current request. Section budgets, including headings and the 精彩金句 subsection: ## 核心观点 about 500 characters, ## 逐章解读 about 6500-8500 characters, ## 适用范围 about 1000 characters.
- Style: storytelling (讲故事的文风): write as if telling the reader a story, with flowing, connected sentences that carry the reader from one idea to the next. Avoid excessive sentence fragments and choppy short breaks. Keep the writing calm, concise, sharp, and direct.
- Final cleanup pass: remove translationese, vague connectors, filler transitions, and empty abstractions.

## Required Output Structure

Use exactly these top-level headings:

```markdown
# 书名

## 核心观点

## 逐章解读

### 精彩金句

## 适用范围
```

## Section Requirements

### 核心观点

About 500 Chinese characters that compress the whole book from above: the book's central judgments and how they hold together. Write the book's actual stance, not a topic label.

### 逐章解读

About 6500-8500 Chinese characters. Go through the book chapter by chapter in reading order. For each chapter, state the chapter's main point and the key evidence or concrete cases that carry it, then note how it feeds the book's overall argument. Ground every chapter entry in what is actually in the PDF; do not invent content. Give the deepest treatment to the chapters that carry the core argument.

When a concept is abstract or hard to understand, add a short everyday-life analogy that makes the author's meaning concrete. Use analogies sparingly, only where they genuinely help; do not force one into every chapter. Mark the analogy clearly as an analogy, keep it to one or two sentences, and immediately return to the book's own terms so the reader can tell the book's claim apart from the comparison. An analogy is an explanatory aid, not evidence: never present it as something the book says, and do not stretch it into a claim the author did not make.

Write each chapter entry in plain, everyday Chinese, as if explaining to a smart friend who has not read the book. Do not interpret with academic language: avoid jargon, abstract noun piles, and formal essay turns of phrase; when a term cannot be avoided, state it once and define it immediately in ordinary words. Simplifying the language must not simplify the logic: keep the premise-evidence-conclusion chain of each step explicit, and state the reasoning and limits of the argument as precisely as the book does.

Prefer a first-principles approach (第一性原理) when interpreting each chapter: start from the author's basic starting points — the facts and assumptions the chapter takes as given — then rebuild the argument step by step, showing each reasoning step in order until the chapter's conclusion. Make the chain visible: every step must follow from the previous one, so the reader can trace how the author got from the starting point to the conclusion. When the book skips a step or jumps in logic, name the gap instead of smoothing it over; do not fill it with claims the book did not make.

Write each chapter as a mini-story: open with the situation or question the chapter faces, move through the evidence and reasoning in a connected flow, and close with where the argument lands. Link each sentence to the one before it instead of dropping short fragments; keep the prose flowing so the reader follows the logic without stopping.

### 精彩金句

Select exactly 10 short, memorable quotations from the book. Every quotation must be supported by an accessible source; do not invent or stitch together quotations. Keep each quotation brief and do not use the section to substitute for the book.

### 适用范围

About 1000 Chinese characters. State the conditions and scope in which the book's conclusions apply. Name who the book is for, in what situations it works, where it overreaches, and where it fails.

## Output File

- Save the generated output as a real Markdown file named `书名.md`.
- Locate the user's Obsidian notes `拆书` folder and copy the generated `书名.md` into that folder. Prefer the iCloud Obsidian vault root `/Users/xiaonaneo/Library/Mobile Documents/iCloud~md~obsidian/Documents`, especially `反脆弱体系/2 积累选择权/学习/阅读/拆书/<current-year>/` when that year folder exists.
- Sanitize filename characters that are invalid or awkward on macOS: `/`, `:`, newline, and leading/trailing whitespace.
- If the output file or Obsidian copy target already exists, do not overwrite silently. Choose another candidate or ask the user if all strong candidates already exist.
- After writing, verify the generated output file with `test -f` or equivalent.
- After copying, verify the copied file in the Obsidian `拆书` folder with `test -f` or equivalent.
- Report the absolute path of the generated output file and the absolute path of the Obsidian copy only after both verification checks pass.

## Final Checklist

Before answering the user:

- If a PDF was provided, the PDF was used as the primary evidence source.
- The output contains exactly three top-level sections: 核心观点, 逐章解读, 适用范围.
- 核心观点 is about 500 Chinese characters and compresses the whole book.
- 逐章解读 is about 6500-8500 Chinese characters, covers every chapter in reading order, and is grounded in evidence from the PDF.
- In 逐章解读, hard-to-understand concepts are explained with short, clearly marked analogies where they genuinely help; each analogy returns to the book's own terms and is not presented as the book's claim.
- 逐章解读 uses plain everyday Chinese without academic language, while keeping each chapter's premise-evidence-conclusion chain explicit and rigorous.
- 逐章解读 derives each chapter's argument step by step from its basic starting points (first principles), makes the logic chain traceable, and names gaps instead of hiding them.
- 逐章解读 is written in a storytelling style with flowing, connected sentences, not choppy fragments or excessive short sentences.
- "精彩金句" contains exactly 10 short, source-supported quotations.
- 适用范围 is about 1000 Chinese characters and names the conditions, audience, and limits of the book's conclusions.
- Copyrighted text is summarized and analyzed; any direct quotations are short, necessary, and supported by accessible evidence.
- The complete output, including headings and quotations, is between 8000 and 10000 Chinese characters unless the user explicitly requested another limit.
- The generated Markdown file exists at the reported absolute path.
- The copied Markdown file exists in the Obsidian `拆书` folder at the reported absolute path.
