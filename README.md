# NovelFlow

NovelFlow is a Claude Code Skill project for writing long-form fiction with AI without losing plot, character, and world continuity. It is designed around one constraint: **the full novel will never fit in the model context window**.

Instead of asking the model to "remember everything", NovelFlow turns a novel into a file-backed memory system. The model reads only the state it needs for the current task, writes one chapter or batch at a time, reviews the output, then updates the persistent memory files before continuing.

The project is packaged as Claude Code Skills, but the core design is plain Markdown plus file I/O. Any agent that can read and write files can implement the same workflow.

## Design Goals

| Goal | Design Response |
|------|-----------------|
| Prevent forgetting across 50-100 chapters | Store outline, character state, summaries, and continuity locks in files, not chat memory |
| Avoid context window overflow | Load skill references and project files progressively, only when needed |
| Keep prose style continuous | Include the previous chapter full text as a voice anchor |
| Preserve long-range plot memory | Use pyramid compression: near chapters detailed, distant chapters one-line |
| Stop late-novel quality decay | Run structural health checks from chapter 30 onward |
| Protect emotional milestones | Mark milestone chapters in the outline and force extra scene development |
| Support cross-session work | Resume from `novel/context-brief.md` and `novel/story-state.md` |

## Architecture Overview

NovelFlow has two Skills and one project workspace:

```text
skills/
  novel-setup/      # Turns raw ideas into structured project files
  novel-write/      # Writes, reviews, and updates chapters

novel/
  context-brief.md  # Compressed entry point and chapter status
  outline.md        # Full chapter plan with milestone markers
  characters.md     # Static character bible
  world.md          # Static world rules, optional
  story-state.md    # Dynamic long-form memory
  thread-ledger.md  # Foreshadowing and payoff ledger
  summaries.md      # Chapter summaries for pyramid compression
  progress.md       # Word counts, review notes, revision log
  chapters/         # Generated chapter files
```

The key design choice is separation between **static canon**, **dynamic state**, and **compressed history**.

| Layer | File | Purpose |
|-------|------|---------|
| Entry state | `context-brief.md` | Small file read first every session: premise, compressed character cards, progress, next chapter, state snapshot |
| Static plan | `outline.md` | Chapter-by-chapter plan, act structure, turning points, milestone column |
| Static canon | `characters.md`, `world.md` | Full character and world rules that should not be loaded unless relevant |
| Dynamic state | `story-state.md` | Current wants, hidden pressures, relationship temperature, open threads, continuity locks |
| Thread lifecycle | `thread-ledger.md` | Foreshadowing, mysteries, red herrings, promises, payoff target, payoff form, status |
| Compressed history | `summaries.md` | Full summaries that are compressed at read time by distance |
| Operational log | `progress.md` | Word counts, review notes, revision log, statistics |

## Why Two Skills

### `novel-setup`

`novel-setup` runs before drafting. It transforms vague ideas into a durable project structure.

Workflow:

1. Detect whether a `novel/` project already exists.
2. Capture only user-provided ideas. It must not invent core creative facts without confirmation.
3. Ask a batched discovery questionnaire covering genre, POV, protagonist, antagonist, plot, world, and scope.
4. Synthesize a working summary and wait for user confirmation.
5. Generate the project files from templates.
6. Validate chapter count, milestone values, character coverage, `context-brief.md` size, `story-state.md`, and `thread-ledger.md`.
7. Hand off to `novel-write`.

The setup Skill exists because long novels fail early if the model starts drafting before structure exists. The plan must become files before chapter generation begins.

### `novel-write`

`novel-write` runs during drafting and review. It never relies on chat history as the source of truth.

Modes:

| Mode | Trigger | Behavior |
|------|---------|----------|
| Interactive | `start`, `continue`, `next chapter` | Write one chapter, review, update files, pause |
| Batch | `batch 5`, `write 3 chapters` | Write N chapters, review each, pause after the batch |
| Full-auto | `write all`, `一口气写完` | Write all remaining chapters with safety gates |
| Review | `review chapter N` | Audit an existing chapter and offer fixes |

The default is interactive mode because author feedback is the strongest quality control loop.

## Progressive Loading Design

NovelFlow follows the Skill progressive disclosure pattern:

| Level | Loaded When | Content |
|-------|-------------|---------|
| L1 | Skill discovery | `name` and `description` only |
| L2 | Skill invoked | `SKILL.md` procedural workflow |
| L3 | Specific step | References such as compression guide, prose guide, review checklist, templates |
| Project entry | Every writing session | `novel/context-brief.md` |
| Project detail | Only if needed | Relevant rows/sections from outline, characters, world, story-state, summaries |

This prevents two common failures:

1. Loading every rule, template, and previous chapter into context before the model knows what task it is doing.
2. Hiding important rules in huge documents the model never reads.

`SKILL.md` files stay procedural. Detailed material lives in `references/` and templates. The agent reads them at the exact step where they matter.

## Chapter Context Assembly

When writing Chapter C, NovelFlow assembles context in a fixed order:

```text
1. Foundation
   - premise
   - genre / POV
   - compressed character cards

2. Dynamic state
   - current narrative pressure
   - relevant character state rows
   - active open threads
   - relationship shifts
   - continuity locks

3. Thread ledger
   - threads planted in C
   - threads due in C/C+1
   - high-risk forgotten threads
   - planned payoff form

4. Immediate outline context
   - chapter C-1 row
   - chapter C row
   - chapter C+1 row

5. Pyramid summaries
   - distant chapters: one sentence
   - mid-distance chapters: first 50-100 words
   - recent chapters: full summaries

6. Voice anchor
   - full text of chapter C-1

7. Current writing instruction
   - chapter title, target events, milestone constraints
```

This gives the model three kinds of memory:

| Memory Type | Mechanism |
|-------------|-----------|
| What the story is | `context-brief.md`, `outline.md` |
| What is currently unstable | `story-state.md` |
| What must pay off later | `thread-ledger.md` |
| What already happened | `summaries.md` + previous chapter full text |

## Pyramid Context Compression

Long-form fiction cannot keep every previous chapter in context. NovelFlow compresses previous chapters by distance from the current chapter.

Example when writing Chapter 20:

| Source | Included As | Reason |
|--------|-------------|--------|
| Chapter 19 | Full text | Voice, rhythm, immediate continuity |
| Chapters 17-18 | Full summaries | Recent plot continuity |
| Chapters 14-16 | First 100 words of summary | Important recent history |
| Chapters 10-13 | First 50 words of summary | Major beats |
| Chapters 1-9 | First sentence only | Long-range memory |

The first sentence of every chapter summary is load-bearing. When Chapter 3 is seventy chapters old, its first sentence may be all the model sees. For that reason, summaries must start with:

```text
named character + concrete event + directional consequence
```

Bad:

```text
The investigation continues and tensions rise.
```

Good:

```text
Kira identifies the mole as her own partner, forcing her to choose between the case and her cover.
```

For Chinese projects:

```text
林夜在审讯室折断嫌犯手臂，导致沈鸢确认他的失控已从异界蔓延到现实。
```

The repository includes `scripts/validate-summaries.sh` to check this heuristic for English and Chinese summaries.

## Dynamic State: `story-state.md`

`story-state.md` is the main addition that makes NovelFlow suitable for long novels rather than just long prompts.

It stores information that changes as chapters are drafted:

| Section | Purpose |
|---------|---------|
| Current Narrative Pressure | What unresolved pressure must shape the next chapter |
| Character State | Last seen, current want, hidden pressure, relationship temperature, arc position |
| Open Threads | Promises, mysteries, planted objects, relationship tensions, future payoffs |
| World Facts Established In Draft | Rules introduced in prose that constrain future scenes |
| Continuity Locks | Short facts that must never drift |
| Recent Relationship Shifts | Meaningful changes in trust, intimacy, hostility, distance |

This file prevents a subtle long-novel failure: the model may remember static character traits but forget where the character currently is emotionally. `characters.md` says who the character is. `story-state.md` says where the character is now.

After every chapter, `novel-write` updates `story-state.md` before updating `context-brief.md`. The `context-brief.md` state snapshot then carries only the 3-6 most important points into the next session.

## Foreshadowing Ledger: `thread-ledger.md`

`thread-ledger.md` is a dedicated lifecycle table for foreshadowing and payoff. It exists because open threads in `story-state.md` are not enough for mystery, horror, political, or long romance structures where planted details need explicit payoff timing.

Each significant thread gets a stable ID and a status:

```text
planned -> planted -> advanced -> paid-off
```

or, for false leads:

```text
planned -> planted -> closed-red-herring
```

The ledger tracks:

| Field | Purpose |
|-------|---------|
| ID | Stable reference like `T01` |
| Thread | What promise, mystery, object, or emotional setup exists |
| Type | mystery, object, relationship, prophecy, red-herring, consequence |
| Planted In | Chapter where it appears or should appear |
| Evidence In Text | Concrete prose evidence after drafting |
| Current State | What readers currently understand |
| Payoff Target | Intended chapter or range |
| Payoff Form | reveal, reversal, emotional-payoff, object-use, consequence, red-herring-close |
| Status | planned, planted, advanced, paid-off, closed-red-herring, dropped |

When writing a chapter, the agent reads only ledger rows that are planted in the current chapter, due now or next chapter, mentioned by the current outline row, or high-risk if forgotten. This keeps payoff tracking active without loading the entire ledger every time.

## Per-Chapter Write Loop

Interactive mode runs this loop:

```text
Step 0: Restore state from context-brief.md
Step 1: Assemble context from story-state, outline, summaries, previous chapter
Step 2: Detect milestone constraints
Step 3: Plan internally: scenes, character beats, state obligations, reveals
Step 4: Write the chapter
Step 5: Review with P0/P1/P2 severity
Step 6: Update chapter file, summaries, story-state, thread-ledger, progress, context-brief
Step 7: Pause for author feedback
```

The loop is intentionally stateful. A chapter is not complete when text is generated. It is complete only after the memory files are updated.

## Quality Gates

NovelFlow uses defense in depth instead of trusting one prompt instruction.

| Gate | What It Catches |
|------|-----------------|
| P0/P1/P2 review | Typos, minor drift, major contradictions |
| Milestone protection | Underwritten climax, death, reunion, revelation, act break |
| Structural health checks | Late-novel outline-ification, low scene density, weak sensory detail |
| Full-auto caps | Quality collapse from writing too many chapters in one session |
| Summary first-sentence rule | Distant memory becoming vague |
| `story-state.md` checks | Forgotten open threads, relationship drift, continuity lock violations |
| `thread-ledger.md` checks | Missed payoff, dropped red herrings, untracked planted clues |

Severity levels:

| Severity | Action |
|----------|--------|
| P0 | Fix immediately without asking |
| P1 | Fix and record in progress notes |
| P2 | Pause and ask the author |

## Full-Auto Safety

Full-auto mode is intentionally constrained.

| Condition | Action |
|-----------|--------|
| More than 30 chapters remaining | Refuse full-auto and suggest batch mode |
| 15-30 chapters remaining | Warn and ask for confirmation |
| Any P2 issue | Pause immediately |
| 3+ P1 issues in one chapter | Pause |
| 2 consecutive structural decay warnings | Pause |
| Milestone chapter shorter than average | Pause |

This is not a throughput tool. It is a controlled drafting system.

## Installation

```bash
git clone https://github.com/DongxUETAFFY/NovelFlow.git
mkdir -p ~/.claude/skills
cp -r NovelFlow/skills/* ~/.claude/skills/
```

Restart Claude Code.

## Scripts

```bash
scripts/sync-skills.sh --local
scripts/sync-skills.sh --check
scripts/validate-summaries.sh novel/summaries.md novel/characters.md
```

| Script | Purpose |
|--------|---------|
| `sync-skills.sh` | Sync tracked `skills/` into local `.claude/skills/` or installed `~/.claude/skills/` |
| `validate-summaries.sh` | Check whether chapter summary first sentences are strong enough for pyramid memory |

## Using With Other Agents

NovelFlow is not locked to Claude Code.

For Codex, Cursor, OpenCode, or any file-capable agent, use the repository entry file:

```text
AGENTS.md
```

That file explains which Skill to load, which project files are source of truth, and how to update state after each chapter.

For a custom agent:

1. Load the relevant `SKILL.md` as procedural instruction.
2. Start every writing session by reading `novel/context-brief.md`.
3. Read references only when the Skill says to.
4. Update `summaries.md`, `story-state.md`, `thread-ledger.md`, `progress.md`, and `context-brief.md` after every chapter.

For ChatGPT or Claude Chat without file tools, build a single context pack:

```bash
python scripts/build-context-pack.py --novel-dir novel --chapter auto --include-review --output context-pack.md
```

Then paste `context-pack.md` into the chat. The pack contains:

1. `context-brief.md`
2. relevant `story-state.md` sections
3. relevant `thread-ledger.md` rows
4. current outline row
5. previous chapter full text
6. pyramid-compressed summaries
7. review checklist if needed

## License

MIT

[中文文档](README_CN.md)
