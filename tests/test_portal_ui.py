"""
Test suite for Portal UI, Live Search, and Simulator DOM integration.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))

from tests.common import read_file, INDEX_FILE


class TestPortalUI(unittest.TestCase):
    """Verify index.html contains all interactive containers and linked assets."""

    @classmethod
    def setUpClass(cls):
        cls.index_content = read_file(INDEX_FILE)

    def test_01_index_html_links_style_css_and_scripts(self):
        """Verify index.html imports style.css and all required JS modules."""
        self.assertIn('<link rel="stylesheet" href="style.css">', self.index_content)
        self.assertIn('src="js/exam_data.js"', self.index_content)
        self.assertIn('src="js/tracker.js"', self.index_content)
        self.assertIn('src="js/simulator.js"', self.index_content)
        self.assertIn('src="js/app.js"', self.index_content)

    def test_02_index_html_has_progress_and_simulator_containers(self):
        """Verify index.html has progress hub, simulator container, and search input."""
        self.assertIn('id="global-progress-hub"', self.index_content)
        self.assertIn('id="exam-simulator-container"', self.index_content)
        self.assertIn('id="lecture-search-input"', self.index_content)
        self.assertIn('class="tag-chip"', self.index_content)

    def test_03_global_progress_hub_export_button_removed_and_reset_preserved(self):
        """Verify 💾 Экспорт is removed from #global-progress-hub while 🔄 Сброс and stats remain."""
        # Extract global-progress-hub section
        start_idx = self.index_content.find('id="global-progress-hub"')
        self.assertNotEqual(start_idx, -1, "global-progress-hub must exist")
        # Hub extends to next major section
        end_idx = self.index_content.find('id="exam-simulator-container"', start_idx)
        hub_html = (
            self.index_content[start_idx:end_idx]
            if end_idx != -1
            else self.index_content[start_idx : start_idx + 1500]
        )

        # Verify Export button is NOT present in progress hub
        self.assertNotIn(
            "💾 Экспорт", hub_html, "💾 Экспорт button must be removed from #global-progress-hub"
        )
        self.assertNotIn(
            "exportProgressJSON",
            hub_html,
            "exportProgressJSON onclick handler must not be in #global-progress-hub",
        )

        # Verify Reset button is present
        self.assertIn("🔄 Сброс", hub_html, "🔄 Сброс button must remain in #global-progress-hub")
        self.assertIn(
            "CourseTracker.resetProgress()",
            hub_html,
            "resetProgress handler must remain in #global-progress-hub",
        )

        # Verify progress bar and stat cards
        self.assertIn(
            'id="global-progress-fill"',
            hub_html,
            "global-progress-fill must remain in #global-progress-hub",
        )
        self.assertIn(
            'id="stat-lecs-val"', hub_html, "stat-lecs-val must remain in #global-progress-hub"
        )
        self.assertIn(
            'id="stat-qas-val"', hub_html, "stat-qas-val must remain in #global-progress-hub"
        )
        self.assertIn(
            'id="stat-tasks-val"', hub_html, "stat-tasks-val must remain in #global-progress-hub"
        )


if __name__ == "__main__":
    unittest.main()
