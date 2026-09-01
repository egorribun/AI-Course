"""
Requirement R1 Tests: Syllabus & Coverage Audit.
State University of Management (GUU, 2026) DL Course Verification.

Verifies:
- All 28 lecture files exist and have substantial content.
- All 25 exam tickets from raw syllabus (dl_guu-dl_26/) are covered.
- index.html table and cards accurately map all 25 tickets to 28 lectures.
- Keyword and concept coverage in lectures matches ticket requirements.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

COURSE_ROOT_DIR = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT_DIR))

from tests.common import (
    DL_GUU_DIR,
    EXPECTED_LECTURES,
    INDEX_FILE,
    LECTURES_DIR,
    TICKETS_METADATA,
    read_file,
)


class TestR1Coverage(unittest.TestCase):
    """Test suite for Requirement R1: Syllabus & Coverage Audit."""

    def test_01_all_28_lecture_files_exist(self):
        """All 28 lecture HTML files must exist in lectures/ and be non-empty."""
        self.assertTrue(LECTURES_DIR.is_dir(), f"Lectures directory not found: {LECTURES_DIR}")

        missing = []
        empty_files = []
        for lec in EXPECTED_LECTURES:
            lec_path = LECTURES_DIR / lec
            if not lec_path.exists():
                missing.append(lec)
            elif lec_path.stat().st_size < 1000:
                empty_files.append(f"{lec} (size: {lec_path.stat().st_size}b)")

        self.assertEqual(missing, [], f"Missing {len(missing)} lecture files: {missing}")
        self.assertEqual(empty_files, [], f"Lectures with insufficient content (<1000b): {empty_files}")

    def test_02_syllabus_source_materials_exist(self):
        """Source syllabus materials in dl_guu-dl_26/ must exist and be accessible."""
        self.assertTrue(DL_GUU_DIR.is_dir(), f"Reference directory dl_guu-dl_26 not found: {DL_GUU_DIR}")

        required_files = ["вопросы.txt", "вопросы_ответы.md", "экзамен_важные_темы.md"]
        for fname in required_files:
            fpath = DL_GUU_DIR / fname
            self.assertTrue(fpath.is_file(), f"Missing syllabus file: {fname}")
            content = read_file(fpath)
            self.assertGreater(len(content), 100, f"Syllabus file {fname} is empty or too short")

    def test_03_extract_and_verify_all_25_tickets_from_syllabus(self):
        """Extract all 25 exam tickets from raw 'вопросы.txt'."""
        voprosy_path = DL_GUU_DIR / "вопросы.txt"
        content = read_file(voprosy_path)

        # Lines starting with digits
        ticket_lines = [line.strip() for line in content.splitlines() if re.match(r"^\d+\.", line.strip())]
        self.assertGreaterEqual(
            len(ticket_lines), 25, f"Expected at least 25 ticket entries in вопросы.txt, found {len(ticket_lines)}"
        )

    def test_04_index_html_mapping_table_covers_all_25_tickets(self):
        """index.html must cover all 25 tickets across its 4-block modular sections and lecture cards."""
        self.assertTrue(INDEX_FILE.is_file(), f"index.html not found: {INDEX_FILE}")
        content = read_file(INDEX_FILE)

        # Check 4-block overview table
        self.assertIn("Тематические блоки курса", content)
        self.assertIn("Билеты 1–7", content)
        self.assertIn("Билеты 8–12", content)
        self.assertIn("Билеты 13–20", content)
        self.assertIn("Билеты 21–25", content)

        # Extract ticket question numbers from lecture cards: <div class="n">ЛЕКЦИЯ X · ВОПРОС Y</div>
        card_kicker_numbers = re.findall(r"ВОПРОС\s*(\d+)", content)
        found_ticket_nums = {int(n) for n in card_kicker_numbers}
        # Check all tickets 1 to 25 are mapped across lecture cards
        missing_tickets = [t for t in range(1, 26) if t not in found_ticket_nums]
        self.assertEqual(
            missing_tickets, [], f"index.html lecture cards are missing tickets: {missing_tickets}"
        )

    def test_05_index_html_grid_cards_cover_all_28_lectures(self):
        """index.html lecture grid cards must link to all 28 lectures."""
        content = read_file(INDEX_FILE)
        card_hrefs = re.findall(r'<a\s+class=["\']lec["\']\s+href=["\']([^"\']+)["\']', content)

        mapped_lectures = {Path(h).name for h in card_hrefs}
        expected_set = set(EXPECTED_LECTURES)

        missing = expected_set - mapped_lectures
        self.assertEqual(missing, set(), f"index.html grid cards missing lectures: {missing}")

    def test_06_lecture_content_keyword_coverage_per_ticket(self):
        """Each of the 25 tickets must have theoretical keyword coverage in its designated lecture(s)."""
        coverage_report = {}

        for ticket_num, meta in TICKETS_METADATA.items():
            combined_text = ""
            for lec_file in meta["lectures"]:
                lec_path = LECTURES_DIR / lec_file
                if lec_path.is_file():
                    combined_text += read_file(lec_path).lower()

            missing_keywords = []
            for kw in meta["keywords"]:
                if kw.lower() not in combined_text:
                    missing_keywords.append(kw)

            coverage_report[ticket_num] = missing_keywords

        failed_tickets = {t: kws for t, kws in coverage_report.items() if len(kws) > len(TICKETS_METADATA[t]["keywords"]) // 2}
        self.assertEqual(
            failed_tickets,
            {},
            f"Tickets failing theoretical keyword coverage (>50% missing): {failed_tickets}",
        )


if __name__ == "__main__":
    unittest.main()
