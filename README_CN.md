# NovelFlow

NovelFlow 是一个面向 AI 长篇小说写作的 Skill 项目，核心目标是解决一个问题：**长篇小说不可能完整塞进模型上下文，模型迟早会忘大纲、人设、伏笔、关系变化和世界规则。**

NovelFlow 不要求模型“凭记忆写完整本书”，而是把小说拆成一套文件化记忆系统。模型每次只读取当前任务需要的状态，写一章或一批章节，审阅输出，然后把新的状态写回文件，再继续。

它目前以 Claude Code Skills 形式打包，但核心不是 Claude 专属能力，而是一套 Markdown 工作流 + 文件读写协议。任何能读写文件的 agent 都可以复用这个设计。

## 设计目标

| 目标 | 对应设计 |
|------|----------|
| 防止 50-100 章后遗忘设定 | 大纲、人设、动态状态、摘要、禁忘项全部写入文件 |
| 防止上下文爆炸 | Skill 与项目文件都采用渐进式加载，只读当前步骤需要的内容 |
| 保持文风连续 | 写第 C 章时注入第 C-1 章全文作为 Voice Anchor |
| 保留长线剧情记忆 | 前文摘要按距离金字塔压缩，近详远略 |
| 防止后期水文和提纲化 | 第 30 章后启用结构健康检查 |
| 保护高潮、死亡、重逢、揭示等情绪节点 | outline 中标记 Milestone，写作时强制给更多场景和篇幅 |
| 支持跨会话恢复 | 每次从 `context-brief.md` 和 `story-state.md` 恢复 |

## 总体架构

NovelFlow 由两个 Skill 和一个小说工作区组成：

```text
skills/
  novel-setup/      # 把零散想法整理成结构化小说项目
  novel-write/      # 分章写作、审阅、更新状态

novel/
  context-brief.md  # 压缩入口文件 + 章节状态
  outline.md        # 完整章节大纲 + Milestone 标记
  characters.md     # 静态人物设定
  world.md          # 静态世界规则，可选
  story-state.md    # 动态长篇记忆
  thread-ledger.md  # 伏笔与回收账本
  summaries.md      # 章节摘要，用于金字塔压缩
  progress.md       # 字数、审阅笔记、修订记录
  chapters/         # 生成的章节正文
```

关键思想是把记忆分层：**静态设定、动态状态、压缩历史** 分开存放。

| 层级 | 文件 | 用途 |
|------|------|------|
| 入口状态 | `context-brief.md` | 每次会话第一个读的小文件：故事 premise、压缩角色卡、进度、下一章、状态快照 |
| 静态计划 | `outline.md` | 三幕结构、每章目标、关键转折点、Milestone 列 |
| 静态正典 | `characters.md`, `world.md` | 完整人物设定和世界规则，只在需要时读相关段落 |
| 动态状态 | `story-state.md` | 当前欲望、隐藏压力、关系温度、未回收线索、世界事实、禁忘项 |
| 伏笔生命周期 | `thread-ledger.md` | 伏笔、悬念、伪线索、承诺、回收目标、回收形式、状态 |
| 压缩历史 | `summaries.md` | 每章完整摘要，读取时按距离压缩 |
| 操作日志 | `progress.md` | 字数、日期、审阅笔记、修订记录 |

## 为什么拆成两个 Skill

### `novel-setup`

`novel-setup` 负责开书前的结构化工作。它不直接写正文，而是把模糊想法变成可长期维护的项目文件。

流程：

1. 检测当前目录是否已有 `novel/` 项目。
2. 只吸收用户明确给出的创意，不擅自编造核心设定。
3. 一次性批量提问：类型、视角、主角、反派、主线、世界观、篇幅。
4. 整理工作摘要，等待用户确认。
5. 根据模板生成项目文件。
6. 校验章节数、Milestone、人物覆盖、`context-brief.md` 长度、`story-state.md` 和 `thread-ledger.md` 结构。
7. 交给 `novel-write` 开始写作。

这个 Skill 存在的原因很明确：长篇失败往往不是写到一半才失败，而是一开始没有结构化状态。正文开始前，计划必须落到文件里。

### `novel-write`

`novel-write` 负责真正写作和审阅。它不把聊天记录当真源，所有状态都从 `novel/` 文件恢复。

模式：

| 模式 | 触发 | 行为 |
|------|------|------|
| 交互模式 | `开始`, `继续`, `下一章` | 写一章、审阅、更新文件、暂停等反馈 |
| 批量模式 | `batch 5`, `写 3 章` | 连续写 N 章，每章审阅，批次结束暂停 |
| 全自动模式 | `全部写完`, `一口气写完` | 带安全门的一次性草稿生成 |
| 审阅模式 | `审阅第 N 章` | 审计已有章节并给出修复选项 |

默认推荐交互模式，因为作者反馈是最强的质量控制。

## 渐进式加载设计

NovelFlow 遵循 Skill 的渐进加载思想：

| 层级 | 何时加载 | 内容 |
|------|----------|------|
| L1 | Skill 发现阶段 | 只加载 `name` 和 `description` |
| L2 | Skill 被调用时 | 加载 `SKILL.md` 的流程说明 |
| L3 | 执行具体步骤时 | 按需读取 compression guide、prose guide、review checklist、templates |
| 项目入口 | 每次写作开始 | 读取 `novel/context-brief.md` |
| 项目细节 | 当前章节需要时 | 读取 outline、characters、world、story-state、summaries 的相关部分 |

这样避免两个问题：

1. 一开始就把所有规则、模板、前文章节塞进上下文。
2. 把关键规则藏在超长文档里，导致模型根本不读。

`SKILL.md` 只保留流程骨架；详细规则放在 `references/`；模板放在 `references/templates/`。

## 每章上下文如何组装

写第 C 章时，NovelFlow 按固定顺序组装上下文：

```text
1. Foundation
   - premise
   - 类型 / 视角
   - 压缩角色卡

2. Dynamic State
   - 当前叙事压力
   - 本章相关人物状态
   - 活跃未回收线索
   - 关系变化
   - 禁止遗忘事项

3. Thread Ledger
   - 本章要种下的伏笔
   - 本章/下一章到期的伏笔
   - 高风险遗忘线索
   - 计划回收形式

4. Immediate Outline Context
   - 第 C-1 章大纲行
   - 第 C 章大纲行
   - 第 C+1 章大纲行

5. Pyramid Summaries
   - 很远的章节：一句话
   - 中距离章节：摘要前 50-100 字
   - 近章节：完整摘要

6. Voice Anchor
   - 第 C-1 章全文

7. Current Writing Instruction
   - 本章标题、目标事件、Milestone 约束
```

这给模型三类记忆：

| 记忆类型 | 机制 |
|----------|------|
| 这个故事是什么 | `context-brief.md`, `outline.md` |
| 现在什么最不稳定 | `story-state.md` |
| 以后必须回收什么 | `thread-ledger.md` |
| 之前发生过什么 | `summaries.md` + 上一章全文 |

## 金字塔上下文压缩

长篇不能把所有前文都放进上下文，所以 NovelFlow 按章节距离压缩。

写第 20 章时：

| 来源 | 放入方式 | 原因 |
|------|----------|------|
| 第 19 章 | 全文 | 保持文风、节奏、直接连续性 |
| 第 17-18 章 | 完整摘要 | 近期剧情连续 |
| 第 14-16 章 | 摘要前 100 字 | 重要近史 |
| 第 10-13 章 | 摘要前 50 字 | 主要事件 |
| 第 1-9 章 | 每章一句话 | 长线记忆 |

每章摘要的第一句非常重要。第 3 章距离当前 70 章以后，模型可能只看到它的第一句话。所以摘要第一句必须包含：

```text
命名角色 + 具体事件 + 方向性后果
```

差：

```text
调查继续推进，局势变得紧张。
```

好：

```text
林夜在审讯室折断嫌犯手臂，导致沈鸢确认他的失控已从异界蔓延到现实。
```

仓库里提供 `scripts/validate-summaries.sh`，可检查中英文摘要第一句是否足够承重。

## 动态状态层：`story-state.md`

`story-state.md` 是让 NovelFlow 真正适合长篇，而不是只适合长提示词的关键文件。

它记录写作过程中会变化的东西：

| 区块 | 用途 |
|------|------|
| Current Narrative Pressure | 下一章必须承接的叙事压力 |
| Character State | 人物最后出现位置、当前欲望、隐藏压力、关系温度、弧线位置 |
| Open Threads | 未回收线索、承诺、谜题、物件、关系张力、未来 payoff |
| World Facts Established In Draft | 正文里已经写出来、会约束未来的世界事实 |
| Continuity Locks | 绝不能漂移的短事实 |
| Recent Relationship Shifts | 信任、亲密、敌意、距离等有意义变化 |

`characters.md` 说明“这个人是谁”；`story-state.md` 说明“这个人现在走到哪了”。长篇里后者经常比前者更容易被模型忘掉。

每章写完后，`novel-write` 会先更新 `story-state.md`，再把其中最关键的 3-6 条压缩进 `context-brief.md` 的 state snapshot。

## 伏笔账本：`thread-ledger.md`

`thread-ledger.md` 是专门管理伏笔和回收的生命周期表。只靠 `story-state.md` 的 Open Threads 不够支撑悬疑、恐怖、权谋、长篇感情线，因为这些类型需要明确知道：什么时候种下、什么时候推进、什么时候反转、什么时候回收。

每条重要线索都有稳定 ID 和状态：

```text
planned -> planted -> advanced -> paid-off
```

伪线索则可以这样关闭：

```text
planned -> planted -> closed-red-herring
```

账本记录：

| 字段 | 用途 |
|------|------|
| ID | 稳定编号，如 `T01` |
| Thread | 具体伏笔、谜题、物件、情感承诺 |
| Type | mystery, object, relationship, prophecy, red-herring, consequence |
| Planted In | 种下章节 |
| Evidence In Text | 正文里的证据 |
| Current State | 读者当前理解 |
| Payoff Target | 计划回收章节或范围 |
| Payoff Form | reveal, reversal, emotional-payoff, object-use, consequence, red-herring-close |
| Status | planned, planted, advanced, paid-off, closed-red-herring, dropped |

写每章时，agent 只读取“本章要种下、当前/下一章到期、当前大纲行提到、或者遗忘风险高”的账本行，不会每次全量塞进上下文。

## 每章写作闭环

交互模式执行这个循环：

```text
Step 0: 从 context-brief.md 恢复状态
Step 1: 读取 story-state、outline、summaries、上一章全文
Step 2: 检测 Milestone 约束
Step 3: 内部规划：场景、人物节拍、状态义务、信息揭示
Step 4: 写完整章节
Step 5: 按 P0/P1/P2 审阅
Step 6: 更新章节正文、summaries、story-state、thread-ledger、progress、context-brief
Step 7: 暂停等待作者反馈
```

注意：一章不是“正文生成完”就完成。只有记忆文件也更新完，这章才算完成。

## 质量防线

NovelFlow 不依赖单一句“请保持一致”。它用多层防线。

| 防线 | 解决什么 |
|------|----------|
| P0/P1/P2 审阅 | 错字、小漂移、重大矛盾 |
| Milestone protection | 高潮、死亡、重逢、揭示写得太短 |
| Structural health checks | 后期提纲化、场景密度下降、感官细节变少 |
| Full-auto caps | 一次写太多章导致质量塌陷 |
| Summary first-sentence rule | 远期记忆变成“气氛紧张”这种废摘要 |
| `story-state.md` 检查 | 忘掉未回收线索、关系漂移、禁忘项冲突 |
| `thread-ledger.md` 检查 | 伏笔未回收、伪线索未关闭、正文种下线索但账本未记录 |

严重级别：

| 级别 | 行为 |
|------|------|
| P0 | 不问用户，直接修 |
| P1 | 修复并记录 |
| P2 | 暂停，交给作者决策 |

## 全自动模式为什么受限

全自动模式不是无限生成器，而是有安全门的草稿模式。

| 条件 | 行为 |
|------|------|
| 剩余超过 30 章 | 拒绝全自动，建议批量模式 |
| 剩余 15-30 章 | 警告并等待确认 |
| 出现任何 P2 | 立即暂停 |
| 单章 3 个以上 P1 | 暂停 |
| 连续两章结构衰减 | 暂停 |
| Milestone 章节短于平均值 | 暂停 |

这个项目追求的是可控长篇写作，不是最大吞吐量。

## 安装

```bash
git clone https://github.com/DongxUETAFFY/NovelFlow.git
mkdir -p ~/.claude/skills
cp -r NovelFlow/skills/* ~/.claude/skills/
```

重启 Claude Code。

## 脚本

```bash
scripts/sync-skills.sh --local
scripts/sync-skills.sh --check
scripts/validate-summaries.sh novel/summaries.md novel/characters.md
```

| 脚本 | 用途 |
|------|------|
| `sync-skills.sh` | 把已跟踪的 `skills/` 同步到本地 `.claude/skills/` 或安装目录 `~/.claude/skills/` |
| `validate-summaries.sh` | 检查章节摘要第一句是否能支撑金字塔记忆 |

## 在其他 Agent 中使用

NovelFlow 不绑定 Claude Code。

对 Codex、Cursor、OpenCode 这类有文件读写能力的 agent，直接使用仓库入口文件：

```text
AGENTS.md
```

它会告诉 agent 什么时候加载哪个 Skill、哪些 `novel/` 文件是真源、每章写完后要更新哪些状态文件。

自建 agent 可以这样用：

1. 把相关 `SKILL.md` 作为流程指令加载。
2. 每次写作先读 `novel/context-brief.md`。
3. 只有 Skill 要求时才读取 references。
4. 每章写完后更新 `summaries.md`、`story-state.md`、`thread-ledger.md`、`progress.md`、`context-brief.md`。

如果是在 ChatGPT / Claude Chat 这种没有文件工具的环境，先生成单次上下文包：

```bash
python scripts/build-context-pack.py --novel-dir novel --chapter auto --include-review --output context-pack.md
```

然后把 `context-pack.md` 粘进聊天窗口。这个包里包含：

1. `context-brief.md`
2. `story-state.md` 相关部分
3. `thread-ledger.md` 相关行
4. 当前章 outline 行
5. 上一章全文
6. 金字塔压缩后的前文摘要
7. 需要时粘入审阅清单

## License

MIT
