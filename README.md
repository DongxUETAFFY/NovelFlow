# NovelFlow

NovelFlow 是一套面向长篇小说写作的 Codex / Claude Code Skill。它的目标不是让模型“记住整本书”，而是把小说拆成可读取、可验证、可重建的项目文件，让 AI 在有限上下文里也能稳定推进长篇创作。

它适合这些场景：

- 从零搭建一本长篇小说的设定、人物、大纲和项目文件。
- 按章节续写，并持续维护人物状态、伏笔、摘要和进度。
- 试写片段、自由草稿，暂时不进入正式项目记账。
- 批量写作、全自动推进，或用更严格的生产锁定模式保障长篇稳定性。
- 接手一本已经中断的旧书，先做诊断和续写路线图，再继续写到完结。

## 核心思路

长篇小说最大的难点不是“写一章”，而是几十章之后仍然不忘：

- 谁知道了什么。
- 哪些伏笔还没回收。
- 人物关系现在处在什么温度。
- 情绪和节奏是否还在升级。
- 当前章节该服务哪一个长期承诺。

NovelFlow 用文件系统承担长期记忆，用 Skill 工作流约束 AI 的读取、写作、审查和更新过程。

## 项目结构

```text
skills/
  novel-setup/      # 从想法生成小说项目
  novel-write/      # 写作、续写、审查、checkpoint

novel/
  context-brief.md  # 每次写作优先读取的压缩入口
  outline.md        # 章节大纲、结构节点、里程碑
  reader-promise.md # 读者承诺、类型钩子、文风契约
  market-brief.md   # 旧名称，兼容为 reader-promise
  characters.md     # 静态人物设定
  world.md          # 静态世界观规则，可选
  story-state.md    # 动态剧情状态
  thread-ledger.md  # 伏笔、谜团、回收账本
  summaries.md      # 章节摘要，用于金字塔压缩
  progress.md       # 字数、审查、修订记录
  chapters/         # 正文章节
  state/
    deltas/         # 每章结构化 delta
    chapter-index.json
  generated/        # 可重建的派生状态和上下文包
```

## 两个 Skill

### novel-setup

用于开新书。它会从零散想法开始，帮助作者确认类型、主角、冲突、世界观、篇幅和章节结构，然后生成 `novel/` 项目文件。

它的原则是：核心创意必须来自作者，不让 AI 擅自替作者确定不可逆的主设定。

### novel-write

用于正式写作、续写、片段试写、审查和长篇维护。它默认不依赖聊天历史，而是从 `novel/context-brief.md` 和相关项目文件恢复状态。

## 写作模式

| 模式 | 适用触发 | 行为 |
|------|----------|------|
| 自由草稿 | `free draft`、`试写`、`不更新状态` | 只写草稿，不更新项目状态 |
| 片段续写 | `续写这段`、`接着这段写`、`continue this fragment` | 接着用户给出的片段写，不自动并入正文 |
| 标准写作 | `继续`、`下一章`、`写第 N 章` | 写一章，生成轻量 delta，更新必要状态 |
| 生产锁定 | `production lock`、`严格模式` | 完整 delta、审查、状态重建和硬性校验 |
| 批量写作 | `batch 5`、`连续写 3 章` | 默认使用生产锁定 |
| 全自动 | `write all`、`一口气写完` | 会先提醒质量风险，再按安全门推进 |
| 断书接诊 | `续写到完结`、`这本书断了，帮我续完` | 先诊断旧书，输出续写路线图，不直接开写 |
| 完结续写 | 作者确认路线图后 | 用生产锁定从当前进度写到结尾 |
| 审查 | `review chapter N`、`审阅第 N 章` | 审查已有章节并给出修改建议 |
| Checkpoint | `十章检查`、`checkpoint` | 全局一致性、节奏、伏笔和回收健康检查 |

默认模式是 **标准写作**。它比早期版本轻，不会让作者每次都背着大量表格写作；但仍然保留必要的项目状态更新。

## 三档约束

NovelFlow 现在把“创作自由”和“长篇稳定性”拆成三档：

1. **自由草稿**
   只读最少上下文，优先写得顺。不跑完整审查，不更新项目状态。

2. **标准写作**
   正常写作入口。先写章节，再整理 delta 和状态更新。审查输出保持简洁，只拦截硬错误。

3. **生产锁定**
   用于批量、全自动、长篇后期、断书续写到完结。完整校验 delta、伏笔账本、checkpoint 和派生状态。

硬规则包括：不能改写核心人设事实、不能丢已承诺伏笔、正式章节不能跳过状态更新。

软建议包括：感官密度、对白比例、章节长度、hook 密度、场景数量。这些会作为写作建议，不会每次都当作红线。

## 片段续写

片段续写是创作模式，不是项目推进模式。

当用户提供一段正文并说“续写这段”时，agent 会：

- 把用户片段当作局部文风和情绪锚点。
- 只读取必要上下文。
- 直接续写正文。
- 不更新 `chapter-delta`、`story-state`、`thread-ledger`、`context-brief`。
- 不把结果自动标记为正式章节。

如果作者明确说“并入正文”或“保存到第 N 章”，才会切换到标准写作流程。

## 断书续写到完结

“续写到完结”不是简单的 `continue`。NovelFlow 会分两步：

1. **Finish Book Intake / 断书接诊**
   读取现有项目状态，整理当前剧情、人物状态、文风、开放伏笔、风险点和可行续写方向，输出路线图。

2. **Finish Book Run / 完结续写**
   只有作者确认路线图后才开始。该模式固定使用生产锁定，逐章写作、审查、提交 delta，并在关键节点 checkpoint。

这样做是为了避免旧书被 AI 直接接管后方向漂移。

## 上下文装配

写第 C 章时，NovelFlow 会按距离装配上下文：

| 来源 | 装配方式 | 目的 |
|------|----------|------|
| 第 C-1 章 | 全文 | 文风、语气、即时连续性 |
| 最近 2 章 | 完整摘要 | 近期剧情连续性 |
| 中距离章节 | 摘要前 50-100 字 | 保留关键事件 |
| 远距离章节 | 一句话摘要 | 长期记忆 |
| 当前大纲行 | 完整读取 | 明确本章目标 |
| 动态状态 | 相关条目 | 人物、关系、伏笔、世界规则 |

远章摘要的第一句话非常重要，必须包含：

```text
具名人物 + 具体事件 + 对后续造成的方向性后果
```

## 文件状态与 delta

正式章节写完后，NovelFlow 会生成或更新：

- `novel/chapters/chapter-{N}.md`
- `novel/state/deltas/chapter-{N}.json`
- `novel/state/chapter-index.json`
- `novel/generated/` 下的派生状态
- legacy Markdown 状态文件，用于兼容旧工作流

长期方向是让 `chapter-delta`、`chapter-index` 和 `generated/` 成为主路线，legacy Markdown 文件作为兼容层或导出层。

## 无文件工具场景

如果 agent 不能直接读取本地文件，可以先生成上下文包：

```bash
python scripts/build-context-pack.py --novel-dir novel --chapter auto --mode standard --include-review --output context-pack.md
```

支持的 `--mode` 包括：

- `free-draft`
- `fragment-continue`
- `standard`
- `production`
- `finish-book-intake`
- `finish-book-run`

然后把 `context-pack.md` 粘贴给模型。

## 安装与使用

把 `skills/` 目录放到支持 Skills 的 agent 环境中即可。对于不能自动发现 Skills、但能读仓库文件的 agent，可以从 [AGENTS.md](AGENTS.md) 开始读取路由说明。

推荐入口：

```text
skills/novel-setup/SKILL.md
skills/novel-write/SKILL.md
```

## 测试

运行写作 skill 的脚本测试：

```bash
python -B -m unittest discover -s skills/novel-write/scripts -p "test_*.py"
```

用于人工评估的场景在：

```text
skills/novel-write/references/testing-scenarios.md
```

## 设计取舍

NovelFlow 不是要把作者变成流程管理员。它的目标是：

- 平时写作尽量轻。
- 想试写时可以跳过记账。
- 真正进入长篇稳定推进时，有足够硬的结构保护。
- 让 AI 先写得像小说，再把必要状态整理成可复用的项目记忆。

也就是说，它既保留“写作的手感”，也给长篇连载留下能走远的轨道。
