"""
Requirement R4 Tests: Structure & Navigation Integrity.
State University of Management (GUU, 2026) DL Course Verification.

Verifies:
- All 28 lectures have >= 10 Q&A elements (<details class="qa">) with valid summary and answer.
- All 28 lectures have >= 6 task elements (<div class="task">) with solutions (<details class="sol"> / .sol).
- All 28 lectures have cheat sheet blocks (<div class="cheat">) with non-empty content.
- All 28 lectures have top navigation backlinks and metadata pills.
- 100% hyperlink graph integrity: every href target file and #anchor ID exists.
- Sequential .navrow prev/next navigation chain is continuous and unbroken across all 28 lectures.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

COURSE_ROOT_DIR = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT_DIR))

from tests.common import (
    COURSE_ROOT,
    CourseStructureParser,
    EXPECTED_LECTURES,
    INDEX_FILE,
    LECTURES_DIR,
    parse_lecture_structure,
    read_file,
)


class TestR4StructureNav(unittest.TestCase):
    """Test suite for Requirement R4: Structure & Navigation Integrity."""

    @classmethod
    def setUpClass(cls):
        cls.lecture_structures: Dict[str, CourseStructureParser] = {}
        cls.lecture_contents: Dict[str, str] = {}

        # Parse index.html
        if INDEX_FILE.is_file():
            content = read_file(INDEX_FILE)
            cls.index_structure = parse_lecture_structure(content)
            cls.index_content = content
        else:
            cls.index_structure = None
            cls.index_content = ""

        # Parse all 28 lectures
        for lec in EXPECTED_LECTURES:
            lec_path = LECTURES_DIR / lec
            if lec_path.is_file():
                content = read_file(lec_path)
                cls.lecture_contents[lec] = content
                cls.lecture_structures[lec] = parse_lecture_structure(content)
            else:
                cls.lecture_contents[lec] = ""
                cls.lecture_structures[lec] = None

    def test_01_all_lectures_have_at_least_10_qa_blocks(self):
        """Every lecture must contain >= 10 '<details class=\"qa\">' elements."""
        qa_deficits = []
        for lec in EXPECTED_LECTURES:
            st = self.lecture_structures.get(lec)
            count = st.qa_count if st else 0
            if count < 10:
                qa_deficits.append(f"{lec}: found {count} QA (needs {10 - count} more)")

        self.assertEqual(
            qa_deficits,
            [],
            f"Found {len(qa_deficits)} lecture(s) with fewer than 10 QA blocks:\n"
            + "\n".join(qa_deficits),
        )

    def test_02_all_lectures_have_at_least_6_tasks_with_solutions(self):
        """Every lecture must contain >= 6 '<div class=\"task\">' elements with solutions."""
        task_deficits = []
        for lec in EXPECTED_LECTURES:
            st = self.lecture_structures.get(lec)
            tasks = st.task_count if st else 0
            sols = st.sol_count if st else 0
            if tasks < 6:
                task_deficits.append(f"{lec}: found {tasks} tasks (needs {6 - tasks} more)")
            elif sols < tasks:
                task_deficits.append(f"{lec}: found {tasks} tasks but only {sols} solution blocks")

        self.assertEqual(
            task_deficits,
            [],
            f"Found {len(task_deficits)} lecture(s) failing task requirements:\n"
            + "\n".join(task_deficits),
        )

    def test_03_all_lectures_have_cheat_sheet_block(self):
        """Every lecture must contain '<div class=\"cheat\">' with non-empty outline."""
        missing_cheats = []
        for lec in EXPECTED_LECTURES:
            st = self.lecture_structures.get(lec)
            if not st or not st.has_cheat:
                missing_cheats.append(f"{lec}: missing .cheat block")
            elif len(st.cheat_text.strip()) < 50:
                missing_cheats.append(f"{lec}: .cheat block content is too short (<50 chars)")

        self.assertEqual(
            missing_cheats,
            [],
            "Lectures with missing or empty cheat sheets:\n" + "\n".join(missing_cheats),
        )

    def test_04_all_lectures_have_top_backlinks_and_pills(self):
        """Every lecture must contain a backlink pointing to index.html and header pills."""
        missing_elements = []
        for lec in EXPECTED_LECTURES:
            st = self.lecture_structures.get(lec)
            if not st:
                missing_elements.append(f"{lec}: unparsed")
                continue

            # Backlink check
            if not st.backlinks:
                missing_elements.append(f'{lec}: missing <a class="backlink">')
            else:
                backlink = st.backlinks[0]
                if not ("index.html" in backlink or backlink == "../"):
                    missing_elements.append(
                        f"{lec}: backlink '{backlink}' does not point to index.html"
                    )

            # Pills check
            if len(st.pills) < 2:
                missing_elements.append(
                    f"{lec}: found only {len(st.pills)} .pill badges (expected >= 2)"
                )

        self.assertEqual(
            missing_elements,
            [],
            "Lectures missing top backlinks or metadata pills:\n" + "\n".join(missing_elements),
        )

    def test_05_link_graph_integrity_all_hrefs_and_anchors_valid(self):
        """All hyperlinks in index.html and all 28 lectures must resolve to existing files or IDs."""
        broken_links = []

        all_pages = [("index.html", COURSE_ROOT / "index.html", self.index_structure)]
        for lec in EXPECTED_LECTURES:
            all_pages.append(
                (f"lectures/{lec}", LECTURES_DIR / lec, self.lecture_structures.get(lec))
            )

        for page_name, page_path, structure in all_pages:
            if not structure:
                continue

            parent_dir = page_path.parent

            for href, line_no in structure.all_hrefs:
                # Ignore external URLs, mailto, javascript, empty
                parsed = urlparse(href)
                if parsed.scheme in ("http", "https", "mailto", "javascript") or not href.strip():
                    continue

                target_file_part = parsed.path
                fragment = parsed.fragment

                # 1. Check file target
                if target_file_part:
                    # Target path relative to current page directory
                    target_file_path = (parent_dir / target_file_part).resolve()
                    if not target_file_path.is_file():
                        broken_links.append(
                            f"[{page_name}:{line_no}] Dead file link '{href}' -> Target not found: {target_file_path}"
                        )
                        continue

                    # If target is another course HTML file with fragment anchor
                    if fragment:
                        target_content = read_file(target_file_path)
                        # Check if target contains id="fragment"
                        id_pattern = re.compile(rf'id=["\']{re.escape(fragment)}["\']')
                        if not id_pattern.search(target_content):
                            broken_links.append(
                                f"[{page_name}:{line_no}] Dead anchor link '{href}' -> ID '{fragment}' not found in {target_file_path.name}"
                            )
                elif fragment:
                    # Same page anchor: #fragment
                    if fragment not in structure.element_ids:
                        # Check regex in content in case parser missed
                        content = self.lecture_contents.get(
                            Path(page_name).name, self.index_content
                        )
                        id_pattern = re.compile(rf'id=["\']{re.escape(fragment)}["\']')
                        if not id_pattern.search(content):
                            broken_links.append(
                                f"[{page_name}:{line_no}] Dead anchor '#{fragment}' -> Element ID not found on page"
                            )

        self.assertEqual(
            broken_links,
            [],
            f"Found {len(broken_links)} broken link(s)/anchor(s):\n" + "\n".join(broken_links[:20]),
        )

    def test_06_navrow_sequential_prev_next_chain(self):
        """Lectures 00 to 27 must form an unbroken, continuous sequential navigation chain."""
        chain_errors = []

        for i, lec in enumerate(EXPECTED_LECTURES):
            st = self.lecture_structures.get(lec)
            if not st or not st.navrow_links:
                chain_errors.append(f"{lec}: missing .navrow navigation links")
                continue

            links = st.navrow_links
            hrefs = [h for h, _ in links]

            # First lecture (00)
            if i == 0:
                # Next must be 01-fcnn.html
                next_expected = EXPECTED_LECTURES[1]
                if not any(next_expected in h for h in hrefs):
                    chain_errors.append(
                        f"{lec}: next link does not point to '{next_expected}' (found {hrefs})"
                    )
            # Last lecture (27)
            elif i == len(EXPECTED_LECTURES) - 1:
                # Prev must be 26-policy-gradient.html
                prev_expected = EXPECTED_LECTURES[i - 1]
                if not any(prev_expected in h for h in hrefs):
                    chain_errors.append(
                        f"{lec}: prev link does not point to '{prev_expected}' (found {hrefs})"
                    )
            # Middle lectures (01 to 26)
            else:
                prev_expected = EXPECTED_LECTURES[i - 1]
                next_expected = EXPECTED_LECTURES[i + 1]

                has_prev = any(prev_expected in h for h in hrefs)
                has_next = any(next_expected in h for h in hrefs)

                if not has_prev:
                    chain_errors.append(
                        f"{lec}: prev link missing or does not point to '{prev_expected}'"
                    )
                if not has_next:
                    chain_errors.append(
                        f"{lec}: next link missing or does not point to '{next_expected}'"
                    )

        self.assertEqual(
            chain_errors,
            [],
            f"Found {len(chain_errors)} navigation chain error(s):\n" + "\n".join(chain_errors),
        )

    def test_07_pill_badge_counts_match_actual_qa_and_task_counts(self):
        """Header .pill badges for questions and tasks must match actual parsed elements."""
        mismatches = []
        for lec in EXPECTED_LECTURES:
            st = self.lecture_structures.get(lec)
            if not st:
                continue
            content = self.lecture_contents.get(lec, "")

            # QA pill check
            qa_pill_match = re.search(r"(\d+)\s+вопрос", content)
            if qa_pill_match:
                qa_pill_num = int(qa_pill_match.group(1))
                if qa_pill_num != st.qa_count:
                    mismatches.append(
                        f"{lec}: QA pill badge says {qa_pill_num}, but actual QA count is {st.qa_count}"
                    )

            # Task pill check
            task_pill_match = re.search(r"(\d+)\s+микро-задач", content)
            if task_pill_match:
                task_pill_num = int(task_pill_match.group(1))
                if task_pill_num != st.task_count:
                    mismatches.append(
                        f"{lec}: Task pill badge says {task_pill_num}, but actual task count is {st.task_count}"
                    )

        self.assertEqual(
            mismatches,
            [],
            f"Found {len(mismatches)} pill badge count mismatch(es):\n" + "\n".join(mismatches),
        )


if __name__ == "__main__":
    unittest.main()
