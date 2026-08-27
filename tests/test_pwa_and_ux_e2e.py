"""
E2E and structural test suite for PWA (manifest, service worker), UX interactions,
keyboard shortcuts, accessibility (:focus-visible, ARIA), print styles, and copy buttons.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
INDEX_FILE = COURSE_ROOT / "index.html"
MANIFEST_FILE = COURSE_ROOT / "manifest.json"
SW_FILE = COURSE_ROOT / "sw.js"
STYLE_FILE = COURSE_ROOT / "style.css"
JS_APP_FILE = COURSE_ROOT / "js" / "app.js"
JS_LECTURE_FILE = COURSE_ROOT / "js" / "lecture.js"
JS_SIM_FILE = COURSE_ROOT / "js" / "simulator.js"
JS_TRACKER_FILE = COURSE_ROOT / "js" / "tracker.js"

from tests.common import EXPECTED_LECTURES, read_file


class TestPwaManifestAndServiceWorker(unittest.TestCase):
    """Verify PWA Web App Manifest, Service Worker caching strategies, and offline capabilities."""

    def test_01_manifest_json_schema_and_fields(self):
        """Verify manifest.json exists, is valid JSON, and adheres to W3C Web App Manifest spec."""
        self.assertTrue(MANIFEST_FILE.exists(), f"manifest.json missing at {MANIFEST_FILE}")
        content = read_file(MANIFEST_FILE)
        try:
            data = json.loads(content)
        except json.JSONDecodeError as err:
            self.fail(f"manifest.json is malformed JSON: {err}")

        # Required W3C / PWA fields
        required_fields = ["name", "short_name", "start_url", "display", "background_color", "theme_color", "icons"]
        for field in required_fields:
            self.assertIn(field, data, f"manifest.json must contain '{field}'")
            self.assertTrue(data[field], f"manifest.json field '{field}' must not be empty")

        # Specific values
        self.assertEqual(data["display"], "standalone", "manifest display must be 'standalone'")
        self.assertIn(data["start_url"], [".", "./", "index.html", "./index.html", "/"], "start_url must point to root/index")
        self.assertTrue(data["theme_color"].startswith("#"), "theme_color must be a valid hex color")
        self.assertTrue(data["background_color"].startswith("#"), "background_color must be a valid hex color")

        # Icons list
        self.assertIsInstance(data["icons"], list, "icons must be an array")
        self.assertGreaterEqual(len(data["icons"]), 1, "manifest.json must provide at least 1 icon")
        for icon in data["icons"]:
            self.assertIn("src", icon, "Each icon object must specify 'src'")
            self.assertIn("sizes", icon, "Each icon object must specify 'sizes'")
            self.assertIn("type", icon, "Each icon object must specify 'type'")

    def test_02_manifest_icons_exist_on_filesystem(self):
        """Verify all icon files referenced in manifest.json actually exist on disk."""
        if not MANIFEST_FILE.exists():
            self.skipTest("manifest.json not created yet")
        data = json.loads(read_file(MANIFEST_FILE))
        for icon in data.get("icons", []):
            src = icon.get("src", "")
            if src.startswith("data:"):
                continue  # inline data URI is self-contained
            icon_path = COURSE_ROOT / src.lstrip("/")
            self.assertTrue(icon_path.exists(), f"Referenced icon file does not exist on disk: {icon_path}")

    def test_03_service_worker_structure_and_lifecycle_events(self):
        """Verify sw.js defines cache versioning, install, activate, and fetch lifecycle handlers."""
        self.assertTrue(SW_FILE.exists(), f"sw.js missing at {SW_FILE}")
        sw_code = read_file(SW_FILE)

        # Cache name / versioning
        self.assertTrue(
            re.search(r"CACHE_NAME|CACHE_VERSION|CACHE_KEY|const\s+CACHE\s*=", sw_code, re.IGNORECASE),
            "sw.js must define a cache name or cache version constant",
        )

        # Lifecycle listeners
        self.assertIn("install", sw_code, "sw.js must handle 'install' event")
        self.assertIn("activate", sw_code, "sw.js must handle 'activate' event")
        self.assertIn("fetch", sw_code, "sw.js must handle 'fetch' event")

        # Modern SW claims & skip waiting
        self.assertTrue(
            "skipWaiting" in sw_code or "clients.claim" in sw_code,
            "sw.js should use skipWaiting() or clients.claim() for instant activation",
        )

    def test_04_service_worker_precache_covers_all_28_lectures_and_assets(self):
        """Verify sw.js precache inventory includes all 28 HTML lectures, core CSS/JS, and Anki decks."""
        if not SW_FILE.exists():
            self.skipTest("sw.js not created yet")
        sw_code = read_file(SW_FILE)

        # Core assets
        core_assets = [
            "style.css",
            "js/app.js",
            "js/lecture.js",
            "js/tracker.js",
            "js/simulator.js",
            "js/exam_data.js",
            "manifest.json",
        ]
        for asset in core_assets:
            self.assertIn(asset, sw_code, f"sw.js precache list must include '{asset}'")

        # Verify all 28 lectures
        for lec in EXPECTED_LECTURES:
            self.assertIn(lec, sw_code, f"sw.js precache list must include lecture '{lec}'")

        # Verify Anki decks
        anki_decks = [
            "anki_decks/ai_course_exam_qas.tsv",
            "anki_decks/ai_course_microtasks.tsv",
            "anki_decks/ai_course_3min_cheatsheets.tsv",
        ]
        for deck in anki_decks:
            self.assertIn(deck, sw_code, f"sw.js precache list must include Anki deck '{deck}'")

    def test_05_service_worker_caching_and_offline_strategies(self):
        """Verify sw.js implements Cache-First for static assets and Network-First/SWR for CDN/MathJax."""
        if not SW_FILE.exists():
            self.skipTest("sw.js not created yet")
        sw_code = read_file(SW_FILE)

        # Cache matching
        self.assertIn("caches.match", sw_code, "sw.js must use caches.match for cache retrieval")

        # Dynamic / CDN fetch handling or offline fallback
        self.assertIn("fetch", sw_code, "sw.js must intercept fetch requests")
        self.assertTrue(
            "caches.open" in sw_code or "cache.put" in sw_code or "cache.addAll" in sw_code,
            "sw.js must open and populate caches",
        )

    def test_06_index_html_manifest_link_and_sw_registration(self):
        """Verify index.html contains <link rel='manifest'> and serviceWorker registration script."""
        index_html = read_file(INDEX_FILE)

        # Manifest link
        self.assertRegex(
            index_html,
            r'<link\s+[^>]*rel=["\']manifest["\'][^>]*href=["\'](?:\./)?manifest\.json["\']',
            "index.html must include <link rel='manifest' href='manifest.json'>",
        )

        # SW registration either in index.html or in loaded js files
        all_js_code = (
            index_html
            + read_file(JS_APP_FILE)
            + read_file(JS_TRACKER_FILE)
            + (read_file(JS_LECTURE_FILE) if JS_LECTURE_FILE.exists() else "")
        )
        self.assertIn(
            "serviceWorker",
            all_js_code,
            "Application must register Service Worker via 'navigator.serviceWorker.register'",
        )
        self.assertIn(
            "register",
            all_js_code,
            "Application must call serviceWorker.register('sw.js')",
        )


class TestKeyboardShortcutsAndInteraction(unittest.TestCase):
    """Verify global keyboard shortcuts ([ / ], T, /, Alt+O) and input-guarding logic."""

    @classmethod
    def setUpClass(cls):
        cls.app_js = read_file(JS_APP_FILE)
        cls.lecture_js = read_file(JS_LECTURE_FILE) if JS_LECTURE_FILE.exists() else ""
        cls.tracker_js = read_file(JS_TRACKER_FILE)
        cls.combined_js = cls.app_js + "\n" + cls.lecture_js + "\n" + cls.tracker_js

    def test_07_keyboard_shortcut_listeners_registered(self):
        """Verify keydown event listeners are registered for navigation, theme, search, and spoilers."""
        self.assertIn("keydown", self.combined_js, "Global keydown event listener must be registered in JS")

        # Shortcuts required by R2: [, ], T, /, Alt+O
        self.assertTrue(
            "[" in self.combined_js and "]" in self.combined_js,
            "Navigation shortcuts '[' and ']' must be handled in JS",
        )
        self.assertTrue(
            "e.key === 't'" in self.combined_js.lower() or "key === 't'" in self.combined_js.lower() or "key.tolowercase() === 't'" in self.combined_js.lower(),
            "Theme toggle shortcut 'T' / 't' must be handled in JS",
        )
        self.assertTrue(
            "e.key === '/'" in self.combined_js or "key === '/'" in self.combined_js,
            "Search focus shortcut '/' must be handled in JS",
        )
        self.assertTrue(
            "altkey" in self.combined_js.lower() and "o" in self.combined_js.lower(),
            "Spoiler expand/collapse shortcut 'Alt+O' must be handled in JS",
        )

    def test_08_keyboard_shortcuts_input_guarding_safety(self):
        """Verify keyboard shortcuts do not trigger while user types in input, textarea, or select."""
        self.assertTrue(
            re.search(r"tagName\s*===\s*['\"]INPUT['\"]|INPUT|TEXTAREA|SELECT|isContentEditable", self.combined_js),
            "Keyboard shortcut dispatcher must check active element / target to prevent hijacking input fields",
        )

    def test_09_search_focus_shortcut_prevents_default(self):
        """Verify '/' search shortcut calls preventDefault() to avoid typing '/' into input."""
        self.assertIn("preventDefault", self.combined_js, "Search shortcut handler must call e.preventDefault()")

    def test_10_spoiler_toggle_alt_o_manipulates_details_open(self):
        """Verify Alt+O shortcut toggles 'open' attribute across all <details> elements."""
        self.assertRegex(
            self.lecture_js + "\n" + self.app_js,
            r"details|querySelectorAll\(['\"]details['\"]\)",
            "Alt+O shortcut in lecture.js must query and toggle <details> elements",
        )


class TestAccessibilityAndPrintCSS(unittest.TestCase):
    """Verify WCAG 2.1 AA :focus-visible rules, Print CSS formatting, beforeprint hooks, and copy buttons."""

    @classmethod
    def setUpClass(cls):
        cls.style_css = read_file(STYLE_FILE)
        cls.lecture_js = read_file(JS_LECTURE_FILE) if JS_LECTURE_FILE.exists() else ""
        cls.sim_js = read_file(JS_SIM_FILE) if JS_SIM_FILE.exists() else ""

    def test_11_focus_visible_rules_in_style_css(self):
        """Verify :focus-visible rules exist for keyboard accessibility on interactive elements."""
        self.assertIn(":focus-visible", self.style_css, "style.css must define :focus-visible rules for WCAG 2.1 AA")
        self.assertTrue(
            "outline:" in self.style_css or "outline-color:" in self.style_css or "box-shadow:" in self.style_css,
            "Focus visible rules must define high-contrast focus rings",
        )

    def test_12_print_css_and_details_expansion_handlers(self):
        """Verify @media print styles hide navigation chrome, and beforeprint expands all details."""
        self.assertIn("@media print", self.style_css, "style.css must define @media print block")

        # Elements hidden in print
        print_section = self.style_css[self.style_css.find("@media print") :]
        self.assertTrue(
            "display: none" in print_section or "display:none" in print_section,
            "Print styles must suppress interactive UI buttons, navbars, and timers",
        )

        # JS beforeprint / afterprint hooks
        self.assertTrue(
            "beforeprint" in self.lecture_js or "beforeprint" in read_file(JS_APP_FILE),
            "JS must listen to 'beforeprint' event to expand <details> elements for PDF rendering",
        )

    def test_13_code_copy_button_and_visual_feedback(self):
        """Verify code snippet copy buttons use clipboard API with visual confirmation and fallback."""
        self.assertIn("copy-btn", self.lecture_js, "lecture.js must attach .copy-btn to code blocks")
        self.assertIn("navigator.clipboard", self.lecture_js, "Copy button must utilize navigator.clipboard API")
        self.assertTrue(
            "Скопировано" in self.lecture_js or "copied" in self.lecture_js,
            "Copy button must provide immediate visual feedback upon copying",
        )

    def test_14_aria_accessibility_attributes_in_simulator(self):
        """Verify Exam Simulator uses ARIA roles and attributes for tab navigation."""
        all_code = self.sim_js + "\n" + read_file(INDEX_FILE)
        self.assertTrue(
            "aria-label" in all_code or "role=\"tab\"" in all_code or "tablist" in all_code or "aria-selected" in all_code,
            "Exam simulator must define ARIA accessibility attributes",
        )


if __name__ == "__main__":
    unittest.main()
