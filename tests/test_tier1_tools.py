"""
Tier 1: Python Tooling & CLI Coverage Suite.
Tests tools/build_exam_data.py and tests/common.py with 100% line and branch coverage.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tests.common import (
    INDEX_FILE,
    DOMViewportEmulator,
    EmulatedElement,
    SM2ReferenceEngine,
    extract_code_blocks,
    extract_math_blocks,
    parse_lecture_structure,
    read_file,
    strip_html_tags,
    validate_8step_structure,
    validate_latex_syntax,
)
from tools.build_exam_data import (
    build_js_content,
    clean_html_text,
    clean_text_plain,
    compile_exam_dataset,
    extract_lecture_data,
    get_block_for_lecture,
    main as build_main,
)


class TestTier1ToolsCoverage(unittest.TestCase):
    """Exhaustive coverage suite for tools/build_exam_data.py and common utilities."""

    def test_01_get_block_for_lecture_all_branches(self):
        """Test block mapping across all lecture ranges and invalid inputs."""
        self.assertEqual(get_block_for_lecture("00"), "A")
        self.assertEqual(get_block_for_lecture("07"), "A")
        self.assertEqual(get_block_for_lecture("08"), "B")
        self.assertEqual(get_block_for_lecture("13"), "B")
        self.assertEqual(get_block_for_lecture("14"), "C")
        self.assertEqual(get_block_for_lecture("21"), "C")
        self.assertEqual(get_block_for_lecture("22"), "D")
        self.assertEqual(get_block_for_lecture("27"), "D")
        # Non-numeric or out-of-range fallback
        self.assertEqual(get_block_for_lecture("invalid"), "A")
        self.assertEqual(get_block_for_lecture("99"), "A")
        self.assertEqual(get_block_for_lecture("-1"), "A")

    def test_02_clean_html_and_text_utilities(self):
        """Test clean_html_text and clean_text_plain on whitespace, tabs, and entities."""
        self.assertEqual(clean_html_text("  Hello \t\r\n World  "), "Hello World")
        self.assertEqual(clean_html_text("<b>Bold</b>\t<i>Italic</i>"), "<b>Bold</b> <i>Italic</i>")

        self.assertEqual(clean_text_plain("<h1>Title &amp; Subtitle</h1>"), "Title &amp; Subtitle")
        self.assertEqual(clean_text_plain("<p>Text with <span>tags</span></p>"), "Text with tags")

    def test_03_extract_lecture_data_all_branches(self):
        """Test lecture HTML extraction across diverse mock files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # 1. Standard lecture file with tasks, QAs, and cheatsheet
            lec1 = tmp_path / "01-test.html"
            lec1.write_text(
                """
                <!DOCTYPE html><html><head><title>Test</title></head><body>
                <header class="top"><h1>Билет 1. Полносвязные сети</h1></header>
                <main>
                <h2>6. 🎯 Препод спросит</h2>
                <details class="qa"><summary><span class="item-check"></span>Вопрос 1?</summary><div class="ans"><p>Ответ 1.</p></div></details>
                <h2>7. 📝 Микро-задачи</h2>
                <div class="task">
                  <div class="tt">Задача 1. Расчет</div>
                  <span class="item-check"></span>Условие задачи.
                  <details class="sol"><div class="sol">Шаг 1: 2+2=4.</div></details>
                </div>
                <div class="cheat">
                  <div class="bt">Шпаргалка</div>
                  <ol><li>Пункт 1</li><li>Пункт 2</li></ol>
                </div>
                <div class="navrow"><a href="00-intro-ml.html">Назад</a></div>
                </main></body></html>
                """,
                encoding="utf-8",
            )

            data1 = extract_lecture_data(lec1)
            self.assertEqual(data1["id"], "01")
            self.assertEqual(data1["title"], "Билет 1. Полносвязные сети")
            self.assertEqual(data1["module"], "A")
            self.assertEqual(len(data1["qas"]), 1)
            self.assertEqual(data1["qas"][0]["question"], "Вопрос 1?")
            self.assertIn("Ответ 1.", data1["qas"][0]["answer"])
            self.assertEqual(len(data1["tasks"]), 1)
            self.assertEqual(data1["tasks"][0]["title"], "Задача 1. Расчет")
            self.assertIn("Условие задачи", data1["tasks"][0]["problem"])
            self.assertIn("2+2=4", data1["tasks"][0]["solution"])
            self.assertEqual(len(data1["cheat_items"]), 2)

            # 2. Minimal lecture without title, empty tasks/QAs
            lec2 = tmp_path / "99-empty.html"
            lec2.write_text("<html><body><main></main></body></html>", encoding="utf-8")
            data2 = extract_lecture_data(lec2)
            self.assertEqual(data2["id"], "99")
            self.assertEqual(data2["title"], "99-empty")
            self.assertEqual(data2["module"], "A")
            self.assertEqual(len(data2["qas"]), 0)
            self.assertEqual(len(data2["tasks"]), 0)
            self.assertEqual(len(data2["cheat_items"]), 0)

    def test_04_compile_exam_dataset_and_build_js(self):
        """Test dataset compilation and JS code generation."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            # Empty directory raises FileNotFoundError
            with self.assertRaises(FileNotFoundError):
                compile_exam_dataset(tmp_path)

            # Non-empty directory
            (tmp_path / "00-intro.html").write_text(
                "<h1>Лекция 0</h1><details class='qa'><summary>Q?</summary><div class='ans'>A</div></details>",
                encoding="utf-8",
            )
            dataset = compile_exam_dataset(tmp_path)
            self.assertEqual(len(dataset), 1)

            js_code = build_js_content(dataset)
            self.assertIn("window.EXAM_DATA =", js_code)
            self.assertIn("00-intro.html", js_code)

    def test_05_build_exam_data_cli_all_flags(self):
        """Test CLI main() across all flags: standard, --verbose, --dry-run, --check (pass & fail), and errors."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            lec_dir = tmp_path / "lectures"
            lec_dir.mkdir()
            (lec_dir / "00-intro.html").write_text("<h1>Intro</h1>", encoding="utf-8")
            out_file = tmp_path / "exam_data.js"

            # 1. Standard build
            code = build_main(["-l", str(lec_dir), "-o", str(out_file), "-v"])
            self.assertEqual(code, 0)
            self.assertTrue(out_file.exists())

            # 2. Check mode on fresh file -> exit 0
            code_check = build_main(["-l", str(lec_dir), "-o", str(out_file), "--check", "-v"])
            self.assertEqual(code_check, 0)

            # 3. Check mode on modified file -> exit 1
            out_file.write_text("outdated", encoding="utf-8")
            code_check_fail = build_main(["-l", str(lec_dir), "-o", str(out_file), "--check"])
            self.assertEqual(code_check_fail, 1)

            # 4. Check mode on missing file -> exit 1
            missing_file = tmp_path / "non_existent.js"
            code_check_missing = build_main(
                ["-l", str(lec_dir), "-o", str(missing_file), "--check"]
            )
            self.assertEqual(code_check_missing, 1)

            # 5. Dry-run
            dry_file = tmp_path / "dry_out.js"
            code_dry = build_main(["-l", str(lec_dir), "-o", str(dry_file), "--dry-run"])
            self.assertEqual(code_dry, 0)
            self.assertFalse(dry_file.exists())

            # 6. Error handling on empty/invalid dir
            bad_dir = tmp_path / "empty_dir"
            bad_dir.mkdir()
            code_err = build_main(["-l", str(bad_dir)])
            self.assertEqual(code_err, 1)

    def test_06_common_utilities_coverage(self):
        """Test all helper functions and classes in tests/common.py."""
        # read_file
        idx_content = read_file(INDEX_FILE)
        self.assertIn("<!DOCTYPE html>", idx_content)

        # strip_html_tags
        self.assertEqual(strip_html_tags("<p>Hello &amp; <b>World</b></p>"), "Hello & World")

        # extract_code_blocks
        html_code = """
        <pre><code class="language-python">
        import torch
        x = torch.randn(2, 3)
        </code></pre>
        <pre>
        $ git clone repo
        </pre>
        <pre><code>
        # ASCII Diagram
        +---+---+
        </code></pre>
        """
        blocks = extract_code_blocks(html_code, "test.html")
        self.assertEqual(len(blocks), 3)
        self.assertTrue(blocks[0].is_python)
        self.assertFalse(blocks[1].is_python)
        self.assertFalse(blocks[2].is_python)

        # extract_math_blocks
        html_math = """
        <!-- $$ignore_comment$$ -->
        <p>Inline math $E = mc^2$ and $x + y = z$.</p>
        <div class="formula">
          $$\\text{ELBO} = \\mathbb{E}[\\log p(x|z)] - D_{KL}(q||p)$$
        </div>
        <script>var x = "$not_math$";</script>
        """
        math_blocks = extract_math_blocks(html_math, "test.html")
        self.assertTrue(any(b.is_display for b in math_blocks))
        self.assertTrue(any(not b.is_display for b in math_blocks))

        # validate_latex_syntax error branches
        self.assertTrue(len(validate_latex_syntax("&lt;formula&gt;")) > 0)
        self.assertTrue(len(validate_latex_syntax("a + b }")) > 0)
        self.assertTrue(len(validate_latex_syntax("{ a + b")) > 0)
        self.assertTrue(len(validate_latex_syntax("\\frac{1}")) > 0)
        self.assertTrue(len(validate_latex_syntax("\\begin{aligned} x \\end{gather}")) > 0)
        self.assertTrue(len(validate_latex_syntax("\\left( x + y")) > 0)
        self.assertEqual(
            len(validate_latex_syntax("\\frac{a}{b} + \\left( \\frac{c}{d} \\right)")), 0
        )

        # CourseStructureParser
        full_sample_html = """
        <html><body>
        <h2>1. Интуиция и мотивация</h2>
        <h2>2. Архитектура и схема</h2>
        <h2>3. Математический аппарат</h2>
        <h2>4. Пошаговый числовой пример</h2>
        <h2>5. Преимущества и недостатки</h2>
        <h2>6. 🎯 Препод спросит</h2>
        <h2>7. 📝 Микро-задачи с решениями</h2>
        <h2>8. ⚡ Скелет ответа по билету</h2>
        <a class="backlink" href="index.html">На главную</a>
        <span class="pill">296 Q&A</span>
        <details class="qa" id="q1"><summary>Вопрос</summary><div class="ans">Ответ</div></details>
        <div class="task" id="t1"><div class="tt">Задача</div>Условие<div class="sol">Решение</div></div>
        <div class="cheat"><div class="bt">Шпаргалка</div><ol><li>Пункт 1</li></ol></div>
        <div class="navrow"><a href="next.html">Следующая</a></div>
        </body></html>
        """
        parser = parse_lecture_structure(full_sample_html)
        self.assertEqual(parser.qa_count, 1)
        self.assertEqual(parser.task_count, 1)
        self.assertEqual(parser.sol_count, 1)
        self.assertTrue(parser.has_cheat)
        self.assertEqual(len(parser.backlinks), 1)
        self.assertEqual(len(parser.navrow_links), 1)
        self.assertIn("q1", parser.element_ids)
        self.assertIn("t1", parser.element_ids)
        self.assertEqual(len(parser.h2_headers), 8)

        # validate_8step_structure
        val_res = validate_8step_structure(full_sample_html)
        self.assertTrue(val_res["valid"])
        self.assertEqual(len(val_res["found_steps"]), 8)
        self.assertEqual(len(val_res["missing_steps"]), 0)

        # SM2ReferenceEngine
        sm2_first = SM2ReferenceEngine.calc_next_review(
            quality=5, repetitions=0, ease_factor=2.5, interval=0
        )
        self.assertEqual(sm2_first["repetitions"], 1)
        self.assertEqual(sm2_first["interval"], 1)
        self.assertGreaterEqual(sm2_first["ease_factor"], 2.5)

        sm2_second = SM2ReferenceEngine.calc_next_review(
            quality=4, repetitions=1, ease_factor=2.6, interval=1
        )
        self.assertEqual(sm2_second["repetitions"], 2)
        self.assertEqual(sm2_second["interval"], 6)

        sm2_third = SM2ReferenceEngine.calc_next_review(
            quality=5, repetitions=2, ease_factor=2.6, interval=6
        )
        self.assertEqual(sm2_third["repetitions"], 3)
        self.assertEqual(sm2_third["interval"], 16)

        sm2_fail = SM2ReferenceEngine.calc_next_review(
            quality=1, repetitions=5, ease_factor=2.5, interval=30
        )
        self.assertEqual(sm2_fail["repetitions"], 0)
        self.assertEqual(sm2_fail["interval"], 1)

        # DOMViewportEmulator & EmulatedElement
        elem = EmulatedElement(
            tag="button", classes=["btn"], width=44.0, height=44.0, padding=(4, 8, 4, 8)
        )
        self.assertEqual(elem.total_width, 60.0)
        self.assertEqual(elem.total_height, 52.0)
        self.assertTrue(DOMViewportEmulator.verify_viewport_overflow(320, 320, False))
        self.assertFalse(DOMViewportEmulator.verify_viewport_overflow(350, 320, False))
        self.assertTrue(DOMViewportEmulator.verify_viewport_overflow(350, 320, True))
        self.assertTrue(DOMViewportEmulator.verify_touch_target(44.0, 44.0))
        self.assertFalse(DOMViewportEmulator.verify_touch_target(43.0, 44.0))


if __name__ == "__main__":
    unittest.main()
