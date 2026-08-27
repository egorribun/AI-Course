"""
Test suite for CSS Theme Engine, Interactive Widgets, and Print Styles.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))

from tests.common import read_file


class TestThemeAndStyles(unittest.TestCase):
    """Verify theme engine, simulator styles, and CSS invariants."""

    @classmethod
    def setUpClass(cls):
        cls.style_css_path = COURSE_ROOT / "style.css"
        cls.style_content = read_file(cls.style_css_path)

    def test_01_light_and_dark_theme_variables_exist(self):
        """Verify CSS root and light/dark theme variables are defined."""
        self.assertIn(":root", self.style_content)
        self.assertIn('[data-theme="light"]', self.style_content)
        self.assertIn("--bg", self.style_content)
        self.assertIn("--text", self.style_content)
        self.assertIn("--card", self.style_content)
        self.assertIn("--accent", self.style_content)

    def test_02_interactive_widget_classes_defined(self):
        """Verify styles for exam simulator, flashcards, timer, progress bars, and copy buttons exist."""
        required_selectors = [
            ".sim-container",
            ".timer-display",
            ".flashcard",
            ".progress-hub",
            ".copy-btn",
            ".reading-progress",
            ".back-to-top",
            ".theme-toggle",
            ".search-input",
            ".tag-chip",
        ]
        for sel in required_selectors:
            self.assertIn(sel, self.style_content, f"Missing required CSS selector: {sel}")

    def test_03_print_media_styles_present(self):
        """Verify @media print styles exist for clean physical printing."""
        self.assertIn("@media print", self.style_content)

    def test_04_summary_marker_suppression_rules_preserved(self):
        """Verify required marker suppression rules for details/summary are preserved in style.css."""
        self.assertIn(".task details summary", self.style_content)
        self.assertIn(".qa > summary", self.style_content)
        self.assertIn("transform: rotate(90deg)", self.style_content)


if __name__ == "__main__":
    unittest.main()
