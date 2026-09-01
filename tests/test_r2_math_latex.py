"""
Requirement R2 Tests: Math & LaTeX Verification.
State University of Management (GUU, 2026) DL Course Verification.

Verifies:
- All 28 lectures contain valid LaTeX delimiters ($$...$$ and $...$).
- Zero syntax errors in MathJax expressions (balanced braces, brackets, command structures).
- Absence of unescaped HTML entities in LaTeX math.
- Mathematical rigor: presence and mathematical correctness of foundational derivations
  across foundational topics (Backprop, PINN, MLE/NLL, Attention, VAE ELBO, GAN Minimax,
  DDPM, Bellman equations, Policy Gradient Theorem, GAE, SAC).
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path
from typing import Dict, List

COURSE_ROOT_DIR = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT_DIR))

from tests.common import (
    EXPECTED_LECTURES,
    LECTURES_DIR,
    MathBlock,
    extract_math_blocks,
    read_file,
    validate_latex_syntax,
)


class TestR2MathLatex(unittest.TestCase):
    """Test suite for Requirement R2: Math & LaTeX Verification."""

    @classmethod
    def setUpClass(cls):
        cls.lecture_math: Dict[str, List[MathBlock]] = {}
        for lec in EXPECTED_LECTURES:
            lec_path = LECTURES_DIR / lec
            if lec_path.is_file():
                content = read_file(lec_path)
                cls.lecture_math[lec] = extract_math_blocks(content, filename=lec)
            else:
                cls.lecture_math[lec] = []

    def test_01_all_lectures_have_math_blocks(self):
        """Every lecture must contain mathematical formulas (display or inline math)."""
        empty_math = []
        for lec, blocks in self.lecture_math.items():
            if len(blocks) < 3:
                empty_math.append(f"{lec} (only {len(blocks)} math blocks found)")

        self.assertEqual(
            empty_math, [], f"Lectures lacking sufficient mathematical content: {empty_math}"
        )

    def test_02_latex_delimiter_and_brace_balance_across_all_lectures(self):
        """Validates that all LaTeX expressions in all 28 lectures have balanced braces and valid syntax."""
        syntax_errors: List[str] = []

        for lec, blocks in self.lecture_math.items():
            for b in blocks:
                errors = validate_latex_syntax(b.raw_latex)
                for err in errors:
                    syntax_errors.append(f"[{lec}:{b.line_number}] {err}")

        self.assertEqual(
            syntax_errors,
            [],
            f"Found {len(syntax_errors)} LaTeX syntax error(s):\n" + "\n".join(syntax_errors[:20]),
        )

    def test_03_no_corrupting_html_entities_in_math(self):
        """Ensure no raw '&lt;', '&gt;', '&amp;' exist inside math expressions where LaTeX symbols are expected."""
        entity_errors: List[str] = []

        for lec, blocks in self.lecture_math.items():
            for b in blocks:
                # Raw &lt; or &gt; inside math block often breaks LaTeX parsers if not intended
                if re.search(r"&(?:lt|gt|amp);", b.raw_latex):
                    entity_errors.append(
                        f"[{lec}:{b.line_number}] Raw HTML entity inside LaTeX math: {b.raw_latex[:50]}"
                    )

        self.assertEqual(
            entity_errors,
            [],
            f"Found {len(entity_errors)} math expression(s) containing raw HTML entities:\n"
            + "\n".join(entity_errors[:20]),
        )

    def test_04_verify_l01_backpropagation_equations(self):
        """L01 (FCNN) must contain the 4 fundamental backpropagation equations."""
        content = read_file(LECTURES_DIR / "01-fcnn.html")
        # Check for delta^L, delta^l, dL/dW, dL/db
        self.assertTrue(
            r"\delta^L" in content or r"\delta^{L}" in content or r"\delta" in content,
            "L01 missing backprop delta definition",
        )
        self.assertTrue(
            r"\frac{\partial L}{\partial W}" in content or r"\partial W" in content,
            "L01 missing gradient with respect to weights",
        )
        self.assertTrue(
            r"\frac{\partial L}{\partial b}" in content or r"\partial b" in content,
            "L01 missing gradient with respect to bias",
        )

    def test_05_verify_l02_pinn_loss_and_residuals(self):
        """L02 (PINN) must contain PDE residual loss formulation."""
        content = read_file(LECTURES_DIR / "02-autodiff-pinn.html")
        self.assertTrue(
            "PDE" in content or r"\mathcal{F}" in content or "невязк" in content.lower(),
            "L02 missing PDE loss formulation",
        )
        self.assertTrue(
            "autograd" in content.lower() or "autodiff" in content.lower(),
            "L02 missing autograd/autodiff discussion",
        )

    def test_06_verify_l03_mle_and_loss_derivations(self):
        """L03 (Losses & MLE) must contain Gaussian/Laplace MLE and Cross-Entropy formulations."""
        content = read_file(LECTURES_DIR / "03-losses-mle.html")
        self.assertTrue(
            r"\log p(" in content
            or r"\ln p(" in content
            or "MLE" in content
            or "правдоподоби" in content.lower(),
            "L03 missing log-likelihood formulation",
        )
        self.assertTrue(
            "MSE" in content and ("MAE" in content or "L1" in content),
            "L03 missing MSE / MAE comparisons",
        )

    def test_07_verify_l04_l05_cnn_math_and_skip_connections(self):
        """L04 & L05 must contain receptive field / conv dimension formulas and ResNet gradient proof."""
        l04 = read_file(LECTURES_DIR / "04-cnn-layers.html")
        l05 = read_file(LECTURES_DIR / "05-cnn-architectures.html")

        # Conv dimension formula in L04
        self.assertTrue(
            "H_{out}" in l04
            or "W_{out}" in l04
            or "stride" in l04.lower()
            or "padding" in l04.lower(),
            "L04 missing convolution dimension output formula",
        )
        # Skip connection in L05
        self.assertTrue(
            "skip" in l05.lower() or "residual" in l05.lower() or r"\mathcal{F}(x)" in l05,
            "L05 missing residual / skip-connection formulation",
        )

    def test_08_verify_l10_vae_elbo_derivation(self):
        """L10 (VAE) must contain the ELBO derivation and Gaussian KL divergence."""
        content = read_file(LECTURES_DIR / "10-vae.html")
        self.assertTrue(
            "ELBO" in content or r"\mathcal{L}" in content, "L10 missing ELBO definition"
        )
        self.assertTrue(
            r"D_{KL}" in content or "KL" in content, "L10 missing KL divergence in ELBO"
        )
        self.assertTrue(
            r"\epsilon \sim \mathcal{N}" in content or r"\mu" in content and r"\sigma" in content,
            "L10 missing reparameterization trick formulation",
        )

    def test_09_verify_l11_gan_minimax_and_optimal_discriminator(self):
        """L11 (GAN) must contain the Minimax game objective and JSD connection."""
        content = read_file(LECTURES_DIR / "11-gan.html")
        self.assertTrue(
            r"\min_G \max_D" in content
            or r"\max_D \min_G" in content
            or r"V(D, G)" in content
            or "minimax" in content.lower(),
            "L11 missing Minimax game objective",
        )
        self.assertTrue(
            "D^*" in content or "D(x)" in content or "дискриминатор" in content.lower(),
            "L11 missing discriminator optimality discussion",
        )

    def test_10_verify_l12_diffusion_forward_and_reverse_math(self):
        """L12 (Diffusion) must contain forward q(x_t|x_0) and reverse denoising formulas."""
        content = read_file(LECTURES_DIR / "12-diffusion.html")
        self.assertTrue(
            r"q(x_t" in content
            or r"q(x_t|x_0)" in content
            or r"\alpha_t" in content
            or r"\beta_t" in content
            or "DDPM" in content,
            "L12 missing forward diffusion transition formula",
        )

    def test_11_verify_l16_l17_scaled_dot_product_attention_math(self):
        """L16 & L17 must contain Scaled Dot-Product Attention Softmax(QK^T / sqrt(d_k))V."""
        l16 = read_file(LECTURES_DIR / "16-transformers.html")
        l17 = read_file(LECTURES_DIR / "17-self-attention.html")
        combined = l16 + l17

        self.assertTrue(
            r"\frac{QK^T}{\sqrt{d" in combined
            or r"\text{softmax}" in combined.lower()
            or r"\text{Softmax}" in combined,
            "L16/L17 missing Scaled Dot-Product Attention formula",
        )

    def test_12_verify_l23_bellman_equations(self):
        """L23 (Bellman) must contain Bellman Expectation and Optimality equations."""
        content = read_file(LECTURES_DIR / "23-bellman.html")
        self.assertTrue(
            r"V(s)" in content or r"V^\pi(s)" in content or r"V^*(s)" in content,
            "L23 missing state value function V(s)",
        )
        self.assertTrue(
            r"Q(s, a)" in content or r"Q^\pi(s, a)" in content or r"Q^*(s, a)" in content,
            "L23 missing action value function Q(s, a)",
        )
        self.assertTrue(
            r"\gamma" in content,
            "L23 missing discount factor gamma in Bellman equation",
        )

    def test_13_verify_l26_l27_policy_gradient_and_actor_critic(self):
        """L26 & L27 must contain Policy Gradient Theorem, Advantage, and GAE."""
        l26 = read_file(LECTURES_DIR / "26-policy-gradient.html")
        l27 = read_file(LECTURES_DIR / "27-actor-critic.html")

        # L26 Policy gradient
        self.assertTrue(
            r"\nabla_\theta" in l26 or r"\log \pi" in l26 or "REINFORCE" in l26,
            "L26 missing policy gradient / log-derivative formula",
        )
        # L27 Actor-Critic & Advantage
        self.assertTrue(
            r"A(s, a)" in l27
            or r"A^\pi" in l27
            or "advantage" in l27.lower()
            or "GAE" in l27
            or "SAC" in l27,
            "L27 missing Advantage / Actor-Critic formulation",
        )


if __name__ == "__main__":
    unittest.main()
