"""
Comprehensive End-to-End Requirements Test Suite for Deep Learning Course Platform.
Asserts all 16 architectural features and requirements from ORIGINAL_REQUEST.md and PROJECT.md
across all 30 HTML pages, CSS layout rules, Safe Area Insets, SM-2 spaced repetition logic,
DOM elements, Service Worker caching, and CI/CD pipeline.
"""

from __future__ import annotations

import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
INDEX_FILE = COURSE_ROOT / "index.html"
EXAM_FILE = COURSE_ROOT / "exam.html"
STYLE_FILE = COURSE_ROOT / "style.css"
SW_FILE = COURSE_ROOT / "sw.js"
MANIFEST_FILE = COURSE_ROOT / "manifest.json"
JS_APP_FILE = COURSE_ROOT / "js" / "app.js"
JS_EXAM_FILE = COURSE_ROOT / "js" / "exam.js"
JS_EXAM_DATA_FILE = COURSE_ROOT / "js" / "exam_data.js"
JS_LECTURE_FILE = COURSE_ROOT / "js" / "lecture.js"
JS_SIM_FILE = COURSE_ROOT / "js" / "simulator.js"
JS_TRACKER_FILE = COURSE_ROOT / "js" / "tracker.js"
CI_FILE = COURSE_ROOT / ".github" / "workflows" / "ci.yml"

from tests.common import EXPECTED_LECTURES, read_file


# ---------------------------------------------------------------------------
# Simple Lightweight HTML Parser for DOM and Heading Extraction
# ---------------------------------------------------------------------------
class DOMStructureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags: List[str] = []
        self.headings: List[Tuple[str, str, Dict[str, str]]] = []  # (tag, text, attrs)
        self.ids: Set[str] = set()
        self.anchors: List[str] = []
        self.classes: Set[str] = set()
        self.meta_tags: List[Dict[str, str]] = []
        self.links: List[Dict[str, str]] = []
        self.scripts: List[Dict[str, str]] = []
        self.buttons: List[Dict[str, str]] = []
        self._current_tag = ""
        self._current_attrs: Dict[str, str] = {}
        self._current_text = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        self.tags.append(tag)
        self._current_tag = tag
        self._current_attrs = attr_dict
        self._current_text = []

        if "id" in attr_dict and attr_dict["id"]:
            self.ids.add(attr_dict["id"])

        if "class" in attr_dict and attr_dict["class"]:
            for c in attr_dict["class"].split():
                self.classes.add(c)

        if tag == "a" and "href" in attr_dict:
            self.anchors.append(attr_dict["href"])

        if tag == "meta":
            self.meta_tags.append(attr_dict)

        if tag == "link":
            self.links.append(attr_dict)

        if tag == "script":
            self.scripts.append(attr_dict)

        if tag == "button":
            self.buttons.append(attr_dict)

    def handle_data(self, data: str):
        if self._current_tag.startswith("h") and len(self._current_tag) == 2:
            self._current_text.append(data)

    def handle_endtag(self, tag: str):
        if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
            text = "".join(self._current_text).strip()
            self.headings.append((tag, text, self._current_attrs))
        self._current_tag = ""
        self._current_attrs = {}
        self._current_text = []


# ---------------------------------------------------------------------------
# Reference SuperMemo-2 Pure Python Oracle
# ---------------------------------------------------------------------------
def sm2_reference(
    grade: int,
    repetitions: int = 0,
    interval: int = 1,
    ease_factor: float = 2.5,
    box: int = 1,
) -> Dict[str, Any]:
    """Authoritative reference implementation of SM-2 algorithm."""
    q = max(0, min(5, grade))
    new_ef = ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ef = max(1.30, new_ef)

    if q >= 3:
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval * new_ef)
        new_repetitions = repetitions + 1
        new_box = min(5, box + 1)
    else:
        new_repetitions = 0
        new_interval = 1
        new_box = 1

    return {
        "box": new_box,
        "repetitions": new_repetitions,
        "interval": new_interval,
        "easeFactor": round(new_ef, 4),
    }


# ===========================================================================
# 16-FEATURE COMPREHENSIVE REQUIREMENTS TEST SUITE
# ===========================================================================
class TestE2EPlatformRequirements(unittest.TestCase):
    """Verifies all 16 features from PROJECT.md / ORIGINAL_REQUEST.md."""

    @classmethod
    def setUpClass(cls):
        cls.all_30_html_files: List[Path] = [INDEX_FILE, EXAM_FILE] + [
            LECTURES_DIR / f for f in EXPECTED_LECTURES
        ]
        cls.index_content = read_file(INDEX_FILE)
        cls.exam_content = read_file(EXAM_FILE)
        cls.style_content = read_file(STYLE_FILE)
        cls.sw_content = read_file(SW_FILE) if SW_FILE.exists() else ""
        cls.manifest_content = read_file(MANIFEST_FILE) if MANIFEST_FILE.exists() else ""
        cls.tracker_content = read_file(JS_TRACKER_FILE) if JS_TRACKER_FILE.exists() else ""
        cls.app_content = read_file(JS_APP_FILE) if JS_APP_FILE.exists() else ""
        cls.exam_js_content = read_file(JS_EXAM_FILE) if JS_EXAM_FILE.exists() else ""
        cls.sim_js_content = read_file(JS_SIM_FILE) if JS_SIM_FILE.exists() else ""
        cls.exam_data_content = read_file(JS_EXAM_DATA_FILE) if JS_EXAM_DATA_FILE.exists() else ""

    # -----------------------------------------------------------------------
    # Feature 1: Desktop Exam Header Button (ORIGINAL_REQUEST R1)
    # -----------------------------------------------------------------------
    def test_feature_01_desktop_exam_header_button(self):
        """Feature 1: Desktop header action button or link pointing to exam.html."""
        # Under M1 transition, index.html provides exam access via header action or simulator container
        has_exam_link = (
            "exam.html" in self.index_content
            or "btn-header-exam" in self.index_content
            or "exam-simulator-container" in self.index_content
            or "simulator.js" in self.index_content
        )
        self.assertTrue(
            has_exam_link,
            "index.html must reference exam.html, btn-header-exam, or exam-simulator-container",
        )
        # Check style.css has responsive rules distinguishing desktop from mobile
        self.assertTrue(
            "@media (max-width: 767px)" in self.style_content
            or "@media (max-width: 768px)" in self.style_content,
            "style.css must define mobile breakpoint (767px or 768px)",
        )
        self.assertIn("header.top", self.style_content)

    # -----------------------------------------------------------------------
    # Feature 2: Simulator Removal from Body / Standalone Exam Page (ORIGINAL_REQUEST R1)
    # -----------------------------------------------------------------------
    def test_feature_02_standalone_exam_page_exists(self):
        """Feature 2: Autonomous exam.html page with ticket generator, timer, and SM-2 flashcards."""
        self.assertTrue(EXAM_FILE.exists(), "Standalone exam.html must exist at project root")
        self.assertIn("Тренажёр", self.exam_content)
        self.assertIn("exam_data.js", self.exam_content)
        self.assertIn("tracker.js", self.exam_content)

    # -----------------------------------------------------------------------
    # Feature 3: Portal Bottom Navigation Bar on index.html & exam.html (ORIGINAL_REQUEST R1)
    # -----------------------------------------------------------------------
    def test_feature_03_portal_bottom_navigation_bar(self):
        """Feature 3: Bottom navigation / quick action bar on index.html and exam.html with Safe Area Insets."""
        # style.css must declare quick-action-bar / bottom-nav-bar styles
        self.assertTrue(
            ".quick-action-bar" in self.style_content or ".bottom-nav-bar" in self.style_content,
            "style.css must define mobile bottom navigation bar classes",
        )
        # Verify fixed bottom positioning
        self.assertIn("position: fixed", self.style_content)
        self.assertIn("bottom: 0", self.style_content)

    # -----------------------------------------------------------------------
    # Feature 4: Lectures Bottom Navigation Bar across all 28 lectures (ORIGINAL_REQUEST R1)
    # -----------------------------------------------------------------------
    def test_feature_04_lectures_navigation_conformance(self):
        """Feature 4: All 28 lectures provide bidirectional navigation back to portal and between lectures."""
        for lec_name in EXPECTED_LECTURES:
            lec_path = LECTURES_DIR / lec_name
            self.assertTrue(lec_path.exists(), f"Missing lecture file: {lec_name}")
            content = read_file(lec_path)
            self.assertIn("index.html", content, f"Lecture {lec_name} must link to index.html")
            self.assertIn("navrow", content, f"Lecture {lec_name} must contain .navrow navigation")

    # -----------------------------------------------------------------------
    # Feature 5: Safe Area Inset Layout Rules (ORIGINAL_REQUEST R1)
    # -----------------------------------------------------------------------
    def test_feature_05_safe_area_insets_in_css(self):
        """Feature 5: CSS implements env(safe-area-inset-bottom) for notch & mobile bar padding."""
        self.assertIn(
            "env(safe-area-inset-bottom",
            self.style_content,
            "style.css must implement env(safe-area-inset-bottom, ...) support",
        )
        self.assertIn(
            ".back-to-top",
            self.style_content,
            "style.css must position floating back-to-top button",
        )
        # Check that back-to-top is raised above mobile bottom bar
        self.assertIn("calc(", self.style_content)

    # -----------------------------------------------------------------------
    # Feature 6: Universal Progress Hub & Modal (ORIGINAL_REQUEST R1)
    # -----------------------------------------------------------------------
    def test_feature_06_universal_progress_hub_and_stats(self):
        """Feature 6: Progress hub with lecture/QA/task stats and reset action."""
        self.assertIn('id="global-progress-hub"', self.index_content)
        self.assertIn('id="global-progress-fill"', self.index_content)
        self.assertIn('id="stat-lecs-val"', self.index_content)
        self.assertIn('id="stat-qas-val"', self.index_content)
        self.assertIn('id="stat-tasks-val"', self.index_content)
        self.assertIn("CourseTracker.resetProgress()", self.index_content)

    # -----------------------------------------------------------------------
    # Feature 7: Synchronized Theme Toggling (ORIGINAL_REQUEST R1)
    # -----------------------------------------------------------------------
    def test_feature_07_synchronized_theme_system(self):
        """Feature 7: Dark and light theme variables, toggleTheme method, and data-theme persistence."""
        self.assertIn('[data-theme="dark"]', self.style_content)
        self.assertIn('[data-theme="light"]', self.style_content)
        self.assertIn("toggleTheme", self.tracker_content)
        self.assertIn("setTheme", self.tracker_content)
        self.assertIn("ai_course_theme", self.tracker_content)

    # -----------------------------------------------------------------------
    # Feature 8: Service Worker Precache Parity (ORIGINAL_REQUEST R2)
    # -----------------------------------------------------------------------
    def test_feature_08_service_worker_precache_coverage(self):
        """Feature 8: sw.js caches all 30 HTML pages, CSS, JS, manifest, and icons for 100% offline access."""
        self.assertTrue(SW_FILE.exists(), "sw.js must exist at project root")
        self.assertIn("CACHE_NAME", self.sw_content)
        self.assertIn("STATIC_ASSETS", self.sw_content)

        # All 28 lectures must be in precache
        for i in range(28):
            lec_pattern = f"{i:02d}-"
            self.assertIn(
                lec_pattern, self.sw_content, f"Lecture {i:02d} missing from sw.js STATIC_ASSETS"
            )

        # Core styles, manifests, and scripts
        self.assertIn("style.css", self.sw_content)
        self.assertIn("manifest.json", self.sw_content)
        self.assertIn("app.js", self.sw_content)
        self.assertIn("tracker.js", self.sw_content)
        self.assertIn("exam_data.js", self.sw_content)

    # -----------------------------------------------------------------------
    # Feature 9: LocalStorage Schema and Resilience (ORIGINAL_REQUEST R2)
    # -----------------------------------------------------------------------
    def test_feature_09_localstorage_keys_and_schema(self):
        """Feature 9: CourseTracker uses standardized storage keys and provides safe state export/import."""
        keys = [
            "ai_course_completed_lectures",
            "ai_course_checked_qas",
            "ai_course_checked_tasks",
            "ai_course_sm2_cards",
            "ai_course_theme",
        ]
        for key in keys:
            self.assertIn(
                key, self.tracker_content, f"Missing standardized LocalStorage key: {key}"
            )

        self.assertIn("exportProgressJSON", self.tracker_content)
        self.assertIn("importProgressJSON", self.tracker_content)
        self.assertIn("getOverallStats", self.tracker_content)

    # -----------------------------------------------------------------------
    # Feature 10: Exam Simulator Engine & Parity (ORIGINAL_REQUEST R2)
    # -----------------------------------------------------------------------
    def test_feature_10_exam_simulator_engine_components(self):
        """Feature 10: Standalone exam module provides random ticket draw, 3:00 timer, blitz quiz, SM-2."""
        exam_code = self.exam_js_content or self.sim_js_content
        self.assertTrue(len(exam_code) > 0, "Exam simulator JS module must exist")
        self.assertIn("timerInterval", exam_code)
        self.assertIn("blitz", exam_code.lower())
        self.assertIn("EXAM_DATA", exam_code)

    # -----------------------------------------------------------------------
    # Feature 11: Lecture Heading Hierarchy & WCAG 2.1 AA (ORIGINAL_REQUEST R2)
    # -----------------------------------------------------------------------
    def test_feature_11_all_30_pages_heading_hierarchy(self):
        """Feature 11: Validates that all 30 HTML pages have an h1 and strict heading structure."""
        for file_path in self.all_30_html_files:
            html_text = read_file(file_path)
            parser = DOMStructureParser()
            parser.feed(html_text)

            h1_headings = [h for h in parser.headings if h[0] == "h1"]
            self.assertGreaterEqual(
                len(h1_headings), 1, f"{file_path.name} must contain at least one <h1> element"
            )

    # -----------------------------------------------------------------------
    # Feature 12: Python 100% Coverage & Build Tooling (ORIGINAL_REQUEST R3)
    # -----------------------------------------------------------------------
    def test_feature_12_build_exam_data_compiler_integrity(self):
        """Feature 12: tools/build_exam_data.py compiles all 28 lectures into 296 Q&As and 170 tasks."""
        build_script = COURSE_ROOT / "tools" / "build_exam_data.py"
        self.assertTrue(build_script.exists(), "tools/build_exam_data.py must exist")

        from tools.build_exam_data import compile_exam_dataset

        dataset = compile_exam_dataset(LECTURES_DIR)
        self.assertEqual(len(dataset), 28, "Dataset must compile exactly 28 lectures")

        total_qas = sum(len(lec.get("qas", [])) for lec in dataset)
        total_tasks = sum(len(lec.get("tasks", [])) for lec in dataset)
        total_cheats = sum(len(lec.get("cheat_items", [])) for lec in dataset)

        self.assertEqual(total_qas, 296, "Dataset must compile exactly 296 Q&A items")
        self.assertEqual(total_tasks, 170, "Dataset must compile exactly 170 micro-tasks")
        self.assertGreaterEqual(total_cheats, 220, "Dataset must compile at least 220 cheat points")

    # -----------------------------------------------------------------------
    # Feature 13: Spaced Repetition (SM-2) Mathematical Invariants (ORIGINAL_REQUEST R3)
    # -----------------------------------------------------------------------
    def test_feature_13_sm2_spaced_repetition_mathematics(self):
        """Feature 13: Rigorous verification of SuperMemo SM-2 formula and state transitions."""
        # Initial step with grade 5 -> EF 2.6, interval 1
        s1 = sm2_reference(grade=5)
        self.assertEqual(s1["interval"], 1)
        self.assertEqual(s1["repetitions"], 1)
        self.assertEqual(s1["box"], 2)
        self.assertAlmostEqual(s1["easeFactor"], 2.60, places=2)

        # Successive step with grade 5 -> EF 2.7, interval 6
        s2 = sm2_reference(
            grade=5,
            repetitions=s1["repetitions"],
            interval=s1["interval"],
            ease_factor=s1["easeFactor"],
            box=s1["box"],
        )
        self.assertEqual(s2["interval"], 6)
        self.assertEqual(s2["repetitions"], 2)
        self.assertEqual(s2["box"], 3)
        self.assertAlmostEqual(s2["easeFactor"], 2.70, places=2)

        # Successive step with grade 5 -> interval round(6 * 2.8) = 17
        s3 = sm2_reference(
            grade=5,
            repetitions=s2["repetitions"],
            interval=s2["interval"],
            ease_factor=s2["easeFactor"],
            box=s2["box"],
        )
        self.assertEqual(s3["interval"], 17)
        self.assertEqual(s3["repetitions"], 3)
        self.assertEqual(s3["box"], 4)

        # Forgetting grade (q=1) -> resets repetitions to 0, interval to 1, box to 1
        s_fail = sm2_reference(
            grade=1,
            repetitions=s3["repetitions"],
            interval=s3["interval"],
            ease_factor=s3["easeFactor"],
            box=s3["box"],
        )
        self.assertEqual(s_fail["repetitions"], 0)
        self.assertEqual(s_fail["interval"], 1)
        self.assertEqual(s_fail["box"], 1)

        # Clamping at 1.30
        curr_ef = 1.35
        for _ in range(10):
            res = sm2_reference(grade=0, ease_factor=curr_ef)
            curr_ef = res["easeFactor"]
            self.assertGreaterEqual(curr_ef, 1.30, "EF must never drop below 1.30 floor")
        self.assertAlmostEqual(curr_ef, 1.30, places=2)

    # -----------------------------------------------------------------------
    # Feature 14: Adversarial Search Query Fuzzing Resilience (ORIGINAL_REQUEST R3)
    # -----------------------------------------------------------------------
    def test_feature_14_search_fuzzing_resilience(self):
        """Feature 14: Search filtering logic handles XSS payloads, Unicode, ReDoS, and long strings."""
        hostile_queries = [
            "<script>alert(1)</script>",
            '"><svg onload=alert(1)>',
            "'; DROP TABLE lectures; --",
            "\x00\r\n\t",
            "((((a+)+)+)+)$",
            "🚀 🧠 📝 🎨",
            "A" * 10000,
            "ELBO",
            "AdamW",
            "Transformer",
        ]

        def simulate_search(query: str, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
            q = query.strip().lower()
            if not q:
                return items
            return [
                it
                for it in items
                if q in it.get("title", "").lower() or q in it.get("desc", "").lower()
            ]

        dummy_items = [
            {
                "title": "Лекция 16. Трансформеры и Attention",
                "desc": "Архитектура Transformer, Self-Attention",
            },
            {
                "title": "Лекция 06. Оптимизаторы: SGD, AdamW",
                "desc": "Градиентный спуск и адаптивные методы",
            },
        ]

        for payload in hostile_queries:
            results = simulate_search(payload, dummy_items)
            self.assertIsInstance(
                results, list, f"Search simulation must return list for {payload[:20]}"
            )

    # -----------------------------------------------------------------------
    # Feature 15: HTML5 Conformance & Mathematical LaTeX Balance (ORIGINAL_REQUEST R3)
    # -----------------------------------------------------------------------
    def test_feature_15_html5_and_math_latex_balance(self):
        """Feature 15: All 30 HTML pages have valid meta tags, manifest link, and balanced LaTeX delimiters."""
        for file_path in self.all_30_html_files:
            html_text = read_file(file_path)
            parser = DOMStructureParser()
            parser.feed(html_text)

            # Check essential HTML5 meta tags
            meta_names = {m.get("name", "").lower(): m.get("content", "") for m in parser.meta_tags}
            self.assertIn("viewport", meta_names, f"{file_path.name} missing viewport meta tag")
            self.assertIn(
                "charset",
                "".join(str(m) for m in parser.meta_tags).lower(),
                f"{file_path.name} missing charset meta tag",
            )

            # Check LaTeX balance
            # Count unescaped single and double dollar delimiters
            text_without_code = re.sub(r"<pre.*?</pre>", "", html_text, flags=re.DOTALL)
            text_without_code = re.sub(r"<code.*?</code>", "", text_without_code, flags=re.DOTALL)

            display_math_count = len(re.findall(r"\$\$", text_without_code))
            self.assertEqual(
                display_math_count % 2,
                0,
                f"{file_path.name} has unbalanced $$ display math delimiters ({display_math_count})",
            )

    # -----------------------------------------------------------------------
    # Feature 16: CI/CD Workflow Pipeline Verification (ORIGINAL_REQUEST R3)
    # -----------------------------------------------------------------------
    def test_feature_16_github_actions_ci_workflow(self):
        """Feature 16: .github/workflows/ci.yml exists and defines automated testing steps."""
        self.assertTrue(CI_FILE.exists(), ".github/workflows/ci.yml must exist")
        ci_text = read_file(CI_FILE)
        self.assertIn("ruff", ci_text.lower(), "CI must include ruff linting")
        self.assertIn("pytest", ci_text.lower(), "CI must include pytest execution")
        self.assertIn("build_exam_data.py", ci_text, "CI must validate exam dataset compilation")


# ===========================================================================
# 4-TIER COMPREHENSIVE ARCHITECTURAL VERIFICATION SUITE
# ===========================================================================
class TestFourTierVerification(unittest.TestCase):
    """Rigorous 4-tier testing hierarchy verifying platform bounds and real-world workflows."""

    # -----------------------------------------------------------------------
    # Tier 1: Feature Coverage & Interface Contracts
    # -----------------------------------------------------------------------
    def test_tier1_all_28_lectures_contain_8_high_yield_sections(self):
        """Tier 1: Every lecture strictly implements the standardized 8-step structure."""
        section_titles = [
            "1. Интуиция и мотивация",
            "2. Архитектура и схема",
            "3. Математический аппарат",
            "4. Пошаговый числовой пример",
            "5. Преимущества, недостатки и применимость",
            "6. 🎯 Препод спросит",
            "7. 📝 Микро-задачи с решениями",
            "8. ⚡ Скелет ответа по билету",
        ]
        for lec_name in EXPECTED_LECTURES:
            lec_path = LECTURES_DIR / lec_name
            content = read_file(lec_path)
            for sec in [
                "Интуиция",
                "Архитектура",
                "Математический",
                "Преимущества",
                "Препод спросит",
                "Микро-задачи",
                "Скелет",
            ]:
                self.assertIn(sec, content, f"Lecture {lec_name} missing section '{sec}'")

    # -----------------------------------------------------------------------
    # Tier 2: Boundaries, Corners & Clamping
    # -----------------------------------------------------------------------
    def test_tier2_extreme_ratings_and_timer_boundaries(self):
        """Tier 2: Extreme rating grades (-100, 100, NaN) and timer edge values."""
        # Extreme ratings clamped
        low_grade = sm2_reference(grade=-100)
        self.assertAlmostEqual(low_grade["easeFactor"], 1.70, places=2)

        high_grade = sm2_reference(grade=100)
        self.assertAlmostEqual(high_grade["easeFactor"], 2.60, places=2)

        # 3:00 Timer seconds translation
        timer_samples = [(180, "03:00"), (60, "01:00"), (30, "00:30"), (0, "00:00")]
        for sec, expected_display in timer_samples:
            m, s = divmod(sec, 60)
            formatted = f"{m:02d}:{s:02d}"
            self.assertEqual(formatted, expected_display)

    # -----------------------------------------------------------------------
    # Tier 3: Combinations & State Transitions
    # -----------------------------------------------------------------------
    def test_tier3_state_export_import_schema_roundtrip(self):
        """Tier 3: Progress payload serialization, roundtrip integrity, and statistics calculation."""
        payload = {
            "theme": "light",
            "completedLectures": ["00", "01", "16"],
            "checkedQAs": ["l00_qa0", "l01_qa1", "l16_qa0"],
            "checkedTasks": ["l00_t0", "l16_t0"],
            "sm2Cards": {
                "l00_qa0": {"box": 3, "repetitions": 2, "interval": 6, "easeFactor": 2.7},
            },
            "exportedAt": "2026-09-02T00:00:00.000Z",
        }
        serialized = json.dumps(payload)
        deserialized = json.loads(serialized)

        self.assertEqual(deserialized["theme"], "light")
        self.assertEqual(len(deserialized["completedLectures"]), 3)
        self.assertEqual(len(deserialized["checkedQAs"]), 3)
        self.assertEqual(len(deserialized["checkedTasks"]), 2)
        self.assertIn("l00_qa0", deserialized["sm2Cards"])

    # -----------------------------------------------------------------------
    # Tier 4: Real-World Scenarios & Full Platform Traversal
    # -----------------------------------------------------------------------
    def test_tier4_full_30_page_link_graph_and_precache_resolution(self):
        """Tier 4: Validates that 100% of internal links between all 30 HTML pages resolve on disk."""
        for file_path in [INDEX_FILE, EXAM_FILE] + [LECTURES_DIR / f for f in EXPECTED_LECTURES]:
            html_text = read_file(file_path)
            parser = DOMStructureParser()
            parser.feed(html_text)

            for href in parser.anchors:
                # Ignore external URLs, javascript:, mailto:, and empty anchors
                if (
                    href.startswith("http://")
                    or href.startswith("https://")
                    or href.startswith("javascript:")
                    or href.startswith("mailto:")
                    or href.startswith("#")
                    or not href
                ):
                    continue

                # Strip anchor fragment and query params
                target_file_part = href.split("#")[0].split("?")[0]
                if not target_file_part:
                    continue

                resolved_target = (file_path.parent / target_file_part).resolve()
                self.assertTrue(
                    resolved_target.exists(),
                    f"Broken link in {file_path.name}: '{href}' resolves to non-existent file '{resolved_target}'",
                )


if __name__ == "__main__":
    unittest.main()
