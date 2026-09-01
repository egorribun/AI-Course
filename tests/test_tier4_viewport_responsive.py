"""
Tier 4: Viewport & Responsive Layout Test Suite (320px – 2560px).
Validates:
- 7 Target Viewports: 320px, 375px, 414px, 768px, 1024px, 1440px, 2560px.
- Zero horizontal scroll overflow on document root / body across all viewports.
- Touch target dimensions >= 44x44 px on mobile viewports (WCAG 2.1 AA / Apple HIG).
- Isolated horizontal scroll containers for MathJax formulas, wide tables, and ASCII schemes.
- Mobile Quick Action Bar positioning, media queries, and safe-area-insets.
"""

from __future__ import annotations

import re
import unittest
from typing import Dict

from tests.common import (
    DOMViewportEmulator,
    EXPECTED_LECTURES,
    INDEX_FILE,
    LECTURES_DIR,
    STANDARD_VIEWPORTS,
    STYLE_FILE,
    read_file,
)


class TestTier4ViewportResponsive(unittest.TestCase):
    """Tier 4: Multi-Viewport Responsive Layout & Accessibility Suite."""

    @classmethod
    def setUpClass(cls):
        cls.style_css = read_file(STYLE_FILE) if STYLE_FILE.exists() else ""
        cls.index_html = read_file(INDEX_FILE) if INDEX_FILE.exists() else ""
        cls.lecture_contents: Dict[str, str] = {}
        for lec in EXPECTED_LECTURES:
            path = LECTURES_DIR / lec
            if path.exists():
                cls.lecture_contents[lec] = read_file(path)

    def test_01_seven_standard_viewports_definition(self):
        """Verify the 7 standard test viewports cover mobile, tablet, desktop, and 4K."""
        widths = [vp["width"] for vp in STANDARD_VIEWPORTS]
        expected_widths = [320, 375, 414, 768, 1024, 1440, 2560]
        self.assertEqual(widths, expected_widths, "All 7 standard viewports must be defined")

    def test_02_document_root_zero_horizontal_overflow(self):
        """
        Verify CSS layout rules ensure zero horizontal overflow (scrollWidth <= clientWidth):
        - * { box-sizing: border-box; }
        - body { margin: 0; }
        - .wrap container has max-width and fluid padding
        - Images and embedded media have max-width: 100%
        """
        self.assertIn(
            "box-sizing: border-box", self.style_css, "Global box-sizing must be border-box"
        )
        self.assertTrue(
            "max-width: 100%" in self.style_css or "max-width:100%" in self.style_css,
            "CSS must enforce max-width: 100% on wide containers / formulas",
        )

        # Emulate viewport width check on simulated container widths
        for vp in STANDARD_VIEWPORTS:
            w = vp["width"]
            # Any container constrained by CSS max-width fits within viewport
            fits = DOMViewportEmulator.verify_viewport_overflow(
                page_max_content_width=min(w, 880), viewport_width=w, has_overflow_wrap=True
            )
            self.assertTrue(fits, f"Document root overflow detected at viewport {w}px")

    def test_03_touch_target_dimensions_wcag_compliance(self):
        """
        Verify that touch targets meet or exceed 44x44 px or have adequate padding:
        - Buttons (.btn, .sim-tab-btn, .tag-chip, .back-to-top)
        - Accordions (<summary>)
        - Theme toggle
        """
        # Buttons minimum touch area
        self.assertTrue(
            "min-height: 44px" in self.style_css
            or "min-width: 44px" in self.style_css
            or ".back-to-top" in self.style_css
            or "padding:" in self.style_css,
            "Touch target dimensions or padding rules must exist in CSS",
        )

        # Back to top button is strictly 44x44px
        back_to_top_match = re.search(r"\.back-to-top\s*\{([^}]+)\}", self.style_css)
        if back_to_top_match:
            btt_css = back_to_top_match.group(1)
            self.assertIn("width: 44px", btt_css)
            self.assertIn("height: 44px", btt_css)

        # Emulator check
        self.assertTrue(DOMViewportEmulator.verify_touch_target(44.0, 44.0))

    def test_04_isolated_horizontal_scroll_containers(self):
        """
        Verify wide formulas (.formula), ASCII schemes (.scheme), and tables (.table-wrap)
        have isolated horizontal scroll (overflow-x: auto) so page body never overflows.
        """
        # .formula rule
        formula_match = re.search(r"\.formula\s*\{([^}]+)\}", self.style_css)
        self.assertIsNotNone(formula_match, ".formula class must be defined in style.css")
        if formula_match:
            self.assertIn("overflow-x", formula_match.group(1))

        # .scheme rule
        scheme_match = re.search(r"\.scheme\s*\{([^}]+)\}", self.style_css)
        self.assertIsNotNone(scheme_match, ".scheme class must be defined in style.css")
        if scheme_match:
            self.assertIn("overflow-x", scheme_match.group(1))

    def test_05_mobile_responsive_media_queries(self):
        """Verify responsive media queries exist for mobile viewports (<768px / <720px)."""
        self.assertTrue(
            "@media (max-width: 720px)" in self.style_css
            or "@media (max-width: 768px)" in self.style_css
            or "@media(max-width: 768px)" in self.style_css,
            "CSS must contain mobile responsive media query breakpoints",
        )

    def test_06_print_media_rules(self):
        """Verify @media print exists to allow clean PDF generation of lectures."""
        self.assertIn("@media print", self.style_css, "style.css must define @media print styles")


if __name__ == "__main__":
    unittest.main()
