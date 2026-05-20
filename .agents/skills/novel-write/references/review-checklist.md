# Chapter Review Checklist

- [1. Character Consistency](#1-character-consistency)
- [2. Plot Consistency](#2-plot-consistency)
- [3. World-Building Consistency](#3-world-building-consistency)
- [4. Voice & Prose Consistency](#4-voice--prose-consistency)
- [5. Structural Health (Anti-Decay)](#5-structural-health-anti-decay)
- [6. Technical Quality](#6-technical-quality)
- [7. Metadata](#7-metadata)
- [Issue Severity Classification](#issue-severity-classification)
- [Review Flow](#review-flow)

Run fully in Production Lock. In Standard Writing, use it lightly: fix P0 issues, flag P2 issues, and turn P1 craft concerns into `soft_notes` unless they affect a hard rule.

Revision boundary: apply P0 fixes and one focused P1 pass. Do not keep rewriting until the chapter feels perfect; unresolved creative or structural questions become P2 and require the author.

## 1. Character Consistency

- [ ] All named characters spelled consistently with `novel/characters.md`
- [ ] Each character's dialogue matches their established voice and mannerisms
- [ ] Character actions align with their traits (or show deliberate, motivated deviation)
- [ ] Character arc position is correct — are they where they should be at this point?
- [ ] Character state matches `novel/story-state.md` (current want, hidden pressure, relationship temperature, arc position)
- [ ] New characters introduced? They need entries in summaries for later setup integration
- [ ] **Side character arcs**: Are side characters' emotional beats getting adequate scene time? (Not resolving too fast, not disappearing for long stretches)

## 2. Plot Consistency

- [ ] Chapter fulfills its outline entry — all key events from the outline are covered
- [ ] No contradiction with events from any previous chapter (cross-check Tier 2 summaries)
- [ ] Timeline: does this chapter's time/date follow logically from chapter C-1's ending?
- [ ] Cause and effect: does this chapter follow logically from where C-1 left off?
- [ ] Foreshadowing: any new threads planted? Existing threads advanced? Check progress.md tracker.
- [ ] Open threads in `novel/story-state.md` are preserved, advanced, paid off, or intentionally left dormant. No thread is contradicted.
- [ ] `novel/thread-ledger.md` updated for any planted, advanced, paid-off, reversed, or closed thread
- [ ] Threads with Payoff Target at or before this chapter are paid off, advanced with a reason, or flagged P2

## 3. World-Building Consistency

- [ ] Location descriptions match `novel/world.md` (skip if world.md doesn't exist)
- [ ] Rules of magic/technology are followed — no accidental rule-breaking for convenience
- [ ] Cultural/social details are consistent with established world norms
- [ ] New world facts introduced in this chapter are added to `novel/story-state.md` if they constrain future scenes
- [ ] Seasonal/temporal details align with the story timeline

## 4. Voice & Prose Consistency

- [ ] Prose style matches the established voice (compare opening paragraphs with chapter C-1)
- [ ] POV character's internal voice is consistent (word choice, observation style, what they notice)
- [ ] Tense is consistent throughout (no accidental shifts between past and present)
- [ ] Pacing: right balance of action, dialogue, introspection, and description for this story's rhythm
- [ ] **Style drift check**: Compare sensory detail density with a chapter from the novel's first third. If the current chapter is noticeably more abstract/conceptual and less sensory/physical, flag as P1.
- [ ] **Scene density check**: Does this chapter contain at least one fully-developed scene (specific place + physical experience + real-time + character interaction)? If the chapter is primarily event-listing or summary, flag as P1.
- [ ] **Reader promise**: Does this chapter preserve the target-reader promise, hook, and prose contract in `novel/reader-promise.md`, legacy `novel/market-brief.md`, or the context snapshot?

## 5. Structural Health (Anti-Decay)

Run these checks for every chapter; they become **mandatory and elevated** from chapter 30 onward.

- [ ] **Scene count**: How many fully-developed scenes in this chapter? Compare to the average from the novel's first 10 chapters. If scene count has dropped by more than 40%, flag as P1.
- [ ] **Dialogue ratio**: Estimate the ratio of rendered dialogue to reported/summarized speech. If this chapter reports more dialogue than it renders (especially for emotional beats), flag as P1.
- [ ] **Sensory benchmark**: Count distinct sensory details in the first 500 words. If fewer than 3 distinct senses are engaged, flag as P1.
- [ ] **Chapter length trend**: Compare word count to the 5-chapter rolling average. A single short chapter is fine. Two consecutive chapters below 70% of the rolling average is a P1 decay signal. Three consecutive is P2.
- [ ] **Milestone chapter protection**: If this chapter contains a key emotional node (darkest moment, climax, major reunion, major death, final confrontation), it must NOT be shorter than the novel's average chapter length. If it is, flag as P2 — these moments need more space, not less.

## 6. Technical Quality

- [ ] No duplicated or repeated paragraphs
- [ ] No placeholder text (lorem ipsum, "TODO", "[insert scene]", "TKTK")
- [ ] Chapter ends with a hook or natural break — not mid-sentence or mid-scene (unless intentional cliffhanger)
- [ ] **Chapter opening**: Does the first paragraph establish immediate presence (body, place, action)? Flag if it opens with weather, waking up, recap, or rhetorical question
- [ ] **Chapter closing**: Does the ending create an obligation to continue? Flag if it uses the same closing strategy as the previous chapter
- [ ] Proper paragraph breaks and scene transitions
- [ ] Dialog tags are varied and appropriate (not every line needs "he said")

## 7. Metadata

- [ ] Chapter title matches the outline entry
- [ ] Chapter number in header matches the filename
- [ ] Word count recorded for progress.md update
- [ ] `novel/state/deltas/chapter-{N}.json` exists, validates, and commits before long-term memory files are updated
- [ ] `story-state.md` updated for character state, open threads, world facts, continuity locks, and relationship shifts
- [ ] `thread-ledger.md` updated for foreshadowing/payoff status changes

---

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
- Minor market/style drift that can be corrected locally without changing plot direction
- Missing `story-state.md` update for a minor character/thread/world change
- Missing `thread-ledger.md` update for a minor planted or advanced thread
- Missing, invalid, or uncommitted chapter delta when the chapter otherwise has no P2 issue
- Weak chapter ending (doesn't hook to next chapter effectively)
- **Scene density warning**: Chapter trending toward event-listing rather than full scenes
- **Style drift warning**: Sensory detail density noticeably lower than first-third baseline
- **Dialogue ratio warning**: Key emotional beats reported rather than rendered as live dialogue
- **Chapter length decay**: Below 70% of 5-chapter rolling average
- **Side character arc compression**: Side character emotional beat resolved in summary rather than scene

### P2 — Flag for User (do NOT change, report only)
- Major character inconsistency (character acts fundamentally against their established nature without setup)
- Plot contradiction with a previous chapter that can't be resolved by minor edits
- World rule violation (magic/technology does something the world bible says is impossible)
- Contradiction with `story-state.md` continuity locks or an active unresolved thread
- Missed payoff for a thread whose target chapter has arrived, unless the author intentionally delayed it
- Timeline impossibility (events couldn't physically happen in the time between chapters)
- Thematic departure (chapter's tone or message contradicts the novel's established tone)
- Character arc derailment (character makes a choice that breaks their arc trajectory)
- **Milestone chapter underdevelopment**: Key emotional node (climax, reunion, death, darkest moment) is shorter or less developed than average chapters
- **Sustained decay**: Three or more consecutive chapters with P1 structural health flags
- **Genre/style contract break**: Major shift in narrative mode (e.g., from sensory-driven fiction to abstract/conceptual discourse) that would alienate existing readers
- **Reader promise break**: Chapter abandons the core promise or hook defined in `reader-promise.md`, legacy `market-brief.md`, or the context snapshot in a way that would require a direction decision

---

## Review Flow

1. Read the generated chapter in full.
2. Run through each checklist section, marking items pass/fail.
3. Apply all P0 fixes directly to the chapter file.
4. Apply one focused P1 revision pass and add a note in progress.md's Review Notes column.
5. Compile P2 issues into the return report with specific suggestions.
6. Create or update `novel/state/deltas/chapter-{N}.json` so it matches the final chapter text.
7. Run chapter-delta validation and commit before updating memory files.
8. Update `story-state.md` after fixes so dynamic continuity matches the final chapter text.
9. Update `thread-ledger.md` after fixes so planted/advanced/paid-off/closed statuses match the final chapter text.
10. Never silently "fix" a P2 issue — these require the author's creative judgment.
11. **From chapter 30 onward**: Pay extra attention to Section 5 (Structural Health). The natural tendency is decay — actively guard against it.
12. Stop after one P1 pass. If another broad rewrite is needed, classify the remaining issue as P2.
