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

For batch, full-auto, review, or checkpoint requests, read `skills/novel-write/references/modes.md` after the mode is detected.

## Project State Contract

Treat files under `novel/` as the source of truth:

| File | Role |
|------|------|
| `context-brief.md` | Entry point, compressed state, chapter status |
| `outline.md` | Chapter plan and milestone constraints |
| `market-brief.md` | Target reader, core promise, hook, and style contract |
| `characters.md` | Static character canon |
| `world.md` | Static world rules, optional |
| `story-state.md` | Dynamic continuity memory |
| `thread-ledger.md` | Foreshadowing and payoff ledger |
| `summaries.md` | Chapter summaries for pyramid compression |
| `progress.md` | Word counts, review notes, revision log |
| `chapters/` | Draft chapter files |

After writing a chapter, update:

1. `novel/chapters/chapter-{N}.md`
2. `novel/summaries.md`
3. `novel/story-state.md`
4. `novel/thread-ledger.md`
5. `novel/progress.md`
6. `novel/context-brief.md`

Do not mark a chapter complete until these files are updated.

## Progressive Loading Rules

- Read `references/compression-guide.md` only when assembling writing context.
- Read `references/modes.md` only after batch, full-auto, review, or checkpoint mode is triggered.
- Read `references/scene-blueprint.md` only when planning the current chapter.
- Read `references/prose-guide.md` only when drafting prose.
- Read `references/review-checklist.md` only when reviewing.
- Read `references/checkpoint-guide.md` only when running a checkpoint/global audit.
- Read `market-brief.md` as 2-4 bullets, not as a long strategy document.
- Read `characters.md` and `world.md` by relevant section, not whole-file by default.
- If `novel/story-state.md` is missing, create it from `context-brief.md`, `outline.md`, and `progress.md` before writing.
- If `novel/thread-ledger.md` is missing, create it from `outline.md` and `progress.md` before writing.

## Skill Testing

Use `skills/novel-write/references/testing-scenarios.md` to test fresh agents. Passing behavior means the agent reads only task-relevant files, updates all required state files, and pauses on P2 or automation guard failures.

## No File Tools

If the agent cannot read local files directly, generate a context pack first:

```bash
python scripts/build-context-pack.py --novel-dir novel --chapter auto --include-review --output context-pack.md
```

Then paste `context-pack.md` into the chat model.
