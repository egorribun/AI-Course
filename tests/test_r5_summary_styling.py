"""
Requirement R5 Tests: Summary Marker & Solution Arrow Polish.
State University of Management (GUU, 2026) DL Course Verification.

Verifies:
- All stylesheets (style.css, index.html, and 28 lectures) properly hide native browser disclosure markers
  with list-style: none, list-style-type: none, ::-webkit-details-marker { display: none }, and ::marker { display: none }.
- ::before pseudo-element acts as the sole expansion indicator (▸ closed, ▾ open).
- No HTML files contain literal arrow characters (▸, ▶, ▾) inside task <summary> tags.
- All 170 task solutions consistently render <summary>Решение</summary>.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path
from typing import List

COURSE_ROOT_DIR = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT_DIR))

from tests.common import EXPECTED_LECTURES, INDEX_FILE, LECTURES_DIR, COURSE_ROOT, read_file


class TestR5SummaryStyling(unittest.TestCase):
    """Test suite for Requirement R5: Summary Marker & Solution Arrow Polish."""

    @classmethod
    def setUpClass(cls):
        cls.style_css_path = COURSE_ROOT / "style.css"
        cls.index_path = INDEX_FILE
        cls.lecture_paths = [LECTURES_DIR / lec for lec in EXPECTED_LECTURES]

    def test_01_style_css_and_html_summary_marker_rules(self):
        """Verify .task details summary and .qa > summary have complete marker suppression rules."""
        files_with_embedded_css = [self.style_css_path, self.index_path] + [
            p for p in self.lecture_paths if p.name != "10-vae.html"
        ]
        
        for fpath in files_with_embedded_css:
            content = read_file(fpath)
            
            # .task details summary checks
            self.assertTrue(
                re.search(r"\.task\s+details\s+summary\s*\{[^}]*list-style:\s*none", content),
                f"{fpath.name}: 'list-style: none' missing in .task details summary",
            )
            self.assertTrue(
                re.search(r"\.task\s+details\s+summary\s*\{[^}]*list-style-type:\s*none", content),
                f"{fpath.name}: 'list-style-type: none' missing in .task details summary",
            )
            self.assertTrue(
                re.search(r"\.task\s+details\s+summary::-webkit-details-marker\s*\{\s*display:\s*none;?\s*\}", content),
                f"{fpath.name}: '::-webkit-details-marker' display:none missing in .task details summary",
            )
            self.assertTrue(
                re.search(r"\.task\s+details\s+summary::marker\s*\{\s*display:\s*none;?\s*\}", content),
                f"{fpath.name}: '::marker' display:none missing in .task details summary",
            )
            self.assertTrue(
                re.search(r'\.task\s+details\s+summary::before\s*\{[^}]*content:\s*"▸ "', content),
                f"{fpath.name}: closed arrow '▸ ' pseudo-element missing in .task details summary::before",
            )
            self.assertTrue(
                re.search(r'\.task\s+details\[open\]\s+summary::before\s*\{[^}]*content:\s*"▾ "', content),
                f"{fpath.name}: open arrow '▾ ' pseudo-element missing in .task details[open] summary::before",
            )

            # .qa > summary checks
            self.assertTrue(
                re.search(r"\.qa\s*>\s*summary\s*\{[^}]*list-style:\s*none", content),
                f"{fpath.name}: 'list-style: none' missing in .qa > summary",
            )
            self.assertTrue(
                re.search(r"\.qa\s*>\s*summary\s*\{[^}]*list-style-type:\s*none", content),
                f"{fpath.name}: 'list-style-type: none' missing in .qa > summary",
            )
            self.assertTrue(
                re.search(r"\.qa\s*>\s*summary::-webkit-details-marker\s*\{\s*display:\s*none;?\s*\}", content),
                f"{fpath.name}: '::-webkit-details-marker' display:none missing in .qa > summary",
            )
            self.assertTrue(
                re.search(r"\.qa\s*>\s*summary::marker\s*\{\s*display:\s*none;?\s*\}", content),
                f"{fpath.name}: '::marker' display:none missing in .qa > summary",
            )
            self.assertTrue(
                re.search(r'\.qa\s*>\s*summary::before\s*\{[^}]*content:\s*"❯ "', content),
                f"{fpath.name}: '❯ ' pseudo-element missing in .qa > summary::before",
            )

    def test_02_no_literal_arrows_in_task_summary_html(self):
        """Verify no hardcoded arrow characters remain in task <summary> across all 28 lectures."""
        for fpath in self.lecture_paths:
            content = read_file(fpath)
            task_summaries = re.findall(r'<div class=["\']task["\'].*?<summary>(.*?)</summary>', content, flags=re.DOTALL)
            self.assertGreater(len(task_summaries), 0, f"No task summaries found in {fpath.name}")
            for s in task_summaries:
                self.assertEqual(s.strip(), "Решение", f"{fpath.name}: Unexpected task summary content '{s}'")
                for arrow in ["▸", "▶", "▾", "►", "▼", "❯", "›"]:
                    self.assertNotIn(arrow, s, f"{fpath.name}: Literal arrow '{arrow}' found in task summary '{s}'")

    def test_03_total_tasks_solution_count_integrity(self):
        """Verify all 170 task solutions across all 28 lectures have uniform <summary>Решение</summary>."""
        total_tasks = 0
        for fpath in self.lecture_paths:
            content = read_file(fpath)
            sols = re.findall(r"<summary>Решение</summary>", content)
            total_tasks += len(sols)
        self.assertEqual(total_tasks, 170, f"Expected exactly 170 standardized task solutions, found {total_tasks}")

    def test_04_lecture_10_vae_stylesheet_link(self):
        """Verify lecture 10-vae.html correctly imports external style.css."""
        content = read_file(LECTURES_DIR / "10-vae.html")
        self.assertIn('<link rel="stylesheet" href="../style.css">', content)

    def test_05_qa_summaries_no_duplicate_arrows(self):
        """Verify none of the 296 QA question summaries have hardcoded leading arrows."""
        arrow_chars = ["▸", "▶", "▾", "►", "▼", "❯", "›", "→", "➜", "➤", "»"]
        total_qa = 0
        for fpath in self.lecture_paths:
            content = read_file(fpath)
            qa_summaries = re.findall(
                r'<details\s+class=["\']qa["\'][^>]*>\s*<summary>(.*?)</summary>',
                content,
                re.DOTALL,
            )
            total_qa += len(qa_summaries)
            for s in qa_summaries:
                s_clean = s.strip()
                for arrow in arrow_chars:
                    self.assertFalse(
                        s_clean.startswith(arrow),
                        f"{fpath.name}: QA summary begins with literal arrow '{arrow}': {s_clean[:40]}",
                    )
        self.assertEqual(total_qa, 296, f"Expected 296 QA blocks across all lectures, found {total_qa}")

    def test_06_qa_open_marker_rotation_rule(self):
        """Verify transform: rotate(90deg) is present on .qa[open] > summary::before in all styles."""
        files_with_embedded_css = [self.style_css_path, self.index_path] + [
            p for p in self.lecture_paths if p.name != "10-vae.html"
        ]
        for fpath in files_with_embedded_css:
            content = read_file(fpath)
            self.assertTrue(
                re.search(
                    r"\.qa\[open\]\s*>\s*summary::before\s*\{[^}]*transform:\s*rotate\(90deg\)",
                    content,
                ),
                f"{fpath.name}: 'transform: rotate(90deg)' missing in .qa[open] > summary::before",
            )

    def test_07_all_details_elements_have_valid_summary(self):
        """Verify all 466 details blocks across all lectures contain exactly one <summary> tag."""
        total_details = 0
        total_summaries = 0
        for fpath in self.lecture_paths:
            content = read_file(fpath)
            details_count = len(re.findall(r"<details\b", content))
            summary_count = len(re.findall(r"<summary\b", content))
            total_details += details_count
            total_summaries += summary_count
            self.assertEqual(
                details_count,
                summary_count,
                f"{fpath.name}: Mismatch between <details> ({details_count}) and <summary> ({summary_count})",
            )
        self.assertEqual(total_details, 466, f"Expected 466 total details tags, found {total_details}")
        self.assertEqual(total_summaries, 466, f"Expected 466 total summary tags, found {total_summaries}")

    def test_08_strict_html_tag_nesting_in_all_files(self):
        """Verify strict HTML tag balance and nesting across all 28 lectures and index.html."""
        from html.parser import HTMLParser

        void_tags = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

        class StrictParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.stack = []
                self.errors = []

            def handle_starttag(self, tag, attrs):
                if tag in void_tags:
                    return
                self.stack.append((tag, self.getpos()))

            def handle_endtag(self, tag):
                if tag in void_tags:
                    return
                if not self.stack:
                    self.errors.append(f"Unexpected </{tag}> with empty stack at line {self.getpos()[0]}")
                    return
                last_tag, pos = self.stack[-1]
                if last_tag == tag:
                    self.stack.pop()
                else:
                    stack_tags = [t for t, _ in self.stack]
                    if tag in stack_tags:
                        idx = len(stack_tags) - 1 - stack_tags[::-1].index(tag)
                        popped = self.stack[idx:]
                        self.stack = self.stack[:idx]
                        self.errors.append(f"Line {self.getpos()[0]}: Closing </{tag}> auto-closed unclosed tags: {[t for t, p in popped]}")
                    else:
                        self.errors.append(f"Line {self.getpos()[0]}: Unexpected closing tag </{tag}> (expected </{last_tag}> from line {pos[0]})")

        all_files = [self.index_path] + self.lecture_paths
        for fpath in all_files:
            content = read_file(fpath)
            parser = StrictParser()
            parser.feed(content)
            unclosed = [t for t, pos in parser.stack if t not in ("html", "body", "head")]
            self.assertEqual(len(unclosed), 0, f"{fpath.name}: Unclosed HTML tags at EOF: {unclosed}")
            self.assertEqual(len(parser.errors), 0, f"{fpath.name}: HTML structural errors: {parser.errors}")

    def test_09_no_unescaped_pseudo_tags_in_math_or_text(self):
        """Verify no unescaped angle brackets form pseudo-tags like <t inside LaTeX or HTML text."""
        valid_html_tags = {
            "a", "abbr", "address", "area", "article", "aside", "audio", "b", "base", "bdi", "bdo", "blockquote",
            "body", "br", "button", "canvas", "caption", "cite", "code", "col", "colgroup", "data", "datalist",
            "dd", "del", "details", "dfn", "dialog", "div", "dl", "dt", "em", "embed", "fieldset", "figcaption",
            "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6", "head", "header", "hgroup", "hr",
            "html", "i", "iframe", "img", "input", "ins", "kbd", "label", "legend", "li", "link", "main", "map",
            "mark", "meta", "meter", "nav", "noscript", "object", "ol", "optgroup", "option", "output", "p",
            "param", "picture", "pre", "progress", "q", "rp", "rt", "ruby", "s", "samp", "script", "section",
            "select", "small", "source", "span", "strong", "style", "sub", "summary", "sup", "table", "tbody",
            "td", "template", "textarea", "tfoot", "th", "thead", "time", "title", "tr", "track", "u", "ul",
            "var", "video", "wbr"
        }
        all_files = [self.index_path] + self.lecture_paths
        for fpath in all_files:
            content = read_file(fpath)
            matches = re.finditer(r'<([a-zA-Z][a-zA-Z0-9_-]*)', content)
            for m in matches:
                tagname = m.group(1).lower()
                self.assertIn(
                    tagname,
                    valid_html_tags,
                    f"{fpath.name}: Found invalid pseudo-tag <{tagname}> at index {m.start()}: {content[max(0, m.start()-15):min(len(content), m.end()+25)]}",
                )


if __name__ == "__main__":
    unittest.main()


