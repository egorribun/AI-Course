import os
import re
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
SW_FILE = COURSE_ROOT / "sw.js"
INDEX_FILE = COURSE_ROOT / "index.html"
TRACKER_FILE = COURSE_ROOT / "js" / "tracker.js"


class TestM1ServiceWorkerEmpirical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sw_text = SW_FILE.read_text(encoding="utf-8")
        cls.index_text = INDEX_FILE.read_text(encoding="utf-8")
        cls.tracker_text = TRACKER_FILE.read_text(encoding="utf-8")

    def test_01_sw_cache_version_and_naming_invariants(self):
        """Verify CACHE_NAME is strictly bumped to 'ai-course-v3'."""
        match = re.search(r"const\s+CACHE_NAME\s*=\s*['\"]([^'\"]+)['\"]", self.sw_text)
        self.assertIsNotNone(match, "CACHE_NAME constant definition not found in sw.js")
        cache_name = match.group(1)
        self.assertEqual(cache_name, "ai-course-v3", f"Expected 'ai-course-v3', got '{cache_name}'")

    def test_02_sw_precache_assets_exist_and_non_empty(self):
        """Verify all static assets listed in STATIC_ASSETS exist on disk and have non-zero size."""
        match = re.search(r"const\s+STATIC_ASSETS\s*=\s*\[([\s\S]*?)\];", self.sw_text)
        self.assertIsNotNone(match, "STATIC_ASSETS array definition not found in sw.js")
        assets_raw = match.group(1)
        asset_paths = re.findall(r"['\"]([^'\"]+)['\"]", assets_raw)

        self.assertGreaterEqual(
            len(asset_paths),
            34,
            f"Expected >= 34 assets in STATIC_ASSETS, found {len(asset_paths)}",
        )

        for asset in asset_paths:
            if asset in (".", "./"):
                continue
            clean_path = asset.lstrip("./").replace("/", os.sep)
            file_path = COURSE_ROOT / clean_path
            self.assertTrue(
                file_path.exists(), f"Precache asset does not exist on disk: {asset} ({file_path})"
            )
            self.assertGreater(file_path.stat().st_size, 0, f"Precache asset is empty: {asset}")

    def test_03_sw_lifecycle_install_skip_waiting_and_cache_opening(self):
        """Verify install event handler opens CACHE_NAME, calls addAll, and invokes self.skipWaiting()."""
        self.assertIn("self.addEventListener('install'", self.sw_text)
        self.assertIn("caches.open(CACHE_NAME)", self.sw_text)
        self.assertIn("cache.addAll(STATIC_ASSETS)", self.sw_text)
        self.assertIn("self.skipWaiting()", self.sw_text)

    def test_04_sw_lifecycle_activate_cache_purging_and_clients_claim(self):
        """Verify activate event handler iterates caches.keys(), deletes stale caches, and calls self.clients.claim()."""
        self.assertIn("self.addEventListener('activate'", self.sw_text)
        self.assertIn("caches.keys()", self.sw_text)
        self.assertIn("key !== CACHE_NAME", self.sw_text)
        self.assertIn("caches.delete(key)", self.sw_text)
        self.assertIn("self.clients.claim()", self.sw_text)

    def test_05_sw_fetch_network_first_and_response_cloning(self):
        """Verify fetch event uses Network-First for local same-origin assets, clones response, and handles errors."""
        self.assertIn("self.addEventListener('fetch'", self.sw_text)
        self.assertIn("if (req.method !== 'GET') return;", self.sw_text)
        self.assertIn("fetch(req)", self.sw_text)
        self.assertIn("networkResponse.clone()", self.sw_text)
        self.assertIn("networkResponse.status === 200", self.sw_text)
        self.assertIn("networkResponse.type === 'basic'", self.sw_text)
        self.assertIn("cache.put(req, responseToCache)", self.sw_text)
        self.assertIn("caches.match(req)", self.sw_text)
        self.assertIn("caches.match('./index.html')", self.sw_text)

    def test_06_sw_fetch_cdn_stale_while_revalidate(self):
        """Verify CDN requests (cdnjs, jsdelivr) use Stale-While-Revalidate."""
        self.assertIn("cdnjs.cloudflare.com", self.sw_text)
        self.assertIn("jsdelivr", self.sw_text)
        self.assertIn("cache.match(req)", self.sw_text)

    def test_07_sw_protocol_filtering(self):
        """Verify fetch handler ignores non-http/https requests to avoid crashing on browser extensions."""
        self.assertIn("url.protocol !== 'http:' && url.protocol !== 'https:'", self.sw_text)


class TestM1ProgressHubUIEmpirical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index_text = INDEX_FILE.read_text(encoding="utf-8")
        cls.tracker_text = TRACKER_FILE.read_text(encoding="utf-8")

    def test_08_global_progress_hub_export_button_strictly_removed(self):
        """Verify рџ’ѕ Р­РєСЃРїРѕСЂС‚ button is completely removed from #global-progress-hub in index.html."""
        start_idx = self.index_text.find('id="global-progress-hub"')
        self.assertNotEqual(start_idx, -1, "#global-progress-hub element must exist in index.html")
        end_idx = self.index_text.find('id="exam-simulator-container"', start_idx)
        self.assertNotEqual(
            end_idx, -1, "#exam-simulator-container element must exist following progress hub"
        )
        hub_slice = self.index_text[start_idx:end_idx]

        self.assertNotIn(
            "\u042d\u043a\u0441\u043f\u043e\u0440\u0442",
            hub_slice,
            "'Р­РєСЃРїРѕСЂС‚' text must not appear anywhere in #global-progress-hub",
        )
        self.assertNotIn(
            "\U0001f4be", hub_slice, "'рџ’ѕ' icon must not appear in #global-progress-hub"
        )
        self.assertNotIn(
            "exportProgressJSON",
            hub_slice,
            "exportProgressJSON call must not be present in #global-progress-hub",
        )

    def test_09_global_progress_hub_reset_button_and_stats_preserved(self):
        """Verify рџ”„ РЎР±СЂРѕСЃ button, stat cards, and progress bar are intact in #global-progress-hub."""
        start_idx = self.index_text.find('id="global-progress-hub"')
        end_idx = self.index_text.find('id="exam-simulator-container"', start_idx)
        hub_slice = self.index_text[start_idx:end_idx]

        self.assertIn(
            "\U0001f504 \u0421\u0431\u0440\u043e\u0441",
            hub_slice,
            "'рџ”„ РЎР±СЂРѕСЃ' button must be present in #global-progress-hub",
        )
        self.assertIn(
            "CourseTracker.resetProgress()",
            hub_slice,
            "resetProgress() handler must be wired to Reset button",
        )
        self.assertIn(
            'id="global-progress-fill"', hub_slice, "'global-progress-fill' bar element must exist"
        )
        self.assertIn('id="stat-lecs-val"', hub_slice, "'stat-lecs-val' card must exist")
        self.assertIn('id="stat-qas-val"', hub_slice, "'stat-qas-val' card must exist")
        self.assertIn('id="stat-tasks-val"', hub_slice, "'stat-tasks-val' card must exist")

    def test_10_course_tracker_api_integrity(self):
        """Verify CourseTracker exports all required methods and constants."""
        self.assertIn("exportProgressJSON()", self.tracker_text)
        self.assertIn("importProgressJSON(", self.tracker_text)
        self.assertIn("resetProgress()", self.tracker_text)
        self.assertIn("getOverallStats()", self.tracker_text)
        self.assertIn("setLectureCompleted(", self.tracker_text)
        self.assertIn("setQAChecked(", self.tracker_text)
        self.assertIn("setTaskChecked(", self.tracker_text)
        self.assertIn("TOTAL_LECTURES = 28", self.tracker_text)
        self.assertIn("TOTAL_QAS = 296", self.tracker_text)
        self.assertIn("TOTAL_TASKS = 170", self.tracker_text)


if __name__ == "__main__":
    unittest.main()
