# NovelFlow

An AI novel-writing framework that solves one core problem: **AI forgets earlier plot and character details when writing long novels due to context window limits.**

The solution: transform scattered ideas into structured outlines and character profiles first, then generate chapter by chapter. Each writing session injects the outline summary, compressed character cards, and pyramid-compressed prior-chapter summaries — keeping context overhead at ~9,000 tokens even for 100-chapter novels.

Packaged as Claude Code Skills, but the core is a Markdown-based workflow — **not locked to Claude Code**. Works with any AI tool that can read and write files.

## Problem & Solution

| Without NovelFlow | With NovelFlow |
|-------------------|----------------|
| 10,000 words in, the AI forgets the protagonist's name | Compressed character cards injected every chapter — core details always in context |
| Dialogue drags, later chapters feel phoned in | Pyramid-compressed summaries: recent chapters detailed, older ones condensed — context stays clean |
| Character voice drifts, plot contradictions pile up | Auto-review checks names, timeline, and world-building consistency every chapter |
| Outline exists only in memory — by chapter 20, it's gone | Outline and chapter status live in files, read fresh every session |

## Two-Step Workflow

**Step 1 — From scattered ideas to structured plan.** Say "I want to write a cyberpunk mystery where the protagonist has amnesia." The AI asks batched questions to clarify genre, POV, characters, world-building, and scope. Once confirmed, it generates a complete chapter outline, character profiles, and world bible.

**Step 2 — Segmented writing.** Based on the confirmed outline, the AI writes one chapter at a time. After each chapter, it self-reviews for name errors and setting violations, then pauses for your feedback. Say "continue" for the next chapter, "write all" to batch the rest, or give specific revision notes.

## Installation

```bash
git clone https://github.com/DongxUETAFFY/NovelFlow.git
mkdir -p ~/.claude/skills && cp -r NovelFlow/skills/* ~/.claude/skills/
```

Restart Claude Code.

---

## Skills

### `novel-setup` — From Fragments to Structured Plan

**Triggers when:** the user says "I want to write a novel," "help me plan a story," or shares a rough story idea.

**What it does:** Through one batched question session (not sequential interrogation), it structures your ideas into:

| Output File | Content |
|------------|---------|
| `novel/context-brief.md` | Compressed system prompt — premise + character card summaries + chapter status table. First file any agent reads |
| `novel/outline.md` | Complete chapter-by-chapter outline with three-act structure, key turning points, per-chapter plot beats |
| `novel/characters.md` | Character profiles — public persona (what readers see) vs hidden depths (slowly revealed subtext) |
| `novel/world.md` | World bible (generated for fantasy/sci-fi; skipped for realistic fiction) |
| `novel/progress.md` | Writing stats — word counts, dates, review notes, foreshadowing tracker |
| `novel/summaries.md` | Chapter summaries (initialized empty, filled by novel-write) |

**Flow:** User shares scattered ideas → AI asks batched questions (7 dimensions, all at once) → synthesizes structured outline → **waits for user confirmation** → generates files → asks "Want to start chapter 1?"

If an existing novel project is detected, it reads `context-brief.md` and asks: "Edit settings / Start new book / Continue writing."

---

### `novel-write` — Segmented Writing + Anti-Forgetting + Review

**Triggers when:** the user says "start writing," "continue," "next chapter," "write all," or "review."

**Three modes:**

| Mode | Trigger | Behavior |
|------|---------|----------|
| Interactive (default) | "start," "continue" | Write one chapter → show summary → **pause for feedback** → wait for user before next chapter |
| Full-auto | "write all," "batch" | Write all remaining chapters continuously, report progress every 5 chapters. Pause only on serious contradictions (P2) |
| Review | "review" | Read previous chapter, check names/timeline/world-building consistency, return revision suggestions |

**Per-chapter execution (Plan → Execute → Review):**

```
Step 0: Read context-brief.md to restore state (premise + character cards + current position)
Step 1: Assemble context using pyramid compression (details below)
Step 2: Internal plan — chapter structure, character beats, voice matching
Step 3: Write the complete chapter
Step 4: Self-review — P0 auto-fix (typos/names/tense), P1 fix & log, P2 flag for author
Step 5: Update files — chapter text + summary + progress + context-brief status
Step 6: Pause, show summary, wait for feedback
```

**Reminder at chapters 5/10/15:** "N chapters written. Conversation context is accumulating. Consider starting a new conversation from chapter N+1."

---

## Core Mechanism: Pyramid Context Compression

The fundamental challenge of long-form novel writing is that the full text won't fit in any model's context window. NovelFlow's approach:

```
Context structure when writing Chapter 20:

┌─────────────────────────────────┐
│ Foundation (injected every time, ~2,000t)    │
│ premise + character cards + current chapter outline  │  ← from context-brief.md
├─────────────────────────────────┤
│ Voice Anchor (~5,000t)          │
│ Chapter 19 full text            │  ← maintains prose continuity
├─────────────────────────────────┤
│ Pyramid Summaries                │
│ Ch 17-18: full summaries (~700t)│  ← near: detailed
│ Ch 14-16: first 100 words (~400t)│
│ Ch 10-13: first 50 words (~270t) │
│ Ch 1-9: one sentence each (~230t)│  ← far: condensed
├─────────────────────────────────┤
│ Total: ~8,900 tokens overhead   │  ← scales to 100+ chapters
└─────────────────────────────────┘
```

The pyramid ensures every chapter is represented — recent ones in detail, older ones as compressed anchors. This prevents the model from forgetting early plot threads while keeping context usage predictable.

---

## Full Workflow

```
User says "I want to write a novel"

    ↓ novel-setup starts
  Input scattered ideas (one sentence or a wall of text)
    ↓
  AI asks batched questions (7 dimensions, all at once)
    ↓
  User answers
    ↓
  AI synthesizes structured outline → shows to user
    ↓
  User says "looks good" → generates novel/ directory
    ↓
  AI asks "Start chapter 1?"
    ↓
  User says "start" → novel-write begins
    ↓
  ┌──────────────────────────────┐
  │  Write Chapter 1              │
  │  → Self-review                │
  │  → Update summaries + progress│
  │  → Show summary:              │
  │   "Chapter 1 done. Continue?" │
  └──────────────────────────────┘
    ↓
  User says "continue"
    ↓
  ┌──────────────────────────────┐
  │  Write Chapter 2              │
  │  Context: outline + Ch1 full  │
  │  text + character cards       │
  │  → Review → Update → Pause    │
  └──────────────────────────────┘
    ↓
  User says "write all"
    ↓
  ┌──────────────────────────────┐
  │  Write Chapters 3-80          │
  │  Progress report every 5 ch   │
  │  Pause on P2 contradictions   │
  │  Final summary report         │
  └──────────────────────────────┘
```

---

## Progressive Loading (Context Protection)

| Level | When Loaded | Content | Size |
|-------|-------------|---------|------|
| L1 | Session start | Skill name + description | ~50 words |
| L2 | Skill invoked | SKILL.md body | ~80-180 lines |
| L3 | During execution | References (question templates, compression algorithm, writing guide, review checklist) | On demand |
| Project entry | First read per session | `novel/context-brief.md` | ~100 lines |

---

## Cross-Session Resume

No dependency on Claude Code Memory or any platform mechanism. All state lives in files:

- `novel/context-brief.md` — chapter status table (planned / draft / reviewed) for all chapters
- `novel/summaries.md` — per-chapter summaries
- `novel/progress.md` — word counts, dates, review notes

On next session, the AI reads `context-brief.md` and says: "Welcome back. 12 chapters completed. Next is Chapter 13. Continue or adjust?"

---

## Using With Other Platforms

NovelFlow's core is not code — it's a Markdown workflow + instruction files. Not locked to Claude Code.

- **Cursor / Codex / OpenCode** — supports the agentskills.io standard; drop `skills/` into the corresponding directory
- **Custom agents** — inject `SKILL.md` as system prompt, tell the agent to start by reading `novel/context-brief.md`. Feed reference files on demand
- **ChatGPT / Claude Chat** — manually paste `context-brief.md` + previous chapter full text + current chapter outline, say "write this chapter." Paste the review checklist for self-review
- **Other reasoning models** — the entire workflow is Markdown instructions + file I/O, no model-specific features required

---

## Uninstall

```bash
rm -rf ~/.claude/skills/novel-setup ~/.claude/skills/novel-write
```

---

## License

MIT

---

[中文文档](README_CN.md)
