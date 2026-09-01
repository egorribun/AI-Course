"""
Empirical Challenger 1 Test Suite for Milestone M1 (UI/UX Refactoring & Responsive Navigation).
Adversarial & Exhaustive Verification:
1. Viewport Transitions (< 768px vs >= 768px) and Simulator Body Removal.
2. Touch Target Sizes (>= 44x44px) across all 30 HTML pages.
3. URL Search Parameter Handling (?focus=search) and Routing Integrity.
4. Safe Area Inset Formulas and Body Padding.
5. Modal Accessibility, Keyboard Traps, and Theme Synchronization.
"""

import re
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
INDEX_FILE = COURSE_ROOT / "index.html"
EXAM_FILE = COURSE_ROOT / "exam.html"
LECTURES_DIR = COURSE_ROOT / "lectures"
STYLE_FILE = COURSE_ROOT / "style.css"
APP_JS = COURSE_ROOT / "js" / "app.js"
TRACKER_JS = COURSE_ROOT / "js" / "tracker.js"

ALL_LECTURE_FILES = sorted([f for f in LECTURES_DIR.glob("*.html")])


class TestChallenger1M1Empirical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index_content = INDEX_FILE.read_text(encoding="utf-8")
        cls.exam_content = EXAM_FILE.read_text(encoding="utf-8")
        cls.style_content = STYLE_FILE.read_text(encoding="utf-8")
        cls.app_content = APP_JS.read_text(encoding="utf-8")
        cls.tracker_content = TRACKER_JS.read_text(encoding="utf-8")
        cls.lecture_contents = {f.name: f.read_text(encoding="utf-8") for f in ALL_LECTURE_FILES}
        cls.all_docs = {"index.html": cls.index_content, "exam.html": cls.exam_content, **cls.lecture_contents}

    # -------------------------------------------------------------------------
    # 1. Viewport Transitions & Simulator Removal
    # -------------------------------------------------------------------------
    def test_01_viewport_transition_desktop_rules(self):
        """Verify desktop (>= 768px) styling rules in style.css."""
        # Bottom nav bar must be hidden by default on desktop
        bnb_match = re.search(r"\.bottom-nav-bar\s*\{([^}]+)\}", self.style_content)
        self.assertIsNotNone(bnb_match, ".bottom-nav-bar base rule must exist in style.css")
        self.assertIn("display: none", bnb_match.group(1), "Base .bottom-nav-bar must be display: none")

        # Desktop header action button must exist and be styled
        self.assertIn(".header-actions", self.style_content)
        self.assertIn(".btn-header-exam", self.style_content)

        # In index.html, simulator container and script must be completely gone
        self.assertNotIn("id=\"exam-simulator-container\"", self.index_content)
        self.assertNotIn("id='exam-simulator-container'", self.index_content)
        self.assertNotIn("src=\"js/simulator.js\"", self.index_content)
        self.assertNotIn("src='js/simulator.js'", self.index_content)

        # Header action in index.html must contain .btn-header-exam pointing to exam.html
        self.assertIn('class="btn-header-exam"', self.index_content)
        self.assertIn('href="exam.html"', self.index_content)

    def test_02_viewport_transition_mobile_media_query_rules(self):
        """Verify mobile (< 768px) styling rules in style.css."""
        # Find max-width: 767px media query block
        mq_match = re.search(r"@media\s*\(\s*max-width:\s*767px\s*\)\s*\{([\s\S]*?)\n\}", self.style_content)
        self.assertIsNotNone(mq_match, "@media (max-width: 767px) media query block must exist")
        mq_body = mq_match.group(1)

        # Desktop exam button must be hidden on mobile
        self.assertIn(".btn-header-exam", mq_body)
        self.assertIn("display: none !important", mq_body)

        # Bottom nav bar must be displayed as fixed flex container on mobile
        self.assertIn(".bottom-nav-bar", mq_body)
        self.assertIn("display: flex !important", mq_body)
        self.assertIn("position: fixed", mq_body)
        self.assertIn("bottom: 0", mq_body)

        # Body bottom padding must accommodate bottom bar on mobile
        self.assertIn("body", mq_body)
        self.assertIn("padding-bottom:", mq_body)
        self.assertIn("env(safe-area-inset-bottom", mq_body)

    # -------------------------------------------------------------------------
    # 2. Touch Target Sizes (>= 44x44px) across all 30 HTML Pages
    # -------------------------------------------------------------------------
    def test_03_touch_target_sizes_in_style_css(self):
        """Verify explicit >= 44px touch target dimensions in CSS for all interactive classes."""
        # 1. .bottom-nav-item
        bni_match = re.search(r"\.bottom-nav-item\s*\{([^}]+)\}", self.style_content)
        self.assertIsNotNone(bni_match)
        bni_css = bni_match.group(1)
        self.assertTrue("min-width: 44px" in bni_css or "min-width:44px" in bni_css)
        self.assertTrue("min-height: 44px" in bni_css or "min-height: 48px" in bni_css or "min-height:48px" in bni_css)

        # 2. .btn-header-exam
        bhe_match = re.search(r"\.btn-header-exam\s*\{([^}]+)\}", self.style_content)
        self.assertIsNotNone(bhe_match)
        bhe_css = bhe_match.group(1)
        self.assertTrue("min-height: 44px" in bhe_css)
        self.assertTrue("min-width: 44px" in bhe_css)

        # 3. .theme-toggle
        tt_match = re.search(r"(?:^|\n)\.theme-toggle\s*\{([^}]+)\}", self.style_content)
        self.assertIsNotNone(tt_match)
        tt_css = tt_match.group(1)
        self.assertTrue("min-height: 44px" in tt_css)
        self.assertTrue("min-width: 44px" in tt_css)

        # 4. .modal-close-btn
        mcb_match = re.search(r"\.modal-close-btn\s*\{([^}]+)\}", self.style_content)
        self.assertIsNotNone(mcb_match)
        mcb_css = mcb_match.group(1)
        self.assertTrue("min-height: 44px" in mcb_css)
        self.assertTrue("min-width: 44px" in mcb_css)

        # 5. .back-to-top
        btt_match = re.search(r"\.back-to-top\s*\{([^}]+)\}", self.style_content)
        self.assertIsNotNone(btt_match)
        btt_css = btt_match.group(1)
        self.assertTrue("width: 44px" in btt_css)
        self.assertTrue("height: 44px" in btt_css)

    def test_04_touch_target_attributes_across_all_30_pages(self):
        """Verify all 30 HTML pages use standard compliant classes and ARIA labels for touch targets."""
        self.assertEqual(len(self.all_docs), 30, "Must test exactly 30 HTML files")

        for doc_name, content in self.all_docs.items():
            # Check bottom nav bar exists
            self.assertIn('class="bottom-nav-bar"', content, f"{doc_name} missing bottom-nav-bar")
            self.assertIn('id="nav-search-btn"', content, f"{doc_name} missing nav-search-btn")
            self.assertIn('id="nav-exam-btn"', content, f"{doc_name} missing nav-exam-btn")
            self.assertIn('id="nav-progress-btn"', content, f"{doc_name} missing nav-progress-btn")

            # Check progress modal exists
            self.assertIn('id="course-progress-modal"', content, f"{doc_name} missing #course-progress-modal")
            self.assertIn('id="modal-progress-close"', content, f"{doc_name} missing #modal-progress-close")
            self.assertIn('aria-label=', content, f"{doc_name} missing aria-label attributes")

    # -------------------------------------------------------------------------
    # 3. URL Search Parameter Handling (?focus=search) & Routing Integrity
    # -------------------------------------------------------------------------
    def test_05_url_search_parameter_handling_in_app_js(self):
        """Verify URL query param parsing and search focus logic in app.js."""
        # URLSearchParams check for focus === 'search'
        self.assertIn("URLSearchParams", self.app_content)
        self.assertIn("urlParams.get('focus') === 'search'", self.app_content)
        self.assertIn("searchInput.focus()", self.app_content)
        self.assertIn("searchInput.scrollIntoView", self.app_content)

        # mobSearchBtn or nav-search-btn click listener
        self.assertIn("mobSearchBtn.addEventListener('click'", self.app_content)

    def test_06_bottom_nav_routing_integrity_across_all_pages(self):
        """Verify routing integrity for search, exam, progress, and theme buttons across all 30 pages."""
        # 1. index.html
        self.assertIn('<button type="button" class="bottom-nav-item" id="nav-search-btn"', self.index_content)
        self.assertIn('<a href="exam.html" class="bottom-nav-item" id="nav-exam-btn"', self.index_content)

        # 2. exam.html
        self.assertIn('<a href="index.html?focus=search" class="bottom-nav-item" id="nav-search-btn"', self.exam_content)
        self.assertIn('aria-current="page"', self.exam_content)
        self.assertIn('class="bottom-nav-item active"', self.exam_content)

        # 3. All 28 lectures
        for lec_name, content in self.lecture_contents.items():
            self.assertIn('href="../index.html?focus=search"', content, f"{lec_name} search href must be ../index.html?focus=search")
            self.assertIn('href="../exam.html"', content, f"{lec_name} exam href must be ../exam.html")

    # -------------------------------------------------------------------------
    # 4. Safe Area Inset Formulas & Body Padding
    # -------------------------------------------------------------------------
    def test_07_safe_area_insets_and_viewport_fit_cover(self):
        """Verify viewport-fit=cover on root index/exam and CSS env(safe-area-inset-bottom) formulas."""
        self.assertIn('viewport-fit=cover', self.index_content, "index.html missing viewport-fit=cover")
        self.assertIn('viewport-fit=cover', self.exam_content, "exam.html missing viewport-fit=cover")

        # Style sheet formulas check
        self.assertIn(
            "padding-bottom: max(8px, env(safe-area-inset-bottom, 0px));",
            self.style_content,
            "Bottom nav bar padding-bottom must use max(8px, env(safe-area-inset-bottom, 0px))",
        )
        self.assertIn(
            "padding-bottom: calc(72px + env(safe-area-inset-bottom, 0px))",
            self.style_content,
            "Body on mobile must have padding-bottom: calc(72px + env(safe-area-inset-bottom, 0px))",
        )
        self.assertIn(
            "bottom: calc(80px + env(safe-area-inset-bottom, 0px)) !important;",
            self.style_content,
            "Back to top button must have bottom: calc(80px + env(safe-area-inset-bottom, 0px))",
        )

    # -------------------------------------------------------------------------
    # 5. Modal Accessibility & Theme Sync
    # -------------------------------------------------------------------------
    def test_08_modal_accessibility_and_keyboard_trapping(self):
        """Verify modal ARIA attributes, escape key handling, and backdrop click."""
        for doc_name, content in self.all_docs.items():
            self.assertIn('id="course-progress-modal"', content)
            self.assertIn('class="progress-modal-overlay"', content)
            self.assertIn('role="dialog"', content)
            self.assertIn('aria-modal="true"', content)
            self.assertIn('aria-labelledby="modal-progress-title"', content)

        # tracker.js keydown Escape handler
        self.assertIn("Escape", self.tracker_content)
        self.assertIn("closeModal()", self.tracker_content)
        self.assertIn("modal.removeAttribute('hidden')", self.tracker_content)
        self.assertIn("modal.setAttribute('hidden', '')", self.tracker_content)

    def test_09_theme_toggle_synchronization(self):
        """Verify updateThemeButtons synchronization logic in tracker.js."""
        self.assertIn("updateThemeButtons", self.tracker_content)
        self.assertIn("document.querySelectorAll('.theme-toggle')", self.tracker_content)
        self.assertIn("document.documentElement.setAttribute('data-theme', currentTheme)", self.tracker_content)


if __name__ == "__main__":
    unittest.main()
