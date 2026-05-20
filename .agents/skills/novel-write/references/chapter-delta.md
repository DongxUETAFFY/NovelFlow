# Chapter Delta Contract

Use this after drafting and self-reviewing a chapter, before updating long-term state files.

## Purpose

The model must not freehand-update every memory file directly. It must first produce a structured chapter delta, validate it, then use that validated delta to update project state. This keeps chapter prose, summaries, thread changes, quality metrics, and review status auditable.

## File Path

Write the delta to:

```text
novel/state/deltas/chapter-{N}.json
```

Use JSON, not Markdown. Do not include comments.

Formal schema:

```text
skills/novel-write/scripts/schemas/chapter-delta.schema.json
```

## Standard Shape

Use this for normal one-chapter continuation. It records what matters without forcing craft metrics into every draft.

```json
{
  "mode": "standard",
  "chapter": 12,
  "summary": {
    "first_sentence": "Named character + concrete event + directional consequence.",
    "what_happened": "2-3 concrete sentences.",
    "character_developments": "1-2 sentences about decisions, arc movement, relationship change.",
    "narrative_significance": "Why this chapter matters to the larger story."
  },
  "state_delta": {
    "characters": [],
    "threads": [],
    "world_facts": [],
    "continuity_locks": []
  },
  "review": {
    "p0": [],
    "p1": [],
    "p2": [],
    "soft_notes": []
  }
}
```

## Production Shape

Use this for Production Lock, batch, full-auto, and checkpoint-sensitive work.

```json
{
  "mode": "production",
  "chapter": 12,
  "summary": {
    "first_sentence": "Named character + concrete event + directional consequence.",
    "what_happened": "2-3 concrete sentences.",
    "character_developments": "1-2 sentences about decisions, arc movement, relationship change.",
    "narrative_significance": "Why this chapter matters to the larger story."
  },
  "quality_metrics": {
    "word_count": 4200,
    "scene_count": 3,
    "rendered_dialogue_blocks": 18,
    "summary_bridge_count": 2,
    "sensory_first_500": {
      "visual": 4,
      "tactile": 2,
      "auditory": 3,
      "olfactory": 0,
      "taste": 0
    },
    "emotional_turns": [
      {
        "from": "suspicion",
        "to": "betrayal",
        "evidence": "Exact short phrase from the chapter text."
      }
    ],
    "conflict_turns": [
      {
        "scene": 2,
        "irreversible_change": "What cannot go back to the prior state.",
        "evidence": "Exact short phrase from the chapter text."
      }
    ]
  },
  "state_delta": {
    "characters": [
      {
        "name": "Mira",
        "last_seen": "Chapter 12",
        "current_want": "Concrete want after this chapter.",
        "hidden_pressure": "Private pressure or secret.",
        "relationship_temperature": "What changed with whom.",
        "arc_position": "Current arc state."
      }
    ],
    "threads": [
      {
        "id": "T03",
        "action": "planted",
        "reader_obligation": "What the reader now expects future text to answer.",
        "evidence": "Exact short phrase from the chapter text.",
        "target_chapter": 18
      }
    ],
    "world_facts": [
      {
        "fact": "Only facts established in prose that constrain future scenes.",
        "evidence": "Exact short phrase from the chapter text."
      }
    ],
    "continuity_locks": [
      {
        "lock": "Hard fact that must not drift.",
        "evidence": "Exact short phrase from the chapter text."
      }
    ]
  },
  "review": {
    "p0": [],
    "p1": [],
    "p2": []
  }
}
```

## Evidence Rules

- Every planted, advanced, reversed, closed, or paid-off thread must include evidence copied from the chapter text.
- In Production Lock, every emotional or conflict turn should include evidence when possible.
- New planted threads require `reader_obligation`; do not log pure mood motifs as threads.
- If evidence cannot be found in the chapter text, revise the chapter or remove the delta claim.

## Hard vs Soft

Validation blocks hard-rule failures: invalid JSON, missing summary, unsupported thread action, missing evidence for thread actions, or P2 issues.

Quality metrics are required only in `mode: "production"`. In `mode: "standard"`, put craft concerns such as sensory density, hook strength, or dialogue ratio in `review.soft_notes`.

## Validation and Commit

Run:

```bash
python skills/novel-write/scripts/novelflow.py validate-delta --novel-dir novel --chapter {N}
```

If validation fails:

- Fix missing fields, unsupported structure, or evidence mismatch.
- If `review.p2` is not empty, stop and ask the author. Do not continue batch/full-auto.
- Do not update `context-brief.md`, `summaries.md`, `story-state.md`, `thread-ledger.md`, or `progress.md` until validation passes.

After validation passes, commit the delta:

```bash
python skills/novel-write/scripts/novelflow.py commit-delta --novel-dir novel --chapter {N}
```

This updates:

- `novel/state/chapter-index.json`
- `novel/generated/summaries.md`
- `novel/generated/progress.md`
- `novel/generated/thread-ledger.md`
- `novel/generated/story-state.md`
- `novel/generated/cards.jsonl`

The generated files are safe rebuild targets. Treat them as the audit-friendly source for legacy Markdown updates. If the chapter text is edited after commit, run:

```bash
python skills/novel-write/scripts/novelflow.py audit --novel-dir novel
```

If audit reports that a chapter is newer than its delta, rebuild that chapter's delta and commit again before writing later chapters.

If the chapter text was edited but the delta still accurately describes the revised text, rebuild committed generated state:

```bash
python skills/novel-write/scripts/novelflow.py rebuild --novel-dir novel --from-chapter {N}
```

If the edit changes plot, thread status, character state, or quality metrics, rewrite that chapter's delta before rebuilding.

To assemble the next chapter's default context pack:

```bash
python skills/novel-write/scripts/novelflow.py assemble-context --novel-dir novel --chapter {NEXT}
```

This writes `novel/generated/context-pack-chapter-{NEXT}.md` from the committed index, active thread cards, prior summaries, and previous chapter voice anchor.
