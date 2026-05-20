# novel-setup

Interactive story discovery and structured novel planning. Transforms scattered ideas into chapter outlines, character profiles, and world-building files.

## Install

```bash
cp -r novel-setup ~/.claude/skills/
```

## Usage

Share your story idea — a sentence, a scene, a character, a vibe. The AI asks batched questions to clarify genre, POV, protagonist, antagonist, plot structure, world-building, and scope. After confirmation, it generates a complete `novel/` project directory with built-in validation.

## 6-Phase Flow

| Phase | Description |
|-------|-------------|
| 0 — Detect | Check for existing project; offer edit / new / continue |
| 1 — Capture | Absorb raw ideas (never fabricate) |
| 2 — Discover | Batched questions (7 dimensions, all at once) |
| 3 — Synthesize | Structured summary → iterate until confirmed |
| 4 — Generate | Create all project files from templates |
| 5 — Validate | Cross-check consistency across all files |
| 6 — Handoff | Offer to start Chapter 1 immediately |

## Output

```
novel/
├── context-brief.md   # Compressed entry point (single source of truth)
├── outline.md         # Chapter outline with Milestone column
├── market-brief.md    # Target reader, core promise, hook, style contract
├── characters.md      # Public Persona vs Hidden Depths profiles
├── world.md           # World bible (conditional — only for invented settings)
├── progress.md        # Stats, foreshadowing tracker, revision log
├── story-state.md     # Dynamic continuity memory and current narrative pressure
├── thread-ledger.md   # Foreshadowing and payoff lifecycle
├── summaries.md       # Chapter summaries (filled by novel-write)
└── chapters/          # Chapter files (written by novel-write)
```

## Progressive Loading

| Level | Content | When |
|-------|---------|------|
| L1 | name + description | Session start |
| L2 | SKILL.md | Skill invoked |
| L3 | references/discovery-questions.md | Phase 2 |
| L3 | references/file-generation.md | Phase 4 |
| L3 | references/templates/* | Phase 4 |

## Dependencies

None. Output consumed by `novel-write`.
