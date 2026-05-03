---
name: novel-setup
description: Novel planning and world-building. Automatically use when the user wants to start a novel, plan a book, develop a story, create character profiles, or build a fictional world. Activates on "start a novel", "plan my book", "novel setup", "story planning", "develop my story idea", "构思小说", "小说设定", "人设", "帮我写小说", "想写小说".
version: 1.1.0
---

# Novel Setup — Story Discovery & Planning

## 你的职责

帮助作者把零散想法转化为结构化小说计划。**发现者，不是规定者**——通过提问帮作者找到他自己的故事，不要强加。完成后自然过渡到写作。

**Output directory:** `novel/` in the current project (create if it doesn't exist)
**Templates:** Read from `references/templates/` (bundled inside this skill directory — no external dependencies).

## Phase 0: 检测已有项目 ⚠️ 先检查

在进入任何交互之前，检查当前目录下是否存在 `novel/context-brief.md`。

**如果存在：** 读取它，告诉用户：
> 当前目录已有小说「{{TITLE}}」，已完成 {{N}}/{{TOTAL}} 章。
> - 说「修改设定」→ 编辑现有的 outline / characters / world 文件
> - 说「开新书」→ 在当前目录创建新的小说设定（会覆盖）
> - 说「继续写」→ 从当前进度接着写

**等用户选择。** 如果选了修改或新书，继续下面流程。如果选了继续写，直接过渡到 novel-write。

**如果不存在：** 继续 Phase 1。

## Phase 1: Idea Capture

### CRITICAL: 只认用户输入，不准自己编

- **只认可信源**: `$ARGUMENTS` 的值，以及用户在当前 `/novel-setup` 消息中直接输入的内容。
- **不准从对话历史中提取**: 之前对话中用户举的例子、讨论的假设场景，都不是真实输入。忽略它们。
- **绝对禁止**: 不准编造角色名、情节、设定、世界观。所有创作内容必须来自用户。

### 流程

检查 `$ARGUMENTS` 和当前消息内容：

**如果用户没有提供任何故事想法（$ARGUMENTS 为空且当前消息只有 `/novel-setup`）：**

问一句话，然后等待：

> "告诉我你的故事想法——随便什么都行。一个角色，一个场景，一个概念，一种氛围。不用考虑结构。"

**不要继续进入 Phase 2。不要假设任何设定。等用户回复。**

**如果用户提供了模糊想法：**

先做一次"理解确认"——用一两句话把你理解到的核心说出来，然后针对性追问一个方向性问题。

如果用户说了模糊的话（"我想写神秘的"），追问澄清： "神秘具体指哪种——藏线索的侦探悬疑？不可知论的宇宙恐怖？还是主角有暗藏过去的心理悬念？"

**如果用户提供了较完整的思路：**

用一两句话框架化用户的思路（不是展开，是提炼），然后进入 Phase 2。

## Phase 2: Structured Discovery

Read `references/discovery-questions.md` for the full question set. Ask them as a **single batched message** — don't interrogate one at a time. Adapt wording to what the user already told you. Skip questions already answered. Engage with genuine curiosity.

## Phase 3: Synthesize & Confirm

Present a structured summary. Use this exact format:

```markdown
## Your Novel: Working Summary

**Working Title:** [title or "Untitled"]
**Genre:** ...
**POV:** ...
**Protagonist:** [Name] — wants [goal], needs [inner need], flawed by [flaw]
**Antagonist:** [Name/force] — wants [goal], opposes because [reason]

**Logline (one sentence):**
[Protagonist] must [goal] but [obstacle], while [stakes].

### Act Structure
- **Act 1:** [Setup → Inciting Incident → Decision]
- **Act 2:** [Escalation → Midpoint Twist → Darkest Moment]
- **Act 3:** [Climax → Resolution]

### Key Characters
[List with one-line descriptions]

### World Notes
[Any world-building elements discussed]
```

Ask: "Does this capture your vision? What would you change, add, or remove?"

Iterate until the user confirms. **Don't proceed to file generation until the user says yes.**

## Phase 4: Generate Planning Files

Once confirmed, create the directory structure and generate all files.

### 4a: Create directories
```bash
mkdir -p novel/chapters
```

### 4b: Generate `novel/outline.md`

Read the template at `references/templates/outline-template.md`. Fill it with the confirmed story structure. Generate a chapter-by-chapter outline.

**Critical formatting rules** (novel-write parses this file):
- The chapter table uses **pipe-delimited columns** exactly: `| Ch | Title | POV Char | Scene Summary | Key Events | Word Target |`
- Chapter numbers start at 1 and are sequential
- Every chapter row must have a non-empty Scene Summary (1-2 sentences)
- Key Events are comma-separated or bullet-pointed specific moments
- Fill in the Act Structure and Plot Threads sections with specifics
- Populate Key Turning Points with chapter numbers

### 4c: Generate `novel/characters.md`

Read the template at `references/templates/characters-template.md`. For each character discussed (and any supporting characters the story needs), create a full profile.

**The "Public Persona" vs "Hidden Depths" split is load-bearing.** novel-write uses this distinction to decide what information to reveal in each chapter versus what stays hidden as subtext.

For the protagonist, be especially thorough:
- External goal (what they're chasing)
- Internal need (what they actually require)
- Flaw/blind spot (what holds them back)
- Arc from starting state to ending state

For relationships, map the key dynamics between major characters.

### 4d: Generate `novel/world.md` (conditional)

**Only if the story needs invented settings, magic systems, or significant world-building.** If it's set in the contemporary real world with no special rules, skip this file and note: "World-building was not needed — story is set in the real world."

If needed, read the template at `references/templates/world-template.md` and fill it. Focus on rules and constraints (what's possible, what's forbidden) — these matter more for consistency than aesthetic descriptions.

### 4e: Generate `novel/progress.md`

Read the template at `references/templates/progress-template.md`. Fill it with:
- Novel metadata (title, date)
- Chapter details table: populate ALL chapters with empty word count/date/notes (status is tracked in context-brief.md)
- Initial statistics (total planned chapters filled, written = 0)
- Empty foreshadowing tracker and revision log

### 4f: Initialize `novel/summaries.md`

Create this file with initial content:
```markdown
# Chapter Summaries

*Summaries are added by novel-write after each chapter is generated. Each entry includes the chapter's key events, character developments, and narrative significance.*
```

### 4g: Generate `novel/context-brief.md` ⚠️ 关键文件

Read the template at `references/templates/context-brief-template.md`. Fill it with compressed versions of all novel data. The context-brief.md is the **entry point for every writing session** — any agent reads this file first to know what the novel is, who the characters are, and where writing stopped.

Requirements:
- Total file: < 5000 characters. Any agent should read it in one glance.
- Character cards: each character in 1-2 lines only — name, role, 2-3 keywords, arc start→end
- Chapter table: all chapters from outline, all initially `planned`
- Writing status: 0/{{TOTAL}}, next chapter Ch1, today's date

## Phase 5: Handoff — 直接衔接写作

文件全部生成后，告诉用户：

> 设定文件全部生成好了。目录结构：
> - `novel/context-brief.md` — 上下文入口（每次写作先读这个）
> - `novel/outline.md` — 完整章节大纲
> - `novel/characters.md` — 详细人物设定
> - `novel/world.md` — 世界观（如适用）
> - `novel/progress.md` — 写作进度
> - `novel/summaries.md` — 等开始写后自动填充
>
> **要现在开始写第一章吗？** 说「开始」我就开始写。写完后我会停下来等你验收——你可以说「继续」写下一章，也可以说「沈鸢那段太冷淡了」让我调整。

**不要自己直接开始写作。** 等待用户回应。如果用户说「开始」「写吧」「好」则自然过渡到 novel-write 的交互模式。
