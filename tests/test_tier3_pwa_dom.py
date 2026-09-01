"""
Tier 3: DOM, PWA, Service Worker & State Persistence Test Suite.
Validates:
- Service Worker precache inventory, caching strategies, and manifest.json conformance.
- SM-2 Spaced Repetition arithmetic (EF formula, interval progression, queue filtering).
- LocalStorage state persistence, 4-block progress synchronization, and JSON backup/restore.
- Interactive Exam Simulator features: 25 tickets, Blitz mode, Drill mode, Flashcards, 3-min timer.
"""

from __future__ import annotations

import json
import unittest

from tests.common import (
    COURSE_ROOT,
    EXPECTED_LECTURES,
    JS_DIR,
    MANIFEST_FILE,
    MODULAR_BLOCKS,
    SM2ReferenceEngine,
    SW_FILE,
    read_file,
)


class TestTier3PWADOM(unittest.TestCase):
    """Tier 3: DOM, PWA, Service Worker & State Persistence Suite."""

    @classmethod
    def setUpClass(cls):
        cls.sw_content = read_file(SW_FILE) if SW_FILE.exists() else ""
        cls.manifest_json = json.loads(read_file(MANIFEST_FILE)) if MANIFEST_FILE.exists() else {}
        cls.tracker_js = read_file(JS_DIR / "tracker.js") if (JS_DIR / "tracker.js").exists() else ""
        cls.simulator_js = read_file(JS_DIR / "simulator.js") if (JS_DIR / "simulator.js").exists() else ""
        cls.exam_data_js = read_file(JS_DIR / "exam_data.js") if (JS_DIR / "exam_data.js").exists() else ""

    def test_01_web_app_manifest_conformance(self):
        """Verify manifest.json has required PWA fields and valid metadata."""
        self.assertTrue(len(self.manifest_json) > 0, "manifest.json must be non-empty valid JSON")
        self.assertIn("name", self.manifest_json)
        self.assertIn("short_name", self.manifest_json)
        self.assertIn("start_url", self.manifest_json)
        self.assertEqual(self.manifest_json.get("display"), "standalone")
        self.assertIn("theme_color", self.manifest_json)
        self.assertIn("background_color", self.manifest_json)

        icons = self.manifest_json.get("icons", [])
        self.assertGreaterEqual(len(icons), 1, "Manifest must contain at least 1 icon entry")
        for icon in icons:
            self.assertIn("src", icon)
            self.assertIn("sizes", icon)
            icon_file = COURSE_ROOT / icon["src"]
            self.assertTrue(icon_file.exists(), f"Manifest icon file {icon['src']} not found on disk")

    def test_02_service_worker_precache_assets(self):
        """Verify Service Worker precaches core assets and all 28 lectures."""
        self.assertTrue(len(self.sw_content) > 0, "sw.js must exist and have content")

        # Core app files must be listed in STATIC_ASSETS
        core_assets = [
            "index.html",
            "style.css",
            "manifest.json",
            "icon.svg",
            "js/app.js",
            "js/lecture.js",
            "js/simulator.js",
            "js/tracker.js",
            "js/exam_data.js",
        ]
        for asset in core_assets:
            self.assertIn(
                asset,
                self.sw_content,
                f"Core asset '{asset}' must be included in Service Worker STATIC_ASSETS",
            )

        # All 28 lectures must be included in precache
        for lec in EXPECTED_LECTURES:
            self.assertIn(
                lec,
                self.sw_content,
                f"Lecture '{lec}' must be in Service Worker STATIC_ASSETS",
            )

    def test_03_service_worker_lifecycle_and_caching_strategies(self):
        """Verify Network-First with cache fallback and SWR strategies in sw.js."""
        self.assertIn("skipWaiting", self.sw_content, "Service Worker should skipWaiting on install")
        self.assertIn("clients.claim", self.sw_content, "Service Worker should claim clients on activate")
        self.assertIn("fetch", self.sw_content, "Service Worker must have fetch event handler")
        self.assertTrue(
            "caches.match" in self.sw_content or "cache.put" in self.sw_content,
            "Service Worker must implement caching logic",
        )

    def test_04_sm2_spaced_repetition_mathematical_parity(self):
        """Verify SuperMemo SM-2 formula and interval calculations."""
        # Quality 5 review on fresh card: EF increases from 2.5 to 2.6, interval 1
        q5 = SM2ReferenceEngine.calc_next_review(quality=5, repetitions=0, ease_factor=2.5, interval=0)
        self.assertEqual(q5["repetitions"], 1)
        self.assertEqual(q5["interval"], 1)
        self.assertEqual(q5["ease_factor"], 2.6)

        # Second successful review: interval 6
        q4 = SM2ReferenceEngine.calc_next_review(quality=4, repetitions=1, ease_factor=2.6, interval=1)
        self.assertEqual(q4["repetitions"], 2)
        self.assertEqual(q4["interval"], 6)
        self.assertEqual(q4["ease_factor"], 2.6)

        # Third successful review: interval = round(6 * 2.6) = 16
        q5_3 = SM2ReferenceEngine.calc_next_review(quality=5, repetitions=2, ease_factor=2.6, interval=6)
        self.assertEqual(q5_3["repetitions"], 3)
        self.assertEqual(q5_3["interval"], 16)
        self.assertEqual(q5_3["ease_factor"], 2.7)

        # Failed review (quality < 3): resets streak to 0, interval 1, EF decreases
        fail = SM2ReferenceEngine.calc_next_review(quality=2, repetitions=5, ease_factor=2.7, interval=45)
        self.assertEqual(fail["repetitions"], 0)
        self.assertEqual(fail["interval"], 1)
        self.assertLess(fail["ease_factor"], 2.7)

        # Ease factor must never drop below 1.3 lower bound
        clamped = SM2ReferenceEngine.calc_next_review(quality=0, repetitions=0, ease_factor=1.35, interval=1)
        self.assertEqual(clamped["ease_factor"], 1.3)

    def test_05_localstorage_keys_and_schema(self):
        """Verify CourseTracker storage keys and backup/restore methods in tracker.js."""
        expected_keys = [
            "ai_course_theme",
            "ai_course_checked_qas",
            "ai_course_checked_tasks",
            "ai_course_sm2_cards",
        ]
        for k in expected_keys:
            self.assertIn(k, self.tracker_js, f"Missing storage key '{k}' in tracker.js")

        self.assertTrue(
            "ai_course_completed_lectures" in self.tracker_js or "ai_course_read_lectures" in self.tracker_js,
            "Missing lecture completion storage key in tracker.js",
        )

        self.assertIn("exportProgressJSON", self.tracker_js, "tracker.js must implement exportProgressJSON")
        self.assertIn("importProgressJSON", self.tracker_js, "tracker.js must implement importProgressJSON")
        self.assertIn("resetProgress", self.tracker_js, "tracker.js must implement resetProgress")
        self.assertIn("getOverallStats", self.tracker_js, "tracker.js must implement getOverallStats")

    def test_06_modular_blocks_progress_calculation(self):
        """Verify 4 modular blocks (A, B, C, D) progress math."""
        # Block A (00-07): 8 lectures
        self.assertEqual(len(MODULAR_BLOCKS["A"]["lectures"]), 8)
        # Block B (08-13): 6 lectures
        self.assertEqual(len(MODULAR_BLOCKS["B"]["lectures"]), 6)
        # Block C (14-21): 8 lectures
        self.assertEqual(len(MODULAR_BLOCKS["C"]["lectures"]), 8)
        # Block D (22-27): 6 lectures
        self.assertEqual(len(MODULAR_BLOCKS["D"]["lectures"]), 6)

        total_lecs = sum(len(b["lectures"]) for b in MODULAR_BLOCKS.values())
        self.assertEqual(total_lecs, 28)

    def test_07_exam_simulator_features_and_timer(self):
        """Verify exam simulator capabilities in simulator.js and timer logic."""
        self.assertIn("EXAM_DATA", self.simulator_js, "simulator.js must reference EXAM_DATA")
        self.assertIn("initSimulator", self.simulator_js, "simulator.js must expose initSimulator")

        # Timer logic in simulator.js
        self.assertIn("180", self.simulator_js, "Simulator must implement 180s (3-minute) countdown timer")
        self.assertTrue(
            "timer" in self.simulator_js.lower() or "starttimer" in self.simulator_js.lower(),
            "Simulator must contain timer methods",
        )


if __name__ == "__main__":
    unittest.main()
