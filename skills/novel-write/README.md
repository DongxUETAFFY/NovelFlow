# novel-write

读取 novel-setup 产出的大纲和人设，分段撰写小说章节。支持三种模式：单章、批量（3-5章）、全自动（全部剩余章节）。

## 安装

复制整个 `novel-write/` 目录到 `~/.claude/skills/`：

```bash
cp -r novel-write ~/.claude/skills/
```

## 使用

| 命令 | 行为 |
|------|------|
| `/novel-write` | 写下一章 |
| `/novel-write batch 3` | 连续写 3 章 |
| `/novel-write all` | 写完全部剩余章节 |
| `/novel-write chapter 5` | 写/重写第 5 章 |
| `/novel-write review` | 审阅上一章 |

## 工作原理

每章执行 Plan → Execute → Review 流程：

1. **Plan** — 读取大纲+人设+金字塔压缩的前文摘要，规划本章结构
2. **Execute** — 撰写完整章节（匹配上一章文风）
3. **Review** — 自动审稿：P0 自动修复（拼写/名字/时态），P2 标记给作者

### 金字塔上下文压缩

| 距离 | 压缩方式 | 用途 |
|------|---------|------|
| 上一章 | 全文 | 保持文风一致性 |
| 前 2-3 章 | 完整摘要 (~300字) | 近期剧情连续性 |
| 前 4-6 章 | 前 100 字摘要 | 上下文记忆 |
| 前 7-10 章 | 前 50 字摘要 | 关键事件提醒 |
| 更早 | 一句话概括 | 全局脉络 |

100 章规模下上下文开销仅 ~9000 tokens。

## 依赖

- 需要先运行 `/novel-setup` 创建 `novel/` 目录
- `novel-write/references/` 内含压缩算法和审稿清单文档，按需读取（L3 加载）

## 渐进式加载

| 层级 | 内容 | 何时加载 |
|------|------|---------|
| L1 元数据 | name + description | 会话启动时 |
| L2 指令 | SKILL.md (297行) | 调用 /novel-write 时 |
| L3 引用 | references/compression-guide.md | 执行上下文组装时 |
| L3 引用 | references/review-checklist.md | 执行审稿时 |
