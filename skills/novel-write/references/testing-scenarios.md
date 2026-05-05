# NovelFlow Skill Test Scenarios

Use these scenarios to test whether agents follow NovelFlow without overloading context. Run them with a fresh agent when possible.

## Success Criteria

- Agent reads `SKILL.md` first, then only the files required by the triggered mode.
- Agent starts from `novel/context-brief.md`, not chat memory.
- Agent does not load all chapters, all character profiles, or all worldbuilding by default.
- After drafting, agent updates chapter text, summaries, story-state, thread-ledger, progress, and context-brief.
- Agent pauses on P2 issues and does not run unlimited rewrite loops.

## Scenario 1: Continue Mid-Novel

Prompt:
> Continue the next chapter.

Expected:
- Reads `novel/context-brief.md`.
- Infers next chapter.
- Reads only C-1/C/C+1 outline rows, relevant state rows, relevant thread-ledger rows, compressed summaries, and previous chapter full text.
- Uses `scene-blueprint.md` only during planning.

## Scenario 2: Batch With Guardrails

Prompt:
> Write the next 5 chapters.

Expected:
- Reads `references/modes.md`.
- Reports chapter range before drafting.
- Runs normal Steps 1-6 per chapter.
- Pauses on P2, 3+ P1 in one chapter, two decay warnings, or milestone underdevelopment.

## Scenario 3: Full-Auto Refusal

Prompt:
> Write all remaining 60 chapters without asking.

Expected:
- Reads `references/modes.md`.
- Counts remaining chapters.
- Refuses full-auto because >30 remain.
- Suggests batch mode.

## Scenario 4: Review Existing Chapter

Prompt:
> Review chapter 12.

Expected:
- Reads `references/modes.md` and `references/review-checklist.md`.
- Reads chapter 12 in full, plus minimal continuity context.
- Does not edit without consent.
- Classifies findings as P0/P1/P2.

## Scenario 5: Ten-Chapter Checkpoint

Prompt:
> 十章检查。

Expected:
- Reads `references/modes.md` and `references/checkpoint-guide.md`.
- Uses summaries, progress, story-state, thread-ledger, outline milestone rows, and market-brief.
- Does not read every chapter file.
- Produces Fix now / Plan forward / Ask author actions.

## Scenario 6: Legacy Project Missing New Files

Prompt:
> Continue writing.

Setup:
- `story-state.md`, `thread-ledger.md`, or `market-brief.md` is missing.

Expected:
- Creates missing `story-state.md` and `thread-ledger.md` from context-brief, outline, and progress.
- Continues if `market-brief.md` is missing, using Market Snapshot if present.
- Marks uncertain facts as `unknown yet`.

## Scenario 7: Payoff Due

Prompt:
> Continue chapter where T03 payoff target is now.

Expected:
- Reads relevant T03 row only, not the whole ledger unless needed.
- Pays off, advances with a reason, or flags P2 if the payoff cannot happen.
- Updates thread-ledger status after drafting.
