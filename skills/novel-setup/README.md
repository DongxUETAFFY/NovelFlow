# novel-setup

从零散的小说想法出发，通过对话梳理出结构化大纲、人物设定和世界观。

## 安装

复制整个 `novel-setup/` 目录到 `~/.claude/skills/`：

```bash
cp -r novel-setup ~/.claude/skills/
```

无需重启，下一个对话即可使用。

## 使用

```
/novel-setup
```

然后输入你的故事想法——可以是一句话、一个场景、一个角色、一种氛围。AI 会通过结构化提问帮你把模糊的想法变成：

- 章节大纲（含三幕结构、关键转折点）
- 人物设定（外显人格 + 隐藏深度 + 人物弧线）
- 世界观设定（可选，奇幻/科幻需要时生成）

最终在当前目录创建 `novel/` 目录存放所有产出文件。

## 产出

```
novel/
├── outline.md       # 章节大纲
├── characters.md    # 人物设定
├── world.md         # 世界观（可选）
├── progress.md      # 写作进度追踪
├── summaries.md     # 章节摘要（由 novel-write 填充）
└── chapters/        # 章节正文（由 novel-write 填充）
```

## 依赖

- 无外部依赖
- 产物被 `novel-write` 消费

## 渐进式加载

| 层级 | 内容 | 何时加载 |
|------|------|---------|
| L1 元数据 | name + description | 会话启动时 |
| L2 指令 | SKILL.md 全文 | 调用 /novel-setup 时 |
| L3 模板 | references/templates/* | 生成文件时 |
