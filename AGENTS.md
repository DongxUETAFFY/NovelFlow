# NovelFlow Agent Entry

Use this file when an agent environment does not auto-discover Claude Code Skills but can read and write repository files.

## Trigger Routing

Use `skills/novel-setup/SKILL.md` when the user wants to:
- start a novel
- plan a story
- create character profiles
- build a fictional world
- turn scattered story ideas into a structured project

Use `skills/novel-write/SKILL.md` when the user wants to:
- free-draft or try a chapter without updating project state
- continue a user-provided fragment
- continue a provided fragment as official canon
- resume or finish an abandoned/incomplete book
- write or continue a chapter
- write the next chapter
- batch-write chapters
- write all remaining chapters
- review or revise an existing chapter
- run a 10-chapter checkpoint or global consistency audit

## Required First Read

For writing or review tasks, read:

1. `skills/novel-write/SKILL.md`
2. `novel/context-brief.md`

Then follow the Skill instructions exactly. Do not read every project file up front.

For batch, full-auto, review, checkpoint, or finish-book requests, read `skills/novel-write/references/modes.md` after the mode is detected.

Default writing mode is **Standard Writing**. Use **Free Draft** when the user says "free draft", "试写", "不更新状态", or "跳过记账". Use **Fragment Continue** when the user provides a partial scene and asks "续写这段" / "continue from here" without canon language. Use **Canon Continue** when the user says "按全书设定续写", "从这里接入正文继续", "作为正式章节继续", or "从这段开始继续全书". Use **Finish Book Intake** before finish-book requests when state/direction is unclear; use **Finish Book Run** after roadmap confirmation, or after a direct-to-ending request when project state is complete enough. Use **Production Lock** for batch, full-auto, checkpoint-sensitive work, Finish Book Run, or strict/stable mode.

## Project State Contract

Treat files under `novel/` as the source of truth:

| File | Role |
|------|------|
| `context-brief.md` | Entry point, compressed state, chapter status |
| `outline.md` | Chapter plan and milestone constraints |
| `reader-promise.md` | Target reader, core promise, hook, and style contract |
| `market-brief.md` | Legacy reader-promise file; use only when `reader-promise.md` is missing |
| `characters.md` | Static character canon |
| `world.md` | Static world rules, optional |
| `story-state.md` | Dynamic continuity memory |
| `thread-ledger.md` | Foreshadowing and payoff ledger |
| `summaries.md` | Chapter summaries for pyramid compression |
| `progress.md` | Word counts, review notes, revision log |
| `chapters/` | Draft chapter files |
| `state/deltas/` | Chapter delta JSON files for Standard/Production modes |
| `state/chapter-index.json` | Committed chapter index |
| `generated/` | Rebuildable summaries, progress, story-state, thread-ledger, cards, context packs |

After writing a Free Draft:

- Save only to `novel/drafts/chapter-{N}-free-draft.md` if saving is requested.
- Do not update project state.
- Clearly tell the user no project state was updated.

After a Fragment Continue:

- Return continuation text only by default.
- Save only to `novel/drafts/fragment-continue-{timestamp}.md` or `novel/drafts/chapter-{N}-fragment-continue.md` if saving is requested.
- Do not update project state or canonical chapter text unless the user explicitly promotes it into a chapter.

After a Canon Continue:

- Locate the target chapter; if unclear, ask whether the fragment belongs to chapter N or the next planned chapter.
- Read relevant dynamic state rows selected by the fragment: character rows, relationship shifts, open threads, due/high-risk thread-ledger rows, and touched world rules.
- Write or merge into `novel/chapters/chapter-{N}.md`.
- Create and commit a `mode: "standard"` delta unless the user requested Production Lock or an ending run.
- Update generated state and sync legacy exports when expected.

For Finish Book:

- Intake first when state or direction is unclear: produce intake report and roadmap; do not write formal chapter prose or update state.
- If the user explicitly says to follow the existing outline directly to the ending and the project state is complete, warn about full-auto quality risk, then run Production Lock.
- Run after confirmation: use Production Lock with full deltas and checkpoint/stop conditions.

After writing a Standard or Production chapter:

1. `novel/chapters/chapter-{N}.md`
2. `novel/state/deltas/chapter-{N}.json`
3. Validate and commit with `skills/novel-write/scripts/novelflow.py`
4. Use `novel/generated/*` as the primary rebuildable state
5. Sync legacy `summaries.md`, `story-state.md`, `thread-ledger.md`, `progress.md`, and `context-brief.md` only when the project expects them

Do not mark a Standard or Production chapter complete until its delta is committed.

## Progressive Loading Rules

- Read `references/compression-guide.md` only when assembling writing context.
- Read `references/modes.md` only after batch, full-auto, finish-book, review, or checkpoint mode is triggered.
- Read `references/scene-blueprint.md` only when planning the current chapter.
- Read `references/prose-guide.md` only when drafting prose.
- Read `references/review-checklist.md` only when reviewing.
- Read `references/checkpoint-guide.md` only when running a checkpoint/global audit.
- Read `reader-promise.md` as 2-4 bullets. If missing, read legacy `market-brief.md` as reader promise, not as a market strategy document.
- Read `characters.md` and `world.md` by relevant section, not whole-file by default.
- If `novel/story-state.md` is missing, create it from `context-brief.md`, `outline.md`, and `progress.md` before writing.
- If `novel/thread-ledger.md` is missing, create it from `outline.md` and `progress.md` before writing.

## Skill Testing

Use `skills/novel-write/references/testing-scenarios.md` to test fresh agents. Passing behavior means the agent respects Free Draft / Standard Writing / Production Lock boundaries, reads only task-relevant files, commits deltas when required, and pauses on P2 or automation guard failures.

## No File Tools

If the agent cannot read local files directly, generate a context pack first:

```bash
python scripts/build-context-pack.py --novel-dir novel --chapter auto --mode standard --include-review --output context-pack.md
```

Use `--mode canon-continue` when the pasted context must treat a provided fragment as official chapter prose.

Then paste `context-pack.md` into the chat model.
