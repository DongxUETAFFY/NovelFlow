# Novel Writing Skills

AI 长篇小说写作助手。即插即用，两句话装好。

## 安装

```bash
# 1. 克隆
git clone https://github.com/xxx/novel-writing-skills

# 2. 安装（一行）
mkdir -p ~/.claude/skills && cp -r novel-writing-skills/skills/* ~/.claude/skills/
```

重启 Claude Code 或开新对话即可。

## 使用

```
我想写小说             → AI 通过对话帮你梳理大纲和人设
开始写                 → 写第一章，写完暂停等你验收
继续                   → 写下一章
全部写完               → 全自动模式
review                 → 审阅上一章
```

## 两个 Skill

| Skill | 做什么 |
|-------|--------|
| `novel-setup` | 零散想法 → 结构化大纲 + 人物设定 + 世界观 |
| `novel-write` | 读取设定 → 分段撰写 → 自动审稿 → 等你验收 |

## 怎么工作的

```
设定阶段：输入想法 → 提问澄清 → 确认大纲 → 生成 novel/ 目录

写作阶段（默认交互模式）：
  写一章 → 展示摘要 → 等你反馈
  → "继续"    写下一章
  → "调整一下" 重写本章
  → 第 5/10/15 章时提醒可开新对话防止上下文过长

全自动模式：
  一口气写完 → 每 5 章汇报 → 严重矛盾暂停问
```

跨会话恢复：下次回来，AI 读 `novel/context-brief.md` 就知道写到哪了。

## 卸载

```bash
rm -rf ~/.claude/skills/novel-setup ~/.claude/skills/novel-write
```

## License

MIT
