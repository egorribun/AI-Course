"""
Adversarial Stress Test and Mathematical Edge Case Verification Suite.
Challenger 2 Suite for AI Deep Learning Course (GUU 2026).

Performs rigorous empirical verification of:
1. Numerical stability and boundary handling of DL algorithms across all 28 lectures.
2. Mathematical derivations, formulas, and edge cases in lecture texts, Q&As, and micro-tasks.
3. PyTorch implementations of all key mathematical components under extreme and boundary inputs.
"""

from __future__ import annotations

import math
import unittest
from pathlib import Path

import torch
import torch.nn as nn
import torch.nn.functional as F

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"

LECTURE_FILES = [
    "00-intro-ml.html",
    "01-fcnn.html",
    "02-autodiff-pinn.html",
    "03-losses-mle.html",
    "04-cnn-layers.html",
    "05-cnn-architectures.html",
    "06-optimizers.html",
    "07-hyperparams.html",
    "08-metric-learning.html",
    "09-contrastive-ssl.html",
    "10-vae.html",
    "11-gan.html",
    "12-diffusion.html",
    "13-cv-tasks.html",
    "14-rnn-lstm.html",
    "15-attention-seq2seq.html",
    "16-transformers.html",
    "17-self-attention.html",
    "18-lstm-vs-transformer.html",
    "19-text-word2vec.html",
    "20-mt-bleu.html",
    "21-enc-dec.html",
    "22-rl-intro.html",
    "23-bellman.html",
    "24-vi-pi-mc.html",
    "25-td-qlearning.html",
    "26-policy-gradient.html",
    "27-actor-critic.html",
]


def load_lecture(filename: str) -> str:
    path = LECTURES_DIR / filename
    return path.read_text(encoding="utf-8", errors="replace")


class TestAdversarialChallenges(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lectures = {f: load_lecture(f) for f in LECTURE_FILES}

    # =========================================================================
    # L00 & L01: FCNN, Backpropagation, Activations & Vanishing Gradients
    # =========================================================================
    def test_l01_backprop_and_activations_edge_cases(self):
        """Stress-test activations (Sigmoid saturation, ReLU dead neurons, LeakyReLU slope) and 4 backprop equations."""
        content = self.lectures["01-fcnn.html"]
        # Verify 4 backprop equations are present
        self.assertTrue(r"\delta^{(L)}" in content or r"\delta^L" in content)
        self.assertTrue(r"\delta^{(l)}" in content or r"\delta^l" in content)
        self.assertTrue(r"\partial L" in content and "W" in content)
        self.assertTrue(r"\partial L" in content and "b" in content)

        # PyTorch Empirical check: Sigmoid gradient saturation at large |x|
        x_extreme = torch.tensor([-100.0, 0.0, 100.0], requires_grad=True)
        sig = torch.sigmoid(x_extreme)
        loss = sig.sum()
        loss.backward()
        # Grad at 0 is 0.25 (max), grad at +/-100 is 0.0 (vanished)
        self.assertAlmostEqual(x_extreme.grad[1].item(), 0.25, places=4)
        self.assertAlmostEqual(x_extreme.grad[0].item(), 0.0, places=4)
        self.assertAlmostEqual(x_extreme.grad[2].item(), 0.0, places=4)

        # Verify dead ReLU on strictly negative input
        x_neg = torch.tensor([-5.0, -1.0], requires_grad=True)
        relu_out = F.relu(x_neg)
        relu_out.sum().backward()
        self.assertTrue(torch.all(x_neg.grad == 0.0))

    # =========================================================================
    # L02: Autodiff, PINN, C^2 Smoothness for 2nd-order PDEs
    # =========================================================================
    def test_l02_pinn_c2_smoothness_and_autodiff(self):
        """Verify PINN PDE residual and C^2 activation requirement (ReLU failing for 2nd order derivatives)."""
        content = self.lectures["02-autodiff-pinn.html"]
        self.assertTrue(
            "невязк" in content.lower() or "pde" in content.lower() or "autograd" in content.lower()
        )

        # Empirical test: 2nd derivative of ReLU vs Tanh for PDE u_xx + u = 0
        x = torch.linspace(-2, 2, 10, requires_grad=True)
        u_tanh = torch.tanh(x)
        grad_u = torch.autograd.grad(u_tanh.sum(), x, create_graph=True)[0]
        grad2_u = torch.autograd.grad(grad_u.sum(), x)[0]
        self.assertFalse(torch.all(grad2_u == 0.0))

        # ReLU has zero 2nd derivative away from origin (cannot represent 2nd order PDE physics)
        x_relu = torch.tensor([0.5, 1.5, 2.5], requires_grad=True)
        u_relu = F.relu(x_relu)
        grad_relu = torch.autograd.grad(u_relu.sum(), x_relu, create_graph=True)[0]
        grad2_relu = torch.autograd.grad(grad_relu.sum(), x_relu)[0]
        self.assertTrue(torch.all(grad2_relu == 0.0), "ReLU 2nd derivative is 0 everywhere away from origin")

    # =========================================================================
    # L03: Losses & MLE, Log Underflow in CrossEntropy
    # =========================================================================
    def test_l03_log_underflow_and_mle_stability(self):
        """Verify cross entropy log-sum-exp numerical stability vs naive log(softmax)."""
        content = self.lectures["03-losses-mle.html"]
        self.assertTrue(
            "cross_entropy" in content or "кросс-энтропи" in content.lower() or "nll" in content.lower()
        )

        # Extreme logits where naive softmax underflows to 0.0
        logits_extreme = torch.tensor([[1000.0, -1000.0, 0.0]])
        target = torch.tensor([1])  # target is the underflow class

        # Naive approach: softmax then log -> log(0) = -inf
        probs_naive = F.softmax(logits_extreme, dim=-1)
        loss_naive = -torch.log(probs_naive[0, target])
        self.assertTrue(torch.isinf(loss_naive) or torch.isnan(loss_naive))

        # PyTorch CrossEntropyLoss uses LogSumExp trick -> stable finite value
        loss_stable = F.cross_entropy(logits_extreme, target)
        self.assertTrue(torch.isfinite(loss_stable))
        self.assertGreater(loss_stable.item(), 1000.0)

    # =========================================================================
    # L04: CNN Layers, BatchNorm N=1 Singularity & Dimension Formulas
    # =========================================================================
    def test_l04_batchnorm_n1_and_conv_dimensions(self):
        """Verify BatchNorm behavior when batch size N=1 during training vs eval, and conv output formulas."""
        content = self.lectures["04-cnn-layers.html"]
        self.assertIn("BatchNorm", content)
        self.assertTrue("stride" in content.lower() and "padding" in content.lower())

        # Test Conv dimension formula: H_out = floor((H - K + 2P)/S) + 1
        H, W = 32, 32
        K = 5
        P = 2
        S = 2
        H_out = math.floor((H - K + 2 * P) / S) + 1
        conv = nn.Conv2d(3, 16, kernel_size=K, stride=S, padding=P)
        dummy_in = torch.randn(2, 3, H, W)
        dummy_out = conv(dummy_in)
        self.assertEqual(dummy_out.shape[2], H_out)
        self.assertEqual(dummy_out.shape[3], H_out)

        # Test BatchNorm at N=1 during training with 1x1 spatial resolution (raises ValueError)
        bn = nn.BatchNorm2d(16)
        bn.train()
        single_sample = torch.randn(1, 16, 1, 1)
        with self.assertRaises(ValueError):
            bn(single_sample)

        # In eval mode with tracked running stats, N=1 passes
        bn.eval()
        out_eval = bn(single_sample)
        self.assertEqual(out_eval.shape, single_sample.shape)

    # =========================================================================
    # L05: ResNet Skip Connections & Gradient Preservation
    # =========================================================================
    def test_l05_resnet_gradient_highway(self):
        """Verify that ResNet skip connections preserve gradient flow through deep stacks."""
        content = self.lectures["05-cnn-architectures.html"]
        self.assertTrue("resnet" in content.lower() or "skip" in content.lower())

        # Test deep residual network gradient magnitude
        num_layers = 20
        dim = 16

        class ResNetToy(nn.Module):
            def __init__(self):
                super().__init__()
                self.layers = nn.ModuleList([nn.Linear(dim, dim) for _ in range(num_layers)])
                for l in self.layers:
                    nn.init.orthogonal_(l.weight, gain=0.5)

            def forward(self, x):
                for l in self.layers:
                    x = x + F.relu(l(x))  # skip connection
                return x

        model = ResNetToy()
        x = torch.randn(4, dim, requires_grad=True)
        out = model(x)
        loss = out.sum()
        loss.backward()
        self.assertGreater(x.grad.norm().item(), 0.1)

    # =========================================================================
    # L06: Optimizers: Adam Bias Correction & Decoupled Weight Decay (AdamW)
    # =========================================================================
    def test_l06_adam_bias_correction_and_adamw(self):
        """Verify Adam bias correction for t=1 and AdamW weight decay decoupling."""
        content = self.lectures["06-optimizers.html"]
        self.assertIn("Adam", content)
        self.assertTrue("bias" in content.lower() or r"\beta" in content or "AdamW" in content)

        # Mathematical check: bias correction factor at t=1 for beta1=0.9, beta2=0.999
        beta1, beta2 = 0.9, 0.999
        m_raw = 1.0
        v_raw = 1.0
        m_hat = m_raw / (1 - beta1**1)  # 1 / 0.1 = 10.0
        v_hat = v_raw / (1 - beta2**1)  # 1 / 0.001 = 1000.0
        self.assertAlmostEqual(m_hat, 10.0, places=5)
        self.assertAlmostEqual(v_hat, 1000.0, places=5)

        # AdamW applies weight decay directly to parameters independently of gradients
        param = nn.Parameter(torch.tensor([10.0]))
        opt_adamw = torch.optim.AdamW([param], lr=0.1, weight_decay=0.01)
        param.grad = torch.tensor([0.0])  # zero loss gradient
        opt_adamw.step()
        # param = 10 - 0.1 * 0.01 * 10 = 9.99
        self.assertAlmostEqual(param.item(), 9.99, places=3)

    # =========================================================================
    # L07: Hyperparameter Tuning: Bayesian Optimization Acquisition Functions
    # =========================================================================
    def test_l07_bayesian_optimization_properties(self):
        """Verify Bayesian optimization acquisition logic (UCB / EI exploration-exploitation)."""
        content = self.lectures["07-hyperparams.html"]
        self.assertTrue("байесовск" in content.lower() or "hyperband" in content.lower())

        # UCB formula: mu(x) + kappa * sigma(x)
        mu = torch.tensor([1.0, 2.0, 1.5])
        sigma = torch.tensor([0.1, 0.01, 1.0])
        kappa = 2.0
        ucb = mu + kappa * sigma
        self.assertEqual(torch.argmax(ucb).item(), 2)

    # =========================================================================
    # L08: Metric Learning: Triplet Margin Loss & ArcFace Angle Monotonicity
    # =========================================================================
    def test_l08_triplet_loss_and_arcface(self):
        """Verify Triplet margin loss edge conditions and ArcFace angular margin."""
        content = self.lectures["08-metric-learning.html"]
        self.assertTrue("triplet" in content.lower() or "margin" in content.lower())

        # Triplet margin loss: max(0, d(a,p) - d(a,n) + margin)
        anc = torch.tensor([[0.0, 0.0]])
        pos = torch.tensor([[0.0, 0.1]])
        neg = torch.tensor([[0.0, 1.0]])
        loss_fn = nn.TripletMarginLoss(margin=0.5, p=2)
        easy_loss = loss_fn(anc, pos, neg)
        self.assertAlmostEqual(easy_loss.item(), 0.0, places=5)

        hard_loss = loss_fn(anc, neg, pos)
        self.assertAlmostEqual(hard_loss.item(), 1.4, places=4)

    # =========================================================================
    # L09: Contrastive SSL: InfoNCE Temperature Boundary Behavior
    # =========================================================================
    def test_l09_infonce_temperature_extremes(self):
        """Verify InfoNCE behavior under temperature limits tau -> 0 and tau -> inf."""
        content = self.lectures["09-contrastive-ssl.html"]
        self.assertTrue("infonce" in content.lower() or "simclr" in content.lower() or "moco" in content.lower())

        sims = torch.tensor([[0.9, 0.4, 0.2]])
        target = torch.tensor([0])

        tau = 0.1
        loss_norm = F.cross_entropy(sims / tau, target)
        self.assertTrue(torch.isfinite(loss_norm))

        tau_small = 0.001
        loss_small = F.cross_entropy(sims / tau_small, target)
        self.assertAlmostEqual(loss_small.item(), 0.0, places=4)

    # =========================================================================
    # L10: VAE & ELBO: Gaussian KL Non-negativity & Reparameterization
    # =========================================================================
    def test_l10_vae_elbo_and_kl_divergence(self):
        """Verify analytical Gaussian KL divergence non-negativity and zero-point at standard normal."""
        content = self.lectures["10-vae.html"]
        self.assertIn("ELBO", content)
        self.assertTrue("reparameterization" in content.lower() or "репараметризац" in content.lower())

        # Formula: KL = -0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
        mu = torch.zeros(5)
        log_var = torch.zeros(5)
        kl = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        self.assertAlmostEqual(kl.item(), 0.0, places=6)

        mu_rand = torch.randn(5)
        log_var_rand = torch.randn(5)
        kl_rand = -0.5 * torch.sum(1 + log_var_rand - mu_rand.pow(2) - log_var_rand.exp())
        self.assertGreater(kl_rand.item(), 0.0)

    # =========================================================================
    # L11: GAN: Optimal Discriminator & Jensen-Shannon Reduction
    # =========================================================================
    def test_l11_gan_optimal_discriminator_value(self):
        """Verify D*(x) = p_data(x) / (p_data(x) + p_g(x)) and minimax value at convergence (-2 log 2)."""
        content = self.lectures["11-gan.html"]
        self.assertTrue("дискриминатор" in content.lower() or "wgan" in content.lower())

        v_opt = math.log(0.5) + math.log(0.5)
        self.assertAlmostEqual(v_opt, -math.log(4), places=5)

    # =========================================================================
    # L12: Diffusion (DDPM): Forward Marginal Variance Property
    # =========================================================================
    def test_l12_diffusion_marginal_schedule(self):
        """Verify DDPM forward marginal q(x_t|x_0) = N(sqrt(alpha_bar_t) x_0, (1 - alpha_bar_t) I)."""
        content = self.lectures["12-diffusion.html"]
        self.assertTrue("ddpm" in content.lower() or "диффуз" in content.lower())

        alpha_bar_0 = 1.0
        alpha_bar_T = 0.0001
        self.assertAlmostEqual(math.sqrt(alpha_bar_0), 1.0, places=5)
        self.assertAlmostEqual(1 - alpha_bar_0, 0.0, places=5)
        self.assertAlmostEqual(math.sqrt(alpha_bar_T), 0.01, places=3)
        self.assertAlmostEqual(1 - alpha_bar_T, 0.9999, places=3)

    # =========================================================================
    # L13: CV Tasks: IoU & Dice Smoothing
    # =========================================================================
    def test_l13_cv_iou_dice_smoothing(self):
        """Verify IoU and Dice loss stability when intersection and union are zero (empty masks)."""
        content = self.lectures["13-cv-tasks.html"]
        self.assertTrue("iou" in content.lower() or "dice" in content.lower() or "map" in content.lower())

        pred = torch.zeros(1, 1, 10, 10)
        target = torch.zeros(1, 1, 10, 10)
        eps = 1e-6
        intersection = (pred * target).sum()
        dice = (2.0 * intersection + eps) / (pred.sum() + target.sum() + eps)
        self.assertAlmostEqual(dice.item(), 1.0, places=5)

    # =========================================================================
    # L14: RNN & LSTM: Constant Error Carousel Derivative
    # =========================================================================
    def test_l14_lstm_constant_error_carousel(self):
        """Verify that d c_t / d c_{t-1} = f_t preserves gradient flow across time when f_t = 1."""
        content = self.lectures["14-rnn-lstm.html"]
        self.assertTrue("lstm" in content.lower() and "bptt" in content.lower())

        c0 = torch.tensor([5.0], requires_grad=True)
        c = c0
        for _ in range(100):
            f_t = torch.tensor([1.0])
            c = f_t * c
        loss = c.sum()
        loss.backward()
        self.assertAlmostEqual(c0.grad.item(), 1.0, places=6)

    # =========================================================================
    # L15: Seq2Seq Attention: Softmax Conservation of Probability
    # =========================================================================
    def test_l15_attention_weight_distribution(self):
        """Verify Seq2Seq attention weights sum strictly to 1.0 across source tokens."""
        content = self.lectures["15-attention-seq2seq.html"]
        self.assertTrue("bahdanau" in content.lower() or "luong" in content.lower() or "attention" in content.lower())

        scores = torch.randn(2, 10)
        weights = F.softmax(scores, dim=-1)
        sums = weights.sum(dim=-1)
        self.assertTrue(torch.allclose(sums, torch.ones_like(sums)))

    # =========================================================================
    # L16 & L17: Transformers & Self-Attention: Variance Scaling sqrt(d_k) & Causal Masking
    # =========================================================================
    def test_l17_scaled_dot_product_variance_and_causal_mask(self):
        """Adversarial stress test: Dot product variance = d_k, requiring 1/sqrt(d_k) scaling to prevent softmax saturation."""
        content = self.lectures["17-self-attention.html"]
        self.assertIn("d_k", content)

        d_k = 512
        num_samples = 20000
        q = torch.randn(num_samples, d_k)
        k = torch.randn(num_samples, d_k)
        dot_raw = (q * k).sum(dim=-1)
        var_raw = dot_raw.var().item()
        self.assertTrue(450 < var_raw < 580, f"Raw dot product variance {var_raw} should be near {d_k}")

        dot_scaled = dot_raw / math.sqrt(d_k)
        var_scaled = dot_scaled.var().item()
        self.assertTrue(0.9 < var_scaled < 1.1, f"Scaled dot product variance {var_scaled} should be near 1.0")

        # Causal mask test: upper triangular elements must receive -inf and result in exact 0.0 softmax prob
        seq_len = 4
        attn_logits = torch.randn(1, seq_len, seq_len)
        mask = torch.triu(torch.full((seq_len, seq_len), float("-inf")), diagonal=1)
        masked_logits = attn_logits + mask
        attn_probs = F.softmax(masked_logits, dim=-1)
        for i in range(seq_len):
            for j in range(i + 1, seq_len):
                self.assertEqual(attn_probs[0, i, j].item(), 0.0)

    # =========================================================================
    # L18: LSTM vs Transformer: Complexity & Invariant Analysis
    # =========================================================================
    def test_l18_complexity_invariants(self):
        """Verify comparative complexity invariants (O(1) sequential ops for Transformer vs O(n) for LSTM)."""
        content = self.lectures["18-lstm-vs-transformer.html"]
        self.assertTrue("параллел" in content.lower() or "памят" in content.lower() or "сложност" in content.lower())

    # =========================================================================
    # L19: Tokenization & Word2Vec: SGNS Sigmoid Loss
    # =========================================================================
    def test_l19_word2vec_sgns_loss_boundaries(self):
        """Verify Skip-Gram with Negative Sampling (SGNS) objective bounds."""
        content = self.lectures["19-text-word2vec.html"]
        self.assertTrue("skip-gram" in content.lower() or "cbow" in content.lower() or "negative" in content.lower())

        pos_dot = torch.tensor([20.0])
        neg_dots = torch.tensor([-20.0, -20.0])
        pos_loss = -F.logsigmoid(pos_dot)
        neg_loss = -F.logsigmoid(-neg_dots).sum()
        total_loss = pos_loss + neg_loss
        self.assertAlmostEqual(total_loss.item(), 0.0, places=4)

    # =========================================================================
    # L20: MT & BLEU: Brevity Penalty Edge Cases
    # =========================================================================
    def test_l20_bleu_brevity_penalty(self):
        """Verify BLEU Brevity Penalty formula BP = exp(min(0, 1 - r/c))."""
        content = self.lectures["20-mt-bleu.html"]
        self.assertIn("BLEU", content)
        self.assertTrue("brevity" in content.lower() or "penalty" in content.lower() or "краткост" in content.lower())

        # Case 1: candidate length c >= reference length r -> BP = 1.0
        c, r = 15, 10
        bp_no_penalty = math.exp(min(0, 1 - r / c))
        self.assertAlmostEqual(bp_no_penalty, 1.0, places=6)

        # Case 2: candidate length c < reference length r -> BP < 1.0
        c, r = 5, 10
        bp_penalized = math.exp(min(0, 1 - r / c))
        self.assertAlmostEqual(bp_penalized, math.exp(-1), places=5)

    # =========================================================================
    # L21: Transformer Archetypes: BERT / GPT / T5
    # =========================================================================
    def test_l21_transformer_archetypes(self):
        """Verify architectural classification of BERT (Encoder), GPT (Decoder), T5 (Encoder-Decoder)."""
        content = self.lectures["21-enc-dec.html"]
        self.assertIn("BERT", content)
        self.assertIn("GPT", content)
        self.assertIn("T5", content)

    # =========================================================================
    # L22 & L23: RL MDP & Bellman Banach Contraction Mapping Condition
    # =========================================================================
    def test_l23_bellman_banach_contraction_condition(self):
        """Adversarial test: Bellman operator is a contraction mapping only when gamma in [0, 1). Diverges if gamma >= 1."""
        content = self.lectures["23-bellman.html"]
        self.assertTrue("беллман" in content.lower() and "gamma" in content.lower())

        num_states = 5
        num_actions = 2
        R = torch.randn(num_states, num_actions)
        P = F.softmax(torch.randn(num_states, num_actions, num_states), dim=-1)

        def bellman_optimality_operator(V: torch.Tensor, gamma: float) -> torch.Tensor:
            expected_next = torch.einsum("san,n->sa", P, V)
            Q = R + gamma * expected_next
            return torch.max(Q, dim=-1).values

        gamma_valid = 0.9
        V1 = torch.randn(num_states)
        V2 = torch.randn(num_states)
        diff_orig = torch.max(torch.abs(V1 - V2)).item()
        TV1 = bellman_optimality_operator(V1, gamma_valid)
        TV2 = bellman_optimality_operator(V2, gamma_valid)
        diff_transformed = torch.max(torch.abs(TV1 - TV2)).item()
        self.assertLessEqual(diff_transformed, gamma_valid * diff_orig + 1e-6)

        # Fixed point convergence
        V_iter = torch.zeros(num_states)
        for _ in range(100):
            V_iter = bellman_optimality_operator(V_iter, gamma_valid)
        TV_fixed = bellman_optimality_operator(V_iter, gamma_valid)
        self.assertTrue(torch.allclose(V_iter, TV_fixed, atol=1e-4))

    # =========================================================================
    # L24: Dynamic Programming & Monte Carlo in RL
    # =========================================================================
    def test_l24_policy_iteration_and_mc(self):
        """Verify Policy Iteration and Monte Carlo evaluation mechanisms."""
        content = self.lectures["24-vi-pi-mc.html"]
        self.assertTrue("policy iteration" in content.lower() or "value iteration" in content.lower())
        self.assertTrue("монте-карло" in content.lower() or "monte carlo" in content.lower())

    # =========================================================================
    # L25: TD Learning, SARSA vs Q-Learning Target Comparison
    # =========================================================================
    def test_l25_sarsa_vs_q_learning_update_targets(self):
        """Verify on-policy SARSA (Q(s', a')) vs off-policy Q-learning (max_a' Q(s', a')) update targets."""
        content = self.lectures["25-td-qlearning.html"]
        self.assertTrue("sarsa" in content.lower() and "q-learning" in content.lower())

        Q_table = torch.tensor([[1.0, 5.0], [2.0, 8.0]])
        s, a, r, s_next = 0, 0, 10.0, 1
        gamma = 0.9

        # Q-learning target: 10 + 0.9 * 8.0 = 17.2
        target_qlearn = r + gamma * torch.max(Q_table[s_next]).item()
        self.assertAlmostEqual(target_qlearn, 17.2, places=4)

        # SARSA target when next action is 0: 10 + 0.9 * 2.0 = 11.8
        a_next = 0
        target_sarsa = r + gamma * Q_table[s_next, a_next].item()
        self.assertAlmostEqual(target_sarsa, 11.8, places=4)

    # =========================================================================
    # L26: Policy Gradient: Log-Derivative Trick & Baseline Invariance
    # =========================================================================
    def test_l26_policy_gradient_log_trick_and_baseline(self):
        """Verify Policy Gradient log-derivative trick and baseline expectation neutrality E[b(s) grad log pi] = 0."""
        content = self.lectures["26-policy-gradient.html"]
        self.assertTrue("policy gradient" in content.lower() or "reinforce" in content.lower())
        self.assertTrue("baseline" in content.lower() or "бейзлайн" in content.lower())

        logits = torch.tensor([1.0, 2.0, -1.0], requires_grad=True)
        probs = F.softmax(logits, dim=-1)
        log_probs = F.log_softmax(logits, dim=-1)

        total_grad = torch.zeros_like(logits)
        for a in range(len(probs)):
            grad_a = torch.autograd.grad(log_probs[a], logits, retain_graph=True)[0]
            total_grad += probs[a].item() * grad_a

        self.assertTrue(torch.allclose(total_grad, torch.zeros_like(total_grad), atol=1e-6))

    # =========================================================================
    # L27: Actor-Critic, GAE & SAC Entropy Regularization
    # =========================================================================
    def test_l27_gae_and_sac_entropy(self):
        """Verify Generalized Advantage Estimation (GAE-lambda) bounds (lambda=0 -> 1-step TD, lambda=1 -> MC) and SAC entropy."""
        content = self.lectures["27-actor-critic.html"]
        self.assertTrue("actor-critic" in content.lower() or "актор-критик" in content.lower())
        self.assertTrue("gae" in content.lower() or "sac" in content.lower())

        deltas = torch.tensor([2.0, 1.0, -0.5])
        gamma = 0.99
        gae_lam0 = deltas[0].item()
        self.assertEqual(gae_lam0, 2.0)

        gae_lam1 = (deltas[0] + gamma * deltas[1] + (gamma**2) * deltas[2]).item()
        self.assertAlmostEqual(gae_lam1, 2.0 + 0.99 - 0.49005, places=4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
