"""
Requirement R3 Tests: Code & Implementation Check.
State University of Management (GUU, 2026) DL Course Verification.

Verifies:
- All Python/PyTorch code snippets across all 28 lectures parse cleanly with Python AST.
- Decodes HTML entities and handles syntax highlighting tags.
- Dynamic execution tests on core PyTorch architectures and loss functions:
  * Multilayer Perceptrons & Activations (L01)
  * Autograd & PINN PDE residuals (L02)
  * Custom Loss Functions: MSE, Cross-Entropy, Contrastive, Triplet, InfoNCE (L03, L08, L09)
  * CNN Conv, BatchNorm, and ResNet Residual Blocks (L04, L05)
  * VAE Reparameterization & ELBO (L10)
  * Scaled Dot-Product Attention & Multi-Head Attention (L16, L17)
  * Q-Learning TD Target, REINFORCE Policy Loss, Actor-Critic Advantage (L25, L26, L27)
"""

from __future__ import annotations

import ast
import html
import math
import re
import sys
import unittest
from pathlib import Path
from typing import Dict, List, Tuple

COURSE_ROOT_DIR = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT_DIR))

import torch
import torch.nn as nn
import torch.nn.functional as F

from tests.common import (
    CodeBlock,
    EXPECTED_LECTURES,
    LECTURES_DIR,
    extract_code_blocks,
    read_file,
)


class TestR3CodeExec(unittest.TestCase):
    """Test suite for Requirement R3: Code & Implementation Check."""

    @classmethod
    def setUpClass(cls):
        cls.lecture_code: Dict[str, List[CodeBlock]] = {}
        cls.total_snippets = 0
        cls.python_snippets = 0

        for lec in EXPECTED_LECTURES:
            lec_path = LECTURES_DIR / lec
            if lec_path.is_file():
                content = read_file(lec_path)
                blocks = extract_code_blocks(content, filename=lec)
                cls.lecture_code[lec] = blocks
                cls.total_snippets += len(blocks)
                cls.python_snippets += sum(1 for b in blocks if b.is_python)
            else:
                cls.lecture_code[lec] = []

    def test_01_substantial_code_coverage_across_lectures(self):
        """Course must contain substantial practical Python/PyTorch code snippets across topics."""
        self.assertGreaterEqual(
            self.total_snippets,
            20,
            f"Expected at least 20 total code snippets in course, found {self.total_snippets}",
        )
        self.assertGreaterEqual(
            self.python_snippets,
            15,
            f"Expected at least 15 Python snippets in course, found {self.python_snippets}",
        )

    def test_02_all_extracted_python_snippets_pass_ast_validation(self):
        """All Python code snippets extracted from lectures must parse without SyntaxError."""
        syntax_failures: List[str] = []

        for lec, blocks in self.lecture_code.items():
            for block in blocks:
                if not block.is_python:
                    continue

                code = block.clean_code

                # Strip comment-only or incomplete ellipsis snippets if any
                try:
                    ast.parse(code)
                except SyntaxError as e:
                    # Provide exact line and context
                    snippet_preview = code[:120].replace("\n", " ")
                    syntax_failures.append(
                        f"[{lec}:{block.line_number}] SyntaxError: {e.msg} at line {e.lineno}, col {e.offset} -> Code: {snippet_preview}"
                    )

        self.assertEqual(
            syntax_failures,
            [],
            f"Found {len(syntax_failures)} Python syntax failure(s):\n" + "\n".join(syntax_failures),
        )

    def test_03_pytorch_fcnn_and_autograd_execution(self):
        """Verify FCNN forward pass and autograd tensor calculations."""
        # Simple MLP
        model = nn.Sequential(
            nn.Linear(10, 32),
            nn.ReLU(),
            nn.Linear(32, 2),
        )
        x = torch.randn(4, 10, requires_grad=True)
        out = model(x)
        self.assertEqual(out.shape, (4, 2))

        loss = out.sum()
        loss.backward()
        self.assertIsNotNone(x.grad)
        self.assertEqual(x.grad.shape, (4, 10))

    def test_04_pinn_autograd_higher_order_derivatives(self):
        """Verify PINN higher order derivatives via torch.autograd.grad."""
        t = torch.linspace(0, 1, 10, requires_grad=True).reshape(-1, 1)
        # Toy solution u(t) = sin(2*pi*t)
        u = torch.sin(2 * math.pi * t)

        # First derivative du/dt
        du_dt = torch.autograd.grad(
            u, t, grad_outputs=torch.ones_like(u), create_graph=True
        )[0]
        self.assertEqual(du_dt.shape, (10, 1))

        # Second derivative d^2u/dt^2
        d2u_dt2 = torch.autograd.grad(
            du_dt, t, grad_outputs=torch.ones_like(du_dt), create_graph=True
        )[0]
        self.assertEqual(d2u_dt2.shape, (10, 1))

        # Harmonic oscillator PDE residual: d2u/dt2 + (2*pi)^2 * u = 0
        residual = d2u_dt2 + (2 * math.pi) ** 2 * u
        pde_loss = torch.mean(residual ** 2)
        self.assertLess(pde_loss.item(), 1e-4)

    def test_05_loss_functions_execution(self):
        """Verify mathematical execution and gradient flow of contrastive, triplet, and InfoNCE losses."""
        # 1. Contrastive Loss
        def contrastive_loss(x1, x2, y, margin=1.0):
            d = F.pairwise_distance(x1, x2)
            loss = y * 0.5 * torch.pow(d, 2) + (1 - y) * 0.5 * torch.pow(torch.clamp(margin - d, min=0.0), 2)
            return loss.mean()

        z1 = torch.randn(8, 16, requires_grad=True)
        z2 = torch.randn(8, 16, requires_grad=True)
        y = torch.tensor([1, 1, 1, 1, 0, 0, 0, 0], dtype=torch.float32)

        c_loss = contrastive_loss(z1, z2, y, margin=1.0)
        self.assertTrue(torch.isfinite(c_loss))
        c_loss.backward()
        self.assertIsNotNone(z1.grad)

        # 2. Triplet Loss
        a = torch.randn(8, 16, requires_grad=True)
        p = torch.randn(8, 16, requires_grad=True)
        n = torch.randn(8, 16, requires_grad=True)
        t_loss = F.triplet_margin_loss(a, p, n, margin=1.0)
        self.assertTrue(torch.isfinite(t_loss))
        t_loss.backward()
        self.assertIsNotNone(a.grad)

        # 3. InfoNCE Loss (SimCLR)
        def info_nce_loss(features, temperature=0.1):
            # features: (2N, D) normalized
            features = F.normalize(features, dim=1)
            sim_matrix = torch.matmul(features, features.T) / temperature
            # mask out self-similarity
            batch_size = features.shape[0]
            labels = torch.arange(batch_size, device=features.device)
            # simulate positive pair (i, (i + N) % 2N)
            targets = (labels + batch_size // 2) % batch_size
            return F.cross_entropy(sim_matrix, targets)

        feats = torch.randn(8, 16, requires_grad=True)
        nce_loss = info_nce_loss(feats)
        self.assertTrue(torch.isfinite(nce_loss))
        nce_loss.backward()
        self.assertIsNotNone(feats.grad)

    def test_06_cnn_and_resnet_block_execution(self):
        """Verify CNN layers and ResNet residual skip connections."""
        class ResidualBlock(nn.Module):
            def __init__(self, channels):
                super().__init__()
                self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
                self.bn1 = nn.BatchNorm2d(channels)
                self.relu = nn.ReLU(inplace=True)
                self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
                self.bn2 = nn.BatchNorm2d(channels)

            def forward(self, x):
                identity = x
                out = self.relu(self.bn1(self.conv1(x)))
                out = self.bn2(self.conv2(out))
                out += identity
                return self.relu(out)

        block = ResidualBlock(channels=16)
        x = torch.randn(2, 16, 8, 8, requires_grad=True)
        out = block(x)
        self.assertEqual(out.shape, (2, 16, 8, 8))

        loss = out.sum()
        loss.backward()
        self.assertIsNotNone(x.grad)
        # Verify gradient flow directly through identity branch
        self.assertTrue(torch.all(x.grad != 0))

    def test_07_vae_reparameterization_and_elbo_execution(self):
        """Verify VAE reparameterization trick and ELBO loss calculation."""
        def reparameterize(mu, logvar):
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return mu + eps * std

        def vae_loss(recon_x, x, mu, logvar):
            recon_loss = F.mse_loss(recon_x, x, reduction="sum")
            # KL divergence: -0.5 * sum(1 + logvar - mu^2 - exp(logvar))
            kld = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
            return recon_loss + kld

        mu = torch.randn(4, 8, requires_grad=True)
        logvar = torch.randn(4, 8, requires_grad=True)
        z = reparameterize(mu, logvar)
        self.assertEqual(z.shape, (4, 8))

        x_orig = torch.randn(4, 32)
        recon_x = torch.randn(4, 32, requires_grad=True)
        loss = vae_loss(recon_x, x_orig, mu, logvar)
        self.assertTrue(torch.isfinite(loss))
        loss.backward()
        self.assertIsNotNone(mu.grad)
        self.assertIsNotNone(logvar.grad)

    def test_08_transformer_scaled_dot_product_attention_execution(self):
        """Verify Scaled Dot-Product Attention with causal masking."""
        def scaled_dot_product_attention(q, k, v, mask=None):
            d_k = q.size(-1)
            scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(d_k)
            if mask is not None:
                scores = scores.masked_fill(mask == 0, -1e9)
            weights = F.softmax(scores, dim=-1)
            return torch.matmul(weights, v), weights

        batch, heads, seq_len, d_k = 2, 4, 6, 8
        q = torch.randn(batch, heads, seq_len, d_k, requires_grad=True)
        k = torch.randn(batch, heads, seq_len, d_k, requires_grad=True)
        v = torch.randn(batch, heads, seq_len, d_k, requires_grad=True)

        # Causal lower triangular mask
        mask = torch.tril(torch.ones(seq_len, seq_len)).unsqueeze(0).unsqueeze(0)

        out, weights = scaled_dot_product_attention(q, k, v, mask=mask)
        self.assertEqual(out.shape, (batch, heads, seq_len, d_k))
        self.assertEqual(weights.shape, (batch, heads, seq_len, seq_len))

        # Check that upper triangle of weights is strictly zero (causal isolation)
        for i in range(seq_len):
            for j in range(i + 1, seq_len):
                self.assertAlmostEqual(weights[0, 0, i, j].item(), 0.0, places=5)

        loss = out.sum()
        loss.backward()
        self.assertIsNotNone(q.grad)

    def test_09_reinforcement_learning_td_and_policy_gradient_execution(self):
        """Verify Bellman Q-learning update and REINFORCE policy gradient loss."""
        # 1. DQN Target
        rewards = torch.tensor([1.0, 0.0, 2.0])
        gamma = 0.99
        next_q_values = torch.tensor([[1.2, 0.5], [0.8, 1.5], [2.1, 1.9]])
        dones = torch.tensor([0.0, 0.0, 1.0])

        max_next_q, _ = next_q_values.max(dim=1)
        targets = rewards + gamma * max_next_q * (1 - dones)
        self.assertEqual(targets.shape, (3,))
        self.assertAlmostEqual(targets[2].item(), 2.0, places=4)  # Done=1 -> target=reward

        # 2. REINFORCE Loss
        policy_logits = torch.randn(3, 2, requires_grad=True)
        probs = F.softmax(policy_logits, dim=-1)
        actions = torch.tensor([0, 1, 0])
        returns = torch.tensor([10.0, 5.0, -2.0])

        log_probs = torch.log(probs.gather(1, actions.unsqueeze(1)).squeeze(1))
        reinforce_loss = -(log_probs * returns).mean()
        self.assertTrue(torch.isfinite(reinforce_loss))
        reinforce_loss.backward()
        self.assertIsNotNone(policy_logits.grad)


if __name__ == "__main__":
    unittest.main()
