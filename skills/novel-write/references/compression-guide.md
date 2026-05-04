# Pyramid Context Compression Guide

- [Purpose](#purpose)
- [The Five Tiers](#the-five-tiers)
- [Foundation Block (Always Included)](#foundation-block-always-included)
- [Voice Anchor (Chapter C-1 Full Text)](#voice-anchor-chapter-c-1-full-text)
- [Tier Compression Algorithm](#tier-compression-algorithm)
- [Context Assembly Order](#context-assembly-order)
- [Importance Overrides (Judgment Calls)](#importance-overrides-judgment-calls)
- [Edge Cases](#edge-cases)
- [Token Budget Estimate](#token-budget-estimate)

## Purpose

When writing chapter C of a novel, you need context from all previous chapters — but you can't include all of them in full. This guide defines the compression algorithm: the farther back a chapter is, the more aggressively it's compressed.

## The Five Tiers

Given current target chapter C, and previously written chapters 1 through C-1:

| Tier | Range | Compression | Rationale |
|------|-------|------------|-----------|
| **Foundation** | Always | Full detail | Never compressed — always in context |
| **Voice Anchor** | C-1 | Full text | Irreplaceable for prose voice continuity |
| **Tier 2 — Detailed** | C-3 to C-2 | Full summary (~200-300 words) | Immediate plot and character continuity |
| **Tier 3 — Moderate** | C-6 to C-4 | First 100 words of each summary | Key events, reduced detail |
| **Tier 4 — Compressed** | C-10 to C-7 | First 50 words of each summary | Major beats only |
| **Tier 5 — One-Liner** | 1 to C-11 | First sentence only (~15-25 words) | Memory jogger for distant events |

## Foundation Block (Always Included)

Extract from the project files:

1. **Premise** — from `novel/outline.md`, the one-sentence premise
2. **Genre & POV** — from the outline header
3. **Character Cards** — from `novel/characters.md`, condensed: name, role, 3 key traits, current arc status (where they are in their journey at this point in the novel)
4. **Dynamic State** — from `novel/story-state.md`, only the current pressure, relevant character rows, active open threads, continuity locks, and relationship shifts for this chapter
5. **Thread Ledger** — from `novel/thread-ledger.md`, only threads planted in C, due in C/C+1, mentioned by C's outline row, or high-risk if forgotten
6. **Outline Context** — from `novel/outline.md`, the table rows for:
   - Chapter C-1 (where we just were)
   - Chapter C (what we're writing now)
   - Chapter C+1 (where we're going next)

## Voice Anchor (Chapter C-1 Full Text)

Read `novel/chapters/chapter-{C-1}.md` and include the complete text.

This is the single most expensive item in the context budget (~3,000-7,000 tokens for a typical chapter) but is irreplaceable. A summary of the previous chapter tells you WHAT happened; the full text shows you HOW it was told — sentence rhythm, dialogue cadence, descriptive density, and the exact prose voice to match.

## Tier Compression Algorithm

The `summaries.md` file stores full detailed summaries for every chapter. Compression is applied **at read time** based on distance from the current chapter.

```
For chapter C, for each previous chapter i (1 to C-1):
  summary = summaries[i]
  distance = C - i

  if distance == 1:
    // Voice Anchor — include full text from chapters/chapter-{i}.md
    // (not from summaries.md at all)
  else if distance <= 3:
    context += summary.full                    // Tier 2: full summary
  else if distance <= 6:
    context += summary.first_n_words(100)      // Tier 3: moderate
  else if distance <= 10:
    context += summary.first_n_words(50)       // Tier 4: compressed
  else:
    context += summary.first_sentence()        // Tier 5: one-liner
```

## Context Assembly Order

Assemble in this order for the generation prompt:

1. Foundation (premise, genre, POV)
2. Character cards (all characters, condensed)
3. Dynamic state from story-state.md
4. Relevant thread-ledger rows
5. Outline context (C-1, C, C+1)
6. Tier 5: Distant one-liners (ch 1 → C-11, chronological)
7. Tier 4: Compressed summaries (ch C-10 → C-7, chronological)
8. Tier 3: Moderate summaries (ch C-6 → C-4, chronological)
9. Tier 2: Detailed summaries (ch C-3 → C-2, chronological)
10. Voice Anchor: Full text of chapter C-1
11. Writing instruction for chapter C

This chronological-then-reverse-proximity order creates a natural narrative flow that builds toward the current moment.

## Importance Overrides (Judgment Calls)

The distance-based algorithm above is the default. But some chapters carry narrative weight disproportionate to their position. Apply these overrides when appropriate:

### Promotion Rules

A chapter can be promoted **one tier higher** than its distance would normally get if it contains:

- A major revelation that recontextualizes earlier events (readers AND the AI need to remember this)
- A character death or irreversible transformation that affects all subsequent chapters
- The introduction of a rule, object, or relationship that will be critical in the climax
- A chapter explicitly marked as `revelation`, `death`, or `climax` in the outline's Milestone column

**How to apply**: If Chapter 12 (normally Tier 5, one-liner) contains a revelation that defines the second half of the novel, promote it to Tier 4 (first 50 words) or even Tier 3 (first 100 words) if it's foundational.

### Demotion Rule

A chapter can be demoted **one tier** if it is a pure transitional chapter (travel, recovery, regrouping) with no character development, no plot advancement, and no new information. These chapters exist for rhythm — their summaries don't need detail at long range.

### Budgeting Overrides

Promotions consume extra tokens. The total overhead budget target is ~9,000 tokens. If you promote a chapter, compensate by demoting another chapter of equal or lesser narrative weight. The budget is a guideline, not a straitjacket — but stay within ~10% of it.

**Default stance**: Use distance-based compression. Override only when a chapter's narrative significance clearly differs from what its position suggests.

---

## Edge Cases

### Chapter 1 (C = 1)
No previous chapters exist. Skip Voice Anchor. Skip all tiers. Only Foundation + writing instruction apply. Foundation's "outline context" includes only chapters 1 and 2.

### Chapter 2 (C = 2)
Only chapter 1 exists. Tier mapping adjusts:
- Voice Anchor: Chapter 1 full text
- Tier 2: Not applicable (no C-3 to C-2)
- All other tiers: Not applicable

### Chapter 3 (C = 3)
- Voice Anchor: Chapter 2 full text
- Tier 2: Chapter 1 full summary
- All other tiers: Not applicable

### Early Novel (C < 11)
Tiers 4 and 5 are empty. Distribute available chapters into the tiers that exist, favoring detail for more recent chapters.

## Token Budget Estimate

For a 20-chapter novel, writing chapter 20:

| Tier | Items | Approx Tokens |
|------|-------|---------------|
| Foundation | Characters + premise + outline | ~2,000 |
| Voice Anchor | Full text of ch 19 (~3,500 words) | ~5,000 |
| Tier 2 | Ch 17-18 full summaries (~250w each) | ~700 |
| Tier 3 | Ch 14-16 first 100w each | ~400 |
| Tier 4 | Ch 10-13 first 50w each | ~270 |
| Tier 5 | Ch 1-9 first sentence each | ~230 |
| Chapter instruction | Outline + writing prompt | ~300 |
| **Total overhead** | | **~8,900 tokens** |

With a typical chapter generation taking 3,000-7,000 tokens, total context usage is ~12,000-16,000 tokens — well within any modern model's context window. The pyramid scales comfortably to 100+ chapter novels.
