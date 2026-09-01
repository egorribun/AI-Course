"""
Test suite for Milestone 1: Web Platform, PWA & EdTech UX Deliverables.
Validates manifest.json, sw.js, SM-2 Spaced Repetition Engine, Exam Simulator enhancements,
Global Keyboard Shortcuts, Print CSS, and WCAG 2.1 AA Accessibility rules.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_FILE = COURSE_ROOT / "manifest.json"
SW_FILE = COURSE_ROOT / "sw.js"
INDEX_FILE = COURSE_ROOT / "index.html"
STYLE_FILE = COURSE_ROOT / "style.css"
JS_APP_FILE = COURSE_ROOT / "js" / "app.js"
JS_LECTURE_FILE = COURSE_ROOT / "js" / "lecture.js"
JS_SIM_FILE = COURSE_ROOT / "js" / "simulator.js"
JS_TRACKER_FILE = COURSE_ROOT / "js" / "tracker.js"
JS_EXAM_DATA_FILE = COURSE_ROOT / "js" / "exam_data.js"


class TestMilestone1PwaWebPlatform(unittest.TestCase):
    """Verify all Milestone 1 deliverables and functional invariants."""

    @classmethod
    def setUpClass(cls):
        cls.manifest_text = MANIFEST_FILE.read_text(encoding="utf-8")
        cls.sw_text = SW_FILE.read_text(encoding="utf-8")
        cls.index_text = INDEX_FILE.read_text(encoding="utf-8")
        cls.style_text = STYLE_FILE.read_text(encoding="utf-8")
        cls.app_text = JS_APP_FILE.read_text(encoding="utf-8")
        cls.lecture_text = JS_LECTURE_FILE.read_text(encoding="utf-8")
        cls.sim_text = JS_SIM_FILE.read_text(encoding="utf-8")
        cls.tracker_text = JS_TRACKER_FILE.read_text(encoding="utf-8")

    # -------------------------------------------------------------
    # 1. Manifest.json Verification
    # -------------------------------------------------------------
    def test_01_manifest_json_structure_and_fields(self):
        """Verify manifest.json exists, parses, and has required PWA fields."""
        self.assertTrue(MANIFEST_FILE.exists(), "manifest.json must exist in root")
        data = json.loads(self.manifest_text)

        self.assertEqual(data.get("name"), "Курс Deep Learning — Подготовка к экзамену")
        self.assertEqual(data.get("short_name"), "DL Course")
        self.assertEqual(data.get("display"), "standalone")
        self.assertEqual(data.get("theme_color"), "#0f1115")
        self.assertEqual(data.get("background_color"), "#0f1115")
        self.assertIn("start_url", data)

        icons = data.get("icons", [])
        self.assertGreaterEqual(len(icons), 1, "manifest.json must have icon definitions")
        sizes = [icon.get("sizes") for icon in icons]
        self.assertTrue(any("192" in s for s in sizes), "Missing 192x192 icon definition")
        self.assertTrue(any("512" in s for s in sizes), "Missing 512x512 icon definition")

    # -------------------------------------------------------------
    # 2. Service Worker sw.js Verification
    # -------------------------------------------------------------
    def test_02_service_worker_caching_and_lifecycle(self):
        """Verify sw.js defines static asset precaching, install, activate, and Network-First fetch handlers."""
        self.assertTrue(SW_FILE.exists(), "sw.js must exist in root")
        self.assertIn("CACHE_NAME", self.sw_text)
        self.assertIn("ai-course-v3", self.sw_text, "CACHE_NAME must be 'ai-course-v3'")
        self.assertIn("STATIC_ASSETS", self.sw_text)

        # Ensure all 28 lectures are in STATIC_ASSETS
        for i in range(28):
            lec_pattern = f"{i:02d}-"
            self.assertIn(
                lec_pattern, self.sw_text, f"Lecture {i:02d} missing from sw.js STATIC_ASSETS"
            )

        # Ensure core static resources are precached
        self.assertIn("style.css", self.sw_text)
        self.assertIn("manifest.json", self.sw_text)
        self.assertIn("app.js", self.sw_text)
        self.assertIn("tracker.js", self.sw_text)
        self.assertIn("simulator.js", self.sw_text)
        self.assertIn("exam_data.js", self.sw_text)

        # Lifecycle events
        self.assertIn("self.addEventListener('install'", self.sw_text)
        self.assertIn("self.addEventListener('activate'", self.sw_text)
        self.assertIn("self.addEventListener('fetch'", self.sw_text)
        self.assertIn("skipWaiting", self.sw_text)
        self.assertIn("clients.claim", self.sw_text)

        # Network-First strategy for local same-origin assets
        self.assertIn(
            "fetch(req)", self.sw_text, "sw.js must use fetch(req) first for local assets"
        )
        self.assertIn("caches.match(req)", self.sw_text, "sw.js must fallback to caches.match(req)")

    # -------------------------------------------------------------
    # 3. index.html PWA Integration and Progress Hub Structure
    # -------------------------------------------------------------
    def test_03_index_html_pwa_tags_and_scripts(self):
        """Verify index.html includes manifest link, favicon, core components, and clean progress hub."""
        self.assertIn('<link rel="manifest" href="manifest.json">', self.index_text)
        self.assertIn('<meta name="theme-color" content="#0f1115">', self.index_text)
        self.assertIn('src="js/tracker.js"', self.index_text)
        self.assertIn('src="js/simulator.js"', self.index_text)
        self.assertIn('src="js/app.js"', self.index_text)
        self.assertIn('id="exam-simulator-container"', self.index_text)
        self.assertIn('id="global-progress-hub"', self.index_text)

        # Verify #global-progress-hub specifics for R1
        start_idx = self.index_text.find('id="global-progress-hub"')
        end_idx = self.index_text.find('id="exam-simulator-container"', start_idx)
        hub_text = (
            self.index_text[start_idx:end_idx]
            if end_idx != -1
            else self.index_text[start_idx : start_idx + 1500]
        )

        self.assertNotIn(
            "💾 Экспорт", hub_text, "💾 Экспорт must be removed from #global-progress-hub"
        )
        self.assertIn("🔄 Сброс", hub_text, "🔄 Сброс must be preserved in #global-progress-hub")
        self.assertIn('id="stat-lecs-val"', hub_text)
        self.assertIn('id="stat-qas-val"', hub_text)
        self.assertIn('id="stat-tasks-val"', hub_text)

    # -------------------------------------------------------------
    # 4. Spaced Repetition (SM-2 / Leitner) Engine in tracker.js
    # -------------------------------------------------------------
    def test_04_sm2_engine_in_tracker_js(self):
        """Verify tracker.js implements full SM-2 algorithm and persistence."""
        self.assertIn("ai_course_sm2_cards", self.tracker_text)
        self.assertIn("sm2:", self.tracker_text)
        self.assertIn("calculateNextState", self.tracker_text)
        self.assertIn("recordReview", self.tracker_text)
        self.assertIn("isCardDue", self.tracker_text)
        self.assertIn("getStats", self.tracker_text)
        self.assertIn("resetSM2", self.tracker_text)

        # Verify SM-2 formula structure in code
        self.assertIn("0.1 - (5 - q)", self.tracker_text)
        self.assertIn("Math.max(1.3", self.tracker_text)

    # -------------------------------------------------------------
    # 5. Exam Simulator Features in simulator.js
    # -------------------------------------------------------------
    def test_05_exam_simulator_features(self):
        """Verify simulator.js contains ticket dropdown, blitz mode, and ARIA roles."""
        self.assertIn("ticket-select-dropdown", self.sim_text)
        self.assertIn("tab-blitz", self.sim_text)
        self.assertIn("startBlitzSession", self.sim_text)
        self.assertIn("renderBlitzActiveQuestion", self.sim_text)
        self.assertIn("renderBlitzResults", self.sim_text)
        self.assertIn('role="tablist"', self.sim_text)
        self.assertIn('role="tab"', self.sim_text)
        self.assertIn('role="tabpanel"', self.sim_text)
        self.assertIn("aria-selected", self.sim_text)

    # -------------------------------------------------------------
    # 6. Global Keyboard Shortcuts in app.js and lecture.js
    # -------------------------------------------------------------
    def test_06_keyboard_shortcuts_and_input_bypass(self):
        """Verify app.js and lecture.js implement [, ], T, /, Alt+O shortcuts and bypass inputs."""
        for js_code in [self.app_text, self.lecture_text]:
            self.assertIn("addEventListener('keydown'", js_code)
            self.assertIn("active.tagName === 'INPUT'", js_code)
            self.assertIn("active.tagName === 'TEXTAREA'", js_code)
            self.assertIn("active.tagName === 'SELECT'", js_code)
            self.assertIn("isContentEditable", js_code)
            # T key for theme
            self.assertTrue(re.search(r"e\.key\s*===\s*['\"]t['\"]", js_code))
            # Alt+O for spoilers
            self.assertTrue(re.search(r"e\.altKey", js_code))
            # Print handlers
            self.assertIn("addEventListener('beforeprint'", js_code)
            self.assertIn("addEventListener('afterprint'", js_code)

        # Search focus '/' in app.js
        self.assertIn("e.key === '/'", self.app_text)
        self.assertIn("lecture-search-input", self.app_text)

    # -------------------------------------------------------------
    # 7. CSS Accessibility and Print Styles in style.css
    # -------------------------------------------------------------
    def test_07_css_accessibility_and_print(self):
        """Verify style.css includes :focus-visible outlines and print media queries."""
        self.assertIn(":focus-visible", self.style_text)
        self.assertIn("outline: 2px solid var(--accent)", self.style_text)
        self.assertIn("@media print", self.style_text)
        self.assertIn(".sim-tab-btn", self.style_text)
        self.assertIn(".flashcard", self.style_text)


if __name__ == "__main__":
    unittest.main()
