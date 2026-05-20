# NovelFlow Mode Simplification Plan

## Goal

Make NovelFlow feel like a writing assistant first and a production control system only when the author asks for it. Keep the reliability work, but move it behind an explicit mode boundary.

## Three Modes

| Mode | Use When | Reads | Writes | Validation |
|---|---|---|---|---|
| Free Draft | Trying a scene, voice, alternate version, or "just write" without project bookkeeping | `context-brief.md`, current outline row, previous chapter | Optional scratch draft only | None unless the author asks |
| Standard Writing | Normal one-chapter continuation | Focused context plus previous chapter | Chapter + light delta + generated progress/summary | Light validation only |
| Production Lock | Long-haul stable drafting, batch/full-auto, checkpoint-sensitive work | Generated context pack + audit + relevant state | Full delta + index + generated state files | Full validation, audit, checkpoint guards |

## Hard Rules

Hard rules are project-safety constraints. They apply to Standard Writing and Production Lock; Free Draft should still respect them in prose but does not need bookkeeping.

- Do not contradict core character facts, irreversible events, or world rules already established.
- Do not drop a promised thread whose payoff is due; pay it off, delay it with a reason, or ask the author.
- Do not mark project state complete without a chapter delta in Standard Writing or Production Lock.
- Do not continue batch/full-auto through P2 continuity problems.

## Soft Suggestions

Soft suggestions are quality nudges, not red lines. Use them to revise when helpful; do not let them choke the draft.

- Three senses in the first 500 words.
- Dialogue ratio.
- Chapter length relative to average.
- Hook density and closing strategy.
- Scene count beyond the minimum needed by the chapter.

## Experience Changes

1. Write first, then bookkeeping.
   - Draft prose should not carry the full schema in mind.
   - Generate delta after the chapter exists.

2. Rename `market-brief.md` in language.
   - Treat it as `reader-promise.md` when available.
   - If only `market-brief.md` exists, read it as reader promise, not sales strategy.

3. Make `chapter-delta + chapter-index + generated/` the primary route.
   - Legacy Markdown files are compatibility exports or sync targets.

4. Add a clear escape hatch.
   - Trigger phrases: "free draft", "试写", "不更新状态", "跳过记账".
   - Output should clearly say no project state was updated.

## Implementation

- Add `mode` to chapter delta: `free-draft`, `standard`, or `production`.
- Add light validation for Standard Writing:
  - required summary
  - required review object
  - required thread actions only when threads are present
  - no required sensory metrics
- Keep full validation for Production Lock:
  - current strict metrics, evidence, audit, commit, generated files
- Free Draft:
  - no delta required
  - no commit
  - no audit unless author asks
  - do not overwrite canonical chapter unless author explicitly says to save it
