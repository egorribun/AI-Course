"""
Challenger M2 Empirical Deep Verification & Forensic Test Suite
Milestone M2: Code Quality, PWA Offline, JS Hardening & Heading Hierarchy
"""

from __future__ import annotations

import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Tuple
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
LECTURES_DIR = ROOT_DIR / "lectures"
JS_DIR = ROOT_DIR / "js"
SW_FILE = ROOT_DIR / "sw.js"
INDEX_FILE = ROOT_DIR / "index.html"
EXAM_FILE = ROOT_DIR / "exam.html"


class HeadingExtractor(HTMLParser):
    """Extracts all headings in order of appearance."""

    def __init__(self):
        super().__init__()
        self.headings: List[Tuple[str, int, str, Dict[str, str]]] = []
        self.current_tag = None
        self.current_attrs = {}
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.current_tag = tag.lower()
            self.current_attrs = dict(attrs)
            self.current_text = []

    def handle_data(self, data):
        if self.current_tag:
            self.current_text.append(data)

    def handle_endtag(self, tag):
        if self.current_tag and tag.lower() == self.current_tag:
            level = int(self.current_tag[1])
            text = "".join(self.current_text).strip()
            self.headings.append((self.current_tag, level, text, self.current_attrs))
            self.current_tag = None
            self.current_text = []


# ============================================================================
# 1. HEADING HIERARCHY & WCAG 2.1 AA AUDIT ACROSS ALL 28 LECTURES
# ============================================================================


class TestLectureHeadingHierarchy:
    """Audits heading hierarchy across all 28 lectures for WCAG 2.1 AA compliance."""

    def test_all_28_lectures_exist(self):
        lecture_files = sorted(list(LECTURES_DIR.glob("*.html")))
        assert len(lecture_files) == 28, f"Expected 28 lecture files, found {len(lecture_files)}"

    @pytest.mark.parametrize(
        "lecture_file", sorted(list(LECTURES_DIR.glob("*.html"))), ids=lambda p: p.name
    )
    def test_lecture_heading_hierarchy_monotonicity(self, lecture_file):
        """Every lecture must have strictly monotonic heading transitions without skips (WCAG 2.1 AA)."""
        content = lecture_file.read_text(encoding="utf-8")
        parser = HeadingExtractor()
        parser.feed(content)

        assert len(parser.headings) > 0, f"{lecture_file.name} has no headings"

        h1s = [h for h in parser.headings if h[0] == "h1"]
        assert len(h1s) >= 1, f"{lecture_file.name} missing <h1>"

        prev_level = 0
        skips = []
        for tag, level, text, _ in parser.headings:
            if prev_level > 0 and level > prev_level + 1:
                skips.append({"from_tag": f"h{prev_level}", "to_tag": tag, "text": text[:40]})
            prev_level = level

        assert len(skips) == 0, f"{lecture_file.name} contains heading skips: {skips}"

    @pytest.mark.parametrize(
        "lecture_file", sorted(list(LECTURES_DIR.glob("*.html"))), ids=lambda p: p.name
    )
    def test_section_4_has_normalized_h3_headings(self, lecture_file):
        """Section 4 in all 28 lectures must use <h3> for step headings (no direct <h4> after <h2>)."""
        content = lecture_file.read_text(encoding="utf-8")
        parser = HeadingExtractor()
        parser.feed(content)

        # Find Section 4 index
        sec4_idx = -1
        for i, (tag, level, text, _) in enumerate(parser.headings):
            if level == 2 and (
                "4." in text
                or "Шаг 4" in text
                or "Практика" in text
                or "Архитектура" in text
                or "Алгоритм" in text
            ):
                sec4_idx = i
                break

        if sec4_idx != -1:
            prev_level = 2
            for i in range(sec4_idx + 1, len(parser.headings)):
                tag, level, text, _ = parser.headings[i]
                if level == 2:
                    break
                assert level <= prev_level + 1, (
                    f"{lecture_file.name} in Section 4 has heading skip: h{prev_level} -> {tag} ({text[:30]})"
                )
                prev_level = level

    def test_index_heading_hierarchy(self):
        """Verify index.html conforms to heading hierarchy."""
        content = INDEX_FILE.read_text(encoding="utf-8")
        parser = HeadingExtractor()
        parser.feed(content)
        assert len(parser.headings) > 0, f"{INDEX_FILE.name} has no headings"

        prev_level = 0
        skips = []
        for tag, level, text, _ in parser.headings:
            if prev_level > 0 and level > prev_level + 1:
                skips.append({"from": f"h{prev_level}", "to": tag, "text": text[:30]})
            prev_level = level

        assert len(skips) == 0, f"{INDEX_FILE.name} has heading skips: {skips}"


# ============================================================================
# 2. PWA SERVICE WORKER & PRECACHE INTEGRITY AUDIT
# ============================================================================


class TestServiceWorkerPrecacheParity:
    """Audits sw.js for complete precache inventory, versioning, and strategy dispatch."""

    @pytest.fixture(autouse=True)
    def setup_sw(self):
        self.sw_content = SW_FILE.read_text(encoding="utf-8")

    def test_sw_cache_version_defined(self):
        match = re.search(r"const CACHE_NAME\s*=\s*['\"]([^'\"]+)['\"];", self.sw_content)
        assert match, "sw.js missing CACHE_NAME declaration"
        cache_name = match.group(1)
        assert len(cache_name) > 0, "CACHE_NAME is empty"

    def test_static_assets_contains_exam_html_and_exam_js(self):
        match = re.search(r"const STATIC_ASSETS\s*=\s*\[([\s\S]*?)\];", self.sw_content)
        assert match, "sw.js missing STATIC_ASSETS declaration"
        raw_assets = match.group(1)
        assets = [a.strip().strip("'").strip('"') for a in raw_assets.split(",") if a.strip()]
        assert "./exam.html" in assets or "exam.html" in assets, (
            "exam.html not found in STATIC_ASSETS"
        )
        assert "./js/exam.js" in assets or "js/exam.js" in assets, (
            "js/exam.js not found in STATIC_ASSETS"
        )
        assert "./index.html" in assets or "index.html" in assets, (
            "index.html not found in STATIC_ASSETS"
        )
        assert "./js/tracker.js" in assets or "js/tracker.js" in assets, (
            "js/tracker.js not found in STATIC_ASSETS"
        )

    def test_all_28_lectures_in_sw_static_assets(self):
        match = re.search(r"const STATIC_ASSETS\s*=\s*\[([\s\S]*?)\];", self.sw_content)
        assets = match.group(1)
        for i in range(28):
            pad = f"{i:02d}"
            pattern = rf"lectures/{pad}-[^.'\"]+\.html"
            assert re.search(pattern, assets), f"Lecture {pad} not found in sw.js STATIC_ASSETS"

    def test_every_static_asset_exists_on_disk(self):
        match = re.search(r"const STATIC_ASSETS\s*=\s*\[([\s\S]*?)\];", self.sw_content)
        raw_assets = match.group(1)
        asset_lines = [
            line.strip().strip(",").strip('"').strip("'")
            for line in raw_assets.splitlines()
            if line.strip() and not line.strip().startswith("//")
        ]
        for asset in asset_lines:
            if asset == "./":
                continue
            clean_rel = asset.replace("./", "")
            disk_path = ROOT_DIR / clean_rel
            assert disk_path.exists(), f"Asset {asset} -> {disk_path} does not exist on disk"
            assert disk_path.stat().st_size > 0, f"Asset {asset} is empty (0 bytes)"

    def test_sw_event_listeners_and_strategies(self):
        assert "install" in self.sw_content
        assert "activate" in self.sw_content
        assert "fetch" in self.sw_content
        assert "skipWaiting" in self.sw_content
        assert "clients.claim" in self.sw_content


# ============================================================================
# 3. JS CONSOLIDATION & CODE SYNCHRONIZATION AUDIT
# ============================================================================


class TestJSConsolidationAndHardening:
    """Verifies JS file redundancy consolidation and CourseTracker hardening."""

    def test_simulator_and_exam_js_zero_drift(self):
        exam_js = (JS_DIR / "exam.js").read_text(encoding="utf-8")
        simulator_js = (JS_DIR / "simulator.js").read_text(encoding="utf-8")
        exam_js_norm = exam_js.replace("\r\n", "\n")
        sim_js_norm = simulator_js.replace("\r\n", "\n")
        assert exam_js_norm == sim_js_norm, "js/exam.js and js/simulator.js differ!"

    def test_tracker_js_safeGetJSON_type_guards(self):
        tracker_code = (JS_DIR / "tracker.js").read_text(encoding="utf-8")
        assert "function safeGetJSON" in tracker_code
        assert "Array.isArray(defaultVal)" in tracker_code
        assert (
            "typeof defaultVal === 'object'" in tracker_code
            or 'typeof defaultVal === "object"' in tracker_code
        )
        assert (
            "typeof defaultVal === 'string'" in tracker_code
            or 'typeof defaultVal === "string"' in tracker_code
        )
        assert (
            "typeof defaultVal === 'number'" in tracker_code
            or 'typeof defaultVal === "number"' in tracker_code
        )
        assert (
            "typeof defaultVal === 'boolean'" in tracker_code
            or 'typeof defaultVal === "boolean"' in tracker_code
        )

    def test_tracker_getOverallStats_isFinite_guards(self):
        tracker_code = (JS_DIR / "tracker.js").read_text(encoding="utf-8")
        assert "getOverallStats()" in tracker_code
        assert "isFinite" in tracker_code
        assert "!isNaN" in tracker_code


# ============================================================================
# 4. ADVERSARIAL NODE HARNESS EXECUTION
# ============================================================================


class TestAdversarialNodeSuitesExecution:
    """Runs Node.js adversarial fuzzing and stress test suites."""

    def test_run_adversarial_client_state_fuzzing(self):
        script_path = ROOT_DIR / "tests" / "adversarial_client_state_fuzzing.cjs"
        result = subprocess.run(
            ["node", str(script_path)], capture_output=True, text=True, cwd=str(ROOT_DIR)
        )
        assert result.returncode == 0, (
            f"adversarial_client_state_fuzzing failed:\n{result.stdout}\n{result.stderr}"
        )
        assert "Results: 4 passed, 0 failed" in result.stdout

    def test_run_adversarial_sw_m1(self):
        script_path = ROOT_DIR / "tests" / "adversarial_sw_m1.cjs"
        result = subprocess.run(
            ["node", str(script_path)], capture_output=True, text=True, cwd=str(ROOT_DIR)
        )
        assert result.returncode == 0, (
            f"adversarial_sw_m1 failed:\n{result.stdout}\n{result.stderr}"
        )
        assert "Challenger M1 Results: 11 passed, 0 failed" in result.stdout

    def test_run_adversarial_harness(self):
        script_path = ROOT_DIR / "tests" / "adversarial_harness.cjs"
        result = subprocess.run(
            ["node", str(script_path)], capture_output=True, text=True, cwd=str(ROOT_DIR)
        )
        assert result.returncode == 0, (
            f"adversarial_harness failed:\n{result.stdout}\n{result.stderr}"
        )
        assert "Total: 13, Passed: 13, Failed: 0" in result.stdout
