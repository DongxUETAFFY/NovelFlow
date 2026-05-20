# File Generation Guide

Detailed instructions for Phase 4 of novel-setup. Read this after the user confirms the story summary in Phase 3.

## 4a: Create Directories

```bash
mkdir -p novel/chapters
```

## 4b: Generate `novel/outline.md`

Read the template at `references/templates/outline-template.md`. Fill it with the confirmed story structure. Generate a chapter-by-chapter outline.

**Critical formatting rules** (novel-write parses this file):
- The chapter table uses **pipe-delimited columns** exactly: `| Ch | Title | POV Char | Scene Summary | Key Events | Word Target | Milestone |`
- Chapter numbers start at 1 and are sequential
- Every chapter row must have a non-empty Scene Summary (1-2 sentences)
- Key Events are comma-separated or bullet-pointed specific moments
- **Milestone column**: Mark key structural/emotional nodes using the values defined in the template. At minimum, mark: inciting incident, midpoint, darkest moment, and climax. Also mark major character deaths, reunions, and revelations. All other chapters default to `normal`. novel-write uses this column for milestone protection — chapters marked as anything other than `normal` get extra scrutiny.
- Fill in the Act Structure and Plot Threads sections with specifics
- Populate Key Turning Points with chapter numbers

## 4c: Generate `novel/characters.md`

Read the template at `references/templates/characters-template.md`. For each character discussed (and any supporting characters the story needs), create a full profile.

**The "Public Persona" vs "Hidden Depths" split is load-bearing.** novel-write uses this distinction to decide what information to reveal in each chapter versus what stays hidden as subtext.

For the protagonist, be especially thorough:
- External goal (what they're chasing)
- Internal need (what they actually require)
- Flaw/blind spot (what holds them back)
- Arc from starting state to ending state

For relationships, map the key dynamics between major characters.

## 4d: Generate `novel/world.md` (conditional)

**Generate only if the story meets ANY of these criteria:**
- Takes place in an invented setting (not contemporary real world)
- Has magic, supernatural, or speculative technology systems with defined rules
- Has non-human species, factions, or cultures that differ significantly from real-world norms
- The world itself has rules that drive plot or character decisions

**Skip if:** Story is set in the contemporary real world with no special rules beyond normal fiction (no magic, no future tech, no invented cultures). Note: "skip file entirely" — do not create an empty or placeholder world.md.

If needed, read the template at `references/templates/world-template.md` and fill it. Focus on rules and constraints (what's possible, what's forbidden) — these matter more for consistency than aesthetic descriptions.

## 4e: Generate `novel/market-brief.md`

Read the template at `references/templates/market-brief-template.md`. Fill it from confirmed user input and the Phase 3 summary.

**Purpose:** `market-brief.md` is a lightweight writing contract, not a marketing research report. It tells novel-write what reader promise and prose style to preserve across long drafting.

Requirements:
- Keep the full file under 1500 characters.
- Include target reader, platform/genre lane, core promise, hook, reader pleasures, content boundaries, and style contract.
- If the user did not specify a field, write `unknown yet` instead of inventing market facts.
- Do not make unsupported claims like "this will sell well" or fabricated platform trends.
- Copy only 2-4 highest-value bullets into `context-brief.md` as the Market Snapshot.

## 4f: Generate `novel/progress.md`

Read the template at `references/templates/progress-template.md`. Fill it with:
- Novel metadata (title, date)
- Chapter details table: populate ALL chapters with empty word count/date/notes (status is tracked in context-brief.md)
- Initial statistics (total planned chapters filled, written = 0)
- Empty foreshadowing tracker and revision log

## 4g: Generate `novel/story-state.md`

Read the template at `references/templates/story-state-template.md`. Fill it with dynamic state that will change during drafting.

**Purpose:** `story-state.md` is the long-form memory layer. It stores current pressures, unresolved threads, character relationship temperature, newly established world facts, and continuity locks. It should be read by novel-write when writing any chapter after Chapter 1.

Initial requirements:
- Character State rows: include every major character with their starting want, hidden pressure, relationship temperature, and arc position
- Open Threads: include major planned mysteries, promises, prophecies, relationship tensions, and planted objects from the outline
- World Facts: include only rules that constrain future scenes; skip aesthetic lore unless it affects plot
- Continuity Locks: 5-12 short facts that must never drift
- Keep the file concise. This is a working memory file, not a second outline.

## 4h: Generate `novel/thread-ledger.md`

Read the template at `references/templates/thread-ledger-template.md`. Fill it with planned foreshadowing, mysteries, planted objects, emotional promises, red herrings, and delayed consequences.

**Purpose:** `thread-ledger.md` is the dedicated foreshadowing/payoff ledger. `story-state.md` stores current pressure; `thread-ledger.md` stores the lifecycle of every significant thread from planned/planted to advanced/paid-off/closed.

Initial requirements:
- Add one row for every major mystery, relationship promise, prophecy, planted object, planned reveal, red herring, or delayed consequence in the outline
- Use stable IDs such as `T01`, `T02`, `T03`
- Set `Planted In` to the planned chapter if not drafted yet
- Set `Payoff Target` to the intended chapter or range
- Set `Payoff Form` from the template values
- Keep minor atmosphere motifs out unless they create a future obligation

## 4i: Initialize `novel/summaries.md`

Create this file with initial content:
```markdown
# Chapter Summaries

*Summaries are added by novel-write after each chapter is generated. Each entry includes the chapter's key events, character developments, and narrative significance.*
```

## 4j: Generate `novel/context-brief.md`

Read the template at `references/templates/context-brief-template.md`. Fill it with compressed versions of all novel data. The context-brief.md is the **entry point for every writing session** — any agent reads this file first to know what the novel is, who the characters are, and where writing stopped.

Requirements:
- Total file: < 5000 characters. Any agent should read it in one glance.
- Character cards: each character in 1-2 lines only — name, role, 2-3 keywords, arc start→end
- Market snapshot: 2-4 bullets copied from `market-brief.md`, not the full file
- State snapshot: 3-6 bullets copied from `story-state.md` covering current pressure, unresolved threads, and continuity locks
- Thread snapshot: 2-5 high-risk or soon-due items copied from `thread-ledger.md`
- Chapter table: all chapters from outline, all initially `planned`
- Writing status: 0/{{TOTAL}}, next chapter Ch1, today's date
