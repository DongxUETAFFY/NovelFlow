# NovelFlow Skill Test Scenarios

Use these scenarios to test whether agents follow NovelFlow without overloading context. Run them with a fresh agent when possible.

## Success Criteria

- Agent reads `SKILL.md` first, then only the files required by the triggered mode.
- Agent starts from `novel/context-brief.md`, not chat memory.
- Agent does not load all chapters, all character profiles, or all worldbuilding by default.
- Free Draft does not update project state. Standard/Production writes chapter text, creates `novel/state/deltas/chapter-{N}.json`, validates and commits it, then updates or syncs summaries, story-state, thread-ledger, progress, and context-brief.
- Agent pauses on P2 issues and does not run unlimited rewrite loops.

## Scenario 0: Free Draft Escape Hatch

Prompt:
> 试写下一章，不更新状态。

Expected:
- Reads only `context-brief.md`, current outline row, and previous chapter if useful.
- Does not run audit, full checklist, delta validation, commit, or checkpoint.
- Saves to `novel/drafts/chapter-{N}-free-draft.md` only if saving is requested.
- Clearly says no project state was updated.

## Scenario 0B: Fragment Continue

Prompt:
> 续写这段：她把钥匙攥进掌心，听见门后有人在笑。

Expected:
- Reads `references/fragment-continue.md`.
- Uses the user-provided fragment as local voice anchor.
- Does not run audit, full checklist, delta validation, commit, or checkpoint.
- Does not update canonical chapter text or project state.
- If saving is requested, saves to `novel/drafts/fragment-continue-{timestamp}.md` or `chapter-{N}-fragment-continue.md`.

## Scenario 1: Continue Mid-Novel

Prompt:
> Continue the next chapter.

Expected:
- Reads `novel/context-brief.md`.
- Infers next chapter.
- Uses Standard Writing by default.
- Reads light context: `context-brief.md`, current outline row, and previous chapter; uses generated context pack if already available.
- Creates `mode: "standard"` delta; quality metrics are optional soft notes.

## Scenario 2: Batch With Guardrails

Prompt:
> Write the next 5 chapters.

Expected:
- Reads `references/modes.md`.
- Reports chapter range before drafting.
- Runs normal Steps 1-7 per chapter.
- Runs chapter-delta validation and commit before starting the next chapter.
- Pauses on P2, failed delta validation/commit, 3+ P1 in one chapter, two decay warnings, or milestone underdevelopment.

## Scenario 3: Full-Auto Warning

Prompt:
> Write all remaining 60 chapters without asking.

Expected:
- Reads `references/modes.md`.
- Counts remaining chapters.
- Warns that full-auto quality is worse and state drift risk is higher.
- Strongly discourages full-auto because >30 remain, asks for explicit confirmation, and recommends batch mode.

## Scenario 3B: Finish Book Intake

Prompt:
> 这本书断了，帮我续写到完结。

Expected:
- Reads `references/modes.md`.
- Runs Finish Book Intake, not chapter drafting.
- Produces `# Finish Book Intake Report`.
- Produces or proposes `# Finish Book Roadmap`.
- Does not write formal chapter prose or update project state before user confirmation.

## Scenario 3C: Finish Book Run After Confirmation

Prompt:
> 路线图确认，按这个续到完结。

Expected:
- Uses Production Lock.
- Creates `mode: "production"` deltas for chapters.
- Runs validation and commit per chapter.
- Pauses on P2, unresolved payoff, failed validation, checkpoint drift, or roadmap conflict.

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
- Uses summaries, progress, story-state, thread-ledger, outline milestone rows, and reader-promise or legacy market-brief.
- Does not read every chapter file.
- Produces Fix now / Plan forward / Ask author actions.

## Scenario 6: Legacy Project Missing New Files

Prompt:
> Continue writing.

Setup:
- `story-state.md`, `thread-ledger.md`, `reader-promise.md`, or `market-brief.md` is missing.

Expected:
- Creates missing `story-state.md` and `thread-ledger.md` from context-brief, outline, and progress.
- Continues if reader-promise/market-brief is missing, using the context snapshot if present.
- Marks uncertain facts as `unknown yet`.

## Scenario 7: Payoff Due

Prompt:
> Continue chapter where T03 payoff target is now.

Expected:
- Reads relevant T03 row only, not the whole ledger unless needed.
- Pays off, advances with a reason, or flags P2 if the payoff cannot happen.
- Writes the thread action into the chapter delta with evidence from the chapter text.
- Updates thread-ledger status only after the delta validates and commits.

## Scenario 8: Edited Chapter After Commit

Prompt:
> Continue writing after I revised chapter 8.

Setup:
- Chapter 8 has a committed delta.
- `novel/chapters/chapter-8.md` is newer than `novel/state/deltas/chapter-8.json`.

Expected:
- Runs or recommends `python skills/novel-write/scripts/novelflow.py audit --novel-dir novel`.
- Detects that Chapter 8 is newer than its delta.
- Rebuilds and commits Chapter 8's delta before writing later chapters, or pauses if the edit changes P2-level continuity.

## Scenario 9: Invalid Thread Action

Prompt:
> Continue and mark T02 as "kind of mentioned".

Expected:
- Rejects unsupported thread action labels.
- Uses one of: `planned`, `planted`, `advanced`, `paid_off`, `delayed`, `reversed`, `closed`, or `retired`.
- Requires evidence for planted/advanced/paid_off/reversed/closed actions.

## Scenario 10: Overdue Thread

Prompt:
> Continue.

Setup:
- `T04` has `target_chapter: 12`.
- Chapter 12 is already committed.
- `T04` is still `planted` or `advanced`.

Expected:
- `audit` reports the overdue thread.
- Agent pauses, pays off the thread, delays it with a reason in the next delta, or asks the author.
- Agent does not continue full-auto silently.

## Scenario 11: Rebuild From Edited Chapter

Prompt:
> I revised chapter 6, continue from chapter 9.

Expected:
- Runs `audit`.
- If chapter 6 is newer than its delta, uses `rebuild --from-chapter 6` only if the existing delta still matches the revised chapter.
- If the edit changed plot/state, rewrites chapter 6's delta before rebuilding.
