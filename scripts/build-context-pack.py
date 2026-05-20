#!/usr/bin/env python3
"""Build a single Markdown context pack for agents without file tools.

The pack includes:
- context-brief.md
- reader-promise.md, or legacy market-brief.md when available
- story-state.md when available
- thread-ledger.md relevant rows when available
- outline rows for C-1/C/C+1
- pyramid-compressed summaries
- previous chapter full text as voice anchor
- optional review checklist

Modes:
- free-draft: write only, no state update
- fragment-continue: continue a user-provided fragment, no state update
- standard: light chapter delta
- production: full chapter delta and review
- finish-book-intake: diagnose an abandoned/incomplete book before continuing
- finish-book-run: production-locked continuation after confirmed roadmap
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def first_sentence(text: str) -> str:
    text = text.strip()
    match = re.search(r"[。！？.!?]", text)
    if match:
        return text[: match.end()].strip()
    return text.splitlines()[0].strip() if text else ""


def first_words_or_chars(text: str, words: int, chars: int) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    if not text:
        return ""
    if re.search(r"[\u4e00-\u9fff]", text):
        return text[:chars].strip()
    parts = text.split()
    return " ".join(parts[:words]).strip()


def infer_next_chapter(context: str) -> Optional[int]:
    patterns = [
        r"Next\s*/\s*下一章:\s*Ch\s*(\d+)",
        r"下一章:\s*Ch\s*(\d+)",
        r"Next:\s*Ch\s*(\d+)",
        r"下一章[:：]\s*第\s*(\d+)\s*章",
    ]
    for pattern in patterns:
        match = re.search(pattern, context, re.IGNORECASE)
        if match:
            return int(match.group(1))

    for line in context.splitlines():
        match = re.match(r"\|\s*(\d+)\s*\|[^|]+\|\s*planned\s*\|", line, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def latest_chapter_number(novel_dir: Path) -> Optional[int]:
    chapters: List[int] = []
    for path in (novel_dir / "chapters").glob("chapter-*.md"):
        match = re.match(r"chapter-(\d+)$", path.stem)
        if match:
            chapters.append(int(match.group(1)))
    return max(chapters) if chapters else None


def extract_outline_rows(outline: str, chapters: Iterable[int]) -> List[str]:
    wanted = {chapter for chapter in chapters if chapter > 0}
    rows: Dict[int, str] = {}
    for line in outline.splitlines():
        match = re.match(r"\|\s*(\d+)\s*\|", line)
        if match:
            chapter = int(match.group(1))
            if chapter in wanted:
                rows[chapter] = line
    return [rows[chapter] for chapter in sorted(rows)]


def extract_thread_rows(ledger: str, current: int, outline_rows: List[str]) -> List[str]:
    if not ledger:
        return []

    haystack = " ".join(outline_rows).lower()
    rows: List[str] = []
    for line in ledger.splitlines():
        if not line.startswith("|") or re.match(r"^\|\s*-+", line):
            continue
        if "| ID " in line or "|----" in line:
            continue

        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 9:
            continue

        thread_id, thread, _type, planted, _evidence, _state, payoff, _form, status = cells[:9]
        searchable = f"{thread_id} {thread}".lower()
        due = chapter_ref_matches(planted, current) or chapter_ref_matches(payoff, current) or chapter_ref_matches(payoff, current + 1)
        active = status not in {"paid-off", "closed-red-herring", "dropped"}
        mentioned = bool(thread and thread.lower() in haystack)
        if active and (due or mentioned):
            rows.append(line)

    return rows[:12]


def chapter_ref_matches(text: str, chapter: int) -> bool:
    if not text:
        return False
    patterns = [
        rf"\bCh\s*{chapter}\b",
        rf"\bChapter\s*{chapter}\b",
        rf"第\s*{chapter}\s*章",
        rf"\b{chapter}\b",
    ]
    return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)


def parse_summaries(summaries: str) -> Dict[int, str]:
    result: Dict[int, List[str]] = {}
    current: Optional[int] = None
    for line in summaries.splitlines():
        header = re.match(r"^##\s+(?:Chapter|第)\s*(\d+)", line, re.IGNORECASE)
        if header:
            current = int(header.group(1))
            result.setdefault(current, [])
            continue
        if current is not None:
            result[current].append(line)
    return {chapter: "\n".join(lines).strip() for chapter, lines in result.items()}


def compress_summary(chapter: int, current: int, summary: str) -> Tuple[str, str]:
    distance = current - chapter
    if distance <= 0:
        return "skip", ""
    if distance == 1:
        return "voice-anchor", ""
    if distance <= 3:
        return "tier-2-full-summary", summary
    if distance <= 6:
        return "tier-3-first-100w", first_words_or_chars(summary, words=100, chars=220)
    if distance <= 10:
        return "tier-4-first-50w", first_words_or_chars(summary, words=50, chars=120)
    return "tier-5-first-sentence", first_sentence(summary)


def build_pack(novel_dir: Path, chapter: Optional[int], include_review: bool, mode: str) -> str:
    context_brief = read_text(novel_dir / "context-brief.md")
    if not context_brief:
        raise SystemExit(f"Missing required file: {novel_dir / 'context-brief.md'}")

    latest_chapter = latest_chapter_number(novel_dir)
    current = chapter or infer_next_chapter(context_brief)
    if current is None and mode == "finish-book-intake":
        current = (latest_chapter or 0) + 1
    if current is None:
        raise SystemExit("Could not infer next chapter. Pass --chapter N.")

    outline = read_text(novel_dir / "outline.md")
    reader_promise = read_text(novel_dir / "reader-promise.md") or read_text(novel_dir / "market-brief.md")
    story_state = read_text(novel_dir / "generated" / "story-state.md") or read_text(novel_dir / "story-state.md")
    thread_ledger = read_text(novel_dir / "generated" / "thread-ledger.md") or read_text(novel_dir / "thread-ledger.md")
    summaries = parse_summaries(read_text(novel_dir / "generated" / "summaries.md") or read_text(novel_dir / "summaries.md"))
    voice_anchor_chapter = latest_chapter if mode == "finish-book-intake" and latest_chapter else current - 1
    previous_chapter = read_text(novel_dir / "chapters" / f"chapter-{voice_anchor_chapter}.md")
    review_checklist = read_text(ROOT / "skills" / "novel-write" / "references" / "review-checklist.md")

    outline_rows = extract_outline_rows(outline, [current - 1, current, current + 1])
    thread_rows = extract_thread_rows(thread_ledger, current, outline_rows)

    compressed: List[str] = []
    for chapter_num in sorted(summaries):
        tier, text = compress_summary(chapter_num, current, summaries[chapter_num])
        if tier == "skip" or tier == "voice-anchor" or not text:
            continue
        compressed.append(f"### Chapter {chapter_num} ({tier})\n\n{text}")

    if mode == "fragment-continue":
        workflow_instruction = (
            "Fragment Continue mode: continue the user-provided fragment as the local voice anchor. "
            "Do not produce chapter delta, audit output, memory patches, or project state updates. "
            "Only promote into canon if the user explicitly asks to merge/save it into a chapter."
        )
        after_drafting = [
            "- the continuation text only",
            "- a brief note that no project state was updated",
            "- if saving is requested, save as a fragment draft rather than canonical chapter text",
        ]
    elif mode == "finish-book-intake":
        workflow_instruction = (
            "Finish Book Intake mode: do not write official chapter prose. Diagnose the current book, "
            "summarize state, infer style, identify open threads, propose continuation directions, "
            "then ask for roadmap confirmation before any Finish Book Run."
        )
        after_drafting = [
            "- `# Finish Book Intake Report`",
            "- Current Story State, Character State, Style Profile, Open Threads, Continuity Locks",
            "- Possible Continuation Directions and Recommended Finish Strategy",
            "- questions requiring author confirmation",
        ]
    elif mode == "finish-book-run":
        workflow_instruction = (
            "Finish Book Run mode: proceed only if the intake report and roadmap were confirmed by the author. "
            "Use Production Lock. Produce full production deltas and stop on P2, unresolved payoff, validation failure, or checkpoint drift."
        )
        after_drafting = [
            "- the chapter text",
            "- a full `mode: \"production\"` chapter delta JSON",
            "- progress note for the confirmed finish roadmap",
        ]
    elif mode == "free-draft":
        workflow_instruction = (
            "Free Draft mode: write the chapter or scene only. Do not produce chapter delta, "
            "memory patches, audit output, or state updates. Clearly say no project state was updated."
        )
        after_drafting = ["- the draft text only", "- a brief note that no project state was updated"]
    elif mode == "production":
        workflow_instruction = (
            "Production Lock mode: after drafting, produce a full production chapter delta with "
            "quality_metrics, evidence-backed thread actions, P0/P1/P2 review, and any checkpoint risks."
        )
        after_drafting = [
            "- the chapter text",
            "- a full `mode: \"production\"` chapter delta JSON",
            "- P0/P1/P2 findings, with P2 requiring author decision",
        ]
    else:
        workflow_instruction = (
            "Standard Writing mode: write first, then produce a light standard chapter delta. "
            "Treat sensory density, dialogue ratio, chapter length, and hook density as soft notes."
        )
        after_drafting = [
            "- the chapter text",
            "- a light `mode: \"standard\"` chapter delta JSON",
            "- hard-rule issues as P0/P1/P2 and craft concerns as `soft_notes`",
        ]

    title = "Finish Book Intake" if mode == "finish-book-intake" else f"Chapter {current}"
    parts = [
        f"# NovelFlow Context Pack: {title}",
        "Use this pack with ChatGPT, Claude Chat, or any agent that cannot read local project files directly.",
        workflow_instruction,
        "",
        "## 1. Context Brief",
        context_brief.strip(),
        "",
        "## 2. Reader Promise",
        reader_promise.strip() if reader_promise else "_Missing reader-promise.md / legacy market-brief.md. Continue from the context snapshot if present._",
        "",
        "## 3. Story State",
        story_state.strip() if story_state else "_Missing story-state.md. Create it before or after this chapter using the NovelFlow template._",
        "",
        "## 4. Immediate Outline Rows (C-1 / C / C+1)",
        "\n".join(outline_rows) if outline_rows else "_No matching outline rows found._",
        "",
        "## 5. Relevant Thread Ledger Rows",
        "\n".join(thread_rows) if thread_rows else "_No due or directly relevant thread-ledger rows found._",
        "",
        "## 6. Pyramid-Compressed Previous Summaries",
        "\n\n".join(compressed) if compressed else "_No prior summaries available._",
        "",
        "## 7. Voice Anchor: Previous / Latest Chapter Full Text",
        previous_chapter.strip() if previous_chapter else "_No previous chapter full text. This is likely Chapter 1._",
        "",
        "## 8. Writing Task",
        ("Do not write a formal chapter yet. Produce the diagnostic report below. Provide:" if mode == "finish-book-intake" else f"Write Chapter {current}. Preserve all continuity constraints above. After drafting, provide:"),
        "\n".join(after_drafting),
    ]

    if include_review:
        parts.extend(["", "## 9. Review Checklist", review_checklist.strip()])

    return "\n\n".join(parts).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a NovelFlow context pack for agents without file tools.")
    parser.add_argument("--novel-dir", default="novel", help="Path to the novel project directory.")
    parser.add_argument("--chapter", default="auto", help="Chapter number, or 'auto' to infer from context-brief.md.")
    parser.add_argument(
        "--mode",
        default="standard",
        choices=("free-draft", "fragment-continue", "standard", "production", "finish-book-intake", "finish-book-run"),
        help="Context pack mode.",
    )
    parser.add_argument("--include-review", action="store_true", help="Include the full review checklist.")
    parser.add_argument("--output", help="Write pack to this file instead of stdout.")
    args = parser.parse_args()

    novel_dir = Path(args.novel_dir)
    chapter = None if args.chapter == "auto" else int(args.chapter)
    pack = build_pack(novel_dir, chapter, args.include_review, args.mode)

    if args.output:
        with Path(args.output).open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(pack)
    else:
        print(pack, end="")


if __name__ == "__main__":
    main()
