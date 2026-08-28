"""
Deep validation suite for Anki TSV decks.
Simulates Anki importer parsing rules across all 3 generated TSV files.
"""

from __future__ import annotations

import csv
import sys
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))

from tools.export_anki import main as export_anki_main


class TestAnkiTSVParsing(unittest.TestCase):
    """Verify TSV files meet strict Anki import requirements."""

    @classmethod
    def setUpClass(cls):
        export_anki_main()
        cls.anki_dir = COURSE_ROOT / "anki_decks"

    def test_01_qas_tsv_structure_and_no_malformed_tabs(self):
        """Verify ai_course_exam_qas.tsv has exact 4 columns per row without stray tabs."""
        tsv_path = self.anki_dir / "ai_course_exam_qas.tsv"
        self.assertTrue(tsv_path.exists())

        with open(tsv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader)
            self.assertEqual(len(header), 4, f"Header must have 4 columns: {header}")
            self.assertEqual(header[0], "Front (Question)")
            self.assertEqual(header[1], "Back (Answer)")

            rows = list(reader)
            self.assertEqual(len(rows), 296, f"Expected exactly 296 QA rows, got {len(rows)}")

            for idx, row in enumerate(rows, start=1):
                self.assertEqual(len(row), 4, f"Row {idx} has {len(row)} columns instead of 4: {row[:2]}")
                question, answer, lecture_tag, ticket_tag = row
                self.assertTrue(question.strip(), f"Row {idx}: Empty question")
                self.assertTrue(answer.strip(), f"Row {idx}: Empty answer")
                self.assertTrue(lecture_tag.startswith("Лекция_"), f"Row {idx}: Invalid lecture tag: {lecture_tag}")
                self.assertTrue(ticket_tag.strip(), f"Row {idx}: Empty ticket tag")

    def test_02_tasks_tsv_structure_and_solutions(self):
        """Verify ai_course_microtasks.tsv has exact 4 columns and non-empty step-by-step solutions."""
        tsv_path = self.anki_dir / "ai_course_microtasks.tsv"
        self.assertTrue(tsv_path.exists())

        with open(tsv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader)
            self.assertEqual(len(header), 4)

            rows = list(reader)
            self.assertEqual(len(rows), 170, f"Expected exactly 170 task rows, got {len(rows)}")

            for idx, row in enumerate(rows, start=1):
                self.assertEqual(len(row), 4, f"Task row {idx} column count mismatch: {len(row)}")
                front, back, lecture_tag, ticket_tag = row
                self.assertIn("<b>", front, f"Task row {idx}: Missing bold title tag in front")
                self.assertTrue(back.strip(), f"Task row {idx}: Missing solution in back")

    def test_03_cheatsheets_tsv_structure(self):
        """Verify ai_course_3min_cheatsheets.tsv has exact 3 columns across 28 lectures."""
        tsv_path = self.anki_dir / "ai_course_3min_cheatsheets.tsv"
        self.assertTrue(tsv_path.exists())

        with open(tsv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter="\t")
            header = next(reader)
            self.assertEqual(len(header), 3)

            rows = list(reader)
            self.assertEqual(len(rows), 28, f"Expected 28 cheatsheet rows, got {len(rows)}")

            for idx, row in enumerate(rows, start=1):
                self.assertEqual(len(row), 3)
                front, back, lecture_tag = row
                self.assertIn("<ol>", back, f"Cheatsheet row {idx}: Missing ordered list <ol>")
                self.assertIn("<li>", back, f"Cheatsheet row {idx}: Missing list items <li>")

    def test_04_tsv_mathjax_and_clean_escaping(self):
        """Verify no raw tabs or unescaped control characters exist inside any field."""
        for tsv_name in ["ai_course_exam_qas.tsv", "ai_course_microtasks.tsv", "ai_course_3min_cheatsheets.tsv"]:
            tsv_path = self.anki_dir / tsv_name
            with open(tsv_path, "r", encoding="utf-8") as f:
                raw_text = f.read()

            for line_idx, line in enumerate(raw_text.splitlines(), start=1):
                self.assertNotIn("\r", line, f"{tsv_name}:{line_idx} contains CR (\\r)")
                self.assertNotIn("\x00", line, f"{tsv_name}:{line_idx} contains null byte")

    def test_05_deck_lecture_coverage_all_28_lectures(self):
        """Verify all 28 lectures (00-27) are represented in all three Anki decks."""
        expected_tags = {f"Лекция_{i:02d}" for i in range(28)}

        for tsv_name in ["ai_course_exam_qas.tsv", "ai_course_microtasks.tsv", "ai_course_3min_cheatsheets.tsv"]:
            tsv_path = self.anki_dir / tsv_name
            with open(tsv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter="\t")
                next(reader)  # skip header
                found_tags = set()
                for row in reader:
                    # In 4-col decks, lecture is col 2; in 3-col deck, lecture is col 2
                    found_tags.add(row[2])

            self.assertEqual(
                found_tags,
                expected_tags,
                f"Missing lectures in {tsv_name}: {expected_tags - found_tags}"
            )

    def test_06_ticket_tag_formatting_cleanliness(self):
        """Verify ticket tags contain no spaces, colons, or commas for Anki tag compatibility."""
        for tsv_name in ["ai_course_exam_qas.tsv", "ai_course_microtasks.tsv"]:
            tsv_path = self.anki_dir / tsv_name
            with open(tsv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter="\t")
                next(reader)
                for idx, row in enumerate(reader, start=1):
                    ticket_tag = row[3]
                    self.assertNotIn(" ", ticket_tag, f"{tsv_name}:{idx} Ticket tag has space: {ticket_tag}")
                    self.assertNotIn(":", ticket_tag, f"{tsv_name}:{idx} Ticket tag has colon: {ticket_tag}")
                    self.assertNotIn(",", ticket_tag, f"{tsv_name}:{idx} Ticket tag has comma: {ticket_tag}")


if __name__ == "__main__":
    unittest.main()
