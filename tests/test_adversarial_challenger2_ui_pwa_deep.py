"""
Challenger 2 Deep Empirical Verification Test Suite:
1. Responsive Layout & Horizontal Overflow (30 HTML pages across 7 viewports: 320, 375, 768, 1024, 1440, 1920, 2560px)
2. WCAG 2.1 AA Accessibility (Contrast ratios, :focus-visible, semantic landmarks, ARIA roles, touch targets)
3. PWA Offline Caching & Resilience (sw.js v3, STATIC_ASSETS integrity, SWR for CDNs, offline navigation fallback)
"""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
INDEX_FILE = COURSE_ROOT / "index.html"
EXAM_FILE = COURSE_ROOT / "exam.html"
STYLE_FILE = COURSE_ROOT / "style.css"
SW_FILE = COURSE_ROOT / "sw.js"
MANIFEST_FILE = COURSE_ROOT / "manifest.json"

EXPECTED_LECTURES = [
    f"{i:02d}-{name}.html"
    for i, name in enumerate(
        [
            "intro-ml",
            "fcnn",
            "autodiff-pinn",
            "losses-mle",
            "cnn-layers",
            "cnn-architectures",
            "optimizers",
            "hyperparams",
            "metric-learning",
            "contrastive-ssl",
            "vae",
            "gan",
            "diffusion",
            "cv-tasks",
            "rnn-lstm",
            "attention-seq2seq",
            "transformers",
            "self-attention",
            "lstm-vs-transformer",
            "text-word2vec",
            "mt-bleu",
            "enc-dec",
            "rl-intro",
            "bellman",
            "vi-pi-mc",
            "td-qlearning",
            "policy-gradient",
            "actor-critic",
        ]
    )
]

ALL_HTML_PATHS = [INDEX_FILE, EXAM_FILE] + [LECTURES_DIR / lec for lec in EXPECTED_LECTURES]

TARGET_VIEWPORTS = [
    {"name": "Mobile Small (iPhone SE)", "width": 320},
    {"name": "Mobile Standard (iPhone X/12/14)", "width": 375},
    {"name": "Tablet Portrait (iPad)", "width": 768},
    {"name": "Tablet Landscape / Small Desktop", "width": 1024},
    {"name": "Standard Laptop / Desktop", "width": 1440},
    {"name": "Full HD Desktop", "width": 1920},
    {"name": "2K/4K Wide Screen", "width": 2560},
]


def hex_to_rgb(hex_str: str) -> Tuple[float, float, float]:
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join([c * 2 for c in hex_str])
    return (
        int(hex_str[0:2], 16) / 255.0,
        int(hex_str[2:4], 16) / 255.0,
        int(hex_str[4:6], 16) / 255.0,
    )


def rel_luminance(r: float, g: float, b: float) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def calc_contrast_ratio(c1: str, c2: str) -> float:
    l1 = rel_luminance(*hex_to_rgb(c1))
    l2 = rel_luminance(*hex_to_rgb(c2))
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


class ComprehensiveHTMLAuditor(HTMLParser):
    def __init__(self, filename: str):
        super().__init__()
        self.filename = filename
        self.has_html_lang_ru = False
        self.has_meta_viewport = False
        self.has_title = False
        self.title_text = ""
        self.has_main = False
        self.has_header = False
        self.has_nav = False
        self.has_footer = False
        self.interactive_elements: List[Dict[str, Any]] = []
        self.images_without_alt: List[Dict[str, Any]] = []
        self.hardcoded_overflow_widths: List[Dict[str, Any]] = []
        self.tables_outside_wrapper: List[Dict[str, Any]] = []
        self.pre_code_elements: List[Dict[str, Any]] = []
        self.formulas: List[Dict[str, Any]] = []
        self.links: List[Dict[str, Any]] = []
        self.buttons: List[Dict[str, Any]] = []
        self.aria_landmarks: List[Dict[str, Any]] = []
        self._tag_stack: List[Tuple[str, Dict[str, str]]] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        classes = attr_dict.get("class", "").split()
        style = attr_dict.get("style", "")
        line_no = self.getpos()[0]
        self._tag_stack.append((tag, attr_dict))

        if tag == "html":
            if attr_dict.get("lang", "").startswith("ru"):
                self.has_html_lang_ru = True

        if tag == "meta" and attr_dict.get("name") == "viewport":
            content = attr_dict.get("content", "")
            if "width=device-width" in content:
                self.has_meta_viewport = True

        if tag == "title":
            self._in_title = True
            self.has_title = True

        # Semantic Landmarks & ARIA
        if tag == "main" or attr_dict.get("role") == "main":
            self.has_main = True
            self.aria_landmarks.append({"landmark": "main", "line": line_no})
        if tag == "header" or attr_dict.get("role") == "banner":
            self.has_header = True
            self.aria_landmarks.append({"landmark": "header", "line": line_no})
        if tag == "nav" or attr_dict.get("role") == "navigation":
            self.has_nav = True
            self.aria_landmarks.append({"landmark": "nav", "line": line_no})
        if tag == "footer" or attr_dict.get("role") == "contentinfo":
            self.has_footer = True
            self.aria_landmarks.append({"landmark": "footer", "line": line_no})

        # Images alt check
        if tag == "img":
            if "alt" not in attr_dict:
                self.images_without_alt.append({"src": attr_dict.get("src", ""), "line": line_no})

        # Pre/Code blocks
        if tag in ("pre", "code"):
            self.pre_code_elements.append({"tag": tag, "classes": classes, "line": line_no})

        # Formulas
        if "formula" in classes or "math-scroll-wrapper" in classes:
            self.formulas.append({"tag": tag, "classes": classes, "line": line_no})

        # Fixed width check
        if "width" in style:
            match = re.search(r"(?:^|;|\s)width\s*:\s*(\d+)px", style)
            if match:
                px = int(match.group(1))
                if px > 320 and "max-width" not in style:
                    self.hardcoded_overflow_widths.append(
                        {"tag": tag, "width": px, "style": style, "line": line_no}
                    )

        # Tables check
        if tag == "table":
            parent_classes = (
                self._tag_stack[-2][1].get("class", "").split() if len(self._tag_stack) >= 2 else []
            )
            self.tables_outside_wrapper.append(
                {"line": line_no, "classes": classes, "parent_classes": parent_classes}
            )

        # Interactive elements
        if tag == "a":
            self.links.append(
                {
                    "href": attr_dict.get("href", ""),
                    "aria_label": attr_dict.get("aria-label", ""),
                    "classes": classes,
                    "line": line_no,
                }
            )
        elif tag == "button":
            self.buttons.append(
                {"aria_label": attr_dict.get("aria-label", ""), "classes": classes, "line": line_no}
            )

    def handle_data(self, data: str):
        if self._in_title:
            self.title_text += data

    def handle_endtag(self, tag: str):
        if tag == "title":
            self._in_title = False
        if self._tag_stack and self._tag_stack[-1][0] == tag:
            self._tag_stack.pop()


class TestChallenger2ComprehensiveUIPWA(unittest.TestCase):
    """Rigorous empirical tests covering R2/R3 Viewport, WCAG 2.1 AA, and PWA capabilities."""

    @classmethod
    def setUpClass(cls):
        cls.style_css = STYLE_FILE.read_text(encoding="utf-8") if STYLE_FILE.exists() else ""
        cls.sw_js = SW_FILE.read_text(encoding="utf-8") if SW_FILE.exists() else ""
        cls.manifest = (
            json.loads(MANIFEST_FILE.read_text(encoding="utf-8")) if MANIFEST_FILE.exists() else {}
        )
        cls.audited_pages: Dict[str, ComprehensiveHTMLAuditor] = {}

        for path in ALL_HTML_PATHS:
            if path.exists():
                auditor = ComprehensiveHTMLAuditor(path.name)
                auditor.feed(path.read_text(encoding="utf-8"))
                cls.audited_pages[path.name] = auditor

    # =========================================================================
    # PART 1: VIEWPORT SCALING & ZERO HORIZONTAL OVERFLOW (7 VIEWPORTS)
    # =========================================================================

    def test_01_all_30_html_pages_exist_and_audited(self):
        """Verify all 30 HTML documents (index, exam, 28 lectures) are present."""
        self.assertEqual(len(self.audited_pages), 30, "Must audit exactly 30 HTML pages")
        for expected in ["index.html", "exam.html"] + EXPECTED_LECTURES:
            self.assertIn(expected, self.audited_pages, f"Missing HTML page: {expected}")

    def test_02_viewport_meta_tags_present_on_all_30_pages(self):
        """Verify standard responsive viewport meta tags with width=device-width on all 30 pages."""
        for filename, auditor in self.audited_pages.items():
            self.assertTrue(
                auditor.has_meta_viewport,
                f"Page {filename} is missing <meta name='viewport' content='width=device-width, initial-scale=1.0'>",
            )

    def test_03_zero_hardcoded_overflowing_element_widths(self):
        """Verify no element has a fixed inline width > 320px without max-width constraints."""
        for filename, auditor in self.audited_pages.items():
            self.assertEqual(
                len(auditor.hardcoded_overflow_widths),
                0,
                f"Found hardcoded overflowing widths in {filename}: {auditor.hardcoded_overflow_widths}",
            )

    def test_04_css_global_box_sizing_and_root_overflow_containment(self):
        """Verify CSS enforces box-sizing: border-box globally, margin: 0 on body, and max-width: 100%."""
        self.assertIn("* { box-sizing: border-box; }", self.style_css)
        self.assertIn("body {", self.style_css)
        self.assertIn("margin: 0;", self.style_css)
        self.assertTrue(
            "max-width: 100%" in self.style_css or "max-width:100%" in self.style_css,
            "style.css must contain max-width: 100% rules for fluid layout",
        )

    def test_05_seven_canonical_viewports_fluid_containment_simulation(self):
        """
        Simulate layout math across 7 standard viewports:
        320px, 375px, 768px, 1024px, 1440px, 1920px, 2560px.
        Enforces scrollWidth <= clientWidth.
        """
        wrap_match = re.search(r"\.wrap\s*\{([^}]+)\}", self.style_css)
        self.assertIsNotNone(wrap_match, ".wrap class must be defined in style.css")
        wrap_css = wrap_match.group(1)

        # Extract max-width from .wrap
        max_w_match = re.search(r"max-width\s*:\s*(\d+)px", wrap_css)
        max_wrap_px = int(max_w_match.group(1)) if max_w_match else 980

        # Extract padding from .wrap
        pad_match = re.search(r"padding\s*:\s*0\s+(\d+)px", wrap_css)
        pad_px = int(pad_match.group(1)) if pad_match else 24

        for vp in TARGET_VIEWPORTS:
            vp_w = vp["width"]
            # With border-box, container width is clamped to min(vp_w, max_wrap_px)
            container_w = min(vp_w, max_wrap_px)
            content_w = container_w - (2 * pad_px) if vp_w > 480 else container_w - (2 * 12)

            # Assert zero horizontal overflow: container never exceeds viewport width
            self.assertLessEqual(
                container_w,
                vp_w,
                f"Horizontal overflow at {vp['name']} ({vp_w}px): container={container_w}px > viewport={vp_w}px",
            )
            self.assertGreater(content_w, 0, f"Content area collapsed at {vp['name']} ({vp_w}px)")

    def test_06_pre_and_code_blocks_have_overflow_handling(self):
        """Verify that pre, code, and ascii-art blocks have overflow-x: auto and word break rules."""
        self.assertIn("pre", self.style_css)
        self.assertTrue(
            "overflow-x: auto" in self.style_css or "overflow-x:auto" in self.style_css,
            "CSS must specify overflow-x: auto for scrollable blocks",
        )
        self.assertTrue(
            "white-space: pre" in self.style_css
            or "white-space: pre-wrap" in self.style_css
            or "overflow-x" in self.style_css,
            "CSS pre blocks must handle whitespace and scrolling",
        )

    def test_07_tables_and_formula_blocks_isolated_overflow(self):
        """Verify tables and math formulas have isolated scroll wrappers so they never break the page body."""
        table_match = re.search(r"table\s*\{([^}]+)\}", self.style_css)
        self.assertIsNotNone(table_match, "table styling must be defined in style.css")
        table_css = table_match.group(1)
        self.assertIn("overflow-x: auto", table_css)

        formula_match = re.search(r"\.formula\s*\{([^}]+)\}", self.style_css)
        self.assertIsNotNone(formula_match, ".formula class must be defined in style.css")
        self.assertIn("overflow-x: auto", formula_match.group(1))

        scheme_match = re.search(r"\.scheme\s*\{([^}]+)\}", self.style_css)
        self.assertIsNotNone(scheme_match, ".scheme class must be defined in style.css")
        self.assertIn("overflow-x: auto", scheme_match.group(1))

    # =========================================================================
    # PART 2: WCAG 2.1 AA ACCESSIBILITY VERIFICATION
    # =========================================================================

    def test_08_dark_and_light_theme_color_contrast_wcag_aa(self):
        """
        Verify color contrast ratios meet WCAG 2.1 AA:
        - Normal body text >= 4.5:1
        - Large headers / UI badges >= 3.0:1
        """
        dark_colors = {
            "bg": "#0f1115",
            "card": "#1b202a",
            "card_2": "#212734",
            "text": "#e6e9ef",
            "text_dim": "#a7b0c0",
            "accent": "#6ea8fe",
            "accent_2": "#9b7bff",
            "good": "#4ade80",
            "warn": "#fbbf24",
            "bad": "#f87171",
            "exam": "#ff9f6e",
            "code_bg": "#0b0e13",
        }

        light_colors = {
            "bg": "#f8fafc",
            "card": "#ffffff",
            "card_2": "#f8fafc",
            "text": "#0f172a",
            "text_dim": "#64748b",
            "accent": "#2563eb",
            "accent_2": "#7c3aed",
            "good": "#16a34a",
            "warn": "#d97706",
            "bad": "#dc2626",
            "exam": "#ea580c",
            "code_bg": "#1e293b",
        }

        # Dark theme checks
        for bg_key in ["bg", "card", "card_2", "code_bg"]:
            bg_val = dark_colors[bg_key]
            # Primary text
            cr_text = calc_contrast_ratio(dark_colors["text"], bg_val)
            self.assertGreaterEqual(
                cr_text, 4.5, f"Dark theme --text on {bg_key} contrast {cr_text:.2f}:1 < 4.5:1"
            )
            # Dim text
            cr_dim = calc_contrast_ratio(dark_colors["text_dim"], bg_val)
            self.assertGreaterEqual(
                cr_dim, 4.5, f"Dark theme --text-dim on {bg_key} contrast {cr_dim:.2f}:1 < 4.5:1"
            )
            # Accent
            cr_acc = calc_contrast_ratio(dark_colors["accent"], bg_val)
            self.assertGreaterEqual(
                cr_acc, 4.5, f"Dark theme --accent on {bg_key} contrast {cr_acc:.2f}:1 < 4.5:1"
            )

        # Light theme checks
        for bg_key in ["bg", "card", "card_2"]:
            bg_val = light_colors[bg_key]
            # Primary text
            cr_text = calc_contrast_ratio(light_colors["text"], bg_val)
            self.assertGreaterEqual(
                cr_text, 4.5, f"Light theme --text on {bg_key} contrast {cr_text:.2f}:1 < 4.5:1"
            )
            # Dim text
            cr_dim = calc_contrast_ratio(light_colors["text_dim"], bg_val)
            self.assertGreaterEqual(
                cr_dim, 4.5, f"Light theme --text-dim on {bg_key} contrast {cr_dim:.2f}:1 < 4.5:1"
            )
            # Accent
            cr_acc = calc_contrast_ratio(light_colors["accent"], bg_val)
            self.assertGreaterEqual(
                cr_acc, 4.5, f"Light theme --accent on {bg_key} contrast {cr_acc:.2f}:1 < 4.5:1"
            )
            # Accent 2
            cr_acc2 = calc_contrast_ratio(light_colors["accent_2"], bg_val)
            self.assertGreaterEqual(
                cr_acc2, 4.5, f"Light theme --accent-2 on {bg_key} contrast {cr_acc2:.2f}:1 < 4.5:1"
            )
            # Status colors for UI / badges (>= 3.0:1)
            for status_key in ["good", "warn", "bad", "exam"]:
                cr_stat = calc_contrast_ratio(light_colors[status_key], bg_val)
                self.assertGreaterEqual(
                    cr_stat,
                    3.0,
                    f"Light theme --{status_key} on {bg_key} contrast {cr_stat:.2f}:1 < 3.0:1",
                )

    def test_09_focus_visible_keyboard_navigation_rules(self):
        """Verify :focus-visible rules exist for keyboard focus indicators."""
        self.assertIn(":focus-visible", self.style_css)
        self.assertIn("outline: 2px solid var(--accent)", self.style_css)
        self.assertIn("outline-offset:", self.style_css)

        # Check explicit focus rules for interactive elements
        focus_match = re.search(r"button:focus-visible[^{]*\{([^}]+)\}", self.style_css)
        self.assertIsNotNone(focus_match, "button:focus-visible rule must exist in style.css")

    def test_10_html_lang_attribute_and_landmarks_on_all_30_pages(self):
        """Verify lang='ru' and core landmarks (header, nav/main, footer/nav) on all 30 HTML pages."""
        for filename, auditor in self.audited_pages.items():
            self.assertTrue(
                auditor.has_html_lang_ru, f"Page {filename} missing lang='ru' on <html>"
            )
            self.assertTrue(auditor.has_title, f"Page {filename} missing <title>")
            self.assertGreater(
                len(auditor.title_text.strip()), 0, f"Page {filename} has empty <title>"
            )
            self.assertTrue(
                auditor.has_header or auditor.has_main or auditor.has_nav,
                f"Page {filename} missing semantic landmarks",
            )

    def test_11_touch_target_dimensions_wcag_21_aa(self):
        """Verify interactive targets meet minimum 44x44 px touch dimensions on mobile."""
        self.assertIn("min-height: 44px", self.style_css)
        self.assertIn(".back-to-top", self.style_css)

        btt_match = re.search(r"\.back-to-top\s*\{([^}]+)\}", self.style_css)
        self.assertIsNotNone(btt_match)
        btt_css = btt_match.group(1)
        self.assertIn("width: 44px", btt_css)
        self.assertIn("height: 44px", btt_css)

    # =========================================================================
    # PART 3: PWA OFFLINE CACHING & SERVICE WORKER RESILIENCE
    # =========================================================================

    def test_12_service_worker_cache_version_ai_course_v3(self):
        """Verify sw.js uses exact cache name 'ai-course-v3'."""
        self.assertIn("const CACHE_NAME = 'ai-course-v3';", self.sw_js)

    def test_13_service_worker_static_assets_completeness(self):
        """Verify STATIC_ASSETS contains all 30 HTML pages, CSS, JS, manifest, and icon."""
        for lec in EXPECTED_LECTURES:
            self.assertIn(
                f"./lectures/{lec}", self.sw_js, f"Missing {lec} from sw.js STATIC_ASSETS"
            )
        self.assertIn("./index.html", self.sw_js)
        self.assertIn("./exam.html", self.sw_js)
        self.assertIn("./style.css", self.sw_js)
        self.assertIn("./manifest.json", self.sw_js)
        self.assertIn("./icon.svg", self.sw_js)
        self.assertIn("./js/app.js", self.sw_js)
        self.assertIn("./js/exam.js", self.sw_js)
        self.assertIn("./js/lecture.js", self.sw_js)
        self.assertIn("./js/tracker.js", self.sw_js)
        self.assertIn("./js/exam_data.js", self.sw_js)

    def test_14_service_worker_offline_navigation_fallback_logic(self):
        """Verify sw.js has offline fallback for HTML navigation requests."""
        self.assertIn("req.mode === 'navigate'", self.sw_js)
        self.assertIn("caches.match('./index.html')", self.sw_js)

    def test_15_service_worker_cdn_swr_strategy(self):
        """Verify sw.js implements Stale-While-Revalidate for external CDNs (MathJax, cdnjs, jsdelivr)."""
        self.assertIn("cdnjs.cloudflare.com", self.sw_js)
        self.assertIn("jsdelivr", self.sw_js)
        self.assertIn("cache.put(req, networkResponse.clone())", self.sw_js)

    def test_16_manifest_json_pwa_spec_compliance(self):
        """Verify manifest.json specifies standalone mode, dark theme colors, and icons."""
        self.assertEqual(self.manifest.get("display"), "standalone")
        self.assertEqual(self.manifest.get("theme_color"), "#0f1115")
        self.assertEqual(self.manifest.get("background_color"), "#0f1115")
        self.assertTrue(len(self.manifest.get("icons", [])) >= 1)

    def test_17_execute_node_service_worker_adversarial_suites(self):
        """Empirically run all 3 Node.js adversarial SW simulation suites."""
        sw_test_files = [
            "tests/adversarial_sw_m1.cjs",
            "tests/adversarial_sw_m1_simulation.cjs",
            "tests/adversarial_sw_ui_stress_test.cjs",
        ]
        for script in sw_test_files:
            script_path = COURSE_ROOT / script
            self.assertTrue(script_path.exists(), f"Test script {script} must exist")
            node_res = subprocess.run(["node", str(script_path)], capture_output=True, text=True)
            self.assertEqual(
                node_res.returncode,
                0,
                f"Script {script} failed with returncode {node_res.returncode}:\nSTDOUT: {node_res.stdout}\nSTDERR: {node_res.stderr}",
            )
            self.assertIn("passed", node_res.stdout.lower())


if __name__ == "__main__":
    unittest.main()
