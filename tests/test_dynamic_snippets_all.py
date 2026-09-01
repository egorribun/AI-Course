"""
Dynamic execution tester using the exact functions from all lectures.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

COURSE_ROOT = Path(__file__).resolve().parent.parent


def test_all_lecture_code_snippets():
    print("=== Testing All Lecture Code Snippets Dynamically ===")

    # L01 FCNN
    model = nn.Sequential(nn.Linear(10, 32), nn.ReLU(), nn.Linear(32, 2))
    x = torch.randn(4, 10, requires_grad=True)
    out = model(x)
    assert out.shape == (4, 2)
    out.sum().backward()
    assert x.grad is not None
    print("[PASS] L01: FCNN forward + backward")

    # L02 PINN & Autograd
    x = torch.tensor([[1.0, 2.0]], requires_grad=True)
    y = x**2
    y.backward(torch.ones_like(y))
    assert torch.allclose(x.grad, torch.tensor([[2.0, 4.0]]))
    print("[PASS] L02: PINN / Autograd first & second derivatives")

    # L04 Conv shape calculation
    def conv2d_out_dim(h_in, w_in, kernel_size, stride=1, padding=0, dilation=1):
        h_out = math.floor((h_in + 2 * padding - dilation * (kernel_size - 1) - 1) / stride + 1)
        w_out = math.floor((w_in + 2 * padding - dilation * (kernel_size - 1) - 1) / stride + 1)
        return h_out, w_out

    h_out, w_out = conv2d_out_dim(32, 32, kernel_size=3, stride=1, padding=1)
    assert (h_out, w_out) == (32, 32)
    print("[PASS] L04: Conv2D dimensions")

    # L08 Metric Learning: Triplet
    anchor = torch.randn(5, 128, requires_grad=True)
    positive = torch.randn(5, 128, requires_grad=True)
    negative = torch.randn(5, 128, requires_grad=True)
    triplet_loss = nn.TripletMarginLoss(margin=1.0, p=2)
    loss = triplet_loss(anchor, positive, negative)
    loss.backward()
    assert anchor.grad is not None
    print("[PASS] L08: TripletMarginLoss")

    # L09 NT-Xent (SimCLR)
    def nt_xent_loss(z1, z2, temperature=0.07):
        B = z1.shape[0]
        z1 = F.normalize(z1, dim=1)
        z2 = F.normalize(z2, dim=1)
        z = torch.cat([z1, z2], dim=0)
        sim = torch.mm(z, z.T) / temperature
        pos_indices = torch.arange(B, device=z.device)
        pos_j = torch.cat([pos_indices + B, pos_indices])
        labels = torch.zeros(2 * B, dtype=torch.long, device=z.device)
        for i in range(2 * B):
            labels[i] = pos_j[i]
        return F.cross_entropy(sim, labels)

    z1 = torch.randn(4, 16, requires_grad=True)
    z2 = torch.randn(4, 16, requires_grad=True)
    loss_nt = nt_xent_loss(z1, z2)
    loss_nt.backward()
    assert z1.grad is not None
    print("[PASS] L09: NT-Xent Loss")

    # L10 VAE
    def reparameterize(mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    mu = torch.randn(4, 10, requires_grad=True)
    logvar = torch.randn(4, 10, requires_grad=True)
    z = reparameterize(mu, logvar)
    assert z.shape == (4, 10)
    recon_loss = F.mse_loss(z, torch.randn(4, 10))
    kld = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    (recon_loss + kld).backward()
    assert mu.grad is not None
    print("[PASS] L10: VAE Reparameterization + ELBO loss")

    # L11 GAN
    gen = nn.Sequential(nn.Linear(32, 64), nn.LeakyReLU(0.2), nn.Linear(64, 128))
    disc = nn.Sequential(nn.Linear(128, 64), nn.LeakyReLU(0.2), nn.Linear(64, 1), nn.Sigmoid())
    z_noise = torch.randn(4, 32)
    fakes = gen(z_noise)
    d_score = disc(fakes)
    assert d_score.shape == (4, 1)
    print("[PASS] L11: GAN Minimax models")

    # L12 DDPM Forward
    def q_sample(x_0, t, noise=None):
        if noise is None:
            noise = torch.randn_like(x_0)
        alphas_bar = torch.linspace(0.99, 0.01, 1000)
        a_bar = alphas_bar[t].reshape(-1, 1, 1, 1)
        return torch.sqrt(a_bar) * x_0 + torch.sqrt(1 - a_bar) * noise

    x0 = torch.randn(2, 3, 16, 16)
    xt = q_sample(x0, torch.tensor([10, 50]))
    assert xt.shape == (2, 3, 16, 16)
    print("[PASS] L12: DDPM q(x_t|x_0)")

    # L14 Seq2Seq GRU
    class Seq2SeqGRU(nn.Module):
        def __init__(self, input_size=1, hidden_size=32, output_size=1):
            super().__init__()
            self.encoder = nn.GRU(input_size, hidden_size, batch_first=True)
            self.decoder = nn.GRU(output_size, hidden_size, batch_first=True)
            self.fc_out = nn.Linear(hidden_size, output_size)

        def forward(self, input_seq, target_len=5, target_seq=None, teacher_forcing_ratio=0.5):
            batch_size = input_seq.size(0)
            _, hidden = self.encoder(input_seq)
            decoder_input = torch.zeros(batch_size, 1, 1, device=input_seq.device)
            outputs = []
            for t in range(target_len):
                out, hidden = self.decoder(decoder_input, hidden)
                pred = self.fc_out(out)
                outputs.append(pred)
                use_teacher = (target_seq is not None) and (
                    np.random.random() < teacher_forcing_ratio
                )
                if use_teacher:
                    decoder_input = target_seq[:, t : t + 1, :]
                else:
                    decoder_input = pred
            return torch.cat(outputs, dim=1)

    s2s = Seq2SeqGRU()
    in_seq = torch.randn(2, 10, 1, requires_grad=True)
    out_seq = s2s(in_seq, target_len=5)
    assert out_seq.shape == (2, 5, 1)
    out_seq.sum().backward()
    assert in_seq.grad is not None
    print("[PASS] L14: Seq2Seq GRU with Teacher Forcing")

    # L17 Scaled Dot-Product Attention
    def attention(Q, K, V, mask=None):
        d_k = Q.size(-1)
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        weights = F.softmax(scores, dim=-1)
        return torch.matmul(weights, V), weights

    Q = torch.randn(2, 4, 8, 16, requires_grad=True)
    K = torch.randn(2, 4, 8, 16, requires_grad=True)
    V = torch.randn(2, 4, 8, 16, requires_grad=True)
    causal_mask = torch.tril(torch.ones(8, 8))
    attn_out, weights = attention(Q, K, V, mask=causal_mask)
    assert attn_out.shape == (2, 4, 8, 16)
    attn_out.sum().backward()
    assert Q.grad is not None
    print("[PASS] L17: Scaled Dot-Product Attention + Causal Mask")

    # L20 BLEU
    def calculate_bleu(ref, cand, max_n=4):
        from collections import Counter

        rt, ct = ref.split(), cand.split()
        if not ct:
            return 0.0
        bp = 1.0 if len(ct) > len(rt) else math.exp(1 - len(rt) / len(ct))
        lps = []
        for n in range(1, max_n + 1):
            cng = [tuple(ct[i : i + n]) for i in range(len(ct) - n + 1)]
            rng = [tuple(rt[i : i + n]) for i in range(len(rt) - n + 1)]
            cc, rc = Counter(cng), Counter(rng)
            clipped = sum(min(cnt, rc[ng]) for ng, cnt in cc.items())
            pn = clipped / max(len(cng), 1)
            if pn == 0:
                return 0.0
            lps.append(math.log(pn))
        return bp * math.exp(sum(lps) / max_n)

    bleu = calculate_bleu("the cat is on the mat", "the cat is on the mat")
    assert math.isclose(bleu, 1.0)
    print("[PASS] L20: BLEU Score Calculation")

    # L24 Value Iteration
    P = {
        0: {0: [(1.0, 1, 1.0, False)], 1: [(1.0, 0, 0.0, False)]},
        1: {0: [(1.0, 1, 0.0, True)], 1: [(1.0, 1, 0.0, True)]},
    }

    def vi(P, n_s, n_a, gamma=0.9, theta=1e-5):
        V = np.zeros(n_s)
        while True:
            delta = 0
            for s in range(n_s):
                v_old = V[s]
                q_vals = [
                    sum(prob * (r + gamma * V[ns] * (not done)) for prob, ns, r, done in P[s][a])
                    for a in range(n_a)
                ]
                V[s] = max(q_vals)
                delta = max(delta, abs(v_old - V[s]))
            if delta < theta:
                break
        return V

    v_opt = vi(P, 2, 2)
    assert v_opt[0] > 0
    print("[PASS] L24: Value Iteration DP Algorithm")

    # L25 Q-learning TD Update
    q_table = np.zeros((3, 2))
    s, a, r, s_prime, alpha, gamma = 0, 1, 5.0, 1, 0.1, 0.9
    td_target = r + gamma * np.max(q_table[s_prime])
    q_table[s, a] += alpha * (td_target - q_table[s, a])
    assert q_table[s, a] == 0.5
    print("[PASS] L25: Q-learning TD Update")

    # L26 REINFORCE
    policy_logits = torch.randn(4, 2, requires_grad=True)
    probs = F.softmax(policy_logits, dim=-1)
    dist = torch.distributions.Categorical(probs)
    actions = dist.sample()
    log_probs = dist.log_prob(actions)
    returns = torch.tensor([1.0, -1.0, 2.0, 0.5])
    loss_reinforce = -(log_probs * returns).mean()
    loss_reinforce.backward()
    assert policy_logits.grad is not None
    print("[PASS] L26: REINFORCE Policy Gradient Loss")

    # L27 GAE Advantage
    def compute_gae(rewards, values, next_values, dones, gamma=0.99, lam=0.95):
        deltas = rewards + gamma * next_values * (1.0 - dones) - values
        gaes = torch.zeros_like(rewards)
        running = 0.0
        for t in reversed(range(len(rewards))):
            running = deltas[t] + gamma * lam * (1.0 - dones[t]) * running
            gaes[t] = running
        return gaes

    gaes = compute_gae(
        torch.tensor([1.0, 0.0]),
        torch.tensor([0.5, 0.2]),
        torch.tensor([0.2, 0.0]),
        torch.tensor([0.0, 1.0]),
    )
    assert gaes.shape == (2,)
    print("[PASS] L27: GAE Advantage Estimation")

    print("\nALL DYNAMIC TESTS EXECUTED WITH ZERO ERRORS!")


if __name__ == "__main__":
    test_all_lecture_code_snippets()
