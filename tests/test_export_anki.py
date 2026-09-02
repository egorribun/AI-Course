"""
Tests for Anki TSV Exporter (tools/export_anki.py).
Provides 100% line and branch coverage across all functions, edge cases, and CLI options.
"""

from __future__ import annotations

import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.export_anki import (
    COURSE_ROOT,
    DEFAULT_OUTPUT_DIR,
    export_all_decks,
    generate_cheatsheets_deck,
    generate_microtasks_deck,
    generate_questions_deck,
    main as anki_main,
    sanitize_tsv_field,
)


class TestExportAnki(unittest.TestCase):
    """Test suite for tools/export_anki.py covering 100% lines and branches."""

    def test_01_sanitize_tsv_field(self):
        """Test sanitization of TSV fields with various newlines, tabs, and empty inputs."""
        self.assertEqual(sanitize_tsv_field(""), "")
        self.assertEqual(sanitize_tsv_field("   "), "")
        self.assertEqual(
            sanitize_tsv_field("Line 1\r\nLine 2\rLine 3\nLine 4"),
            "Line 1<br>Line 2<br>Line 3<br>Line 4",
        )
        self.assertEqual(
            sanitize_tsv_field("Col 1\tCol 2\t\tCol 3"),
            "Col 1 Col 2  Col 3",
        )
        self.assertEqual(
            sanitize_tsv_field("  <b>Bold</b>\t\n<i>Italic</i>  "),
            "<b>Bold</b> <br><i>Italic</i>",
        )

    def test_02_generate_questions_deck(self):
        """Test Q&A deck generation with complete data and fallback attributes."""
        # Empty dataset
        self.assertEqual(generate_questions_deck([]), "")

        # Dataset with full data and missing optional keys
        dataset = [
            {
                "id": "01",
                "ticket": "Билет 1: FCNN",
                "module": "A",
                "qas": [
                    {"question": "What is ReLU?", "answer": "max(0, x)"},
                    {
                        "question": "Why use dropout?",
                        "answer": "Prevents overfitting\nby dropping units.",
                    },
                ],
            },
            {
                "id": "02",
                # Missing ticket and module keys -> trigger default fallbacks
                "qas": [
                    {"question": "Q2?", "answer": "A2"},
                ],
            },
            {
                "id": "03",
                "ticket": "Билет 3",
                "module": "A",
                "qas": [],  # Empty QAs
            },
        ]

        tsv = generate_questions_deck(dataset)
        lines = [line for line in tsv.splitlines() if line]
        self.assertEqual(len(lines), 3)

        # Line 1 check
        self.assertIn("[Билет 1: FCNN] What is ReLU?", lines[0])
        self.assertIn("max(0, x)", lines[0])
        self.assertIn("AI_Course Block_A Ticket_01", lines[0])

        # Line 2 newline sanitization check
        self.assertIn("Prevents overfitting<br>by dropping units.", lines[1])

        # Line 3 default fallbacks check
        self.assertIn("[Лекция 02] Q2?", lines[2])
        self.assertIn("AI_Course Block_A Ticket_02", lines[2])

    def test_03_generate_microtasks_deck(self):
        """Test micro-tasks deck generation with titles, problems, solutions, and fallbacks."""
        # Empty dataset
        self.assertEqual(generate_microtasks_deck([]), "")

        dataset = [
            {
                "id": "04",
                "ticket": "Билет 4: CNN",
                "module": "A",
                "tasks": [
                    {
                        "title": "Conv Output Size",
                        "problem": "Input 32x32, kernel 3, pad 1, stride 1.",
                        "solution": "(32 - 3 + 2)/1 + 1 = 32.",
                    },
                    {
                        "title": "Receptive Field",
                        "problem": "",  # Empty problem branch
                        "solution": "RF = 5.",
                    },
                ],
            },
            {
                "id": "05",
                # Missing ticket, module, title, problem, solution
                "tasks": [
                    {},
                ],
            },
            {
                "id": "06",
                "ticket": "Билет 6",
                "module": "A",
                "tasks": [],
            },
        ]

        tsv = generate_microtasks_deck(dataset)
        lines = [line for line in tsv.splitlines() if line]
        self.assertEqual(len(lines), 3)

        # Line 1 check
        self.assertIn("<b>[Билет 4: CNN] Conv Output Size</b><br><br>Input 32x32", lines[0])
        self.assertIn("(32 - 3 + 2)/1 + 1 = 32.", lines[0])
        self.assertIn("AI_Course Block_A Microtask Ticket_04", lines[0])

        # Line 2 check (empty problem)
        self.assertIn("<b>[Билет 4: CNN] Receptive Field</b>\t", lines[1])

        # Line 3 check (default fallbacks)
        self.assertIn("<b>[Лекция 05] Микро-задача</b>", lines[2])
        self.assertIn("AI_Course Block_A Microtask Ticket_05", lines[2])

    def test_04_generate_cheatsheets_deck(self):
        """Test cheatsheets deck generation with items, empty cheat_items, and fallbacks."""
        # Empty dataset
        self.assertEqual(generate_cheatsheets_deck([]), "")

        dataset = [
            {
                "id": "16",
                "ticket": "Билет 15: Transformer",
                "module": "C",
                "cheat_items": [
                    "Тезис 1: Self-Attention $O(N^2)$",
                    "Тезис 2: Positional Encoding",
                    "Тезис 3: Multi-Head Attention",
                ],
            },
            {
                "id": "17",
                "ticket": "Билет 16",
                "module": "C",
                "cheat_items": [],  # Empty cheat_items -> continue branch
            },
            {
                "id": "18",
                # Missing ticket and module
                "cheat_items": [
                    "Point A",
                ],
            },
        ]

        tsv = generate_cheatsheets_deck(dataset)
        lines = [line for line in tsv.splitlines() if line]
        self.assertEqual(len(lines), 2)

        # Line 1 check
        self.assertIn("[Билет 15: Transformer] Шпаргалка: Скелет ответа по билету (3:00)", lines[0])
        self.assertIn("<ol><li>Тезис 1: Self-Attention $O(N^2)$</li>", lines[0])
        self.assertIn("AI_Course Block_C Cheatsheet Ticket_16", lines[0])

        # Line 2 check (fallback ticket/module)
        self.assertIn("[Лекция 18] Шпаргалка", lines[1])
        self.assertIn("AI_Course Block_A Cheatsheet Ticket_18", lines[1])

    def test_05_export_all_decks(self):
        """Test export_all_decks structure and keys."""
        self.assertEqual(DEFAULT_OUTPUT_DIR, COURSE_ROOT / "anki_decks")
        decks = export_all_decks([])
        self.assertIn("questions.tsv", decks)
        self.assertIn("microtasks.tsv", decks)
        self.assertIn("cheatsheets.tsv", decks)

    def test_06_main_cli_all_modes_and_flags(self):
        """Test main() with all CLI flags: normal export, --verbose, --dry-run, --check, errors."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            lec_dir = tmp_path / "lectures"
            lec_dir.mkdir()

            (lec_dir / "00-intro.html").write_text(
                """
                <!DOCTYPE html><html><body>
                <h1>00. Разгон</h1>
                <details class="qa"><summary>Вопрос 1?</summary><div class="ans">Ответ 1.</div></details>
                <div class="task"><div class="tt">Задача 1</div>Условие 1<div class="sol">Решение 1</div></div>
                <div class="cheat"><div class="bt">Шпаргалка</div><ol><li>Тезис 1</li></ol></div>
                </body></html>
                """,
                encoding="utf-8",
            )

            out_dir = tmp_path / "decks"

            # 1. Standard build with verbose
            code_build = anki_main(["-l", str(lec_dir), "-o", str(out_dir), "-v"])
            self.assertEqual(code_build, 0)
            self.assertTrue((out_dir / "questions.tsv").exists())
            self.assertTrue((out_dir / "microtasks.tsv").exists())
            self.assertTrue((out_dir / "cheatsheets.tsv").exists())

            # 2. Check mode with verbose on matching files -> exit 0
            code_check_pass = anki_main(["-l", str(lec_dir), "-o", str(out_dir), "--check", "-v"])
            self.assertEqual(code_check_pass, 0)

            # 3. Check mode without verbose on matching files -> exit 0
            code_check_pass_noverbose = anki_main(
                ["-l", str(lec_dir), "-o", str(out_dir), "--check"]
            )
            self.assertEqual(code_check_pass_noverbose, 0)

            # 4. Check mode on modified file -> exit 1
            (out_dir / "questions.tsv").write_text("modified content", encoding="utf-8")
            code_check_fail = anki_main(["-l", str(lec_dir), "-o", str(out_dir), "--check"])
            self.assertEqual(code_check_fail, 1)

            # 5. Check mode on missing file -> exit 1
            (out_dir / "questions.tsv").unlink()
            code_check_missing = anki_main(["-l", str(lec_dir), "-o", str(out_dir), "--check"])
            self.assertEqual(code_check_missing, 1)

            # 6. Dry run -> exit 0, does not create non-existent dir
            dry_dir = tmp_path / "dry_decks"
            code_dry = anki_main(["-l", str(lec_dir), "-o", str(dry_dir), "--dry-run"])
            self.assertEqual(code_dry, 0)
            self.assertFalse(dry_dir.exists())

            # 7. Error on invalid/empty lectures dir -> exit 1
            bad_dir = tmp_path / "bad_lectures"
            bad_dir.mkdir()
            code_err = anki_main(["-l", str(bad_dir), "-o", str(out_dir)])
            self.assertEqual(code_err, 1)

    def test_07_main_runpy_execution(self):
        """Test execution via runpy to cover `if __name__ == '__main__': sys.exit(main())`."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            lec_dir = tmp_path / "lectures"
            lec_dir.mkdir()
            (lec_dir / "00-intro.html").write_text("<h1>00. Intro</h1>", encoding="utf-8")
            out_dir = tmp_path / "decks"

            tool_path = COURSE_ROOT / "tools" / "export_anki.py"
            test_argv = ["export_anki.py", "-l", str(lec_dir), "-o", str(out_dir), "--dry-run"]
            with patch.object(sys, "argv", test_argv):
                with self.assertRaises(SystemExit) as cm:
                    runpy.run_path(str(tool_path), run_name="__main__")
                self.assertEqual(cm.exception.code, 0)

    def test_08_import_fallback_coverage(self):
        """Test fallback import branch when tools package is unimported."""
        tools_dir = COURSE_ROOT / "tools"
        saved_sys_path = list(sys.path)
        try:
            sys.path.insert(0, str(tools_dir))
            with patch.dict(sys.modules, {"tools": None, "tools.build_exam_data": None}):
                # Run the export_anki script code in an isolated namespace to exercise fallback import
                tool_path = tools_dir / "export_anki.py"
                runpy.run_path(str(tool_path), run_name="export_anki_isolated")
        finally:
            sys.path = saved_sys_path


if __name__ == "__main__":
    unittest.main()
