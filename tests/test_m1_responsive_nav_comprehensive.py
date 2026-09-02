"""
Comprehensive Verification Test Suite for Milestone M1 (UI/UX Refactoring & Responsive Navigation).
Validates all requirements (R1 / Features F1-F7):
1. Desktop Header Action Button in index.html (>=768px).
2. Complete removal of exam simulator container and script from index.html.
3. Universal 4-item Bottom Navigation Bar across index.html, exam.html, and all 28 lectures/*.html.
4. Active indicator on exam tab in exam.html (aria-current="page").
5. Relative link paths in lectures bottom navigation.
6. Universal Progress Modal (#course-progress-modal) across all 30 HTML documents.
7. CSS Responsive rules, safe-area-insets, elevation of back-to-top, and >=44x44px touch targets.
8. JavaScript logic: URL search focus parameter, search button click, modal open/close, and theme sync.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))

from tests.common import (
    EXPECTED_LECTURES,
    INDEX_FILE,
    EXAM_FILE,
    LECTURES_DIR,
    STYLE_FILE,
    read_file,
)


class TestMilestone1ResponsiveNav(unittest.TestCase):
    """Deep verification of M1 UI/UX refactoring and responsive navigation contract."""

    @classmethod
    def setUpClass(cls):
        cls.index_html = read_file(INDEX_FILE)
        cls.exam_html = read_file(EXAM_FILE)
        cls.style_css = read_file(STYLE_FILE)
        cls.app_js = read_file(COURSE_ROOT / "js" / "app.js")
        cls.tracker_js = read_file(COURSE_ROOT / "js" / "tracker.js")
        cls.lecture_htmls = {
            lec_name: read_file(LECTURES_DIR / lec_name) for lec_name in EXPECTED_LECTURES
        }

    # -------------------------------------------------------------------------
    # Feature F1 & F2: Desktop Header Action & Simulator Removal in index.html
    # -------------------------------------------------------------------------
    def test_01_index_html_simulator_removed_and_header_button_added(self):
        """Verify simulator is removed from index.html body and header button is present."""
        # Simulator container must NOT be in index.html
        self.assertNotIn(
            'id="exam-simulator-container"',
            self.index_html,
            "id='exam-simulator-container' must be removed from index.html",
        )
        # simulator.js script must NOT be loaded in index.html head
        self.assertNotIn(
            'src="js/simulator.js"',
            self.index_html,
            "js/simulator.js should not be linked in index.html head",
        )

        # Header actions container and desktop exam button must exist
        self.assertIn(
            'class="header-actions"',
            self.index_html,
            "header.top .inner must contain .header-actions flex container",
        )
        self.assertIn(
            'class="btn-header-exam"',
            self.index_html,
            "Desktop exam button .btn-header-exam must exist in index.html header",
        )
        self.assertIn(
            'href="exam.html"',
            self.index_html,
            ".btn-header-exam must link to exam.html",
        )
        self.assertIn(
            "Тренажёр экзамена",
            self.index_html,
            ".btn-header-exam must have descriptive text",
        )

    # -------------------------------------------------------------------------
    # Feature F3: Bottom Navigation Bar in index.html and exam.html
    # -------------------------------------------------------------------------
    def test_02_index_and_exam_bottom_nav_bar_structure(self):
        """Verify .bottom-nav-bar structure and 4 action buttons in index.html and exam.html."""
        for name, html in [("index.html", self.index_html), ("exam.html", self.exam_html)]:
            self.assertIn(
                'class="bottom-nav-bar"',
                html,
                f"{name} must contain .bottom-nav-bar",
            )
            self.assertIn(
                'id="nav-search-btn"',
                html,
                f"{name} bottom nav must contain #nav-search-btn (Search)",
            )
            self.assertIn(
                'id="nav-exam-btn"',
                html,
                f"{name} bottom nav must contain #nav-exam-btn (Exam)",
            )
            self.assertIn(
                'id="nav-progress-btn"',
                html,
                f"{name} bottom nav must contain #nav-progress-btn (Progress)",
            )

        # In exam.html, nav-exam-btn must be marked active with aria-current="page"
        self.assertIn(
            'aria-current="page"',
            self.exam_html,
            "exam.html nav-exam-btn must have aria-current='page'",
        )
        self.assertIn(
            'class="bottom-nav-item active"',
            self.exam_html,
            "exam.html nav-exam-btn must have .active class",
        )

    # -------------------------------------------------------------------------
    # Feature F4: Bottom Navigation Bar in all 28 Lectures
    # -------------------------------------------------------------------------
    def test_03_all_28_lectures_have_bottom_nav_with_relative_paths(self):
        """Verify all 28 lectures contain .bottom-nav-bar with correct ../ relative paths."""
        self.assertEqual(len(self.lecture_htmls), 28, "Must verify all 28 lecture files")

        for lec_name, html in self.lecture_htmls.items():
            self.assertIn(
                'class="bottom-nav-bar"',
                html,
                f"{lec_name} must contain .bottom-nav-bar",
            )
            # Search button must link to ../index.html?focus=search
            self.assertIn(
                'href="../index.html?focus=search"',
                html,
                f"{lec_name} search nav button must link to ../index.html?focus=search",
            )
            # Exam button must link to ../exam.html
            self.assertIn(
                'href="../exam.html"',
                html,
                f"{lec_name} exam nav button must link to ../exam.html",
            )
            # Progress button
            self.assertIn(
                'id="nav-progress-btn"',
                html,
                f"{lec_name} must contain #nav-progress-btn",
            )

    # -------------------------------------------------------------------------
    # Feature F5: Universal Progress Modal (#course-progress-modal)
    # -------------------------------------------------------------------------
    def test_04_universal_progress_modal_in_all_30_documents(self):
        """Verify all 30 documents (index, exam, 28 lectures) contain #course-progress-modal markup."""
        all_docs = [("index.html", self.index_html), ("exam.html", self.exam_html)] + list(
            self.lecture_htmls.items()
        )
        self.assertEqual(len(all_docs), 30)

        for name, html in all_docs:
            self.assertIn(
                'id="course-progress-modal"',
                html,
                f"{name} must contain #course-progress-modal",
            )
            self.assertIn(
                'class="progress-modal-overlay"',
                html,
                f"{name} modal must have .progress-modal-overlay class",
            )
            self.assertIn(
                'role="dialog"',
                html,
                f"{name} modal must have role='dialog'",
            )
            self.assertIn(
                'aria-modal="true"',
                html,
                f"{name} modal must have aria-modal='true'",
            )
            self.assertIn(
                'id="modal-progress-close"',
                html,
                f"{name} modal must have close button #modal-progress-close",
            )
            self.assertIn(
                'id="modal-progress-fill"',
                html,
                f"{name} modal must have progress bar #modal-progress-fill",
            )
            self.assertIn(
                'id="modal-stat-lecs"',
                html,
                f"{name} modal must have #modal-stat-lecs stat element",
            )
            self.assertIn(
                'id="modal-stat-qas"',
                html,
                f"{name} modal must have #modal-stat-qas stat element",
            )
            self.assertIn(
                'id="modal-stat-tasks"',
                html,
                f"{name} modal must have #modal-stat-tasks stat element",
            )
            self.assertIn(
                'id="modal-reset-progress-btn"',
                html,
                f"{name} modal must have #modal-reset-progress-btn reset button",
            )

    # -------------------------------------------------------------------------
    # Feature F6: CSS Responsive Rules, Safe Area Insets & Elevation
    # -------------------------------------------------------------------------
    def test_05_css_responsive_navigation_and_safe_area_insets(self):
        """Verify CSS defines desktop hiding, mobile bottom bar, and safe area insets."""
        # Desktop header actions
        self.assertIn(".header-actions", self.style_css)
        self.assertIn(".btn-header-exam", self.style_css)

        # Bottom nav bar base (hidden on desktop)
        self.assertIn(".bottom-nav-bar", self.style_css)

        # Mobile media query (@media (max-width: 767px))
        self.assertIn("@media (max-width: 767px)", self.style_css)

        # Safe area inset support
        self.assertIn("env(safe-area-inset-bottom", self.style_css)

        # Elevation of back-to-top button above bottom bar on mobile
        self.assertTrue(
            "calc(80px + env(safe-area-inset-bottom" in self.style_css
            or "calc(92px + env(safe-area-inset-bottom" in self.style_css,
            "back-to-top must be elevated above bottom navigation bar",
        )

        # Touch targets >= 44px
        bni_match = re.search(r"\.bottom-nav-item\s*\{([^}]+)\}", self.style_css)
        self.assertIsNotNone(bni_match, ".bottom-nav-item class must exist in style.css")
        bni_rules = bni_match.group(1)
        self.assertIn("min-width: 44px", bni_rules)

        # Modal CSS styles
        self.assertIn(".progress-modal-overlay", self.style_css)
        self.assertIn(".progress-modal-content", self.style_css)
        self.assertIn(".modal-close-btn", self.style_css)

    # -------------------------------------------------------------------------
    # Feature F7: JavaScript Implementation Logic & Theme Sync
    # -------------------------------------------------------------------------
    def test_06_js_search_focus_and_modal_and_theme_sync(self):
        """Verify JavaScript logic in app.js and tracker.js for URL focus, modal, and theme sync."""
        # app.js handles focus query parameter
        self.assertIn("focus", self.app_js)
        self.assertIn("search", self.app_js)
        self.assertIn("scrollIntoView", self.app_js)

        # tracker.js implements initProgressModal
        self.assertIn("initProgressModal", self.tracker_js)
        self.assertIn("course-progress-modal", self.tracker_js)
        self.assertIn("modal-progress-close", self.tracker_js)
        self.assertIn("modal-reset-progress-btn", self.tracker_js)

        # tracker.js updates both header and bottom nav theme toggle buttons
        self.assertIn("updateThemeButtons", self.tracker_js)
        self.assertIn("bottom-nav-item", self.tracker_js)


if __name__ == "__main__":
    unittest.main()
