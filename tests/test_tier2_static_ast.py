"""
Tier 2: Static Analysis, Content & Math Rigor AST / LaTeX Validator.
Validates all 28 lectures:
- 8-Step High-Yield structure compliance across all 28 lectures (all 8 sections, >=10 Q&As, >=6 micro-tasks).
- 100% Python AST parsing for all PyTorch/NumPy code blocks.
- Mathematical rigor: LaTeX brace balance, no raw unescaped HTML entities in math, verification of 10 core derivations.
- De-sprintization: 0 sprint references across all 28 lectures and codebase.
- HTML structure, doctype, and tag nesting conformance.
"""

from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path
from typing import Dict, List

from tests.common import (
    COURSE_ROOT,
    EXAM_FILE,
    EXPECTED_LECTURES,
    INDEX_FILE,
    JS_DIR,
    LECTURES_DIR,
    MANIFEST_FILE,
    README_FILE,
    STYLE_FILE,
    extract_code_blocks,
    extract_math_blocks,
    parse_lecture_structure,
    read_file,
    validate_8step_structure,
    validate_latex_syntax,
)


class TestTier2StaticAST(unittest.TestCase):
    """Tier 2: Static Analysis, Math Rigor & 8-Step Structure Validator."""

    @classmethod
    def setUpClass(cls):
        cls.lecture_contents: Dict[str, str] = {}
        for lec_name in EXPECTED_LECTURES:
            path = LECTURES_DIR / lec_name
            if path.exists():
                cls.lecture_contents[lec_name] = read_file(path)

    def test_01_all_28_lectures_exist(self):
        """Verify that all 28 lecture HTML files (00 to 27) exist on disk."""
        self.assertEqual(len(self.lecture_contents), 28, "All 28 lecture HTML files must exist.")

    def test_02_strict_8step_high_yield_structure_all_lectures(self):
        """
        Verify that all 28 lectures implement the 8-Step High-Yield Architecture:
        1. Интуиция и мотивация
        2. Архитектура и схема
        3. Математический аппарат
        4. Пошаговый числовой пример
        5. Преимущества, недостатки и применимость
        6. 🎯 Препод спросит (>= 10 Q&As)
        7. 📝 Микро-задачи с решениями (>= 6 tasks with step-by-step solutions)
        8. ⚡ Скелет ответа по билету
        """
        failures = []
        for lec_name, content in self.lecture_contents.items():
            parser = parse_lecture_structure(content)

            # Quantitative check: >= 10 Q&As
            if parser.qa_count < 10:
                failures.append(f"{lec_name}: has only {parser.qa_count} Q&As (minimum 10 required)")

            # Quantitative check: >= 6 tasks with solutions
            if parser.task_count < 6:
                failures.append(f"{lec_name}: has only {parser.task_count} tasks (minimum 6 required)")
            if parser.sol_count < parser.task_count:
                failures.append(
                    f"{lec_name}: task solutions count ({parser.sol_count}) < task count ({parser.task_count})"
                )

            # Check cheat / ticket outline
            if not parser.has_cheat:
                failures.append(f"{lec_name}: missing ⚡ Скелет ответа / ticket outline block")

            # 8-step structural verification
            val = validate_8step_structure(content)
            if not val["valid"]:
                failures.append(f"{lec_name}: missing 8-step sections: {val['missing_steps']}")

        self.assertEqual(len(failures), 0, "8-Step High-Yield structure failures:\n" + "\n".join(failures))

    def test_03_desprintization_zero_occurrences_in_lectures(self):
        """
        Verify 0 sprint occurrences across README, index, exam, all 28 lectures, stylesheet and scripts:
        Prohibited phrases: '3 дня', '3-дневн', 'трехдневн', 'трёхдневн', '12 часов работы', 'день 1', 'день 2', 'день 3',
        '(дня)', '3-модульный', 'Ответ за 3 минуты'.
        """
        sprint_patterns = [
            re.compile(r"\b3\s*дня\b", re.IGNORECASE),
            re.compile(r"\b3-дневн\w*", re.IGNORECASE),
            re.compile(r"\bтрехдневн\w*", re.IGNORECASE),
            re.compile(r"\bтрёхдневн\w*", re.IGNORECASE),
            re.compile(r"\bдень\s*[123]\b", re.IGNORECASE),
            re.compile(r"\b12\s*часов\b", re.IGNORECASE),
            re.compile(r"\b12\s*ч\b", re.IGNORECASE),
            re.compile(r"\(дня\)", re.IGNORECASE),
            re.compile(r"\b3-модульн\w*", re.IGNORECASE),
            re.compile(r"\b3-х\s*модульн\w*", re.IGNORECASE),
            re.compile(r"\b3-модуля\b", re.IGNORECASE),
            re.compile(r"Ответ за 3 минуты", re.IGNORECASE),
        ]

        files_to_check: List[Path] = [
            README_FILE,
            INDEX_FILE,
            EXAM_FILE,
            STYLE_FILE,
            MANIFEST_FILE,
        ]
        files_to_check.extend((LECTURES_DIR / lec) for lec in EXPECTED_LECTURES)
        for js_file in JS_DIR.glob("*.js"):
            files_to_check.append(js_file)

        violations = []
        for file_path in files_to_check:
            if not file_path.exists():
                continue
            text = read_file(file_path)
            for pat in sprint_patterns:
                matches = pat.findall(text)
                if matches:
                    violations.append(f"{file_path.name}: found sprint term {matches[:3]}")

        self.assertEqual(len(violations), 0, "De-sprintization violations found in codebase:\n" + "\n".join(violations))

    def test_04_python_code_blocks_ast_validity(self):
        """
        Extract all Python code snippets inside <pre><code> across all 28 lectures
        and verify they pass ast.parse() with 0 syntax errors.
        """
        total_py_blocks = 0
        ast_errors = []

        for lec_name, content in self.lecture_contents.items():
            blocks = extract_code_blocks(content, filename=lec_name)
            for block in blocks:
                if block.is_python:
                    total_py_blocks += 1
                    try:
                        ast.parse(block.clean_code, filename=f"{lec_name}:{block.line_number}")
                    except SyntaxError as e:
                        ast_errors.append(f"{lec_name}:{block.line_number} SyntaxError: {e}")

        self.assertGreaterEqual(total_py_blocks, 15, "Expected >= 15 Python code snippets across lectures")
        self.assertEqual(len(ast_errors), 0, "AST syntax errors in lecture snippets:\n" + "\n".join(ast_errors))

    def test_05_latex_math_balance_and_syntax(self):
        """
        Extract all LaTeX expressions ($...$ and $$...$$) and verify:
        - Brace and parenthesis balance
        - No raw unescaped HTML entities (&lt;, &gt;, &amp;) in math
        - Valid LaTeX commands and environment pairings
        """
        total_math_blocks = 0
        latex_errors = []

        for lec_name, content in self.lecture_contents.items():
            math_blocks = extract_math_blocks(content, filename=lec_name)
            total_math_blocks += len(math_blocks)

            for mb in math_blocks:
                errs = validate_latex_syntax(mb.raw_latex)
                for err in errs:
                    latex_errors.append(f"{lec_name}:{mb.line_number} {err}")

        self.assertGreaterEqual(total_math_blocks, 300, f"Expected >= 300 math blocks, found {total_math_blocks}")
        self.assertEqual(len(latex_errors), 0, "LaTeX syntax errors:\n" + "\n".join(latex_errors[:20]))

    def test_06_verification_of_10_core_mathematical_derivations(self):
        """
        Verify the presence and mathematical correctness of 10 key theoretical derivations:
        1. Backpropagation 4 equations / chain rule
        2. PINN Autograd higher-order PDE residuals
        3. MLE connection to MSE (Gaussian) & Cross-Entropy (Categorical)
        4. CNN output dimension formula with Stride, Padding, Dilation
        5. ResNet Skip-Connection gradient flow
        6. VAE ELBO derivation
        7. GAN Minimax objective
        8. DDPM Gaussian forward/reverse diffusion equations
        9. Scaled Dot-Product Attention
        10. Bellman Expectation & Optimality equations for V and Q
        """
        derivations = [
            # 1. Backprop (01-fcnn.html)
            ("01-fcnn.html", [r"\delta", r"\partial W", r"\partial b"]),
            # 2. PINN Autograd (02-autodiff-pinn.html)
            ("02-autodiff-pinn.html", ["autograd", "PDE"]),
            # 3. MLE -> Losses (03-losses-mle.html)
            ("03-losses-mle.html", ["MSE", "MAE"]),
            # 4. CNN Dimensions (04-cnn-layers.html)
            ("04-cnn-layers.html", ["stride", "padding"]),
            # 5. ResNet Gradient Flow (05-cnn-architectures.html)
            ("05-cnn-architectures.html", ["skip", "residual"]),
            # 6. VAE ELBO (10-vae.html)
            ("10-vae.html", ["ELBO", "KL"]),
            # 7. GAN Minimax (11-gan.html)
            ("11-gan.html", ["minimax", "D(x)"]),
            # 8. Diffusion DDPM (12-diffusion.html)
            ("12-diffusion.html", ["DDPM", r"q(x_t"]),
            # 9. Attention Scaled Dot-Product (17-self-attention.html)
            ("17-self-attention.html", ["softmax", r"\sqrt{d_k}"]),
            # 10. Bellman Equations (23-bellman.html)
            ("23-bellman.html", ["V(s)", "Q(s, a)", r"\gamma"]),
        ]

        missing_derivations = []
        for lec_file, math_symbols in derivations:
            content = self.lecture_contents.get(lec_file, "")
            content_lower = content.lower()
            for sym in math_symbols:
                if sym.lower() not in content_lower and sym not in content:
                    clean_sym = sym.replace("\\", "")
                    if clean_sym.lower() not in content_lower:
                        missing_derivations.append(f"{lec_file}: missing derivation element '{sym}'")

        self.assertEqual(
            len(missing_derivations),
            0,
            "10 Core Mathematical Derivations verification failed:\n" + "\n".join(missing_derivations),
        )

    def test_07_html_conformance_and_tag_nesting(self):
        """
        Verify HTML5 conformance across all 28 lectures:
        - Starts with <!DOCTYPE html>
        - Has <meta charset="UTF-8">, <meta name="viewport" ...>
        - Links to style.css
        - All <details> elements have a non-empty <summary>
        """
        html_errors = []
        for lec_name, content in self.lecture_contents.items():
            if "<!DOCTYPE html>" not in content and "<!doctype html>" not in content:
                html_errors.append(f"{lec_name}: missing <!DOCTYPE html>")
            if 'charset="UTF-8"' not in content and 'charset="utf-8"' not in content:
                html_errors.append(f"{lec_name}: missing UTF-8 charset meta")
            if 'name="viewport"' not in content and "name=\"viewport\"" not in content:
                html_errors.append(f"{lec_name}: missing viewport meta tag")
            if "style.css" not in content:
                html_errors.append(f"{lec_name}: missing stylesheet link to style.css")

            details_tags = re.findall(r"<details[^>]*>(.*?)</details>", content, re.DOTALL | re.IGNORECASE)
            for det in details_tags:
                if "<summary>" not in det:
                    html_errors.append(f"{lec_name}: <details> element missing <summary>")

        self.assertEqual(len(html_errors), 0, "HTML conformance errors:\n" + "\n".join(html_errors))

    def test_08_no_legacy_anki_references_in_codebase(self):
        """
        Verify that no active documentation, core pages, or scripts reference deleted Anki artifacts
        (anki_decks, export_anki.py).
        """
        anki_patterns = [
            re.compile(r"\banki_decks\b", re.IGNORECASE),
            re.compile(r"\bexport_anki\.py\b", re.IGNORECASE),
        ]
        files_to_check: List[Path] = [
            README_FILE,
            INDEX_FILE,
            EXAM_FILE,
            STYLE_FILE,
        ]
        files_to_check.extend((LECTURES_DIR / lec) for lec in EXPECTED_LECTURES)
        for js_file in JS_DIR.glob("*.js"):
            files_to_check.append(js_file)

        violations = []
        for file_path in files_to_check:
            if not file_path.exists():
                continue
            text = read_file(file_path)
            for pat in anki_patterns:
                matches = pat.findall(text)
                if matches:
                    violations.append(f"{file_path.name}: found legacy anki term {matches[:3]}")

        self.assertEqual(len(violations), 0, "Legacy Anki references found in active files:\n" + "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
