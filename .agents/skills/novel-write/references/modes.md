# Novel Write Modes

- [Batch Mode](#batch-mode)
- [Full-Auto Mode](#full-auto-mode)
- [Finish Book Intake](#finish-book-intake)
- [Finish Book Run](#finish-book-run)
- [Review Mode](#review-mode)
- [Checkpoint Mode](#checkpoint-mode)

Read this only after the requested mode is not normal Standard Writing.

## Batch Mode

Triggered by: "batch N", "write N chapters", "一口气写N章", "批量N章".

### Pre-flight

Report:
> Writing chapters {C} through {C+N-1} ({N} chapters, {remaining_after} remaining after). I'll pause after chapter {C+N-1} for your feedback.

Then proceed.

### Execution

Use Production Lock unless the user explicitly asks for lighter drafting. Loop novel-write Steps 1-7 for N chapters. Each chapter must pass chapter-delta validation and `commit-delta` before the next chapter starts. Report after each chapter:
> Ch{N} 「{title}」 · {word_count}字 · P0:{n} P1:{n} P2:{n}

Pause after chapter C+N-1:
> **{N} chapters complete** ({C}-{C+N-1}). Continue with the next batch, or want to adjust anything?

### Batch Constraints

- **P2 issue**: pause immediately.
- **Delta validation or commit failure**: fix and rerun once; if still failing, pause.
- **Overdue thread audit**: pay off, delay with a reason, or ask the author before continuing.
- **Single-chapter quality flood**: 3+ P1 issues in one chapter -> pause in Production Lock; report as soft notes in Standard Writing.
- **Decay guard**: 2 consecutive chapters with P1 structural warnings -> pause in Production Lock; report as soft notes in Standard Writing.
- **Milestone chapters**: enforce milestone protection rules in Production Lock; in Standard Writing, warn if underdeveloped.

## Full-Auto Mode

Triggered by: "write all", "all", "一口气写完", "全部写完", "don't ask, just write", "别问我了".

### Step A: Pre-Flight Check

Before writing a single chapter:

1. Count remaining planned chapters.
2. Warn the user before proceeding:

> Full-auto is available, but quality is usually worse than supervised batches: pacing can flatten, dialogue can become templated, side-character arcs can compress, and state drift is more likely. I will continue only with validation gates, and I will stop on P2, failed delta validation, repeated structural decay, or milestone underdevelopment.

3. Apply:

| Condition | Action |
|-----------|--------|
| >30 chapters remaining | Strongly discourage full-auto, explain quality risk, and ask for explicit confirmation. Recommend batch mode. |
| 15-30 chapters remaining | Warn and ask for explicit confirmation or switch to batch mode. |
| <15 chapters remaining | Warn and proceed if the user has clearly requested full-auto. |

Wait for confirmation unless the user's latest message already explicitly accepts lower quality/risk ("yes full-auto", "I accept the risk", "别问继续全自动"). Full-auto remains allowed, but never silent.

### Step B: Execution

Loop novel-write Steps 1-7 for each remaining chapter. Each chapter must pass chapter-delta validation and `commit-delta` before the next chapter starts. Report:
> Ch{N} 「{title}」 · {word_count}字 · P0:{n} P1:{n} P2:{n} · [{chapter_number}/{total_remaining}]

### Full-Auto Guards

Pause immediately on:
- Any P2 issue.
- Any chapter-delta validation or commit failure that cannot be fixed in one local pass.
- Any overdue thread audit that cannot be paid off or explicitly delayed in the next chapter.
- 3+ P1 issues in one chapter.
- 2 consecutive chapters with P1 structural health warnings.
- Milestone chapter shorter or less developed than the novel average.

Hard guards every chapter:
- No P2 continuity issue.
- A committed `novel/state/deltas/chapter-{N}.json` with evidence-backed thread actions.

Soft quality targets:
- At least one fully-developed scene.
- At least 3 distinct senses in the first 500 words.
- Emotional beats rendered as live dialogue/action, not reported speech.

### Completion Report

Output chapter list with word counts, total word count, P0/P1/P2 summary, structural health trend, and recommended chapters to review before publication.

## Finish Book Intake

Triggered by: "finish book intake", "resume abandoned book", "续写到完结", "这本书断了，帮我续完", "从现在写到完结", "接着这本书一直写到结局".

This is diagnostic. Do not write formal chapter prose and do not update chapter state.

### Reading Strategy

Prefer existing structure:
- `novel/context-brief.md`
- `novel/generated/summaries.md` or `novel/summaries.md`
- `novel/generated/story-state.md` or `novel/story-state.md`
- `novel/generated/thread-ledger.md` or `novel/thread-ledger.md`
- `novel/outline.md`
- `novel/reader-promise.md` or legacy `novel/market-brief.md`
- latest chapter full text as voice anchor

If summaries/deltas/generated state are missing, read existing chapters in batches and summarize before reasoning. Never load all chapters at once.

### Intake Report

Output:

```markdown
# Finish Book Intake Report

## Current Story State
- where the story stopped
- main conflict pressure
- current chapter / stopping point

## Character State
- major character goals
- relationship state
- unfinished arcs

## Style Profile
- POV and narrative distance
- sentence rhythm
- scene density
- dialogue / interiority / description balance
- prose traits to preserve

## Open Threads
- unresolved foreshadowing
- mysteries
- promised emotional or plot payoffs
- high-risk omissions

## Continuity Locks
- facts that must not change
- irreversible events

## Possible Continuation Directions
- Direction A
- Direction B
- Direction C, optional

## Recommended Finish Strategy
- recommended direction
- estimated remaining chapters
- major phases
- questions requiring author confirmation
```

### Roadmap Gate

After the intake report, produce a `# Finish Book Roadmap` with assumptions, remaining arc, chapter range, must-pay threads, character end states, and stop conditions.

Do not enter Finish Book Run until the author confirms the roadmap. Allowed before confirmation: intake report, roadmap, and optional trial fragment. Not allowed: formal next chapter, batch/full-auto, or state updates.

## Finish Book Run

Entry conditions:
- Finish Book Intake report exists.
- Finish Book Roadmap exists.
- Author explicitly confirmed the roadmap.

Execution is always Production Lock.

Per chapter:
1. Assemble context.
2. Write chapter.
3. Run full review checklist.
4. Create `mode: "production"` chapter delta.
5. Validate delta.
6. Commit delta.
7. Update generated state.
8. Sync legacy exports if needed.
9. Continue unless a stop condition triggers.

Checkpoint policy:
- Every 5 chapters: output a lightweight progress report.
- Every 10 chapters: run checkpoint.
- Near the ending: check unresolved threads before climax/resolution chapters.

Stop and ask author on:
- P2 continuity problem.
- Important thread cannot be naturally paid off.
- Roadmap conflicts with hard facts.
- Delta validation fails twice.
- Chapter text is newer than committed delta and cannot be safely rebuilt.
- 2 consecutive structural decay warnings.
- Milestone chapter underdeveloped.

Completion report:

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
- chapters most needing polish
- pacing issues
- style drift risks
```

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
- `reader-promise.md` or legacy `market-brief.md` target reader, core promise, hook, and style contract

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
- `novel/reader-promise.md` or legacy `novel/market-brief.md` target reader, core promise, hook, and style contract

Do not read every chapter file. Only read a chapter file if a concrete contradiction cannot be evaluated from summaries.

### Step C1: Run Checkpoint

Read `references/checkpoint-guide.md` and output the report.

### Step C2: Action Boundary

Do not rewrite chapters automatically. Produce:
- **Fix now**: safe metadata or memory-file corrections
- **Plan forward**: issues better handled in upcoming chapters
- **Ask author**: creative decisions or major direction changes
