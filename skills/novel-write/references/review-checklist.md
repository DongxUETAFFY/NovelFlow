# Chapter Review Checklist

Run after each chapter generation. Fix P0 issues inline. Fix P1 issues and note them. Flag P2 issues for the user.

## 1. Character Consistency

- [ ] All named characters spelled consistently with `novel/characters.md`
- [ ] Each character's dialogue matches their established voice and mannerisms
- [ ] Character actions align with their traits (or show deliberate, motivated deviation)
- [ ] Character arc position is correct — are they where they should be at this point?
- [ ] New characters introduced? They need entries in summaries for later setup integration

## 2. Plot Consistency

- [ ] Chapter fulfills its outline entry — all key events from the outline are covered
- [ ] No contradiction with events from any previous chapter (cross-check Tier 2 summaries)
- [ ] Timeline: does this chapter's time/date follow logically from chapter C-1's ending?
- [ ] Cause and effect: does this chapter follow logically from where C-1 left off?
- [ ] Foreshadowing: any new threads planted? Existing threads advanced? Check progress.md tracker.

## 3. World-Building Consistency

- [ ] Location descriptions match `novel/world.md` (skip if world.md doesn't exist)
- [ ] Rules of magic/technology are followed — no accidental rule-breaking for convenience
- [ ] Cultural/social details are consistent with established world norms
- [ ] Seasonal/temporal details align with the story timeline

## 4. Voice & Prose Consistency

- [ ] Prose style matches the established voice (compare opening paragraph with chapter C-1)
- [ ] POV character's internal voice is consistent (word choice, observation style, what they notice)
- [ ] Tense is consistent throughout (no accidental shifts between past and present)
- [ ] Pacing: right balance of action, dialogue, introspection, and description for this story's rhythm

## 5. Technical Quality

- [ ] No duplicated or repeated paragraphs
- [ ] No placeholder text (lorem ipsum, "TODO", "[insert scene]", "TKTK")
- [ ] Chapter ends with a hook or natural break — not mid-sentence or mid-scene (unless intentional cliffhanger)
- [ ] Proper paragraph breaks and scene transitions
- [ ] Dialog tags are varied and appropriate (not every line needs "he said")

## 6. Metadata

- [ ] Chapter title matches the outline entry
- [ ] Chapter number in header matches the filename
- [ ] Word count recorded for progress.md update

## Issue Severity Classification

### P0 — Auto-Fix (fix immediately without asking)
- Spelling errors and typos
- Character name misspellings vs. characters.md
- Tense inconsistencies (accidental shifts)
- Duplicated or repeated paragraphs
- Placeholder text or TODO markers
- Chapter number/header format errors

### P1 — Fix and Note (fix now, document in progress.md)
- Minor character voice drift (dialogue doesn't quite match established patterns)
- Missing or incomplete outline beat (key event from outline not addressed)
- Pacing issues (scene feels rushed or drags)
- Minor world detail inconsistency (e.g., color of a described object)
- Weak chapter ending (doesn't hook to next chapter effectively)

### P2 — Flag for User (do NOT change, report only)
- Major character inconsistency (character acts fundamentally against their established nature without setup)
- Plot contradiction with a previous chapter that can't be resolved by minor edits
- World rule violation (magic/technology does something the world bible says is impossible)
- Timeline impossibility (events couldn't physically happen in the time between chapters)
- Thematic departure (chapter's tone or message contradicts the novel's established tone)
- Character arc derailment (character makes a choice that breaks their arc trajectory)

## Review Flow

1. Read the generated chapter in full.
2. Run through each checklist section, marking items pass/fail.
3. Apply all P0 fixes directly to the chapter file.
4. Apply P1 fixes and add a note in progress.md's Review Notes column.
5. Compile P2 issues into the return report with specific suggestions.
6. Never silently "fix" a P2 issue — these require the author's creative judgment.
