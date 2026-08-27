"""
Test suite for Anki Exporter tool.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))

from tools.export_anki import main as export_main


class TestAnkiExporter(unittest.TestCase):
    """Verify Anki decks generation and card counts."""

    @classmethod
    def setUpClass(cls):
        export_main()
        cls.anki_dir = COURSE_ROOT / "anki_decks"
        cls.js_data_path = COURSE_ROOT / "js" / "exam_data.js"

    def test_01_tsv_files_generated(self):
        """Verify all TSV files and exam_data.js exist and are non-empty."""
        qas_file = self.anki_dir / "ai_course_exam_qas.tsv"
        tasks_file = self.anki_dir / "ai_course_microtasks.tsv"
        cheat_file = self.anki_dir / "ai_course_3min_cheatsheets.tsv"

        self.assertTrue(qas_file.exists(), "ai_course_exam_qas.tsv missing")
        self.assertTrue(tasks_file.exists(), "ai_course_microtasks.tsv missing")
        self.assertTrue(cheat_file.exists(), "ai_course_3min_cheatsheets.tsv missing")
        self.assertTrue(self.js_data_path.exists(), "js/exam_data.js missing")

        # Check line counts
        qa_lines = qas_file.read_text(encoding="utf-8").strip().splitlines()
        self.assertGreaterEqual(len(qa_lines), 280, f"Expected >= 280 Q&A cards, found {len(qa_lines)}")

        task_lines = tasks_file.read_text(encoding="utf-8").strip().splitlines()
        self.assertGreaterEqual(len(task_lines), 170, f"Expected >= 170 task cards, found {len(task_lines)}")

        cheat_lines = cheat_file.read_text(encoding="utf-8").strip().splitlines()
        self.assertGreaterEqual(len(cheat_lines), 28, f"Expected >= 28 cheatsheet cards, found {len(cheat_lines)}")


if __name__ == "__main__":
    unittest.main()
