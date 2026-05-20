import json
import time
import tempfile
import unittest
from pathlib import Path

import novelflow


def write_project(root: Path, chapter_text: str, delta: dict) -> tuple[Path, Path]:
    novel = root / "novel"
    chapters = novel / "chapters"
    deltas = novel / "state" / "deltas"
    chapters.mkdir(parents=True)
    deltas.mkdir(parents=True)
    chapter_path = chapters / "chapter-1.md"
    delta_path = deltas / "chapter-1.json"
    chapter_path.write_text(chapter_text, encoding="utf-8")
    delta_path.write_text(json.dumps(delta, ensure_ascii=False), encoding="utf-8")
    return novel, delta_path


def write_chapter_delta(novel: Path, chapter: int, chapter_text: str, delta: dict) -> Path:
    chapter_path = novel / "chapters" / f"chapter-{chapter}.md"
    delta_path = novel / "state" / "deltas" / f"chapter-{chapter}.json"
    chapter_path.parent.mkdir(parents=True, exist_ok=True)
    delta_path.parent.mkdir(parents=True, exist_ok=True)
    chapter_path.write_text(chapter_text, encoding="utf-8")
    delta["chapter"] = chapter
    delta_path.write_text(json.dumps(delta, ensure_ascii=False), encoding="utf-8")
    return delta_path


def valid_delta() -> dict:
    return {
        "mode": "production",
        "chapter": 1,
        "summary": {
            "first_sentence": "Mira finds the brass key and realizes the archive door can be opened.",
            "what_happened": "Mira finds the brass key.",
            "character_developments": "Mira chooses secrecy over trust.",
            "narrative_significance": "The archive thread becomes actionable.",
        },
        "quality_metrics": {
            "word_count": 1200,
            "scene_count": 1,
            "rendered_dialogue_blocks": 4,
            "summary_bridge_count": 1,
            "sensory_first_500": {
                "visual": 2,
                "tactile": 1,
                "auditory": 1,
            },
            "emotional_turns": [
                {
                    "from": "caution",
                    "to": "resolve",
                    "evidence": "Mira closed her fist around the brass key.",
                }
            ],
            "conflict_turns": [
                {
                    "scene": 1,
                    "irreversible_change": "Mira hides the brass key from Tomas.",
                    "evidence": "She slipped the brass key into her sleeve before Tomas saw it.",
                }
            ],
        },
        "state_delta": {
            "characters": [],
            "threads": [
                {
                    "id": "T01",
                    "action": "planted",
                    "reader_obligation": "The reader expects the brass key to open the archive door.",
                    "evidence": "Mira closed her fist around the brass key.",
                }
            ],
            "world_facts": [],
            "continuity_locks": [],
        },
        "review": {
            "p0": [],
            "p1": [],
            "p2": [],
        },
    }


def standard_delta() -> dict:
    return {
        "mode": "standard",
        "chapter": 1,
        "summary": {
            "first_sentence": "Mira finds the brass key and realizes the archive door can be opened.",
            "what_happened": "Mira finds the brass key.",
            "character_developments": "Mira chooses secrecy over trust.",
            "narrative_significance": "The archive thread becomes actionable.",
        },
        "state_delta": {
            "characters": [],
            "threads": [
                {
                    "id": "T01",
                    "action": "planted",
                    "reader_obligation": "The reader expects the brass key to open the archive door.",
                    "evidence": "Mira closed her fist around the brass key.",
                }
            ],
            "world_facts": [],
            "continuity_locks": [],
        },
        "review": {
            "p0": [],
            "p1": [],
            "p2": [],
            "soft_notes": ["Sensory density can be improved later."],
        },
    }


class ValidateDeltaTests(unittest.TestCase):
    def test_valid_delta_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            novel, delta_path = write_project(Path(tmp), chapter, valid_delta())

            result = novelflow.validate_delta(novel, 1, delta_path)

            self.assertTrue(result.ok)
            self.assertEqual(result.errors, [])

    def test_standard_delta_does_not_require_full_quality_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            novel, delta_path = write_project(Path(tmp), chapter, standard_delta())

            result = novelflow.validate_delta(novel, 1, delta_path)

            self.assertTrue(result.ok)

    def test_thread_evidence_must_exist_in_chapter_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = "# Chapter 1: The Key\n\nMira found nothing but dust."
            novel, delta_path = write_project(Path(tmp), chapter, valid_delta())

            result = novelflow.validate_delta(novel, 1, delta_path)

            self.assertFalse(result.ok)
            self.assertTrue(any("evidence not found" in error for error in result.errors))

    def test_production_delta_still_requires_quality_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            delta = valid_delta()
            del delta["quality_metrics"]
            novel, delta_path = write_project(Path(tmp), chapter, delta)

            result = novelflow.validate_delta(novel, 1, delta_path)

            self.assertFalse(result.ok)
            self.assertTrue(any("quality_metrics" in error for error in result.errors))

    def test_invalid_mode_fails_even_with_production_metrics(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            delta = valid_delta()
            delta["mode"] = "free-draft"
            novel, delta_path = write_project(Path(tmp), chapter, delta)

            result = novelflow.validate_delta(novel, 1, delta_path)

            self.assertFalse(result.ok)
            self.assertTrue(any("mode" in error for error in result.errors))

    def test_free_draft_writes_scratch_without_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            novel = Path(tmp) / "novel"
            draft_text = "# Chapter 1: The Key\n\nA looser alternate opening."

            result = novelflow.save_free_draft(novel, 1, draft_text)

            self.assertTrue(result.ok)
            self.assertTrue((novel / "drafts" / "chapter-1-free-draft.md").exists())
            self.assertFalse((novel / "state" / "deltas" / "chapter-1.json").exists())

    def test_fragment_continue_saves_timestamped_scratch_without_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            novel = Path(tmp) / "novel"
            draft_text = "Mira held the brass key tighter and kept walking."

            result = novelflow.save_fragment_draft(novel, draft_text)

            self.assertTrue(result.ok)
            drafts = list((novel / "drafts").glob("fragment-continue-*.md"))
            self.assertEqual(len(drafts), 1)
            self.assertIn(draft_text, drafts[0].read_text(encoding="utf-8"))
            self.assertFalse((novel / "state" / "deltas").exists())

    def test_fragment_continue_can_save_chapter_specific_scratch_without_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            novel = Path(tmp) / "novel"
            draft_text = "Mira held the brass key tighter and kept walking."

            result = novelflow.save_fragment_draft(novel, draft_text, chapter=3)

            self.assertTrue(result.ok)
            self.assertTrue((novel / "drafts" / "chapter-3-fragment-continue.md").exists())
            self.assertFalse((novel / "state" / "deltas").exists())

    def test_p2_blocks_commit_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            delta = valid_delta()
            delta["review"]["p2"] = ["Archive payoff contradicts outline."]
            novel, delta_path = write_project(Path(tmp), chapter, delta)

            result = novelflow.validate_delta(novel, 1, delta_path)

            self.assertFalse(result.ok)
            self.assertTrue(any("P2" in error for error in result.errors))

    def test_commit_delta_updates_index_and_generated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            novel, delta_path = write_project(Path(tmp), chapter, valid_delta())

            result = novelflow.commit_delta(novel, 1, delta_path)

            self.assertTrue(result.ok)
            index = json.loads((novel / "state" / "chapter-index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["chapters"]["1"]["summary"]["what_happened"], "Mira finds the brass key.")
            self.assertIn("## Chapter 1", (novel / "generated" / "summaries.md").read_text(encoding="utf-8"))
            self.assertIn("| 1 | 1200 | 1 | 4 | 0 | 0 | 0 |", (novel / "generated" / "progress.md").read_text(encoding="utf-8"))
            self.assertIn("| T01 | 1 | planted |", (novel / "generated" / "thread-ledger.md").read_text(encoding="utf-8"))
            self.assertIn("Mira chooses secrecy", (novel / "generated" / "story-state.md").read_text(encoding="utf-8"))

    def test_audit_reports_stale_delta_when_chapter_is_newer(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            novel, delta_path = write_project(Path(tmp), chapter, valid_delta())
            novelflow.commit_delta(novel, 1, delta_path)
            time.sleep(0.02)
            (novel / "chapters" / "chapter-1.md").write_text(chapter + "\n\nA later edit.", encoding="utf-8")

            result = novelflow.audit(novel)

            self.assertFalse(result.ok)
            self.assertTrue(any("newer than its delta" in error for error in result.errors))

    def test_invalid_thread_action_fails_validation(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            delta = valid_delta()
            delta["state_delta"]["threads"][0]["action"] = "kind-of-mentioned"
            novel, delta_path = write_project(Path(tmp), chapter, delta)

            result = novelflow.validate_delta(novel, 1, delta_path)

            self.assertFalse(result.ok)
            self.assertTrue(any("unsupported thread action" in error for error in result.errors))

    def test_assemble_context_writes_context_pack(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            novel, delta_path = write_project(Path(tmp), chapter, valid_delta())
            (novel / "context-brief.md").write_text("# Context Brief\n\nPremise line.", encoding="utf-8")
            novelflow.commit_delta(novel, 1, delta_path)

            output = novel / "generated" / "context-pack-chapter-2.md"
            result = novelflow.assemble_context(novel, 2, output)

            self.assertTrue(result.ok)
            text = output.read_text(encoding="utf-8")
            self.assertIn("# Context Pack: Chapter 2", text)
            self.assertIn("Premise line.", text)
            self.assertIn("Mira finds the brass key", text)
            self.assertIn("Voice Anchor", text)

    def test_audit_reports_overdue_thread(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            novel, delta_path = write_project(Path(tmp), chapter, valid_delta())
            delta = valid_delta()
            delta["state_delta"]["threads"][0]["target_chapter"] = 1
            delta_path.write_text(json.dumps(delta, ensure_ascii=False), encoding="utf-8")
            novelflow.commit_delta(novel, 1, delta_path)

            result = novelflow.audit(novel)

            self.assertFalse(result.ok)
            self.assertTrue(any("overdue thread" in error for error in result.errors))

    def test_rebuild_from_refreshes_stale_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            chapter = (
                "# Chapter 1: The Key\n\n"
                "Mira closed her fist around the brass key. "
                "She slipped the brass key into her sleeve before Tomas saw it."
            )
            novel, delta_path = write_project(Path(tmp), chapter, valid_delta())
            novelflow.commit_delta(novel, 1, delta_path)
            time.sleep(0.02)
            (novel / "chapters" / "chapter-1.md").write_text(chapter + "\n\nA later edit.", encoding="utf-8")

            result = novelflow.rebuild_from(novel, 1)

            self.assertTrue(result.ok)
            audit = novelflow.audit(novel)
            self.assertTrue(audit.ok)


if __name__ == "__main__":
    unittest.main()
