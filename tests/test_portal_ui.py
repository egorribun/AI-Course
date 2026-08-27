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


if __name__ == "__main__":
    unittest.main()
