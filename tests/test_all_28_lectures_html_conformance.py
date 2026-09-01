"""
Strict conformance and structural invariance suite for all 28 HTML lectures.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))

from tests.common import EXPECTED_LECTURES, LECTURES_DIR, read_file


class TestAll28LecturesHTMLConformance(unittest.TestCase):
    """Verify each of the 28 lectures adheres 100% to the course contract."""

    def test_01_all_lectures_have_doctypes_and_metadata(self):
        """Verify all lectures have <!DOCTYPE html>, <meta charset="UTF-8">, viewport, and title."""
        for lec_name in EXPECTED_LECTURES:
            lec_path = LECTURES_DIR / lec_name
            self.assertTrue(lec_path.exists(), f"Lecture file missing: {lec_name}")
            content = read_file(lec_path)

            self.assertIn("<!DOCTYPE html>", content, f"{lec_name}: Missing <!DOCTYPE html>")
            self.assertIn('<meta charset="UTF-8">', content, f"{lec_name}: Missing utf-8 charset")
            self.assertIn('name="viewport"', content, f"{lec_name}: Missing viewport meta")
            self.assertIn("<title>", content, f"{lec_name}: Missing <title>")

    def test_02_all_lectures_link_style_css_and_modular_scripts(self):
        """Verify all lectures link to style.css, tracker.js, and lecture.js."""
        for lec_name in EXPECTED_LECTURES:
            lec_path = LECTURES_DIR / lec_name
            content = read_file(lec_path)

            self.assertIn(
                '<link rel="stylesheet" href="../style.css">',
                content,
                f"{lec_name}: Missing style.css",
            )
            self.assertIn(
                '<script src="../js/tracker.js"></script>',
                content,
                f"{lec_name}: Missing tracker.js",
            )
            self.assertIn(
                '<script src="../js/lecture.js"></script>',
                content,
                f"{lec_name}: Missing lecture.js",
            )
            self.assertNotIn(
                "<style>",
                content,
                f"{lec_name}: Embedded <style> tag should be removed (DRY violation)",
            )

    def test_03_all_lectures_have_backlinks_and_navrow(self):
        """Verify every lecture has a top backlink to index.html and a bottom navrow."""
        for lec_name in EXPECTED_LECTURES:
            lec_path = LECTURES_DIR / lec_name
            content = read_file(lec_path)

            self.assertIn(
                'href="../index.html"', content, f"{lec_name}: Missing backlink to ../index.html"
            )
            self.assertIn(
                'class="navrow"', content, f"{lec_name}: Missing .navrow footer navigation"
            )

    def test_04_all_lectures_have_exact_section_distribution(self):
        """Verify every lecture has >= 10 QA details and >= 6 task divs with solutions."""
        for lec_name in EXPECTED_LECTURES:
            lec_path = LECTURES_DIR / lec_name
            content = read_file(lec_path)

            qa_count = len(re.findall(r'<details\s+class=["\']qa["\']', content))
            task_count = len(re.findall(r'<div\s+class=["\']task["\']', content))

            self.assertGreaterEqual(
                qa_count, 10, f"{lec_name}: Has {qa_count} QAs (expected >= 10)"
            )
            self.assertGreaterEqual(
                task_count, 6, f"{lec_name}: Has {task_count} tasks (expected >= 6)"
            )


if __name__ == "__main__":
    unittest.main()
