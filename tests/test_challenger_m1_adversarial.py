"""
Empirical Challenger Test Suite for Milestone M1 (UI & PWA Modernization).
Validates Service Worker lifecycle, Network-First caching, cache version purge on activation,
offline navigation fallback, and DOM progress hub invariants.
"""

from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
SW_FILE = COURSE_ROOT / "sw.js"
INDEX_FILE = COURSE_ROOT / "index.html"
TRACKER_FILE = COURSE_ROOT / "js" / "tracker.js"
SIM_FILE = COURSE_ROOT / "js" / "simulator.js"


class TestChallengerM1ServiceWorker(unittest.TestCase):
    """Empirical verification of sw.js lifecycle, caching strategies, and asset integrity."""

    @classmethod
    def setUpClass(cls):
        cls.sw_content = SW_FILE.read_text(encoding="utf-8")

    def test_01_sw_cache_version_and_name(self):
        """Verify CACHE_NAME is bumped to ai-course-v3."""
        match = re.search(r"const\s+CACHE_NAME\s*=\s*['\"]([^'\"]+)['\"];", self.sw_content)
        self.assertIsNotNone(match, "CACHE_NAME definition not found in sw.js")
        cache_name = match.group(1)
        self.assertEqual(
            cache_name, "ai-course-v3", f"Expected CACHE_NAME='ai-course-v3', found '{cache_name}'"
        )

    def test_02_all_static_assets_exist_on_filesystem(self):
        """Verify every single asset in STATIC_ASSETS exists on disk and is non-empty."""
        match = re.search(r"const\s+STATIC_ASSETS\s*=\s*\[([\s\S]*?)\];", self.sw_content)
        self.assertIsNotNone(match, "STATIC_ASSETS array not found in sw.js")

        raw_assets = match.group(1)
        assets = [
            item.strip().strip("'\"") for item in raw_assets.split(",") if item.strip().strip("'\"")
        ]

        self.assertGreaterEqual(
            len(assets), 35, f"Expected at least 35 assets, found {len(assets)}"
        )

        # Check all 28 lectures
        for i in range(28):
            lec_pad = f"{i:02d}-"
            self.assertTrue(
                any(lec_pad in a for a in assets),
                f"Lecture {lec_pad} missing from sw.js precache list",
            )

        # Check existence on filesystem
        missing = []
        for asset in assets:
            rel = asset.lstrip("./")
            if rel == "" or rel == ".":
                target = COURSE_ROOT / "index.html"
            else:
                target = COURSE_ROOT / rel
            if not target.exists() or target.stat().st_size == 0:
                missing.append((asset, str(target)))

        self.assertEqual(missing, [], f"Missing or empty precached files: {missing}")

    def test_03_lifecycle_activation_and_cache_purge(self):
        """Verify sw.js deletes all old caches on activate and calls clients.claim()."""
        self.assertIn("self.addEventListener('activate'", self.sw_content)
        self.assertIn("caches.keys()", self.sw_content)
        self.assertIn("caches.delete", self.sw_content)
        self.assertIn("clients.claim()", self.sw_content)
        self.assertIn("skipWaiting()", self.sw_content)

    def test_04_network_first_strategy_for_same_origin(self):
        """Verify local same-origin assets use Network-First with cache fallback."""
        # Find fetch listener block
        fetch_idx = self.sw_content.find("addEventListener('fetch'")
        self.assertNotEqual(fetch_idx, -1, "fetch event listener missing")
        fetch_block = self.sw_content[fetch_idx:]

        # Must check method == 'GET' and protocol == http/https
        self.assertIn("req.method !== 'GET'", fetch_block)
        self.assertIn("url.protocol !== 'http:' && url.protocol !== 'https:'", fetch_block)

        # Must execute fetch(req) first
        self.assertIn("fetch(req)", fetch_block)
        self.assertIn("cache.put(req, responseToCache)", fetch_block)
        self.assertIn("caches.match(req)", fetch_block)

        # Must provide offline navigation fallback to index.html
        self.assertIn("req.mode === 'navigate'", fetch_block)
        self.assertIn("index.html", fetch_block)


class TestChallengerM1DOMAndUI(unittest.TestCase):
    """Empirical verification of index.html DOM structure, progress hub, and tracker invariants."""

    @classmethod
    def setUpClass(cls):
        cls.index_content = INDEX_FILE.read_text(encoding="utf-8")
        cls.tracker_content = TRACKER_FILE.read_text(encoding="utf-8")
        cls.sim_content = SIM_FILE.read_text(encoding="utf-8")

    def test_05_global_progress_hub_has_no_export_button(self):
        """Verify #global-progress-hub contains NO export button."""
        start_idx = self.index_content.find('id="global-progress-hub"')
        self.assertNotEqual(start_idx, -1, "global-progress-hub must exist")
        end_idx = self.index_content.find('id="exam-simulator-container"', start_idx)
        hub_html = (
            self.index_content[start_idx:end_idx]
            if end_idx != -1
            else self.index_content[start_idx : start_idx + 1500]
        )

        # R1: 💾 Экспорт must be completely absent from header
        self.assertNotIn("💾 Экспорт", hub_html, "Export button must not exist in progress hub")
        self.assertNotIn(
            "exportProgressJSON",
            hub_html,
            "exportProgressJSON onclick must not exist in progress hub",
        )

    def test_06_global_progress_hub_preserves_reset_and_stats(self):
        """Verify #global-progress-hub preserves reset button and stat card IDs."""
        start_idx = self.index_content.find('id="global-progress-hub"')
        end_idx = self.index_content.find('id="exam-simulator-container"', start_idx)
        hub_html = (
            self.index_content[start_idx:end_idx]
            if end_idx != -1
            else self.index_content[start_idx : start_idx + 1500]
        )

        self.assertIn("🔄 Сброс", hub_html, "Reset button must remain in progress hub")
        self.assertIn(
            "CourseTracker.resetProgress()",
            hub_html,
            "CourseTracker.resetProgress() must be invoked by reset button",
        )
        self.assertIn('id="global-progress-fill"', hub_html, "global-progress-fill must exist")
        self.assertIn('id="stat-lecs-val"', hub_html, "stat-lecs-val must exist")
        self.assertIn('id="stat-qas-val"', hub_html, "stat-qas-val must exist")
        self.assertIn('id="stat-tasks-val"', hub_html, "stat-tasks-val must exist")

    def test_07_course_tracker_methods_and_exam_data_preserved(self):
        """Verify CourseTracker has exportProgressJSON, importProgressJSON, resetProgress, and getOverallStats."""
        self.assertIn("exportProgressJSON()", self.tracker_content)
        self.assertIn("importProgressJSON(jsonStr)", self.tracker_content)
        self.assertIn("resetProgress()", self.tracker_content)
        self.assertIn("getOverallStats()", self.tracker_content)
        self.assertIn("window.EXAM_DATA", self.sim_content)


class TestChallengerM1NodeHarnessExecution(unittest.TestCase):
    """Run the Node.js adversarial Service Worker mock harness."""

    def test_08_run_node_adversarial_sw_harness(self):
        """Execute tests/adversarial_sw_m1.cjs and verify 0 failures."""
        harness_path = COURSE_ROOT / "tests" / "adversarial_sw_m1.cjs"
        self.assertTrue(harness_path.exists(), "adversarial_sw_m1.cjs missing")

        result = subprocess.run(
            ["node", str(harness_path)],
            cwd=str(COURSE_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
        )
        self.assertEqual(
            result.returncode,
            0,
            f"Adversarial SW harness failed with output:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}",
        )
        self.assertIn("Challenger M1 Results: 11 passed, 0 failed", result.stdout)


if __name__ == "__main__":
    unittest.main()
