"""
Test suite for JavaScript assets and CourseTracker integrity.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))

from tests.common import read_file


class TestJSAssetsAndTracker(unittest.TestCase):
    """Verify JS assets structure, methods, and contract invariants."""

    @classmethod
    def setUpClass(cls):
        cls.tracker_path = COURSE_ROOT / "js" / "tracker.js"
        cls.lecture_js_path = COURSE_ROOT / "js" / "lecture.js"
        cls.tracker_content = read_file(cls.tracker_path)
        cls.lecture_content = read_file(cls.lecture_js_path)

    def test_01_tracker_file_exists_and_has_required_methods(self):
        """Verify CourseTracker has full CRUD for theme, lectures, QAs, tasks, and stats."""
        required_signatures = [
            "getTheme",
            "setTheme",
            "toggleTheme",
            "getCompletedLectures",
            "isLectureCompleted",
            "setLectureCompleted",
            "toggleLecture",
            "getCheckedQAs",
            "isQAChecked",
            "setQAChecked",
            "toggleQA",
            "getCheckedTasks",
            "isTaskChecked",
            "setTaskChecked",
            "toggleTask",
            "getOverallStats",
            "exportProgressJSON",
            "importProgressJSON",
            "resetProgress",
        ]
        for sig in required_signatures:
            self.assertIn(sig, self.tracker_content, f"CourseTracker missing method: {sig}")

    def test_02_tracker_storage_keys_contract(self):
        """Verify expected LocalStorage keys are defined in tracker.js."""
        expected_keys = [
            "ai_course_theme",
            "ai_course_completed_lectures",
            "ai_course_checked_qas",
            "ai_course_checked_tasks",
        ]
        for key in expected_keys:
            self.assertIn(key, self.tracker_content, f"Missing storage key: {key}")

    def test_03_lecture_js_has_required_interactivity_hooks(self):
        """Verify lecture.js implements reading progress, code copy, checkmarks, and back-to-top."""
        self.assertIn("reading-progress", self.lecture_content)
        self.assertIn("copy-btn", self.lecture_content)
        self.assertIn("item-check", self.lecture_content)
        self.assertIn("back-to-top", self.lecture_content)
        self.assertIn("theme-toggle", self.lecture_content)


if __name__ == "__main__":
    unittest.main()
