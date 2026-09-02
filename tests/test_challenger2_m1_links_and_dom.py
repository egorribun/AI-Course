"""
Adversarial Challenger 2 Verification Suite for Milestone M1 (PyTest Runner).
Verifies:
1. Universal #course-progress-modal markup & attributes across all 30 HTML documents.
2. Complete Isolation of #exam-simulator-container (absent in index and 28 lectures, present in exam.html).
3. Relative link graph resolution from all 28 lectures to index.html and exam.html.
4. Synchronized theme toggling DOM contracts.
5. CSS Safe Area Inset and Responsive rules.
"""

from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Set, Tuple

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
INDEX_HTML = COURSE_ROOT / "index.html"
EXAM_HTML = COURSE_ROOT / "exam.html"
STYLE_CSS = COURSE_ROOT / "style.css"
TRACKER_JS = COURSE_ROOT / "js" / "tracker.js"
APP_JS = COURSE_ROOT / "js" / "app.js"

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


class LinkAndDOMCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.element_ids: Set[str] = set()
        self.classes: Set[str] = set()
        self.links: List[Tuple[str, str, Dict[str, str]]] = []  # (tag, text, attrs)
        self.scripts: List[str] = []
        self._current_tag: str | None = None
        self._current_attrs: Dict[str, str] = {}
        self._current_text: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag_id = attr_dict.get("id")
        if tag_id:
            self.element_ids.add(tag_id)

        tag_cls = attr_dict.get("class", "")
        for c in tag_cls.split():
            if c:
                self.classes.add(c)

        if tag == "script" and "src" in attr_dict:
            self.scripts.append(attr_dict["src"])

        if tag == "a" or tag == "button":
            self._current_tag = tag
            self._current_attrs = attr_dict
            self._current_text = []

    def handle_data(self, data: str):
        if self._current_tag:
            self._current_text.append(data)

    def handle_endtag(self, tag: str):
        if tag == self._current_tag:
            self.links.append((tag, "".join(self._current_text).strip(), self._current_attrs))
            self._current_tag = None
            self._current_attrs = {}
            self._current_text = []


class TestM1Challenger2Empirical(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index_content = INDEX_HTML.read_text(encoding="utf-8")
        cls.exam_content = EXAM_HTML.read_text(encoding="utf-8")
        cls.style_content = STYLE_CSS.read_text(encoding="utf-8")
        cls.tracker_content = TRACKER_JS.read_text(encoding="utf-8")
        cls.app_content = APP_JS.read_text(encoding="utf-8")

        cls.lecture_contents = {
            lec: (LECTURES_DIR / lec).read_text(encoding="utf-8") for lec in EXPECTED_LECTURES
        }

    # -------------------------------------------------------------------------
    # 1. Universal Progress Modal Markup in All 30 Pages
    # -------------------------------------------------------------------------
    def test_01_progress_modal_in_all_30_documents(self):
        """Verify #course-progress-modal exists with all required child IDs across all 30 HTML files."""
        all_docs = [("index.html", self.index_content), ("exam.html", self.exam_content)] + [
            (f"lectures/{lec}", content) for lec, content in self.lecture_contents.items()
        ]
        self.assertEqual(len(all_docs), 30)

        required_modal_ids = [
            "course-progress-modal",
            "modal-progress-title",
            "modal-progress-close",
            "modal-progress-fill",
            "modal-progress-percent",
            "modal-stat-lecs",
            "modal-stat-qas",
            "modal-stat-tasks",
            "modal-reset-progress-btn",
            "modal-close-action-btn",
        ]

        for doc_name, content in all_docs:
            parser = LinkAndDOMCollector()
            parser.feed(content)

            for req_id in required_modal_ids:
                self.assertIn(
                    req_id,
                    parser.element_ids,
                    f"Document {doc_name} is missing modal element #{req_id}",
                )

            # Check modal overlay attributes
            self.assertIn(
                'class="progress-modal-overlay"',
                content,
                f"{doc_name} missing .progress-modal-overlay",
            )
            self.assertIn('role="dialog"', content, f"{doc_name} missing role='dialog'")
            self.assertIn('aria-modal="true"', content, f"{doc_name} missing aria-modal='true'")

    # -------------------------------------------------------------------------
    # 2. Simulator Isolation Invariants
    # -------------------------------------------------------------------------
    def test_02_exam_simulator_strictly_isolated_to_exam_page(self):
        """Verify #exam-simulator-container is strictly absent from index.html & 28 lectures, present in exam.html."""
        # 1. index.html checks
        self.assertNotIn(
            'id="exam-simulator-container"',
            self.index_content,
            "index.html must NOT contain id='exam-simulator-container'",
        )
        self.assertNotIn(
            "id='exam-simulator-container'",
            self.index_content,
            "index.html must NOT contain id='exam-simulator-container'",
        )
        self.assertNotIn(
            "js/simulator.js",
            self.index_content,
            "index.html must NOT link js/simulator.js",
        )

        # 2. exam.html checks
        exam_parser = LinkAndDOMCollector()
        exam_parser.feed(self.exam_content)
        has_simulator = (
            "exam-simulator-container" in exam_parser.element_ids
            or "sim-container" in exam_parser.classes
        )
        self.assertTrue(has_simulator, "exam.html must contain simulator container")
        self.assertIn("js/exam.js", exam_parser.scripts, "exam.html must link js/exam.js")

        # 3. All 28 lectures
        for lec, content in self.lecture_contents.items():
            self.assertNotIn(
                'id="exam-simulator-container"',
                content,
                f"Lecture {lec} must NOT contain id='exam-simulator-container'",
            )
            self.assertNotIn(
                "js/simulator.js",
                content,
                f"Lecture {lec} must NOT link js/simulator.js",
            )

    # -------------------------------------------------------------------------
    # 3. Relative Navigation Links Graph Resolution
    # -------------------------------------------------------------------------
    def test_03_relative_navigation_links_resolution_from_lectures(self):
        """Verify all 28 lectures contain valid relative navigation links in .bottom-nav-bar."""
        for lec, content in self.lecture_contents.items():
            lec_file = LECTURES_DIR / lec
            parser = LinkAndDOMCollector()
            parser.feed(content)

            # Check search nav link
            search_links = [
                attrs.get("href")
                for tag, text, attrs in parser.links
                if attrs.get("id") == "nav-search-btn"
            ]
            self.assertEqual(len(search_links), 1, f"{lec} must have exactly one #nav-search-btn")
            search_href = search_links[0]
            self.assertEqual(
                search_href,
                "../index.html?focus=search",
                f"{lec} #nav-search-btn must link to ../index.html?focus=search",
            )

            # Check target exists on disk
            target_path = (lec_file.parent / search_href.split("?")[0]).resolve()
            self.assertTrue(
                target_path.is_file(),
                f"Target {target_path} referenced by {lec} must exist on disk",
            )

            # Check exam nav link
            exam_links = [
                attrs.get("href")
                for tag, text, attrs in parser.links
                if attrs.get("id") == "nav-exam-btn"
            ]
            self.assertEqual(len(exam_links), 1, f"{lec} must have exactly one #nav-exam-btn")
            exam_href = exam_links[0]
            self.assertEqual(
                exam_href,
                "../exam.html",
                f"{lec} #nav-exam-btn must link to ../exam.html",
            )
            target_exam = (lec_file.parent / exam_href).resolve()
            self.assertTrue(
                target_exam.is_file(),
                f"Target {target_exam} referenced by {lec} must exist on disk",
            )

            # Check Progress button
            self.assertIn(
                "nav-progress-btn", parser.element_ids, f"{lec} must contain #nav-progress-btn"
            )

    # -------------------------------------------------------------------------
    # 4. Theme Synchronization DOM Contracts
    # -------------------------------------------------------------------------
    def test_04_theme_sync_contract_and_event_handling(self):
        """Verify tracker.js provides complete theme update and synchronization contracts."""
        self.assertIn("updateThemeButtons()", self.tracker_content)
        self.assertIn("toggleTheme()", self.tracker_content)
        self.assertIn("setTheme(", self.tracker_content)
        self.assertIn(".theme-toggle", self.tracker_content)
        self.assertIn("data-theme", self.tracker_content)
        self.assertIn("ai_course_theme", self.tracker_content)

        # In index.html and exam.html, verify header theme toggle exists
        for name, html in [("index.html", self.index_content), ("exam.html", self.exam_content)]:
            self.assertIn(
                'class="theme-toggle"', html, f"{name} must contain .theme-toggle button in header"
            )

    # -------------------------------------------------------------------------
    # 5. CSS Responsive Viewport and Safe Area Insets
    # -------------------------------------------------------------------------
    def test_05_css_responsive_navigation_and_safe_area_insets(self):
        """Verify CSS responsive media queries and Safe Area Inset properties."""
        # Check desktop header actions
        self.assertIn(".header-actions", self.style_content)
        self.assertIn(".btn-header-exam", self.style_content)

        # Check mobile breakpoint
        self.assertIn("@media (max-width: 767px)", self.style_content)

        # Check bottom nav display and position on mobile
        self.assertIn(".bottom-nav-bar", self.style_content)
        self.assertIn("env(safe-area-inset-bottom", self.style_content)
        self.assertIn(
            "padding-bottom: max(8px, env(safe-area-inset-bottom, 0px))", self.style_content
        )
        self.assertIn(
            "padding-bottom: calc(72px + env(safe-area-inset-bottom, 0px))", self.style_content
        )

        # Back to top button elevation
        self.assertIn("calc(80px + env(safe-area-inset-bottom, 0px))", self.style_content)

        # Modal styles
        self.assertIn(".progress-modal-overlay", self.style_content)
        self.assertIn(".progress-modal-content", self.style_content)
        self.assertIn(".progress-modal-overlay[hidden]", self.style_content)


if __name__ == "__main__":
    unittest.main()
