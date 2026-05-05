# Novel Write Modes

- [Batch Mode](#batch-mode)
- [Full-Auto Mode](#full-auto-mode)
- [Review Mode](#review-mode)
- [Checkpoint Mode](#checkpoint-mode)

Read this only after the requested mode is not normal Interactive writing.

## Batch Mode

Triggered by: "batch N", "write N chapters", "一口气写N章", "批量N章".

### Pre-flight

Report:
> Writing chapters {C} through {C+N-1} ({N} chapters, {remaining_after} remaining after). I'll pause after chapter {C+N-1} for your feedback.

Then proceed.

### Execution

Loop novel-write Steps 1-6 for N chapters. Report after each chapter:
> Ch{N} 「{title}」 · {word_count}字 · P0:{n} P1:{n} P2:{n}

Pause after chapter C+N-1:
> **{N} chapters complete** ({C}-{C+N-1}). Continue with the next batch, or want to adjust anything?

### Batch Constraints

- **P2 issue**: pause immediately.
- **Single-chapter quality flood**: 3+ P1 issues in one chapter -> pause.
- **Decay guard**: 2 consecutive chapters with P1 structural warnings -> pause.
- **Milestone chapters**: enforce milestone protection rules.

## Full-Auto Mode

Triggered by: "write all", "all", "一口气写完", "全部写完", "don't ask, just write", "别问我了".

### Step A: Pre-Flight Check

Before writing a single chapter:

1. Count remaining planned chapters.
2. Apply:

| Condition | Action |
|-----------|--------|
| >30 chapters remaining | Refuse full-auto and suggest batch mode. |
| 15-30 chapters remaining | Warn and ask for confirmation or switch to batch mode. |
| <15 chapters remaining | Acknowledge and proceed with guards. |

Wait for confirmation when warning is required. If the user already insisted and remaining chapters are <=30, proceed.

### Step B: Execution

Loop novel-write Steps 1-6 for each remaining chapter. Report:
> Ch{N} 「{title}」 · {word_count}字 · P0:{n} P1:{n} P2:{n} · [{chapter_number}/{total_remaining}]

### Full-Auto Guards

Pause immediately on:
- Any P2 issue.
- 3+ P1 issues in one chapter.
- 2 consecutive chapters with P1 structural health warnings.
- Milestone chapter shorter or less developed than the novel average.

Enforce every chapter:
- At least one fully-developed scene.
- At least 3 distinct senses in the first 500 words.
- Emotional beats rendered as live dialogue/action, not reported speech.

### Completion Report

Output chapter list with word counts, total word count, P0/P1/P2 summary, structural health trend, and recommended chapters to review before publication.

## Review Mode

Triggered by: "review", "审阅", "check the last chapter", "review chapter N".

### Step R0: Identify Target

- If no chapter number, target the most recent non-`planned` chapter.
- If a chapter number is given, target that chapter.
- If the target chapter does not exist, report and stop.

Confirm: "Reviewing Chapter {N}: {title}."

### Step R1: Assemble Review Context

Read the target chapter in full. Then read only:
- the chapter outline row
- chapter N-1 as Voice Anchor
- relevant `characters.md` entries
- relevant `world.md` sections if world rules matter
- `progress.md` review notes and stats
- relevant `story-state.md` rows
- relevant `thread-ledger.md` rows
- `market-brief.md` target reader, core promise, hook, and style contract

### Step R2: Run Review

Read `references/review-checklist.md`. Run all sections and classify findings:

```markdown
## Review: Chapter {N} — {title}

### P0 Issues
- ...

### P1 Issues
- [issue]: [evidence] -> [suggested fix]

### P2 Issues
- [issue]: [evidence] -> [author decision needed]

### Structural Health
- Scene density:
- Dialogue ratio:
- Sensory benchmark:
- Length trend:
```

### Step R3: Offer Action

Ask:
> **Review complete.** Apply P0 fixes automatically and P1 fixes for review? Or would you prefer to handle everything yourself?
> - "apply all" / 「全修」
> - "apply P0 only" / 「只修P0」
> - "I'll handle it" / 「我自己来」

Do not apply fixes without consent. When applying fixes, update the chapter file and progress.md Revision Log.

## Checkpoint Mode

Triggered by: "checkpoint", "10-chapter check", "十章检查", "全书检查", "阶段检查".

Use after every 10 chapters or before long batch/full-auto continuation. This is diagnostic, not rewriting.

### Step C0: Assemble Checkpoint Context

Read only:
- `novel/context-brief.md`
- `novel/story-state.md`
- `novel/thread-ledger.md` rows due, overdue, high-risk, or recently changed
- `novel/progress.md` statistics and review notes
- `novel/outline.md` milestone rows plus last 10 and next 10 chapter rows
- `novel/summaries.md` first sentences for distant chapters and full summaries for the last 3 chapters
- `novel/market-brief.md` target reader, core promise, hook, and style contract

Do not read every chapter file. Only read a chapter file if a concrete contradiction cannot be evaluated from summaries.

### Step C1: Run Checkpoint

Read `references/checkpoint-guide.md` and output the report.

### Step C2: Action Boundary

Do not rewrite chapters automatically. Produce:
- **Fix now**: safe metadata or memory-file corrections
- **Plan forward**: issues better handled in upcoming chapters
- **Ask author**: creative decisions or major direction changes
