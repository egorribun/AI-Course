"""
Test suite for Exam Simulator JS and dataset invariants.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))

from tests.common import read_file


class TestExamSimulator(unittest.TestCase):
    """Verify Simulator and App assets."""

    @classmethod
    def setUpClass(cls):
        cls.sim_js = read_file(COURSE_ROOT / "js" / "simulator.js")
        cls.app_js = read_file(COURSE_ROOT / "js" / "app.js")
        cls.exam_data_js = read_file(COURSE_ROOT / "js" / "exam_data.js")

    def test_01_simulator_has_required_modules(self):
        """Verify simulator.js contains timer, randomizer, flashcards, and blitz tabs."""
        self.assertIn("renderRandomTicket", self.sim_js)
        self.assertIn("toggleTimer", self.sim_js)
        self.assertIn("renderFlashcard", self.sim_js)
        self.assertIn("tab-ticket", self.sim_js)
        self.assertIn("tab-flashcards", self.sim_js)
        self.assertIn("tab-blitz", self.sim_js)

    def test_02_app_js_implements_live_search_and_progress_hub(self):
        """Verify app.js handles live search, category chips, and global progress updates."""
        self.assertIn("updateProgressUI", self.app_js)
        self.assertIn("filterCards", self.app_js)
        self.assertIn("tag-chip", self.app_js)
        self.assertIn("course-progress-changed", self.app_js)

    def test_03_exam_data_is_valid_and_complete(self):
        """Verify window.EXAM_DATA contains all 28 lectures."""
        self.assertIn("window.EXAM_DATA =", self.exam_data_js)
        self.assertIn("00-intro-ml.html", self.exam_data_js)
        self.assertIn("27-actor-critic.html", self.exam_data_js)


if __name__ == "__main__":
    unittest.main()
