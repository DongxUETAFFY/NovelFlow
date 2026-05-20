# NovelFlow Continuation Modes Design

这份文档用于和另一个 AI 对齐“续写功能”的设计。它只描述架构与行为边界，不代表已经写入 `novel-write` 主流程。

## Goal

NovelFlow 需要支持两类“续写”：

1. **片段续写 / Fragment Continue**：用户给一段未完成正文，AI 接着这段往下写。
2. **续写到完结 / Finish Book**：一本书已经断更或中断，AI 先理解已有内容，再在作者确认方向后，从当前进度一路写到完结。

这两个功能不能混成一个简单的 `continue`。片段续写偏创作试写，默认不更新项目状态；续写到完结偏长篇接管，必须受 Production Lock 保护。

## Mode Overview

| Mode | Purpose | Default State Updates | Safety Level |
|---|---|---:|---|
| Fragment Continue | 接着用户提供的片段往下写 | No | Free Draft by default |
| Finish Book Intake | 读取旧书、总结现状、提炼文风和伏笔、生成续写方向 | No chapter updates | Diagnostic |
| Finish Book Run | 用户确认方向后，从当前进度写到完结 | Yes | Production Lock |

## 1. Fragment Continue / 片段续写

### Trigger Phrases

- `continue this fragment`
- `continue from here`
- `续写这段`
- `接着这段写`
- `从这里往下写`
- `帮我续写这个片段`

### Use Case

用户提供一段正文或半个场景，希望 AI 接着写一小段、一个场景、或补完这一章的一部分。

### Behavior

1. 读取 `novel/context-brief.md`。
2. 优先使用用户提供的片段作为 **local voice anchor**。
3. 如果能判断当前章节，可读取当前 outline row；否则只按片段和 context-brief 续写。
4. 默认不运行 audit、review checklist、delta validation、commit。
5. 默认不更新 `novel/chapters/`、`story-state.md`、`thread-ledger.md`、`context-brief.md`。
6. 输出续写文本，并明确说明：项目状态没有更新。

### Saving Rules

默认只返回文本。

如果用户要求保存：

```text
novel/drafts/fragment-continue-{timestamp}.md
```

或如果能确定章节：

```text
novel/drafts/chapter-{N}-fragment-continue.md
```

### Promotion To Canon

片段续写不能自动并入正文章节。

只有当用户明确说：

- `并入正文`
- `保存到第 N 章`
- `把这段作为正式章节的一部分`

才进入 Standard Writing：

1. 写入或合并到 `novel/chapters/chapter-{N}.md`。
2. 创建 `mode: "standard"` chapter delta。
3. validate + commit delta。
4. 更新 generated state / legacy exports。

### Hard Boundary

Fragment Continue 是创作模式，不是状态推进模式。不能因为写得像正文，就自动标记章节完成。

## 2. Finish Book Intake / 断书接诊

### Trigger Phrases

- `finish book intake`
- `resume abandoned book`
- `续写到完结`
- `这本书断了，帮我续完`
- `从现在写到完结`
- `接着这本书一直写到结局`

### Purpose

在正式续写到完结之前，AI 必须先理解旧书，而不是直接写下一章。

断更项目最容易出的问题是：

- 文风突变
- 人物状态漂移
- 伏笔忘记回收
- 后续方向和前文承诺冲突
- 作者其实想改变结局，但没有被询问

Intake 阶段用于把旧书转换成可续写的项目状态和后续路线图。

### Reading Strategy

优先读取已有结构化状态：

1. `novel/context-brief.md`
2. `novel/generated/summaries.md` or `novel/summaries.md`
3. `novel/generated/story-state.md` or `novel/story-state.md`
4. `novel/generated/thread-ledger.md` or `novel/thread-ledger.md`
5. `novel/outline.md`
6. `novel/reader-promise.md` or legacy `novel/market-brief.md`
7. 最近一章全文作为 voice anchor

如果项目没有有效 summaries/deltas/generated state，则分批读取已有章节，生成诊断材料。不要一次把所有章节塞进上下文。

### Intake Report

AI 先输出一份《续写诊断报告》，不写正式正文。

报告应包含：

```markdown
# Finish Book Intake Report

## Current Story State
- 当前故事讲到哪里
- 主线卡点
- 当前章节/停笔点

## Character State
- 主要人物当前目标
- 情感关系状态
- 未完成人物弧线

## Style Profile
- 叙述视角
- 句子节奏
- 场景密度
- 对话/内心/描写比例
- 需要保持的文风特征

## Open Threads
- 未回收伏笔
- 未解谜题
- 已承诺的情感/剧情 payoff
- 高风险遗漏点

## Continuity Locks
- 不能违背的事实
- 已发生的不可逆事件

## Possible Continuation Directions
- 方向 A
- 方向 B
- 方向 C（可选）

## Recommended Finish Strategy
- 推荐方向
- 预计剩余章节数
- 关键阶段
- 需要作者确认的问题
```

### User Optional Input

在 Intake Report 后，用户可以输入续写要求，例如：

- 结局要 HE / BE / 开放式
- 某角色不能死
- 感情线加重
- 节奏加快
- 更贴近原文文风
- 跳过支线，专注主线
- 不输入，按 AI 推荐方向继续

如果用户不输入，AI 可以基于诊断报告给出默认路线图，但仍需要用户确认。

## 3. Finish Book Roadmap / 续写路线图

在正式开写前，AI 必须给出后续大体走向。

这不是完整章纲，而是一个可确认的后半本路线图。

### Roadmap Shape

```markdown
# Finish Book Roadmap

## Assumptions
- 根据现有文本推断的前提
- 用户新输入的要求

## Remaining Arc
1. 阶段一：承接断点，恢复主线张力
2. 阶段二：推进主要冲突，回收近端伏笔
3. 阶段三：进入最终危机或情感临界点
4. 阶段四：高潮与主要 payoff
5. 阶段五：结局与余波

## Chapter Range
- 预计还需 N-M 章
- 每章目标字数或节奏建议

## Must-Pay Threads
- T01: ...
- T02: ...

## Character End States
- 角色 A 最终状态
- 角色 B 最终状态

## Stop Conditions
- 遇到 P2 continuity conflict
- 用户要求改方向
- checkpoint 发现全局漂移
```

### Confirmation Gate

在用户确认路线图之前，AI 不能写正式正文。

允许输出：

- 诊断报告
- 后续路线图
- 试写片段

不允许：

- 直接写下一章并标记完成
- 自动进入 batch/full-auto
- 自动更新 project state

## 4. Finish Book Run / 续写到完结

### Entry Condition

必须满足：

1. Intake Report 已完成。
2. Roadmap 已给出。
3. 用户明确确认继续。

### Execution Mode

Finish Book Run 固定使用 **Production Lock**。

原因：续写到完结是高风险自动化，不能使用轻模式。

### Per-Chapter Loop

每章执行：

1. Assemble context.
2. Write chapter.
3. Full review checklist.
4. Create `mode: "production"` chapter delta.
5. Validate delta.
6. Commit delta.
7. Update generated state.
8. Sync legacy files if project expects them.
9. Continue unless a stop condition triggers.

### Checkpoint Policy

建议：

- 每 5 章输出一次轻量 progress report。
- 每 10 章运行 checkpoint。
- 接近结局前强制检查未回收线程。

### Stop Conditions

必须暂停并询问作者：

- P2 continuity problem
- 重要伏笔无法自然回收
- 用户路线图和前文硬事实冲突
- delta validation fails twice
- chapter text edited after committed delta and cannot be safely rebuilt
- 2 consecutive structural decay warnings
- milestone chapter underdeveloped

### Completion Report

完结后输出：

```markdown
# Finish Book Completion Report

## Chapters Written
- Chapter N: title, word count

## Total Words Added

## Resolved Threads
- T01 ...

## Remaining / Ambiguous Threads
- T08 ...

## Character End States

## Suggested Revision Passes
- 最需要精修的章节
- 节奏问题
- 文风漂移风险
```

## Relationship To Existing Modes

```text
Free Draft
  └─ Fragment Continue 默认归这里

Standard Writing
  └─ Fragment Continue 被用户确认并入正文后使用

Production Lock
  └─ Finish Book Run 固定使用
```

## Suggested Files To Update

如果把这个设计落地到 NovelFlow，建议修改：

1. `skills/novel-write/SKILL.md`
   - 增加 Fragment Continue、Finish Book Intake、Finish Book Run 触发词与流程入口。

2. `skills/novel-write/references/modes.md`
   - 增加 Finish Book Intake / Run 的详细流程。

3. `skills/novel-write/references/fragment-continue.md`
   - 可选新增，专门定义片段续写规则。

4. `scripts/build-context-pack.py`
   - 支持 `--mode fragment-continue` 和 `--mode finish-book-intake` / `finish-book-run`。

5. `skills/novel-write/references/testing-scenarios.md`
   - 增加 fresh-agent 测试：
     - 用户给片段续写，不更新状态。
     - 用户要求续写到完结，AI 先输出诊断报告和路线图，等待确认。
     - 用户确认后，Production Lock 写章节并提交 delta。

6. `skills/novel-write/scripts/novelflow.py`
   - 可选新增 `save-fragment-draft` helper。
   - Finish Book 本身不一定需要新 CLI 命令，核心是流程约束。

## Non-Goals

- 不做无限制自动写完全书。
- 不在 Intake 阶段写正式章节。
- 不把片段续写自动并入正稿。
- 不让 Finish Book Run 跳过 delta 或 checkpoint。
- 不把所有旧章节一次性塞进模型上下文。
