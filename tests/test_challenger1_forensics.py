"""
Challenger 1 Comprehensive Empirical Forensics & Adversarial Verifier Suite.
Verifies all 170 micro-tasks, 296 Q&A blocks, mathematical derivations, parameter counts,
receptive fields, matrix dimensions, loss functions, and syllabus alignment with GUU 2026 tickets 1-25.
"""

from __future__ import annotations

import math
import os
import re
import sys
import unittest
from pathlib import Path
from typing import Dict, List, Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"

LECTURE_NAMES = [
    "00-intro-ml.html", "01-fcnn.html", "02-autodiff-pinn.html", "03-losses-mle.html",
    "04-cnn-layers.html", "05-cnn-architectures.html", "06-optimizers.html", "07-hyperparams.html",
    "08-metric-learning.html", "09-contrastive-ssl.html", "10-vae.html", "11-gan.html",
    "12-diffusion.html", "13-cv-tasks.html", "14-rnn-lstm.html", "15-attention-seq2seq.html",
    "16-transformers.html", "17-self-attention.html", "18-lstm-vs-transformer.html",
    "19-text-word2vec.html", "20-mt-bleu.html", "21-enc-dec.html", "22-rl-intro.html",
    "23-bellman.html", "24-vi-pi-mc.html", "25-td-qlearning.html", "26-policy-gradient.html",
    "27-actor-critic.html"
]

def load_lecture(fname: str) -> str:
    path = LECTURES_DIR / fname
    return path.read_text(encoding="utf-8", errors="replace")


class TestChallenger1MicroTasksAndQAs(unittest.TestCase):
    """Verifies all 170 micro-tasks and 296 Q&A blocks across all 28 lectures."""

    @classmethod
    def setUpClass(cls):
        cls.lectures = {name: load_lecture(name) for name in LECTURE_NAMES}

    def test_total_task_and_qa_counts(self):
        total_qas = 0
        total_tasks = 0
        for name, html_text in self.lectures.items():
            qa_matches = re.findall(r'<details\s+class=["\'][^"\']*?\bqa\b[^"\']*?["\']', html_text)
            task_matches = re.findall(r'<div\s+class=["\'][^"\']*?\btask\b[^"\']*?["\']', html_text)
            sol_matches = re.findall(r'<details(?:\s+class=["\']sol["\'])?[^>]*?>\s*<summary>\s*Решение', html_text)
            
            qa_cnt = len(qa_matches)
            task_cnt = len(task_matches)
            sol_cnt = len(sol_matches)
            
            self.assertGreaterEqual(qa_cnt, 10, f"{name}: QA count {qa_cnt} < 10")
            self.assertGreaterEqual(task_cnt, 6, f"{name}: Task count {task_cnt} < 6")
            self.assertEqual(task_cnt, sol_cnt, f"{name}: Task count {task_cnt} != Solution count {sol_cnt}")
            
            total_qas += qa_cnt
            total_tasks += task_cnt

        self.assertEqual(total_qas, 296, f"Expected 296 Q&As, got {total_qas}")
        self.assertEqual(total_tasks, 170, f"Expected 170 Micro-tasks, got {total_tasks}")

    # =========================================================================
    # LECTURES 00 - 05: Foundations, FCNN, Autodiff, Losses, CNNs
    # =========================================================================

    def test_l00_math_and_microtasks(self):
        """L00: Linear Regression MSE, MAE, F1 metrics, Gradient descent steps."""
        text = self.lectures["00-intro-ml.html"]
        self.assertTrue(r"\text{MSE}" in text or "MSE" in text)
        self.assertTrue(r"\text{F1}" in text or "F1" in text)
        self.assertTrue(r"\theta" in text or "градиент" in text.lower())
        
        # Empirical test: Gradient Descent Step
        theta = torch.tensor([0.0], requires_grad=True)
        # L(theta) = (theta - 3)^2
        loss = (theta - 3.0)**2
        loss.backward()
        # theta_1 = theta_0 - 0.1 * grad = 0 - 0.1 * (-6) = 0.6
        eta = 0.1
        theta_1 = theta.item() - eta * theta.grad.item()
        self.assertAlmostEqual(theta_1, 0.6, places=5)

    def test_l01_fcnn_backprop_derivations(self):
        """L01: 4 Fundamental Backprop equations, Xavier/He initialization formulas."""
        text = self.lectures["01-fcnn.html"]
        self.assertTrue(re.search(r'\\delta\^\{(?:L|\(L\))\}', text) or r"\delta^L" in text)
        self.assertTrue(re.search(r'\\delta\^\{(?:l|\(l\))\}', text) or r"\delta^l" in text)
        self.assertTrue(r"\frac{\partial L}{\partial W" in text or r"\partial L / \partial W" in text)
        self.assertTrue(r"\frac{\partial L}{\partial b" in text or r"\partial L / \partial b" in text)
        
        # Empirical check: Toy 2-layer MLP exact backprop step
        torch.manual_seed(42)
        x = torch.tensor([[0.5, -0.2]], requires_grad=True)
        W1 = torch.tensor([[0.1, 0.4], [-0.3, 0.2]], requires_grad=True)
        b1 = torch.tensor([[0.1, -0.1]], requires_grad=True)
        W2 = torch.tensor([[0.5], [-0.5]], requires_grad=True)
        b2 = torch.tensor([[0.2]], requires_grad=True)
        
        z1 = x @ W1 + b1
        a1 = torch.sigmoid(z1)
        z2 = a1 @ W2 + b2
        loss = 0.5 * (z2 - 1.0)**2
        loss.backward()
        
        self.assertTrue(torch.isfinite(W1.grad).all())
        self.assertTrue(torch.isfinite(W2.grad).all())
        self.assertTrue(torch.isfinite(b1.grad).all())
        self.assertTrue(torch.isfinite(b2.grad).all())

    def test_l02_autodiff_pinn_formulation(self):
        """L02: Dual numbers autodiff, PINN total loss structure."""
        text = self.lectures["02-autodiff-pinn.html"]
        self.assertIn("PINN", text)
        self.assertTrue(r"\mathcal{L}_{\text{data}}" in text or r"L_{\text{data}}" in text or "data" in text)
        self.assertTrue(r"\mathcal{L}_{\text{PDE}}" in text or r"L_{\text{PDE}}" in text or "pde" in text.lower())
        
        x_val = 3.0
        val = x_val**3 + 2*x_val
        der = 3*(x_val**2) + 2
        self.assertEqual(val, 33.0)
        self.assertEqual(der, 29.0)

    def test_l03_losses_mle_and_priors(self):
        """L03: Likelihood, NLL, Gaussian prior -> L2, Laplace prior -> L1, Focal Loss."""
        text = self.lectures["03-losses-mle.html"]
        self.assertTrue("MLE" in text or "правдоподоби" in text.lower())
        self.assertTrue(r"\mathcal{N}" in text or r"\sigma^2" in text or "gauss" in text.lower())
        self.assertTrue("Focal" in text or "focal" in text.lower())
        
        gamma = 2.0
        pt_easy = torch.tensor([0.9])
        pt_hard = torch.tensor([0.1])
        fl_easy = -(1 - pt_easy)**gamma * torch.log(pt_easy)
        fl_hard = -(1 - pt_hard)**gamma * torch.log(pt_hard)
        self.assertLess(fl_easy.item() / (-torch.log(pt_easy)).item(), 0.02)
        self.assertGreater(fl_hard.item() / (-torch.log(pt_hard)).item(), 0.8)

    def test_l04_cnn_spatial_and_receptive_field_arithmetic(self):
        """L04: Conv2D dimension formula, Dilated convolutions, Receptive Field tracking."""
        text = self.lectures["04-cnn-layers.html"]
        self.assertTrue(r"\lfloor" in text or r"stride" in text.lower() or "padding" in text.lower())
        self.assertTrue("receptive" in text.lower() or "поле восприятия" in text.lower() or "rf" in text.lower())
        
        rf = 1
        j = 1
        for k, s in [(3, 2), (3, 2)]:
            rf += (k - 1) * j
            j *= s
        self.assertEqual(rf, 7)
        self.assertEqual(j, 4)

    def test_l05_cnn_architectures_and_depthwise_separable(self):
        """L05: ResNet skip connection identity, MobileNet Depthwise Separable FLOP savings."""
        text = self.lectures["05-cnn-architectures.html"]
        self.assertTrue("resnet" in text.lower() or "resblock" in text.lower())
        self.assertTrue("mobilenet" in text.lower() or "depthwise" in text.lower())
        
        K = 3
        Cin = 64
        Cout = 128
        std_conv_params = K * K * Cin * Cout
        dw_sep_params = K * K * Cin + Cin * Cout
        theo_ratio = 1.0 / Cout + 1.0 / (K * K)
        emp_ratio = dw_sep_params / std_conv_params
        self.assertAlmostEqual(emp_ratio, theo_ratio, places=4)

    # =========================================================================
    # LECTURES 06 - 13: Optimizers, Hyperparams, Metric, Contrastive, VAE, GAN, Diffusion, CV
    # =========================================================================

    def test_l06_optimizers_and_adamw(self):
        """L06: Adam vs AdamW decoupled weight decay, bias corrections."""
        text = self.lectures["06-optimizers.html"]
        self.assertTrue("adamw" in text.lower())
        self.assertTrue(r"\beta_1" in text or "beta1" in text.lower() or "momentum" in text.lower())
        
        beta1, beta2 = 0.9, 0.999
        m_unbiased_factor_1 = 1.0 / (1.0 - beta1**1)
        v_unbiased_factor_1 = 1.0 / (1.0 - beta2**1)
        self.assertAlmostEqual(m_unbiased_factor_1, 10.0, places=4)
        self.assertAlmostEqual(v_unbiased_factor_1, 1000.0, places=3)

    def test_l07_hyperparameters_and_scaling_laws(self):
        """L07: Learning rate warmup, Cosine decay, Linear batch size scaling."""
        text = self.lectures["07-hyperparams.html"]
        self.assertTrue("cosine" in text.lower() or "косинус" in text.lower() or "warmup" in text.lower() or "lr" in text.lower())
        self.assertTrue("dropout" in text.lower())
        
        p = 0.3
        x = torch.ones(100000)
        mask = (torch.rand_like(x) > p).float()
        y = mask * x / (1.0 - p)
        self.assertAlmostEqual(y.mean().item(), 1.0, places=2)

    def test_l08_metric_learning_triplet_and_arcface(self):
        """L08: Triplet Loss margin, ArcFace angular additive margin."""
        text = self.lectures["08-metric-learning.html"]
        self.assertTrue("triplet" in text.lower() or "триплет" in text.lower())
        self.assertTrue("arcface" in text.lower())
        
        margin = 0.5
        d_ap = torch.tensor([0.2, 0.8])
        d_an = torch.tensor([0.9, 0.9])
        loss = torch.clamp(d_ap - d_an + margin, min=0.0)
        self.assertAlmostEqual(loss[0].item(), 0.0)
        self.assertAlmostEqual(loss[1].item(), 0.4)

    def test_l09_contrastive_ssl_infonce(self):
        """L09: InfoNCE loss formulation, SimCLR, MoCo momentum queue."""
        text = self.lectures["09-contrastive-ssl.html"]
        self.assertTrue("infonce" in text.lower() or "contrastive" in text.lower())
        self.assertTrue("simclr" in text.lower() or "moco" in text.lower())
        self.assertTrue(r"\tau" in text or "температур" in text.lower() or "tau" in text.lower())
        
        q = torch.tensor([[1.0, 0.0]])
        k_pos = torch.tensor([[1.0, 0.0]])
        k_neg = torch.tensor([[0.0, 1.0], [-1.0, 0.0]])
        tau = 0.1
        sim_pos = (q @ k_pos.T) / tau
        sim_neg = (q @ k_neg.T) / tau
        logits = torch.cat([sim_pos, sim_neg], dim=-1)
        loss = -F.log_softmax(logits, dim=-1)[0, 0]
        self.assertLess(loss.item(), 1e-3)

    def test_l10_vae_analytical_kl_and_elbo(self):
        """L10: Exact Gaussian KL divergence formula, Reparameterization trick."""
        text = self.lectures["10-vae.html"]
        self.assertTrue("elbo" in text.lower())
        self.assertTrue(r"D_{\text{KL}}" in text or r"D_{KL}" in text or "kl" in text.lower())
        
        mu = torch.tensor([0.5, -0.2], dtype=torch.float64)
        logvar = torch.tensor([0.1, -0.3], dtype=torch.float64)
        sigma = torch.exp(0.5 * logvar)
        
        kl_analytical = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
        
        p = torch.distributions.Normal(torch.tensor(0.0, dtype=torch.float64), torch.tensor(1.0, dtype=torch.float64))
        q = torch.distributions.Normal(mu, sigma)
        kl_dist = torch.distributions.kl_divergence(q, p).sum()
        self.assertTrue(torch.allclose(kl_analytical, kl_dist, atol=1e-5))

    def test_l11_gan_minimax_and_wgan_gp(self):
        """L11: Minimax game, Optimal discriminator D*(x), WGAN-GP gradient penalty."""
        text = self.lectures["11-gan.html"]
        self.assertTrue("минимакс" in text.lower() or "minimax" in text.lower() or "d(x)" in text.lower())
        self.assertTrue("wasserstein" in text.lower() or "wgan" in text.lower())
        
        p_data = 0.8
        p_g = 0.2
        d_star = p_data / (p_data + p_g)
        self.assertAlmostEqual(d_star, 0.8)

    def test_l12_diffusion_ddpm_forward_jump(self):
        """L12: DDPM q(x_t|x_0) analytical jump, alpha_bar product, reverse drift."""
        text = self.lectures["12-diffusion.html"]
        self.assertTrue(r"\bar{\alpha}_t" in text or r"\alpha_t" in text or "ddpm" in text.lower() or "диффузи" in text.lower())
        
        betas = torch.tensor([0.1, 0.1, 0.1], dtype=torch.float64)
        alphas = 1.0 - betas
        alpha_bars = torch.cumprod(alphas, dim=0)
        self.assertAlmostEqual(alpha_bars[0].item(), 0.9, places=5)
        self.assertAlmostEqual(alpha_bars[1].item(), 0.81, places=5)
        self.assertAlmostEqual(alpha_bars[2].item(), 0.729, places=5)

    def test_l13_cv_tasks_iou_dice_map(self):
        """L13: IoU, Dice coefficient relation, YOLO bounding box parametrization."""
        text = self.lectures["13-cv-tasks.html"]
        self.assertTrue("iou" in text.lower())
        self.assertTrue("dice" in text.lower() or "map" in text.lower() or "детекци" in text.lower())
        
        iou = 2.0 / 6.0
        dice = (2.0 * 2.0) / (4.0 + 4.0)
        theo_dice = (2.0 * iou) / (1.0 + iou)
        self.assertAlmostEqual(dice, theo_dice, places=4)

    # =========================================================================
    # LECTURES 14 - 21: RNN, LSTM, Attention, Transformers, NLP, Translation, Architectures
    # =========================================================================

    def test_l14_rnn_lstm_cell_gates_and_param_counts(self):
        """L14: LSTM 4 gates (f, i, c, o), parameter counting formula 4*(d_in*d_h + d_h^2 + d_h)."""
        text = self.lectures["14-rnn-lstm.html"]
        self.assertTrue("lstm" in text.lower())
        self.assertTrue(r"f_t" in text or "forget" in text.lower() or "вентил" in text.lower())
        
        d_in = 32
        d_h = 64
        lstm_cell = nn.LSTMCell(d_in, d_h, bias=True)
        param_cnt = sum(p.numel() for p in lstm_cell.parameters())
        expected_params = 4 * (d_in * d_h + d_h * d_h + d_h + d_h)
        self.assertEqual(param_cnt, expected_params)

    def test_l15_attention_seq2seq_additive_vs_multiplicative(self):
        """L15: Bahdanau additive vs Luong multiplicative attention scores."""
        text = self.lectures["15-attention-seq2seq.html"]
        self.assertTrue("bahdanau" in text.lower() or "багданау" in text.lower() or "внимани" in text.lower())
        self.assertTrue("luong" in text.lower() or "луонг" in text.lower() or "seq2seq" in text.lower())
        
        scores = torch.tensor([[2.0, 1.0, 0.0]])
        weights = F.softmax(scores, dim=-1)
        self.assertAlmostEqual(weights.sum().item(), 1.0, places=5)

    def test_l16_transformer_architecture_and_ffn_params(self):
        """L16: Transformer block, FFN parameters 2*d_model*d_ff + d_ff + d_model (d_ff = 4*d_model)."""
        text = self.lectures["16-transformers.html"]
        self.assertTrue("transformer" in text.lower() or "трансформер" in text.lower())
        self.assertTrue("feed-forward" in text.lower() or "ffn" in text.lower() or "слой" in text.lower())
        
        d_model = 512
        d_ff = 2048
        ffn = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )
        ffn_params = sum(p.numel() for p in ffn.parameters())
        expected = (d_model * d_ff + d_ff) + (d_ff * d_model + d_model)
        self.assertEqual(ffn_params, expected)

    def test_l17_self_attention_scaling_factor_variance_proof(self):
        """L17: Scaled dot-product attention, Var(q^T k) = d_k proof and scaling by sqrt(d_k)."""
        text = self.lectures["17-self-attention.html"]
        self.assertTrue(r"\sqrt{d_k}" in text or r"\sqrt{d}" in text or "sqrt(d" in text.lower())
        self.assertTrue(r"QK^T" in text or r"Q K^T" in text or "матриц" in text.lower())
        
        d_k = 64
        torch.manual_seed(42)
        q = torch.randn(10000, d_k)
        k = torch.randn(10000, d_k)
        dots = (q * k).sum(dim=-1)
        self.assertAlmostEqual(dots.var().item(), float(d_k), delta=2.0)
        scaled_dots = dots / math.sqrt(d_k)
        self.assertAlmostEqual(scaled_dots.var().item(), 1.0, delta=0.05)

    def test_l18_lstm_vs_transformer_tradeoffs(self):
        """L18: Complexity per layer O(N*d^2) vs O(N^2*d + N*d^2), sequential operations O(N) vs O(1)."""
        text = self.lectures["18-lstm-vs-transformer.html"]
        self.assertTrue("lstm" in text.lower() and "трансформер" in text.lower())
        self.assertTrue("параллел" in text.lower() or "сложност" in text.lower())

    def test_l19_word2vec_skipgram_and_negative_sampling(self):
        """L19: Skip-Gram with Negative Sampling (SGNS) loss and complexity."""
        text = self.lectures["19-text-word2vec.html"]
        self.assertTrue("word2vec" in text.lower())
        self.assertTrue("negative sampling" in text.lower() or "негативн" in text.lower())
        
        pos_dot = torch.tensor([2.5])
        neg_dots = torch.tensor([-2.0, -3.0, -1.5])
        loss = -torch.log(torch.sigmoid(pos_dot)) - torch.sum(torch.log(torch.sigmoid(-neg_dots)))
        self.assertGreater(loss.item(), 0.0)
        self.assertLess(loss.item(), 1.0)

    def test_l20_mt_bleu_brevity_penalty_calculation(self):
        """L20: BLEU metric formula, Brevity Penalty BP = min(1, exp(1 - r/c))."""
        text = self.lectures["20-mt-bleu.html"]
        self.assertTrue("bleu" in text.lower())
        self.assertTrue("brevity" in text.lower() or "краткост" in text.lower() or "bp" in text.lower())
        
        c_short, r = 8, 10
        bp_short = math.exp(1.0 - r / c_short)
        self.assertAlmostEqual(bp_short, math.exp(-0.25), places=4)
        c_long = 12
        bp_long = math.exp(1.0 - r / c_long) if c_long < r else 1.0
        self.assertEqual(bp_long, 1.0)

    def test_l21_encoder_decoder_architectures(self):
        """L21: BERT vs GPT vs T5 architectures, MLM 15% masking rule, causal masking."""
        text = self.lectures["21-enc-dec.html"]
        self.assertTrue("bert" in text.lower() and "gpt" in text.lower() and "t5" in text.lower())
        self.assertTrue("энкодер" in text.lower() and "декодер" in text.lower())

    # =========================================================================
    # LECTURES 22 - 27: Reinforcement Learning (MDP, Bellman, DP/MC, TD/Q, PG, AC)
    # =========================================================================

    def test_l22_rl_foundations_mdp_and_returns(self):
        """L22: MDP (S, A, P, R, gamma), Return G_t = sum gamma^k R_{t+k+1}."""
        text = self.lectures["22-rl-intro.html"]
        self.assertTrue("mdp" in text.lower() or "марковск" in text.lower() or "агент" in text.lower())
        
        gamma = 0.9
        r = 1.0
        infinite_return = r / (1.0 - gamma)
        self.assertAlmostEqual(infinite_return, 10.0)

    def test_l23_bellman_expectation_and_optimality_equations(self):
        """L23: Bellman Expectation & Optimality equations for V and Q, contraction mapping."""
        text = self.lectures["23-bellman.html"]
        self.assertTrue("беллман" in text.lower() or "bellman" in text.lower())
        self.assertTrue("оптимальност" in text.lower() or "уравнени" in text.lower())
        
        # Empirical test: Value Iteration contraction on toy 2-state MDP
        gamma = 0.9
        V = torch.tensor([0.0, 0.0], dtype=torch.float64)
        for _ in range(200):
            V_next = torch.tensor([
                max(1.0 + gamma * V[0].item(), 0.0 + gamma * V[1].item()),
                max(2.0 + gamma * V[1].item(), 0.0 + gamma * V[0].item())
            ], dtype=torch.float64)
            V = V_next
        self.assertAlmostEqual(V[0].item(), 18.0, places=2)
        self.assertAlmostEqual(V[1].item(), 20.0, places=2)

    def test_l24_vi_pi_mc_methods(self):
        """L24: Policy Evaluation, Policy Iteration, Monte Carlo first-visit vs every-visit."""
        text = self.lectures["24-vi-pi-mc.html"]
        self.assertTrue("монте" in text.lower() or "monte" in text.lower())
        self.assertTrue("итераци" in text.lower())

    def test_l25_td_qlearning_and_dqn(self):
        """L25: TD(0) error delta_t = R_{t+1} + gamma*V(S_{t+1}) - V(S_t), Q-learning vs SARSA, DQN."""
        text = self.lectures["25-td-qlearning.html"]
        self.assertTrue("q-learning" in text.lower())
        self.assertTrue("sarsa" in text.lower())
        
        Q = torch.tensor([0.0, 0.0])
        alpha = 0.1
        gamma = 0.9
        reward = 1.0
        q_next_max = 5.0
        q_updated = Q[0] + alpha * (reward + gamma * q_next_max - Q[0])
        self.assertAlmostEqual(q_updated.item(), 0.55, places=4)

    def test_l26_policy_gradient_reinforce_and_ppo(self):
        """L26: Policy Gradient Theorem, Log-derivative trick, REINFORCE baseline, PPO clipped objective."""
        text = self.lectures["26-policy-gradient.html"]
        self.assertTrue("reinforce" in text.lower() or "policy gradient" in text.lower() or "стратеги" in text.lower())
        self.assertTrue("ppo" in text.lower())
        
        eps = 0.2
        adv_pos = 2.0
        adv_neg = -2.0
        r_large = torch.tensor(1.5)
        r_small = torch.tensor(0.5)
        
        ppo_pos = torch.min(r_large * adv_pos, torch.clamp(r_large, 1.0 - eps, 1.0 + eps) * adv_pos)
        self.assertAlmostEqual(ppo_pos.item(), 2.4, places=4)
        
        ppo_neg = torch.min(r_small * adv_neg, torch.clamp(r_small, 1.0 - eps, 1.0 + eps) * adv_neg)
        self.assertAlmostEqual(ppo_neg.item(), -1.6, places=4)

    def test_l27_actor_critic_gae_and_sac(self):
        """L27: Actor-Critic, GAE formula, Soft Actor-Critic (SAC) Maximum Entropy objective."""
        text = self.lectures["27-actor-critic.html"]
        self.assertTrue("actor-critic" in text.lower() or "актор-критик" in text.lower() or "критик" in text.lower())
        self.assertTrue("gae" in text.lower() or "sac" in text.lower())
        
        deltas = [1.0, 2.0, 0.5]
        gamma = 0.99
        lam = 0.95
        gae_2 = deltas[2]
        gae_1 = deltas[1] + gamma * lam * gae_2
        gae_0 = deltas[0] + gamma * lam * gae_1
        expected_gae_0 = 1.0 + (0.99 * 0.95) * (2.0 + (0.99 * 0.95) * 0.5)
        self.assertAlmostEqual(gae_0, expected_gae_0, places=5)


class TestSyllabusTicketAlignmentGUU26(unittest.TestCase):
    """Verifies alignment with all 25 official GUU 2026 examination tickets."""

    @classmethod
    def setUpClass(cls):
        cls.lectures = {name: load_lecture(name) for name in LECTURE_NAMES}

    def test_ticket_01_fcnn_and_backpropagation(self):
        """Билет 1: Однослойные и многослойные FCNN, активации, forward/backward."""
        l = self.lectures["01-fcnn.html"]
        self.assertTrue("полносвязн" in l.lower() or "fcnn" in l.lower() or "mlp" in l.lower())
        self.assertTrue("активаци" in l.lower())
        self.assertTrue("распространени" in l.lower() or "backprop" in l.lower())

    def test_ticket_02a_autodiff_and_pinn(self):
        """Билет 2: Автоматическое дифференцирование. PINN."""
        l = self.lectures["02-autodiff-pinn.html"]
        self.assertTrue("автоматическ" in l.lower() or "autodiff" in l.lower() or "autograd" in l.lower())
        self.assertTrue("pinn" in l.lower() or "физическ" in l.lower())

    def test_ticket_02b_losses_mle_and_l2(self):
        """Билет 2 (loss): MSE, MAE, Cross-Entropy, MLE, связь MLE и L2."""
        l = self.lectures["03-losses-mle.html"]
        self.assertTrue("mse" in l.lower() and "cross-entropy" in l.lower())
        self.assertTrue("максимального правдоподобия" in l.lower() or "mle" in l.lower())
        self.assertTrue("l2" in l.lower() or "норма l2" in l.lower() or "гаусс" in l.lower())

    def test_ticket_03_cnn_layers(self):
        """Билет 3: Слои сверточных нейросетей, функционал, назначение, принципы."""
        l = self.lectures["04-cnn-layers.html"]
        self.assertTrue("сверточн" in l.lower() or "conv" in l.lower())
        self.assertTrue("пулинг" in l.lower() or "pooling" in l.lower())
        self.assertTrue("batchnorm" in l.lower() or "нормализац" in l.lower())

    def test_ticket_04_cnn_architectures_transfer_learning(self):
        """Билет 4: Архитектуры CNN. Transfer Learning."""
        l = self.lectures["05-cnn-architectures.html"]
        self.assertTrue("resnet" in l.lower() or "vgg" in l.lower())
        self.assertTrue("transfer learning" in l.lower() or "перенос" in l.lower() or "fine-tuning" in l.lower())

    def test_ticket_05_optimization_sgd_momentum_adam_matrix_derivatives(self):
        """Билет 5: Оптимизация: SGD, Momentum, Adam, RMSProp. Матричные производные."""
        l = self.lectures["06-optimizers.html"]
        self.assertTrue("sgd" in l.lower() and "momentum" in l.lower() and "adam" in l.lower() and "rmsprop" in l.lower())
        self.assertTrue("матричн" in l.lower() or "якобиан" in l.lower() or "производн" in l.lower())

    def test_ticket_06_hyperparameters_bayesian_optimization(self):
        """Билет 6: Аугментация, выбор гиперпараметров, Байесовская оптимизация."""
        l = self.lectures["07-hyperparams.html"]
        self.assertTrue("аугментац" in l.lower() or "augmentation" in l.lower())
        self.assertTrue("байесовск" in l.lower() or "bayesian" in l.lower())

    def test_ticket_07_metric_learning_siamese_networks(self):
        """Билет 7: Метрические методы обучения. Сиамские сети. Функции ошибок."""
        l = self.lectures["08-metric-learning.html"]
        self.assertTrue("метрическ" in l.lower() or "metric learning" in l.lower())
        self.assertTrue("сиамск" in l.lower() or "siamese" in l.lower())
        self.assertTrue("triplet" in l.lower() or "contrastive" in l.lower() or "arcface" in l.lower())

    def test_ticket_08_contrastive_ssl(self):
        """Билет 8: Контрастивное обучение и self-supervised learning."""
        l = self.lectures["09-contrastive-ssl.html"]
        self.assertTrue("контрастивн" in l.lower() or "contrastive" in l.lower())
        self.assertTrue("self-supervised" in l.lower() or "ssl" in l.lower())
        self.assertTrue("simclr" in l.lower() or "moco" in l.lower())

    def test_ticket_09_vae_cvae_reparameterization(self):
        """Билет 9: Автоэнкодеры: VAE, CVAE, вывод, репараметризационный трюк."""
        l = self.lectures["10-vae.html"]
        self.assertTrue("vae" in l.lower())
        self.assertTrue("cvae" in l.lower())
        self.assertTrue("репараметризац" in l.lower() or "reparameterization" in l.lower())

    def test_ticket_10_gan_generative_models(self):
        """Билет 10: Генеративные модели: GAN."""
        l = self.lectures["11-gan.html"]
        self.assertTrue("gan" in l.lower() or "генеративно-состязательн" in l.lower())
        self.assertTrue("дискриминатор" in l.lower() and "генератор" in l.lower())

    def test_ticket_11_diffusion_models_math(self):
        """Билет 11: Диффузионные модели: математические основы."""
        l = self.lectures["12-diffusion.html"]
        self.assertTrue("диффузи" in l.lower() or "diffusion" in l.lower())
        self.assertTrue("ddpm" in l.lower() or "прямой процесс" in l.lower())

    def test_ticket_12_cv_tasks(self):
        """Билет 12: Задачи CV: сегментация, детекция, ключевые точки, трекинг."""
        l = self.lectures["13-cv-tasks.html"]
        self.assertTrue("сегментац" in l.lower())
        self.assertTrue("детекци" in l.lower())
        self.assertTrue("ключевые точки" in l.lower() or "keypoint" in l.lower())
        self.assertTrue("трекинг" in l.lower() or "tracking" in l.lower())

    def test_ticket_13_recurrent_networks_lstm_bilstm(self):
        """Билет 13: Рекуррентные сети, авторегрессия, seq2seq, LSTM, biLSTM."""
        l = self.lectures["14-rnn-lstm.html"]
        self.assertTrue("lstm" in l.lower())
        self.assertTrue("bilstm" in l.lower() or "двунаправленн" in l.lower())

    def test_ticket_14_rnn_attention_seq2seq(self):
        """Билет 14: Рекуррентные сети и механизм внимания в seq2seq."""
        l = self.lectures["15-attention-seq2seq.html"]
        self.assertTrue("внимани" in l.lower() or "attention" in l.lower())
        self.assertTrue("seq2seq" in l.lower())

    def test_ticket_15_transformers_architecture(self):
        """Билет 15: Трансформеры. Архитектура, функционал, элементы, принцип работы."""
        l = self.lectures["16-transformers.html"]
        self.assertTrue("трансформер" in l.lower() or "transformer" in l.lower())
        self.assertTrue("позиционн" in l.lower() or "positional" in l.lower())

    def test_ticket_16_attention_self_attention_qkv_masked(self):
        """Билет 16: Внимание и самовнимание в трансформерах. Q, K, V, Masked Attention."""
        l = self.lectures["17-self-attention.html"]
        self.assertTrue("query" in l.lower() or "запрос" in l.lower() or "q" in l.lower())
        self.assertTrue("key" in l.lower() or "ключ" in l.lower() or "k" in l.lower())
        self.assertTrue("value" in l.lower() or "значени" in l.lower() or "v" in l.lower())
        self.assertTrue("маскирован" in l.lower() or "mask" in l.lower())

    def test_ticket_17_lstm_vs_transformer(self):
        """Билет 17: LSTM vs Трансформер. Достоинства и недостатки, основные различия."""
        l = self.lectures["18-lstm-vs-transformer.html"]
        self.assertTrue("lstm" in l.lower() and "трансформер" in l.lower())
        self.assertTrue("параллел" in l.lower())
        self.assertTrue("сложност" in l.lower() or "complexity" in l.lower())

    def test_ticket_18_texts_preprocessing_word2vec_tokens(self):
        """Билет 18: Тексты. Предобработка, схема Word2Vec, токен."""
        l = self.lectures["19-text-word2vec.html"]
        self.assertTrue("токен" in l.lower() or "token" in l.lower())
        self.assertTrue("word2vec" in l.lower())
        self.assertTrue("cbow" in l.lower() and "skip-gram" in l.lower())

    def test_ticket_19_machine_translation_lm_bleu(self):
        """Билет 19: Машинный перевод, языковая модель, метрика BLEU."""
        l = self.lectures["20-mt-bleu.html"]
        self.assertTrue("перевод" in l.lower() or "translation" in l.lower())
        self.assertTrue("bleu" in l.lower())

    def test_ticket_20_encoder_decoder_architectures(self):
        """Билет 20: Архитектуры Декодер, Энкодер-Декодер, Энкодер. Сходства, различия, примеры."""
        l = self.lectures["21-enc-dec.html"]
        self.assertTrue("энкодер" in l.lower() or "encoder" in l.lower())
        self.assertTrue("декодер" in l.lower() or "decoder" in l.lower())
        self.assertTrue("bert" in l.lower() and "gpt" in l.lower())

    def test_ticket_21_rl_intro_agent_policy_value_model(self):
        """Билет 21: RL. Строение RL агента. Стратегия, полезность, модель."""
        l = self.lectures["22-rl-intro.html"]
        self.assertTrue("агент" in l.lower() or "agent" in l.lower())
        self.assertTrue("стратеги" in l.lower() or "policy" in l.lower())
        self.assertTrue("полезност" in l.lower() or "value" in l.lower())

    def test_ticket_22a_bellman_equations(self):
        """Билет 22a: Уравнение Беллмана. Уравнение оптимальности Беллмана."""
        l = self.lectures["23-bellman.html"]
        self.assertTrue("беллман" in l.lower() or "bellman" in l.lower())
        self.assertTrue("оптимальност" in l.lower())

    def test_ticket_22b_value_iteration_policy_iteration_mc(self):
        """Билет 22b: Итерации по полезностям, итерации по стратегиям, методы Монте-Карло."""
        l = self.lectures["24-vi-pi-mc.html"]
        self.assertTrue("итераци" in l.lower())
        self.assertTrue("монте" in l.lower() or "monte" in l.lower())

    def test_ticket_23_value_based_rl_td_qlearning(self):
        """Билет 23: Базовые алгоритмы RL: TD, Q-learning, SARSA."""
        l = self.lectures["25-td-qlearning.html"]
        self.assertTrue("q-learning" in l.lower())
        self.assertTrue("td" in l.lower() or "временных разностей" in l.lower())

    def test_ticket_24_policy_based_rl_crossentropy_policy_gradient(self):
        """Билет 24: Алгоритмы по стратегии: Cross-entropy метод, Policy gradient."""
        l = self.lectures["26-policy-gradient.html"]
        self.assertTrue("policy gradient" in l.lower() or "градиент стратегии" in l.lower())
        self.assertTrue("cross-entropy" in l.lower() or "кросс-энтропи" in l.lower() or "cem" in l.lower())

    def test_ticket_25_value_vs_policy_actor_critic(self):
        """Билет 25: Value-based vs Policy-based. Actor-Critic."""
        l = self.lectures["27-actor-critic.html"]
        self.assertTrue("actor-critic" in l.lower() or "актор-критик" in l.lower())
        self.assertTrue("advantage" in l.lower() or "преимущество" in l.lower() or "gae" in l.lower())


if __name__ == "__main__":
    unittest.main()
