---
name: novel-write
description: Write novel chapters with full context-aware generation. Automatically use when the user says "write a chapter", "start writing", "continue my novel", "draft the next chapter", "开始写", "写第一章", "继续写", "写小说", or any expression of wanting to write/generate novel chapters. Supports interactive mode (default, pauses after each chapter) and full-auto mode (writes all remaining chapters).
version: 1.2.0
---

# Novel Write

## 前提

需要 `novel/context-brief.md`（由 `/novel-setup` 产出）。

**如果找不到 `novel/context-brief.md`：** 直接问用户：
> 当前目录还没有小说项目。要我帮你创建一个吗？告诉我你的故事想法就好。

如果用户给想法 → 转入 novel-setup 的 Phase 1 流程（提问、确认、生成文件），生成完后回到写作。

## 两种模式

| 模式 | 触发 | 行为 |
|------|------|------|
| **交互模式**（默认） | "写一章""继续写""下一章" | 写一章 → 展示摘要 → **停下来等反馈** → 用户说继续才继续 |
| **全自动模式** | "全部写完""all""一口气写完""自动写" | 连续写完所有剩余章节，每 5 章汇报，P2 暂停 |

---

## 交互模式（默认）流程

### Step 0: 恢复状态

**只读 `novel/context-brief.md`**——这是压缩版系统提示词和章节状态的**唯一真源**。包含 premise、角色卡摘要、写作进度、章节目录+状态。任何 agent 进入后第一眼看它。

不要读 outline.md / characters.md / progress.md / world.md。context-brief.md 已有足够信息判断当前状态。

根据已完成章节数给出欢迎语，然后直接进入 Step 1。

### Step 1: 按需组装上下文

Foundation 已在 context-brief.md 中。现在只读写作本章**必需**的：

- `novel/summaries.md` — 按 `references/compression-guide.md` 叠加金字塔摘要
- 上一章全文（如有）作为 Voice Anchor。第一章跳过
- 如果本章涉及具体世界观规则，读 `novel/world.md` 的相关章节（不要全读）
- 如果本章有新角色或需要角色细节，读 `novel/characters.md` 中该角色的条目（不要全读）

不要无脑全读。context-brief.md 的压缩角色卡对于大多数章节已经够了。

### Step 3: 内部规划
思考本章结构、角色节拍、文风匹配、信息揭示节奏。不输出。

### Step 4: 撰写
读取 `references/prose-guide.md` 获取详细写作指南。写完整一章。用 Markdown 格式，`# Chapter {C}: {title}` 开头，场景断用 `---`。

### Step 5: 自审
读取 `references/review-checklist.md`。P0 自动修复（拼写、名字、时态），P1 修复并记录，P2 标记为「待作者决策」。

### Step 6: 更新文件
- `novel/chapters/chapter-{C}.md` — 写入正文
- `novel/summaries.md` — 追加完整摘要
- `novel/progress.md` — 更新统计（字数、日期、审阅笔记）
- `novel/context-brief.md` — 更新「写作状态」和章节目录状态列。**context-brief 是章节状态的唯一真源，progress 只存详细统计。**

### Step 7: 暂停等待反馈 ⚠️
展示一个简短摘要（约 150-200 字），然后问：

> **第 {C} 章完成。** 继续下一章，还是想调整什么？

- 用户说「继续」「接着写」「下一章」→ 回到 Step 0（写 C+1）
- 用户提修改意见 → 按意见调整或重写（不要动其他章节）
- 用户不回复 → 等待。**绝对不要自己决定继续。**

**上下文提醒：** 如果已完成章数是 5 的倍数（5、10、15...），在反馈中附加提醒：
> 已写 {N} 章。对话上下文已累积较多。建议下次开新对话，输入 /novel-write 即可从第 {N+1} 章继续——进度已保存在 context-brief.md 中。

---

## 全自动模式流程

触发：「全部写完」「all」「一口气」「自动」等。

循环执行 Step 1-6。每 5 章输出一次进度报告。发现 P2 矛盾**立即暂停**，描述问题询问用户。

完成后输出总结报告：章节列表、字数汇总、P0/P1/P2 统计。

---

## 审阅模式

触发：「review」「审阅」「检查上一章」。

读取最新非 planned 章节，运行 review-checklist.md 的完整检查。不写新内容，只输出检查结果和修改建议。
