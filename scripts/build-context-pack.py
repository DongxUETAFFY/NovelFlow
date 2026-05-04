#!/usr/bin/env python3
"""Build a single Markdown context pack for agents without file tools.

The pack includes:
- context-brief.md
- story-state.md when available
- thread-ledger.md relevant rows when available
- outline rows for C-1/C/C+1
- pyramid-compressed summaries
- previous chapter full text as voice anchor
- optional review checklist
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


def build_pack(novel_dir: Path, chapter: Optional[int], include_review: bool) -> str:
    context_brief = read_text(novel_dir / "context-brief.md")
    if not context_brief:
        raise SystemExit(f"Missing required file: {novel_dir / 'context-brief.md'}")

    current = chapter or infer_next_chapter(context_brief)
    if current is None:
        raise SystemExit("Could not infer next chapter. Pass --chapter N.")

    outline = read_text(novel_dir / "outline.md")
    story_state = read_text(novel_dir / "story-state.md")
    thread_ledger = read_text(novel_dir / "thread-ledger.md")
    summaries = parse_summaries(read_text(novel_dir / "summaries.md"))
    previous_chapter = read_text(novel_dir / "chapters" / f"chapter-{current - 1}.md")
    review_checklist = read_text(ROOT / "skills" / "novel-write" / "references" / "review-checklist.md")

    outline_rows = extract_outline_rows(outline, [current - 1, current, current + 1])
    thread_rows = extract_thread_rows(thread_ledger, current, outline_rows)

    compressed: List[str] = []
    for chapter_num in sorted(summaries):
        tier, text = compress_summary(chapter_num, current, summaries[chapter_num])
        if tier == "skip" or tier == "voice-anchor" or not text:
            continue
        compressed.append(f"### Chapter {chapter_num} ({tier})\n\n{text}")

    parts = [
        f"# NovelFlow Context Pack: Chapter {current}",
        "Use this pack with ChatGPT, Claude Chat, or any agent that cannot read local project files directly.",
        "Follow the novel-write workflow: plan internally, write the chapter, self-review, then produce updated memory file patches.",
        "",
        "## 1. Context Brief",
        context_brief.strip(),
        "",
        "## 2. Story State",
        story_state.strip() if story_state else "_Missing story-state.md. Create it before or after this chapter using the NovelFlow template._",
        "",
        "## 3. Immediate Outline Rows (C-1 / C / C+1)",
        "\n".join(outline_rows) if outline_rows else "_No matching outline rows found._",
        "",
        "## 4. Relevant Thread Ledger Rows",
        "\n".join(thread_rows) if thread_rows else "_No due or directly relevant thread-ledger rows found._",
        "",
        "## 5. Pyramid-Compressed Previous Summaries",
        "\n\n".join(compressed) if compressed else "_No prior summaries available._",
        "",
        "## 6. Voice Anchor: Previous Chapter Full Text",
        previous_chapter.strip() if previous_chapter else "_No previous chapter full text. This is likely Chapter 1._",
        "",
        "## 7. Writing Task",
        f"Write Chapter {current}. Preserve all continuity constraints above. After drafting, provide:",
        "- the chapter text",
        "- a chapter summary whose first sentence contains named character + concrete event + directional consequence",
        "- updates needed for story-state.md",
        "- updates needed for thread-ledger.md",
        "- updates needed for context-brief.md and progress.md",
    ]

    if include_review:
        parts.extend(["", "## 8. Review Checklist", review_checklist.strip()])

    return "\n\n".join(parts).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a NovelFlow context pack for agents without file tools.")
    parser.add_argument("--novel-dir", default="novel", help="Path to the novel project directory.")
    parser.add_argument("--chapter", default="auto", help="Chapter number, or 'auto' to infer from context-brief.md.")
    parser.add_argument("--include-review", action="store_true", help="Include the full review checklist.")
    parser.add_argument("--output", help="Write pack to this file instead of stdout.")
    args = parser.parse_args()

    novel_dir = Path(args.novel_dir)
    chapter = None if args.chapter == "auto" else int(args.chapter)
    pack = build_pack(novel_dir, chapter, args.include_review)

    if args.output:
        with Path(args.output).open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(pack)
    else:
        print(pack, end="")


if __name__ == "__main__":
    main()
