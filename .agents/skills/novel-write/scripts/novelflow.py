import argparse
import json
import shutil
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


REQUIRED_SUMMARY_FIELDS = (
    "first_sentence",
    "what_happened",
    "character_developments",
    "narrative_significance",
)

REQUIRED_TOP_LEVEL_FIELDS = (
    "mode",
    "chapter",
    "summary",
    "state_delta",
    "review",
)
PRODUCTION_REQUIRED_FIELDS = REQUIRED_TOP_LEVEL_FIELDS + ("quality_metrics",)
ALLOWED_MODES = {"standard", "production"}

INDEX_PATH = Path("state") / "chapter-index.json"
ALLOWED_THREAD_ACTIONS = {
    "planned",
    "planted",
    "advanced",
    "paid_off",
    "delayed",
    "reversed",
    "closed",
    "retired",
}
EVIDENCE_REQUIRED_THREAD_ACTIONS = {"planted", "advanced", "paid_off", "reversed", "closed"}


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def _as_dict(value: Any, field_name: str, errors: list[str]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    errors.append(f"{field_name} must be an object.")
    return {}


def _as_list(value: Any, field_name: str, errors: list[str]) -> list[Any]:
    if isinstance(value, list):
        return value
    errors.append(f"{field_name} must be a list.")
    return []


def _text_contains(text: str, evidence: str) -> bool:
    normalized_text = " ".join(text.lower().split())
    normalized_evidence = " ".join(evidence.lower().split())
    return normalized_evidence in normalized_text


def _validate_evidence(
    chapter_text: str,
    evidence: Any,
    location: str,
    errors: list[str],
) -> None:
    if not isinstance(evidence, str) or not evidence.strip():
        errors.append(f"{location} evidence must be a non-empty string.")
        return
    if not _text_contains(chapter_text, evidence):
        errors.append(f"{location} evidence not found in chapter text: {evidence!r}")


def _load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.exists():
        errors.append(f"Delta file not found: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Delta file is not valid JSON: {exc}")
        return {}


def _read_json_or_empty(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _chapter_numbers(novel_dir: Path) -> list[int]:
    chapters: list[int] = []
    for path in (novel_dir / "chapters").glob("chapter-*.md"):
        stem = path.stem[len("chapter-"):]
        if stem.isdigit():
            chapters.append(int(stem))
    return sorted(chapters)


def _load_delta(delta_path: Path) -> dict[str, Any]:
    return json.loads(delta_path.read_text(encoding="utf-8"))


def _delta_mode(delta: dict[str, Any]) -> str:
    mode = delta.get("mode")
    return mode if isinstance(mode, str) else ""


def _quality(entry: dict[str, Any]) -> dict[str, Any]:
    return entry.get("quality_metrics") or {}


def _render_summaries(novel_dir: Path, index: dict[str, Any]) -> None:
    lines = ["# Generated Summaries", "", "Do not edit directly. Generated from validated chapter deltas.", ""]
    for chapter_key in sorted(index.get("chapters", {}), key=lambda value: int(value)):
        entry = index["chapters"][chapter_key]
        summary = entry["summary"]
        lines.extend([
            f"## Chapter {chapter_key}",
            "",
            summary["first_sentence"],
            "",
            f"**What happened:** {summary['what_happened']}",
            "",
            f"**Character developments:** {summary['character_developments']}",
            "",
            f"**Narrative significance:** {summary['narrative_significance']}",
            "",
        ])
    output = novel_dir / "generated" / "summaries.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def _render_progress(novel_dir: Path, index: dict[str, Any]) -> None:
    lines = [
        "# Generated Progress",
        "",
        "Do not edit directly. Generated from validated chapter deltas.",
        "",
        "| Chapter | Words | Scenes | Dialogue Blocks | P0 | P1 | P2 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for chapter_key in sorted(index.get("chapters", {}), key=lambda value: int(value)):
        entry = index["chapters"][chapter_key]
        quality = _quality(entry)
        review = entry["review"]
        lines.append(
            f"| {chapter_key} | {quality.get('word_count', 0)} | {quality.get('scene_count', 0)} | "
            f"{quality.get('rendered_dialogue_blocks', 0)} | {len(review.get('p0', []))} | "
            f"{len(review.get('p1', []))} | {len(review.get('p2', []))} |"
        )
    output = novel_dir / "generated" / "progress.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_thread_ledger(novel_dir: Path, index: dict[str, Any]) -> None:
    lines = [
        "# Generated Thread Ledger",
        "",
        "Do not edit directly. Generated from validated chapter deltas.",
        "",
        "| Thread | Chapter | Action | Reader Obligation | Evidence |",
        "|---|---:|---|---|---|",
    ]
    for chapter_key in sorted(index.get("chapters", {}), key=lambda value: int(value)):
        entry = index["chapters"][chapter_key]
        for thread in entry.get("state_delta", {}).get("threads", []):
            lines.append(
                f"| {thread.get('id', '')} | {chapter_key} | {thread.get('action', '')} | "
                f"{thread.get('reader_obligation', '')} | {thread.get('evidence', '')} |"
            )
    output = novel_dir / "generated" / "thread-ledger.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _render_story_state(novel_dir: Path, index: dict[str, Any]) -> None:
    lines = [
        "# Generated Story State",
        "",
        "Do not edit directly. Generated from validated chapter deltas.",
        "",
        "## Character State",
        "",
    ]
    character_rows: list[str] = []
    world_rows: list[str] = []
    lock_rows: list[str] = []
    for chapter_key in sorted(index.get("chapters", {}), key=lambda value: int(value)):
        entry = index["chapters"][chapter_key]
        summary = entry["summary"]
        character_rows.append(f"- Chapter {chapter_key}: {summary['character_developments']}")
        for character in entry.get("state_delta", {}).get("characters", []):
            name = character.get("name", "unknown")
            want = character.get("current_want", "")
            pressure = character.get("hidden_pressure", "")
            arc = character.get("arc_position", "")
            character_rows.append(f"  - {name}: want={want}; pressure={pressure}; arc={arc}")
        for fact in entry.get("state_delta", {}).get("world_facts", []):
            world_rows.append(f"- Chapter {chapter_key}: {fact.get('fact', '')} Evidence: {fact.get('evidence', '')}")
        for lock in entry.get("state_delta", {}).get("continuity_locks", []):
            lock_rows.append(f"- Chapter {chapter_key}: {lock.get('lock', '')} Evidence: {lock.get('evidence', '')}")

    lines.extend(character_rows or ["- None recorded."])
    lines.extend(["", "## World Facts", ""])
    lines.extend(world_rows or ["- None recorded."])
    lines.extend(["", "## Continuity Locks", ""])
    lines.extend(lock_rows or ["- None recorded."])
    lines.append("")
    output = novel_dir / "generated" / "story-state.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def _render_cards(novel_dir: Path, index: dict[str, Any]) -> None:
    output = novel_dir / "generated" / "cards.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for chapter_key in sorted(index.get("chapters", {}), key=lambda value: int(value)):
        entry = index["chapters"][chapter_key]
        lines.append(json.dumps({
            "chapter": int(chapter_key),
            "type": "summary",
            "importance": "normal",
            "text": entry["summary"]["first_sentence"],
        }, ensure_ascii=False))
        for thread in entry.get("state_delta", {}).get("threads", []):
            lines.append(json.dumps({
                "chapter": int(chapter_key),
                "type": "thread",
                "thread_id": thread.get("id"),
                "action": thread.get("action"),
                "importance": "high",
                "text": thread.get("reader_obligation") or thread.get("evidence", ""),
            }, ensure_ascii=False))
    output.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _render_generated_files(novel_dir: Path, index: dict[str, Any]) -> None:
    _render_summaries(novel_dir, index)
    _render_progress(novel_dir, index)
    _render_thread_ledger(novel_dir, index)
    _render_story_state(novel_dir, index)
    _render_cards(novel_dir, index)


def _max_committed_chapter(index: dict[str, Any]) -> int:
    chapters = [int(chapter) for chapter in index.get("chapters", {}) if str(chapter).isdigit()]
    return max(chapters) if chapters else 0


def validate_delta(novel_dir: Path, chapter: int, delta_path: Optional[Path] = None) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    novel_dir = Path(novel_dir)
    delta_path = delta_path or novel_dir / "state" / "deltas" / f"chapter-{chapter}.json"
    chapter_path = novel_dir / "chapters" / f"chapter-{chapter}.md"

    if not chapter_path.exists():
        errors.append(f"Chapter file not found: {chapter_path}")
        return ValidationResult(False, errors, warnings)

    chapter_text = chapter_path.read_text(encoding="utf-8")
    delta = _load_json(Path(delta_path), errors)
    if not delta:
        return ValidationResult(False, errors, warnings)

    mode = _delta_mode(delta)
    if mode not in ALLOWED_MODES:
        errors.append(f"mode must be one of {sorted(ALLOWED_MODES)}; got {delta.get('mode')!r}.")
    required_fields = PRODUCTION_REQUIRED_FIELDS if mode == "production" else REQUIRED_TOP_LEVEL_FIELDS
    for field_name in required_fields:
        if field_name not in delta:
            errors.append(f"Missing required field: {field_name}")

    if delta.get("chapter") != chapter:
        errors.append(f"Delta chapter {delta.get('chapter')!r} does not match target chapter {chapter}.")

    summary = _as_dict(delta.get("summary"), "summary", errors)
    for field_name in REQUIRED_SUMMARY_FIELDS:
        value = summary.get(field_name)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"summary.{field_name} must be a non-empty string.")

    quality = _as_dict(delta.get("quality_metrics", {}), "quality_metrics", errors)
    if mode == "production":
        scene_count = quality.get("scene_count")
        if not isinstance(scene_count, int) or scene_count < 1:
            errors.append("quality_metrics.scene_count must be at least 1.")

        word_count = quality.get("word_count")
        if not isinstance(word_count, int) or word_count <= 0:
            errors.append("quality_metrics.word_count must be a positive integer.")

        senses = _as_dict(quality.get("sensory_first_500"), "quality_metrics.sensory_first_500", errors)
        active_senses = [
            name for name, count in senses.items()
            if isinstance(count, int) and count > 0
        ]
        if len(active_senses) < 3:
            errors.append("quality_metrics.sensory_first_500 must include at least 3 senses with positive counts.")

    for index, turn in enumerate(_as_list(quality.get("emotional_turns", []), "quality_metrics.emotional_turns", errors), start=1):
        if isinstance(turn, dict) and turn.get("evidence"):
            _validate_evidence(chapter_text, turn.get("evidence"), f"emotional_turns[{index}]", errors)

    for index, turn in enumerate(_as_list(quality.get("conflict_turns", []), "quality_metrics.conflict_turns", errors), start=1):
        if isinstance(turn, dict) and turn.get("evidence"):
            _validate_evidence(chapter_text, turn.get("evidence"), f"conflict_turns[{index}]", errors)

    state_delta = _as_dict(delta.get("state_delta"), "state_delta", errors)
    threads = _as_list(state_delta.get("threads", []), "state_delta.threads", errors)
    for index, thread in enumerate(threads, start=1):
        if not isinstance(thread, dict):
            errors.append(f"state_delta.threads[{index}] must be an object.")
            continue
        if not thread.get("id"):
            errors.append(f"state_delta.threads[{index}].id is required.")
        action = thread.get("action")
        if not action:
            errors.append(f"state_delta.threads[{index}].action is required.")
        elif action not in ALLOWED_THREAD_ACTIONS:
            errors.append(f"state_delta.threads[{index}] has unsupported thread action: {action!r}.")
        if action in EVIDENCE_REQUIRED_THREAD_ACTIONS:
            _validate_evidence(chapter_text, thread.get("evidence"), f"state_delta.threads[{index}]", errors)
        if action == "planted" and not thread.get("reader_obligation"):
            errors.append(f"state_delta.threads[{index}].reader_obligation is required when planting a thread.")

    review = _as_dict(delta.get("review"), "review", errors)
    p2 = _as_list(review.get("p2", []), "review.p2", errors)
    if p2:
        errors.append("P2 issues block commit readiness; pause for author decision.")

    p1 = _as_list(review.get("p1", []), "review.p1", errors)
    if len(p1) >= 3:
        warnings.append("3 or more P1 issues: batch/full-auto should pause after this chapter.")

    return ValidationResult(not errors, errors, warnings)


def commit_delta(novel_dir: Path, chapter: int, delta_path: Optional[Path] = None) -> ValidationResult:
    novel_dir = Path(novel_dir)
    delta_path = delta_path or novel_dir / "state" / "deltas" / f"chapter-{chapter}.json"
    result = validate_delta(novel_dir, chapter, delta_path)
    if not result.ok:
        return result

    canonical_delta_path = novel_dir / "state" / "deltas" / f"chapter-{chapter}.json"
    canonical_delta_path.parent.mkdir(parents=True, exist_ok=True)
    if Path(delta_path).resolve() != canonical_delta_path.resolve():
        shutil.copyfile(delta_path, canonical_delta_path)
    else:
        delta_text = canonical_delta_path.read_text(encoding="utf-8")
        canonical_delta_path.write_text(delta_text, encoding="utf-8")

    delta = _load_delta(canonical_delta_path)
    chapter_path = novel_dir / "chapters" / f"chapter-{chapter}.md"
    index_path = novel_dir / INDEX_PATH
    index = _read_json_or_empty(index_path)
    index.setdefault("version", 1)
    index.setdefault("chapters", {})
    index["updated_at"] = datetime.now(timezone.utc).isoformat()
    index["chapters"][str(chapter)] = {
        "chapter_path": str(chapter_path.relative_to(novel_dir)),
        "delta_path": str(canonical_delta_path.relative_to(novel_dir)),
        "chapter_mtime": chapter_path.stat().st_mtime,
        "delta_mtime": canonical_delta_path.stat().st_mtime,
        "committed_at": datetime.now(timezone.utc).isoformat(),
        "mode": _delta_mode(delta),
        "summary": delta["summary"],
        "quality_metrics": delta.get("quality_metrics", {}),
        "state_delta": delta["state_delta"],
        "review": delta["review"],
    }
    _write_json(index_path, index)
    _render_generated_files(novel_dir, index)
    return result


def audit(novel_dir: Path) -> ValidationResult:
    novel_dir = Path(novel_dir)
    errors: list[str] = []
    warnings: list[str] = []
    index = _read_json_or_empty(novel_dir / INDEX_PATH)
    indexed_chapters = set(index.get("chapters", {}).keys())

    for chapter in _chapter_numbers(novel_dir):
        chapter_key = str(chapter)
        chapter_path = novel_dir / "chapters" / f"chapter-{chapter}.md"
        delta_path = novel_dir / "state" / "deltas" / f"chapter-{chapter}.json"
        if not delta_path.exists():
            errors.append(f"Chapter {chapter} has no delta file.")
            continue
        validation = validate_delta(novel_dir, chapter, delta_path)
        errors.extend(validation.errors)
        warnings.extend(validation.warnings)
        if chapter_key not in indexed_chapters:
            errors.append(f"Chapter {chapter} has not been committed to chapter-index.json.")
            continue
        if chapter_path.stat().st_mtime > delta_path.stat().st_mtime + 0.001:
            errors.append(f"Chapter {chapter} is newer than its delta; rebuild chapter delta before continuing.")

    max_chapter = _max_committed_chapter(index)
    for chapter_key in sorted(index.get("chapters", {}), key=lambda value: int(value)):
        for thread in index["chapters"][chapter_key].get("state_delta", {}).get("threads", []):
            action = thread.get("action")
            target = thread.get("target_chapter")
            if action in {"paid_off", "closed", "retired"} or not isinstance(target, int):
                continue
            if target <= max_chapter:
                errors.append(
                    f"Chapter {chapter_key} has overdue thread {thread.get('id', '')}: "
                    f"target chapter {target}, latest committed chapter {max_chapter}."
                )

    return ValidationResult(not errors, errors, warnings)


def rebuild_from(novel_dir: Path, from_chapter: int) -> ValidationResult:
    novel_dir = Path(novel_dir)
    errors: list[str] = []
    warnings: list[str] = []
    for chapter in _chapter_numbers(novel_dir):
        if chapter < from_chapter:
            continue
        delta_path = novel_dir / "state" / "deltas" / f"chapter-{chapter}.json"
        if not delta_path.exists():
            errors.append(f"Chapter {chapter} has no delta file.")
            continue
        result = commit_delta(novel_dir, chapter, delta_path)
        errors.extend(result.errors)
        warnings.extend(result.warnings)
        if not result.ok:
            break
    return ValidationResult(not errors, errors, warnings)


def save_free_draft(novel_dir: Path, chapter: int, draft_text: str) -> ValidationResult:
    novel_dir = Path(novel_dir)
    output = novel_dir / "drafts" / f"chapter-{chapter}-free-draft.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(draft_text, encoding="utf-8")
    return ValidationResult(True, [], ["Free draft saved; project state was not updated."])


def save_fragment_draft(novel_dir: Path, draft_text: str, chapter: Optional[int] = None) -> ValidationResult:
    novel_dir = Path(novel_dir)
    if chapter is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = novel_dir / "drafts" / f"fragment-continue-{stamp}.md"
    else:
        output = novel_dir / "drafts" / f"chapter-{chapter}-fragment-continue.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(draft_text, encoding="utf-8")
    return ValidationResult(True, [], ["Fragment continuation saved; project state was not updated."])


def assemble_context(novel_dir: Path, chapter: int, output_path: Optional[Path] = None) -> ValidationResult:
    novel_dir = Path(novel_dir)
    errors: list[str] = []
    warnings: list[str] = []
    index = _read_json_or_empty(novel_dir / INDEX_PATH)
    if not index:
        errors.append("chapter-index.json not found. Commit at least one chapter delta before assembling context.")
        return ValidationResult(False, errors, warnings)

    output_path = output_path or novel_dir / "generated" / f"context-pack-chapter-{chapter}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# Context Pack: Chapter {chapter}",
        "",
        "Generated from committed chapter deltas. Use this as the default context entry for drafting.",
        "",
    ]

    context_brief = novel_dir / "context-brief.md"
    if context_brief.exists():
        lines.extend(["## Context Brief", "", context_brief.read_text(encoding="utf-8").strip(), ""])
    else:
        warnings.append("context-brief.md not found.")

    lines.extend(["## Prior Chapter Summaries", ""])
    for chapter_key in sorted(index.get("chapters", {}), key=lambda value: int(value)):
        prior_chapter = int(chapter_key)
        if prior_chapter >= chapter:
            continue
        summary = index["chapters"][chapter_key]["summary"]
        lines.extend([
            f"### Chapter {chapter_key}",
            "",
            summary["first_sentence"],
            "",
            summary["what_happened"],
            "",
            summary["character_developments"],
            "",
            summary["narrative_significance"],
            "",
        ])

    lines.extend(["## Active Thread Cards", ""])
    has_thread = False
    for chapter_key in sorted(index.get("chapters", {}), key=lambda value: int(value)):
        if int(chapter_key) >= chapter:
            continue
        for thread in index["chapters"][chapter_key].get("state_delta", {}).get("threads", []):
            if thread.get("action") in {"closed", "retired"}:
                continue
            has_thread = True
            lines.append(
                f"- {thread.get('id', '')} ({thread.get('action', '')}, ch {chapter_key}): "
                f"{thread.get('reader_obligation') or thread.get('evidence', '')}"
            )
    if not has_thread:
        lines.append("- None recorded.")
    lines.append("")

    previous_chapter_path = novel_dir / "chapters" / f"chapter-{chapter - 1}.md"
    if previous_chapter_path.exists():
        lines.extend([
            f"## Voice Anchor: Chapter {chapter - 1}",
            "",
            previous_chapter_path.read_text(encoding="utf-8").strip(),
            "",
        ])
    elif chapter > 1:
        warnings.append(f"Voice anchor missing: {previous_chapter_path}")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    return ValidationResult(not errors, errors, warnings)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and commit NovelFlow chapter deltas.")
    parser.add_argument("command", choices=("validate-delta", "commit-delta", "audit", "assemble-context", "rebuild", "save-free-draft", "save-fragment-draft"))
    parser.add_argument("--novel-dir", default="novel", type=Path)
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--from-chapter", type=int)
    parser.add_argument("--delta", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--text-file", type=Path)
    args = parser.parse_args()

    if args.command in {"validate-delta", "commit-delta", "assemble-context"} and args.chapter is None:
        parser.error("--chapter is required for validate-delta, commit-delta, and assemble-context")
    if args.command == "rebuild" and args.from_chapter is None:
        parser.error("--from-chapter is required for rebuild")
    if args.command == "save-free-draft" and (args.chapter is None or args.text_file is None):
        parser.error("--chapter and --text-file are required for save-free-draft")
    if args.command == "save-fragment-draft" and args.text_file is None:
        parser.error("--text-file is required for save-fragment-draft")

    if args.command == "validate-delta":
        result = validate_delta(args.novel_dir, args.chapter, args.delta)
    elif args.command == "commit-delta":
        result = commit_delta(args.novel_dir, args.chapter, args.delta)
    elif args.command == "assemble-context":
        result = assemble_context(args.novel_dir, args.chapter, args.output)
    elif args.command == "rebuild":
        result = rebuild_from(args.novel_dir, args.from_chapter)
    elif args.command == "save-free-draft":
        result = save_free_draft(args.novel_dir, args.chapter, args.text_file.read_text(encoding="utf-8"))
    elif args.command == "save-fragment-draft":
        result = save_fragment_draft(args.novel_dir, args.text_file.read_text(encoding="utf-8"), args.chapter)
    else:
        result = audit(args.novel_dir)

    for warning in result.warnings:
        print(f"WARNING: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.ok:
        print(f"OK: {args.command} completed.")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
