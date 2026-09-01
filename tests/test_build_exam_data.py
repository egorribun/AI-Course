"""
Unit and integration tests for tools/build_exam_data.py.
Verifies CLI flags, parsing engine, 4-block mapping, and output consistency.
"""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.build_exam_data import (
    LECTURES_DIR,
    TICKET_MAPPING,
    clean_html_text,
    clean_text_plain,
    compile_exam_dataset,
    extract_lecture_data,
    get_block_for_lecture,
    main,
)


class TestBuildExamData(unittest.TestCase):
    """Test suite for tools/build_exam_data.py."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.out_path = Path(self.temp_dir.name) / "exam_data.js"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_01_helper_functions(self):
        """Test clean_html_text, clean_text_plain, and get_block_for_lecture."""
        # clean_html_text
        self.assertEqual(clean_html_text("  hello \t  world \r\n 123 "), "hello world 123")
        self.assertEqual(clean_html_text(""), "")

        # clean_text_plain
        self.assertEqual(clean_text_plain("<b>Title</b> <span class='x'>Sub</span>"), "Title Sub")
        self.assertEqual(clean_text_plain("No tags here"), "No tags here")

        # get_block_for_lecture
        self.assertEqual(get_block_for_lecture("00"), "A")
        self.assertEqual(get_block_for_lecture("07"), "A")
        self.assertEqual(get_block_for_lecture("08"), "B")
        self.assertEqual(get_block_for_lecture("13"), "B")
        self.assertEqual(get_block_for_lecture("14"), "C")
        self.assertEqual(get_block_for_lecture("21"), "C")
        self.assertEqual(get_block_for_lecture("22"), "D")
        self.assertEqual(get_block_for_lecture("27"), "D")
        # Boundary / invalid fallbacks
        self.assertEqual(get_block_for_lecture("invalid"), "A")
        self.assertEqual(get_block_for_lecture("99"), "A")

    def test_02_compile_exam_dataset_full(self):
        """Verify compiling dataset from the real lectures directory."""
        dataset = compile_exam_dataset(LECTURES_DIR)
        self.assertEqual(len(dataset), 28, "Must contain all 28 lectures")

        total_qas = sum(len(l["qas"]) for l in dataset)
        total_tasks = sum(len(l["tasks"]) for l in dataset)
        self.assertEqual(total_qas, 296, f"Expected 296 Q&As, got {total_qas}")
        self.assertEqual(total_tasks, 170, f"Expected 170 tasks, got {total_tasks}")

        # Check block distribution
        blocks = {l["module"] for l in dataset}
        self.assertEqual(blocks, {"A", "B", "C", "D"})

        block_a = [l for l in dataset if l["module"] == "A"]
        block_b = [l for l in dataset if l["module"] == "B"]
        block_c = [l for l in dataset if l["module"] == "C"]
        block_d = [l for l in dataset if l["module"] == "D"]

        self.assertEqual(len(block_a), 8)  # 00-07
        self.assertEqual(len(block_b), 6)  # 08-13
        self.assertEqual(len(block_c), 8)  # 14-21
        self.assertEqual(len(block_d), 6)  # 22-27

    def test_03_cli_generate_output(self):
        """Verify main() generates valid js/exam_data.js with CLI arguments."""
        ret = main(["--output", str(self.out_path), "--verbose"])
        self.assertEqual(ret, 0)
        self.assertTrue(self.out_path.exists())

        content = self.out_path.read_text(encoding="utf-8")
        self.assertIn("window.EXAM_DATA =", content)

        # Parse array part
        start_idx = content.find("[")
        end_idx = content.rfind("]")
        data = json.loads(content[start_idx : end_idx + 1])
        self.assertEqual(len(data), 28)

    def test_04_cli_check_flag(self):
        """Verify --check flag returns 0 when fresh and 1 when outdated or missing."""
        # 1. Missing output file
        missing_path = Path(self.temp_dir.name) / "nonexistent.js"
        self.assertEqual(main(["--output", str(missing_path), "--check"]), 1)

        # 2. Outdated content
        missing_path.write_text("window.EXAM_DATA = [];", encoding="utf-8")
        self.assertEqual(main(["--output", str(missing_path), "--check"]), 1)

        # 3. Generate correct content and verify check passes
        self.assertEqual(main(["--output", str(missing_path)]), 0)
        self.assertEqual(main(["--output", str(missing_path), "--check", "-v"]), 0)

    def test_05_cli_dry_run_flag(self):
        """Verify --dry-run parses without writing files."""
        ret = main(["--output", str(self.out_path), "--dry-run"])
        self.assertEqual(ret, 0)
        self.assertFalse(self.out_path.exists(), "Dry run must not create output file")

    def test_06_error_handling_empty_dir(self):
        """Verify handling when lecture directory contains no HTML files."""
        empty_dir = Path(self.temp_dir.name) / "empty"
        empty_dir.mkdir()
        ret = main(["--lectures-dir", str(empty_dir), "--output", str(self.out_path)])
        self.assertEqual(ret, 1)

    def test_07_extract_lecture_data_synthetic_edges(self):
        """Verify extract_lecture_data handles minimal or malformed HTML snippets."""
        mock_html = Path(self.temp_dir.name) / "99-test.html"
        mock_html.write_text(
            "<html><body>"
            "<div class='task'><p>Simple problem without details</p></div>"
            "</body></html>",
            encoding="utf-8",
        )
        data = extract_lecture_data(mock_html)
        self.assertEqual(data["id"], "99")
        self.assertEqual(data["title"], "99-test")
        self.assertEqual(len(data["qas"]), 0)
        self.assertEqual(len(data["tasks"]), 1)
        self.assertEqual(data["tasks"][0]["title"], "Задача")
        self.assertEqual(data["tasks"][0]["solution"], "")
        self.assertEqual(len(data["cheat_items"]), 0)

    def test_08_all_25_tickets_covered(self):
        """Verify that all 25 official exam tickets are mapped in TICKET_MAPPING."""
        for i in range(1, 26):
            matches = [v for k, v in TICKET_MAPPING.items() if f"Билет {i}" in v]
            self.assertGreaterEqual(
                len(matches),
                1,
                f"Билет {i} must be mapped in TICKET_MAPPING",
            )


if __name__ == "__main__":
    unittest.main()
