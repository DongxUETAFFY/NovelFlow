# Fragment Continue

Use this when the author provides unfinished prose and asks to continue from that exact fragment.

## Principle

Fragment Continue is creative drafting, not project advancement. The user's fragment is the local voice anchor. Do not treat the result as canon unless the author explicitly promotes it.

## Read

- `novel/context-brief.md`
- Current outline row only if the chapter is obvious
- Previous chapter only if it helps match voice
- `references/prose-guide.md` only if prose guidance is needed

Do not run audit, checkpoint, full review checklist, delta validation, or commit.

## Write

- Continue directly from the fragment.
- Match the fragment's POV, tense, sentence rhythm, and emotional temperature.
- Prefer 300-1200 words unless the author asks for a different length.
- Do not recap the fragment unless needed for the first sentence to flow.

## Save

Default: return text only.

If saving is requested:

```text
novel/drafts/fragment-continue-{timestamp}.md
```

If the chapter is clear:

```text
novel/drafts/chapter-{N}-fragment-continue.md
```

Helper:

```bash
python skills/novel-write/scripts/novelflow.py save-fragment-draft --novel-dir novel --text-file {draft_file}
```

Add `--chapter {N}` when the chapter is known.

## Promotion To Canon

Only promote when the author explicitly says:

- "并入正文"
- "保存到第 N 章"
- "把这段作为正式章节的一部分"
- "按全书设定续写"
- "从这里继续全书"
- "merge into chapter N"

Then switch to Canon Continue:

1. Merge or write into `novel/chapters/chapter-{N}.md`.
2. Load relevant dynamic state rows from `story-state.md` and `thread-ledger.md`.
3. Read relevant `characters.md` and `world.md` sections only if the fragment touches those facts.
4. Create `mode: "standard"` chapter delta unless the user asked for Production Lock, batch/full-auto, or ending run.
5. Validate and commit delta.
6. Update generated state / legacy exports as needed.

Never mark a fragment continuation complete as a chapter by itself.
