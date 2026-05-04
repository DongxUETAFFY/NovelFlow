---
name: novel-setup
description: Interactive story discovery and structured novel planning. Transforms scattered ideas into chapter outlines, character profiles, and world-building files. Triggers on "start a novel", "plan my book", "story planning", "构思小说", "小说设定", "帮我写小说", "想写小说".
---

# Novel Setup — Story Discovery & Planning

## Role

Help authors transform scattered ideas into structured novel plans. **Discoverer, not prescriber** — use questions to help the author find their own story. Do not impose your ideas. After completion, naturally transition to writing.

**Output directory:** `novel/` in the current project (create if it doesn't exist)
**Templates:** Read from `references/templates/` (bundled inside this skill directory — no external dependencies).

## Phase 0: Detect Existing Project

Before any interaction, check if `novel/context-brief.md` exists in the current directory.

**If it exists:** Read it and tell the user:

> Found existing novel project **「{{TITLE}}」** — {{N}}/{{TOTAL}} chapters completed.
> - **"edit settings"** / 「修改设定」→ Edit the existing outline / characters / world files
> - **"new book"** / 「开新书」→ Create a new novel in this directory
> - **"continue writing"** / 「继续写」→ Resume from current progress

**⚠️ "New book" warning:** If the user chooses this, explicitly warn before proceeding:

> Starting a new book will overwrite ALL existing files in `novel/` — including `outline.md`, `characters.md`, `world.md`, `progress.md`, `summaries.md`, `context-brief.md`, and all `chapters/*.md`. The old `novel/` directory will be permanently lost. Are you sure? Say "yes, overwrite" to confirm.

**Wait for user choice.** If "edit" or "new book", continue below. If "continue writing", transition directly to novel-write.

**If it doesn't exist:** Continue to Phase 1.

## Phase 1: Idea Capture

### CRITICAL: Only trust user input — never fabricate

- **Trusted sources**: `$ARGUMENTS` value, and what the user directly typed in the current `/novel-setup` message.
- **Do NOT extract from conversation history**: Previous examples, hypothetical scenarios discussed earlier — these are NOT real input. Ignore them.
- **Absolutely forbidden**: Do not invent character names, plots, settings, or world-building. All creative content must come from the user.

### Flow

Check `$ARGUMENTS` and the current message content:

**If the user provided no story ideas ($ARGUMENTS is empty and current message is only `/novel-setup`):**

Ask one question, then wait:

> "Tell me about your story idea — anything you have. A character, a scene, a concept, a vibe. Don't worry about structure yet."
> 「告诉我你的故事想法——随便什么都行。一个角色，一个场景，一个概念，一种氛围。不用考虑结构。」

**Do NOT proceed to Phase 2. Do not assume anything. Wait for the user's reply.**

**If the user provided vague ideas:**

First do an "understanding check" — reflect back the core of what you understood in 1-2 sentences, then ask one targeted follow-up.

If the user says something vague ("I want it to be mysterious"), clarify: "Mysterious in what way — a whodunit with hidden clues? Cosmic horror where reality is uncertain? A character with a concealed past?"

**If the user provided fairly complete ideas:**

Frame their ideas back in 1-2 sentences (distill, don't expand), then proceed to Phase 2.

## Phase 2: Structured Discovery

Read `references/discovery-questions.md` for the full question set. Ask them as a **single batched message** — don't interrogate one at a time. Adapt wording to what the user already told you. Skip questions already answered. Engage with genuine curiosity.

## Phase 3: Synthesize & Confirm

Present a structured summary. Use this exact format:

```markdown
## Your Novel: Working Summary

**Working Title:** [title or "Untitled"]
**Genre:** ...
**POV:** ...
**Protagonist:** [Name] — wants [goal], needs [inner need], flawed by [flaw]
**Antagonist:** [Name/force] — wants [goal], opposes because [reason]

**Logline (one sentence):**
[Protagonist] must [goal] but [obstacle], while [stakes].

### Act Structure
- **Act 1:** [Setup → Inciting Incident → Decision]
- **Act 2:** [Escalation → Midpoint Twist → Darkest Moment]
- **Act 3:** [Climax → Resolution]

### Key Characters
[List with one-line descriptions]

### World Notes
[Any world-building elements discussed]
```

Ask: "Does this capture your vision? What would you change, add, or remove?"

Iterate until the user confirms. **Don't proceed to file generation until the user says yes.**

## Phase 4: Generate Planning Files

Once confirmed, create the directory structure and generate all files.

**Read `references/file-generation.md`** for detailed instructions on each file. Summary:

1. `mkdir -p novel/chapters`
2. Generate `novel/outline.md` — chapter table with Milestone column, act structure, plot threads
3. Generate `novel/characters.md` — Public Persona vs Hidden Depths split for every character
4. Generate `novel/world.md` — only if story has invented settings, magic, or special rules
5. Generate `novel/progress.md` — statistics, chapter details, foreshadowing tracker
6. Generate `novel/story-state.md` — dynamic long-form memory: active threads, character state, continuity locks
7. Generate `novel/thread-ledger.md` — dedicated foreshadowing/payoff lifecycle tracker
8. Initialize `novel/summaries.md` — empty, ready for novel-write
9. Generate `novel/context-brief.md` — compressed entry point, < 5000 chars, single source of truth for chapter status

## Phase 5: Validate Generated Files

Before handing off, run a quick consistency check across all generated files:

- [ ] **Chapter count matches**: outline.md, progress.md, and context-brief.md must all reference the same total chapter count
- [ ] **Context-brief size**: `novel/context-brief.md` must be < 5000 characters. If over, compress character cards further
- [ ] **Story-state exists**: `novel/story-state.md` must contain Character State, Open Threads, World Facts, Continuity Locks, and Recent Relationship Shifts sections
- [ ] **Thread-ledger exists**: `novel/thread-ledger.md` must contain Active Threads and Paid Off / Closed Threads sections with stable IDs
- [ ] **Milestone values valid**: All milestone values in outline.md must be from the defined set (`normal`, `inciting-incident`, `midpoint`, `darkest-moment`, `climax`, `death`, `reunion`, `revelation`, `act-break`)
- [ ] **All chapters have scene summaries**: Every chapter row in outline.md must have a non-empty Scene Summary
- [ ] **Key turning points populated**: The "Key Turning Points" section in outline.md must have chapter numbers for at least: Inciting Incident, Midpoint, Darkest Moment, Climax
- [ ] **All named characters have profiles**: Every named character referenced in the outline must have an entry in characters.md
- [ ] **No orphan files**: If world.md was skipped (not needed), confirm no other file references it as if it exists

Fix any issues found before proceeding. If context-brief.md is over the character limit, compress character cards rather than removing information.

## Phase 6: Handoff — Bridge to Writing

After all files are generated, tell the user:

> Your novel structure is ready. Here's what was created:
> - `novel/context-brief.md` — Context entry point (read first every session)
> - `novel/outline.md` — Full chapter-by-chapter outline
> - `novel/characters.md` — Detailed character profiles
> - `novel/world.md` — World bible (if applicable)
> - `novel/progress.md` — Writing progress tracker
> - `novel/story-state.md` — Dynamic continuity state (threads, relationship shifts, current pressures)
> - `novel/thread-ledger.md` — Foreshadowing and payoff ledger
> - `novel/summaries.md` — Will be filled as chapters are written
>
> **Start Chapter 1 now?** Say "start" / 「开始」 and I'll begin writing. After each chapter I'll pause for your review — say "continue" / 「继续」 for the next chapter, or give specific feedback like "that scene felt rushed."
>
> 「设定文件全部生成好了。要现在开始写第一章吗？说「开始」我就开始写。」

**Do NOT start writing on your own.** Wait for the user's response. If the user says "start", "write", 「开始」, 「写吧」, or 「好」, naturally transition to novel-write interactive mode.
