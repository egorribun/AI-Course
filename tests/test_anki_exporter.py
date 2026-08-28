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
        """Verify all TSV files and exam_data.js exist and match exact row counts."""
        qas_file = self.anki_dir / "ai_course_exam_qas.tsv"
        tasks_file = self.anki_dir / "ai_course_microtasks.tsv"
        cheat_file = self.anki_dir / "ai_course_3min_cheatsheets.tsv"

        self.assertTrue(qas_file.exists(), "ai_course_exam_qas.tsv missing")
        self.assertTrue(tasks_file.exists(), "ai_course_microtasks.tsv missing")
        self.assertTrue(cheat_file.exists(), "ai_course_3min_cheatsheets.tsv missing")
        self.assertTrue(self.js_data_path.exists(), "js/exam_data.js missing")

        # Check line counts (including header)
        qa_lines = qas_file.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(qa_lines), 297, f"Expected 297 lines (1 header + 296 cards), found {len(qa_lines)}")

        task_lines = tasks_file.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(task_lines), 171, f"Expected 171 lines (1 header + 170 cards), found {len(task_lines)}")

        cheat_lines = cheat_file.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(cheat_lines), 29, f"Expected 29 lines (1 header + 28 cards), found {len(cheat_lines)}")

    def test_02_exam_data_js_structure_and_types(self):
        """Verify js/exam_data.js defines window.EXAM_DATA with 28 valid lecture items."""
        import json
        content = self.js_data_path.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("/** Pre-compiled dataset for DL Exam Course Simulator **/"))
        self.assertIn("window.EXAM_DATA = ", content)

        json_text = content.split("window.EXAM_DATA = ", 1)[1].rstrip(";\n ")
        data = json.loads(json_text)

        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 28, f"Expected 28 lectures in EXAM_DATA, got {len(data)}")

        total_qas = 0
        total_tasks = 0
        for item in data:
            self.assertIn("id", item)
            self.assertIn("filename", item)
            self.assertIn("title", item)
            self.assertIn("ticket", item)
            self.assertIn("qas", item)
            self.assertIn("tasks", item)
            self.assertIn("cheat_items", item)
            self.assertIsInstance(item["qas"], list)
            self.assertIsInstance(item["tasks"], list)
            self.assertIsInstance(item["cheat_items"], list)
            total_qas += len(item["qas"])
            total_tasks += len(item["tasks"])

        self.assertEqual(total_qas, 296, f"Expected 296 total Q&As in EXAM_DATA, got {total_qas}")
        self.assertEqual(total_tasks, 170, f"Expected 170 total tasks in EXAM_DATA, got {total_tasks}")

    def test_03_ticket_mapping_coverage(self):
        """Verify all 25 official exam tickets are mapped across the 28 lectures."""
        import json
        content = self.js_data_path.read_text(encoding="utf-8")
        json_text = content.split("window.EXAM_DATA = ", 1)[1].rstrip(";\n ")
        data = json.loads(json_text)

        tickets = [item["ticket"] for item in data]
        for t_idx in range(1, 26):
            expected = f"Билет {t_idx}"
            self.assertTrue(
                any(expected in t for t in tickets),
                f"Ticket {expected} missing in EXAM_DATA mapping"
            )

    def test_04_tsv_utf8_without_bom(self):
        """Verify all TSV files are valid UTF-8 and contain no BOM bytes."""
        for tsv_name in ["ai_course_exam_qas.tsv", "ai_course_microtasks.tsv", "ai_course_3min_cheatsheets.tsv"]:
            raw = (self.anki_dir / tsv_name).read_bytes()
            self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), f"{tsv_name} contains unexpected UTF-8 BOM")
            # Ensure valid UTF-8 decoding
            decoded = raw.decode("utf-8")
            self.assertTrue(len(decoded) > 0)


if __name__ == "__main__":
    unittest.main()
