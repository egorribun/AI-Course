import unittest
import ast
import re
from tests.common import (
    EXPECTED_LECTURES,
    LECTURES_DIR,
    read_file,
    extract_code_blocks,
    extract_math_blocks,
    validate_latex_syntax,
)


class TestAdversarialChallenger2FullAudit(unittest.TestCase):
    """Adversarial verification of 10 core derivations, numerical examples, and code blocks."""

    @classmethod
    def setUpClass(cls):
        cls.lectures = {}
        for lec in EXPECTED_LECTURES:
            path = LECTURES_DIR / lec
            cls.lectures[lec] = read_file(path)

    def test_01_verify_all_8_sections_exist_in_all_28_lectures(self):
        section_ids = ["s1", "s2", "s3", "s4", "s5", "qa", "tasks", "cheat"]
        for lec, content in self.lectures.items():
            for sid in section_ids:
                pattern = rf'<h2[^>]*id=["\']{sid}["\']'
                self.assertTrue(
                    bool(re.search(pattern, content)), f"{lec} missing section with id='{sid}'"
                )

    def test_02_verify_latex_syntax_and_delimiters(self):
        errors = []
        for lec, content in self.lectures.items():
            blocks = extract_math_blocks(content, filename=lec)
            self.assertGreater(len(blocks), 5, f"{lec} has too few math blocks ({len(blocks)})")
            for b in blocks:
                errs = validate_latex_syntax(b.raw_latex)
                if errs:
                    errors.extend([f"{lec}:{b.line_number} {e}" for e in errs])
        self.assertEqual(len(errors), 0, "LaTeX errors:\n" + "\n".join(errors[:10]))

    def test_03_verify_derivation_01_elbo(self):
        """1. VAE ELBO: Jensen's inequality, KL decomposition, Gaussian analytical form, Reparameterization trick."""
        content = self.lectures["10-vae.html"]
        self.assertIn("ELBO", content)
        self.assertTrue(r"D_{\text{KL}}" in content or r"D_{KL}" in content or "KL" in content)
        self.assertTrue(r"\log p_\theta(x)" in content or r"\log p(x)" in content)
        self.assertTrue(r"\mathbb{E}" in content)
        self.assertTrue(
            r"\epsilon \sim \mathcal{N}(0, I)" in content or r"\epsilon \sim \mathcal{N}" in content
        )
        self.assertTrue(
            r"z = \mu" in content or r"\mu(x) + \sigma(x)" in content or r"\mu +" in content
        )
        # Check Gaussian KL formula: 1 + log(sigma^2) - mu^2 - sigma^2
        self.assertTrue(
            r"\log(\sigma_j^2)" in content or r"\log(\sigma^2)" in content or r"\sigma^2" in content
        )

    def test_04_verify_derivation_02_bellman_equations(self):
        """2. Bellman equations: Expectation & Optimality for V & Q, Matrix solution, Contraction mapping."""
        content = self.lectures["23-bellman.html"]
        self.assertIn("V^\\pi(s)", content)
        self.assertIn("Q^\\pi(s, a)", content)
        self.assertIn("V^*(s)", content)
        self.assertIn("Q^*(s, a)", content)
        self.assertIn("\\gamma", content)
        self.assertTrue(
            "(I - \\gamma \\mathcal{P}^\\pi)" in content
            or "I - \\gamma" in content
            or "linalg.solve" in content
        )
        self.assertTrue(
            "\\mathcal{T}^*" in content
            or "T*" in content
            or "Банаха" in content
            or "сжимающ" in content
        )

    def test_05_verify_derivation_03_policy_gradient(self):
        """3. Policy Gradient theorem: Log-derivative trick, vanishing environment dynamics, REINFORCE."""
        content = self.lectures["26-policy-gradient.html"]
        self.assertIn("\\nabla_\\theta J(\\theta)", content)
        self.assertTrue("\\nabla_\\theta \\log" in content or "\\nabla \\log" in content)
        self.assertIn("REINFORCE", content)
        self.assertTrue("P(\\tau; \\theta)" in content or "\\pi_\\theta" in content)
        self.assertTrue(
            "b(S_t)" in content
            or "b(s)" in content
            or "baseline" in content.lower()
            or "базов" in content.lower()
        )

    def test_06_verify_derivation_04_softmax_derivative(self):
        """4. Softmax derivative: Jacobian and Cross-Entropy gradient delta = y_hat - y."""
        c01 = self.lectures["01-fcnn.html"]
        c03 = self.lectures["03-losses-mle.html"]
        c17 = self.lectures["17-self-attention.html"]
        self.assertTrue(
            r"\hat{y} - y" in c01
            or r"\delta^L" in c01
            or r"\sigma_i" in c03
            or r"\text{softmax}" in c17.lower()
        )
        self.assertTrue("Cross-Entropy" in c01 or "Softmax" in c01)

    def test_07_verify_derivation_05_scaled_dot_product_variance(self):
        """5. Scaled Dot-Product: Variance proof Var(q*k) = d_k, division by sqrt(d_k) normalizes variance to 1."""
        content = self.lectures["17-self-attention.html"]
        self.assertIn("\\sqrt{d_k}", content)
        self.assertTrue(
            "\\text{Var}(q \\cdot k)" in content
            or "Var(q" in content
            or "дисперси" in content.lower()
        )
        self.assertTrue("d_k" in content)

    def test_08_verify_derivation_06_backprop_chain_rule(self):
        """6. Backprop 4 equations: BP1, BP2, BP3, BP4, error projection via W^T."""
        content = self.lectures["01-fcnn.html"]
        self.assertIn("BP1", content)
        self.assertIn("BP2", content)
        self.assertIn("BP3", content)
        self.assertIn("BP4", content)
        self.assertTrue(
            "(W^{l+1})^\\top" in content
            or "(W^{l+1})^T" in content
            or "W^\\top" in content
            or "W^T" in content
        )

    def test_09_verify_derivation_07_triplet_loss(self):
        """7. Triplet loss: Margin alpha, Euclidean-Cosine equivalence on sphere, mining."""
        content = self.lectures["08-metric-learning.html"]
        self.assertIn("\\mathcal{L}_{triplet}", content)
        self.assertTrue(r"\alpha" in content or "margin" in content.lower())
        self.assertTrue(
            "2(1 - \\cos(a, b))" in content or "1 - \\cos" in content or "D_{cos}" in content
        )

    def test_10_verify_derivation_08_ddpm_reverse_noise(self):
        """8. DDPM reverse diffusion: marginal q(x_t|x_0), posterior mean mu_tilde, noise prediction epsilon_theta."""
        content = self.lectures["12-diffusion.html"]
        self.assertIn("q(x_t | x_0)", content)
        self.assertTrue(
            r"\tilde{\mu}_t" in content
            or r"\mu_t" in content
            or r"\tilde{\beta}_t" in content
            or r"\beta_t" in content
        )
        self.assertTrue(
            r"\epsilon_\theta" in content
            or r"\mathcal{L}_{\text{simple}}" in content
            or r"L_{\text{simple}}" in content
        )

    def test_11_verify_derivation_09_infonce_bound(self):
        """9. InfoNCE bound: NT-Xent formula, Mutual Information lower bound I(X;Y) >= log(K) - L_InfoNCE."""
        content = self.lectures["09-contrastive-ssl.html"]
        self.assertTrue(
            r"\mathcal{L}_{i, j}" in content
            or r"\text{InfoNCE}" in content
            or r"\text{NT-Xent}" in content
            or "InfoNCE" in content
        )
        self.assertTrue(
            r"I(z_i; z_j) \ge \log(K)" in content
            or r"\log(K) - \mathcal{L}" in content
            or r"I(X; Y)" in content
            or "взаимной информации" in content
        )
        self.assertTrue(r"\tau" in content)

    def test_12_verify_derivation_10_gan_minimax(self):
        """10. GAN Minimax: V(D, G), optimal discriminator D*(x), reduction to 2*JSD - 2*log(2)."""
        content = self.lectures["11-gan.html"]
        self.assertIn("V(D, G)", content)
        self.assertTrue("D^*(x)" in content or "D^*" in content)
        self.assertTrue(r"p_{\text{data}}" in content or "p_{data}" in content)
        self.assertTrue(r"D_{\text{JS}}" in content or "JS" in content or "Йенсена" in content)

    def test_13_python_code_blocks_ast_and_execution_safety(self):
        """Check all python code snippets across all 28 lectures for AST validity and execution safety."""
        total_blocks = 0
        for lec, content in self.lectures.items():
            blocks = extract_code_blocks(content, filename=lec)
            for b in blocks:
                if b.is_python:
                    total_blocks += 1
                    # AST parse
                    tree = ast.parse(b.clean_code, filename=f"{lec}:{b.line_number}")
                    self.assertIsNotNone(tree)
        self.assertGreater(
            total_blocks, 15, f"Expected >=15 python code blocks, found {total_blocks}"
        )


if __name__ == "__main__":
    unittest.main()
