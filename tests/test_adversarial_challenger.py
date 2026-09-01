import re
import math
import unittest
from pathlib import Path
from html.parser import HTMLParser
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
INDEX_FILE = COURSE_ROOT / "index.html"

EXPECTED_LECTURES = [
    f"{i:02d}-" + name
    for i, name in enumerate(
        [
            "intro-ml.html",
            "fcnn.html",
            "autodiff-pinn.html",
            "losses-mle.html",
            "cnn-layers.html",
            "cnn-architectures.html",
            "optimizers.html",
            "hyperparams.html",
            "metric-learning.html",
            "contrastive-ssl.html",
            "vae.html",
            "gan.html",
            "diffusion.html",
            "cv-tasks.html",
            "rnn-lstm.html",
            "attention-seq2seq.html",
            "transformers.html",
            "self-attention.html",
            "lstm-vs-transformer.html",
            "text-word2vec.html",
            "mt-bleu.html",
            "enc-dec.html",
            "rl-intro.html",
            "bellman.html",
            "vi-pi-mc.html",
            "td-qlearning.html",
            "policy-gradient.html",
            "actor-critic.html",
        ]
    )
]


class SimpleHTMLDocParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []  # list of (href, text)
        self.ids = set()
        self.qa_count = 0
        self.task_count = 0
        self.total_details_count = 0
        self.cheat_count = 0
        self.pills = []
        self._current_tag = None
        self._current_data = []
        self._in_pill = False

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        if "id" in attr_dict:
            self.ids.add(attr_dict["id"])

        classes = attr_dict.get("class", "").split()
        if tag == "details":
            self.total_details_count += 1
            if "qa" in classes:
                self.qa_count += 1
        elif tag == "div" and "task" in classes:
            self.task_count += 1
        elif tag == "div" and "cheat" in classes:
            self.cheat_count += 1

        if tag == "span" and "pill" in classes:
            self._in_pill = True
            self._current_data = []

        if tag == "a" and "href" in attr_dict:
            self.links.append((attr_dict["href"], ""))

    def handle_endtag(self, tag):
        if tag == "span" and self._in_pill:
            self.pills.append("".join(self._current_data).strip())
            self._in_pill = False
            self._current_data = []

    def handle_data(self, data):
        if self._in_pill:
            self._current_data.append(data)


class AdversarialHyperlinkTests(unittest.TestCase):
    """Stress tests internal/external navigation links, anchor targets, and sequential chain."""

    def test_index_card_links(self):
        content = INDEX_FILE.read_text(encoding="utf-8")
        parser = SimpleHTMLDocParser()
        parser.feed(content)
        lecture_links = [href for href, _ in parser.links if href.startswith("lectures/")]
        unique_lecture_links = set(lecture_links)

        self.assertEqual(
            len(unique_lecture_links),
            28,
            f"Expected 28 unique lecture links in index.html, found {len(unique_lecture_links)}",
        )
        for expected in EXPECTED_LECTURES:
            expected_href = f"lectures/{expected}"
            self.assertIn(
                expected_href,
                unique_lecture_links,
                f"Missing link to {expected_href} in index.html",
            )

    def test_lecture_navigation_chain(self):
        for idx, filename in enumerate(EXPECTED_LECTURES):
            path = LECTURES_DIR / filename
            self.assertTrue(path.exists(), f"File {filename} does not exist")
            content = path.read_text(encoding="utf-8")
            parser = SimpleHTMLDocParser()
            parser.feed(content)

            # Check backlink to index
            hrefs = [href for href, _ in parser.links]
            self.assertTrue(
                any("../index.html" in link or "index.html" in link for link in hrefs),
                f"{filename}: Missing backlink to index.html",
            )

            # If not first, should link to prev
            if idx > 0:
                prev_file = EXPECTED_LECTURES[idx - 1]
                self.assertTrue(
                    any(prev_file in h for h in hrefs),
                    f"{filename}: Missing link to previous lecture {prev_file}",
                )

            # If not last, should link to next
            if idx < 27:
                next_file = EXPECTED_LECTURES[idx + 1]
                self.assertTrue(
                    any(next_file in h for h in hrefs),
                    f"{filename}: Missing link to next lecture {next_file}",
                )

    def test_internal_anchors_exist(self):
        """Verify every href="#foo" points to an element with id="foo" in that file."""
        for filename in EXPECTED_LECTURES:
            path = LECTURES_DIR / filename
            content = path.read_text(encoding="utf-8")
            parser = SimpleHTMLDocParser()
            parser.feed(content)

            for href, _ in parser.links:
                if href.startswith("#") and len(href) > 1:
                    target_id = href[1:]
                    self.assertIn(
                        target_id,
                        parser.ids,
                        f"{filename}: Broken anchor link href='{href}', id not found in page",
                    )


class AdversarialDOMAndPillTests(unittest.TestCase):
    """Stress tests header pill badges against parsed DOM counts for QA and Micro-tasks."""

    def test_pill_counters_match_dom(self):
        for filename in EXPECTED_LECTURES:
            path = LECTURES_DIR / filename
            content = path.read_text(encoding="utf-8")
            parser = SimpleHTMLDocParser()
            parser.feed(content)

            self.assertGreaterEqual(
                parser.qa_count, 10, f"{filename}: QA count {parser.qa_count} < 10"
            )
            self.assertGreaterEqual(
                parser.task_count, 6, f"{filename}: Task count {parser.task_count} < 6"
            )

            # Each task contains a solution details block -> total details = qa_count + task_count
            task_solutions_count = parser.total_details_count - parser.qa_count
            self.assertEqual(
                parser.task_count,
                task_solutions_count,
                f"{filename}: Tasks count {parser.task_count} != Solution details count {task_solutions_count}",
            )
            self.assertGreaterEqual(
                parser.cheat_count, 1, f"{filename}: Missing cheat sheet <div class='cheat'>"
            )

            # Check header pills
            pill_texts = " ".join(parser.pills)

            # Extract QA number from pills (e.g. "10 вопросов" or "10 QA" or "10 Q&A")
            qa_match = re.search(r"(\d+)\s*(?:вопрос|QA|Q&A|вопросов)", pill_texts, re.IGNORECASE)
            if qa_match:
                pill_qa_count = int(qa_match.group(1))
                self.assertEqual(
                    pill_qa_count,
                    parser.qa_count,
                    f"{filename}: Pill QA count {pill_qa_count} != actual DOM QA count {parser.qa_count}",
                )

            # Extract task number from pills (e.g. "6 задач" or "6 микро-задач")
            task_match = re.search(
                r"(\d+)\s*(?:задач|микро-задач|задачи|tasks)", pill_texts, re.IGNORECASE
            )
            if task_match:
                pill_task_count = int(task_match.group(1))
                self.assertEqual(
                    pill_task_count,
                    parser.task_count,
                    f"{filename}: Pill task count {pill_task_count} != actual DOM task count {parser.task_count}",
                )


class AdversarialMathJaxStressTests(unittest.TestCase):
    """Stress tests MathJax formulas for delimiter balancing, braces, and standard commands."""

    def test_math_delimiters_and_braces(self):
        for filename in EXPECTED_LECTURES:
            path = LECTURES_DIR / filename
            content = path.read_text(encoding="utf-8")

            # Remove pre / code blocks to avoid false positives with shell/code comments
            clean_content = re.sub(r"<pre[^>]*>.*?</pre>", "", content, flags=re.DOTALL)
            clean_content = re.sub(r"<code[^>]*>.*?</code>", "", clean_content, flags=re.DOTALL)

            # Check display math $$...$$
            display_math = re.findall(r"\$\$(.*?)\$\$", clean_content, flags=re.DOTALL)
            for dm in display_math:
                # Check brace balancing in display math
                open_b = dm.count("{") - dm.count(r"\{")
                close_b = dm.count("}") - dm.count(r"\}")
                self.assertEqual(
                    open_b,
                    close_b,
                    f"{filename}: Unbalanced braces in display math: $${dm[:40]}...$$",
                )

            # Check inline math $...$
            without_dm = re.sub(r"\$\$.*?\$\$", "", clean_content, flags=re.DOTALL)
            inline_math = re.findall(r"\$([^\$\n]+?)\$", without_dm)
            for im in inline_math:
                open_b = im.count("{") - im.count(r"\{")
                close_b = im.count("}") - im.count(r"\}")
                self.assertEqual(
                    open_b, close_b, f"{filename}: Unbalanced braces in inline math: ${im}$"
                )


class AdversarialAlgorithmicStressTests(unittest.TestCase):
    """Empirically stress-tests deep learning algorithms, mathematical properties, and PyTorch tensors."""

    def test_l01_fcnn_random_tensors(self):
        """L01: FCNN Forward & Backprop with randomized dimensions."""
        for b_size in [1, 7, 32]:
            for in_dim in [3, 16, 64]:
                for h_dim in [8, 32]:
                    for out_dim in [1, 5]:
                        model = nn.Sequential(
                            nn.Linear(in_dim, h_dim), nn.ReLU(), nn.Linear(h_dim, out_dim)
                        )
                        x = torch.randn(b_size, in_dim, requires_grad=True)
                        y_target = torch.randn(b_size, out_dim)
                        out = model(x)
                        self.assertEqual(out.shape, (b_size, out_dim))
                        loss = F.mse_loss(out, y_target)
                        loss.backward()

                        # Verify input and weight gradients exist and are finite
                        self.assertIsNotNone(x.grad)
                        self.assertTrue(torch.isfinite(x.grad).all())
                        for p in model.parameters():
                            self.assertIsNotNone(p.grad)
                            self.assertTrue(torch.isfinite(p.grad).all())

    def test_l02_pinn_second_derivative(self):
        """L02: Higher-order Autograd for PINN PDE residuals."""
        x = torch.linspace(-2.0, 2.0, 50, requires_grad=True)
        # Function: u(x) = sin(3x) + x^3
        # u'(x) = 3cos(3x) + 3x^2
        # u''(x) = -9sin(3x) + 6x
        u = torch.sin(3 * x) + x**3
        u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x))[0]

        expected_u_x = 3 * torch.cos(3 * x) + 3 * x**2
        expected_u_xx = -9 * torch.sin(3 * x) + 6 * x

        self.assertTrue(torch.allclose(u_x, expected_u_x, atol=1e-5))
        self.assertTrue(torch.allclose(u_xx, expected_u_xx, atol=1e-5))

    def test_l04_conv2d_dimension_calculator(self):
        """L04: Conv2D spatial dimensions formula stress-tested against nn.Conv2d across 50 random configs."""
        np.random.seed(42)
        for _ in range(50):
            h_in = int(np.random.randint(10, 100))
            w_in = int(np.random.randint(10, 100))
            c_in = int(np.random.randint(1, 8))
            c_out = int(np.random.randint(1, 8))
            k = int(np.random.randint(1, min(7, h_in, w_in)))
            p = int(np.random.randint(0, k))
            s = int(np.random.randint(1, 4))
            d = int(np.random.randint(1, 3))

            effective_k = d * (k - 1) + 1
            if effective_k > h_in + 2 * p or effective_k > w_in + 2 * p:
                continue

            h_out_theo = math.floor((h_in + 2 * p - d * (k - 1) - 1) / s) + 1
            w_out_theo = math.floor((w_in + 2 * p - d * (k - 1) - 1) / s) + 1

            conv = nn.Conv2d(c_in, c_out, kernel_size=k, stride=s, padding=p, dilation=d)
            x = torch.randn(2, c_in, h_in, w_in)
            out = conv(x)

            self.assertEqual(
                out.shape[2],
                h_out_theo,
                f"Height mismatch for config H_in={h_in}, K={k}, P={p}, S={s}, D={d}",
            )
            self.assertEqual(
                out.shape[3],
                w_out_theo,
                f"Width mismatch for config W_in={w_in}, K={k}, P={p}, S={s}, D={d}",
            )

    def test_l10_vae_elbo_and_reparameterization(self):
        """L10: VAE KL analytical divergence and reparameterization trick."""
        torch.manual_seed(42)
        mu = torch.randn(64, 32, requires_grad=True)
        logvar = torch.randn(64, 32, requires_grad=True)
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        z = mu + eps * std

        kl_div = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp(), dim=-1).mean()
        self.assertGreaterEqual(kl_div.item(), 0.0, "KL divergence must be non-negative")

        bce = F.binary_cross_entropy_with_logits(z, torch.sigmoid(torch.randn_like(z)))
        elbo_loss = bce + kl_div
        elbo_loss.backward()

        self.assertTrue(torch.isfinite(mu.grad).all())
        self.assertTrue(torch.isfinite(logvar.grad).all())

    def test_l12_ddpm_marginal_properties(self):
        """L12: DDPM forward diffusion analytical marginal q(x_t | x_0)."""
        T = 100
        beta = torch.linspace(1e-4, 0.02, T)
        alpha = 1.0 - beta
        alpha_bar = torch.cumprod(alpha, dim=0)

        self.assertTrue(
            (alpha_bar[1:] <= alpha_bar[:-1]).all(), "alpha_bar must be monotonically decreasing"
        )
        self.assertLess(
            alpha_bar[-1].item(), 0.5, "alpha_bar_T should be significantly lower than 1.0"
        )

        x_0 = torch.randn(10000, 1)
        t = 50
        a_bar_t = alpha_bar[t]
        eps = torch.randn_like(x_0)
        x_t = torch.sqrt(a_bar_t) * x_0 + torch.sqrt(1 - a_bar_t) * eps

        empirical_var = torch.var(x_t).item()
        self.assertAlmostEqual(empirical_var, 1.0, delta=0.08)

    def test_l17_self_attention_causal_mask_and_scaling(self):
        """L17: Scaled Dot-Product Attention variance scaling and causal mask correctness."""
        torch.manual_seed(42)
        B, H, N, d_k = 4, 8, 16, 64
        q = torch.randn(B, H, N, d_k)
        k = torch.randn(B, H, N, d_k)
        v = torch.randn(B, H, N, d_k)

        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(d_k)
        self.assertEqual(scores.shape, (B, H, N, N))

        mask = torch.triu(torch.full((N, N), float("-inf")), diagonal=1)
        masked_scores = scores + mask
        attn_weights = F.softmax(masked_scores, dim=-1)

        for i in range(N):
            for j in range(i + 1, N):
                self.assertTrue(
                    (attn_weights[:, :, i, j] == 0.0).all(),
                    f"Non-zero attention at masked position ({i}, {j})",
                )

        out = torch.matmul(attn_weights, v)
        self.assertEqual(out.shape, (B, H, N, d_k))

    def test_l20_bleu_metric_adversarial(self):
        """L20: BLEU modified n-gram precision and Brevity Penalty properties."""

        def compute_bleu(ref_tokens, cand_tokens, max_n=4):
            c = len(cand_tokens)
            r = len(ref_tokens)
            if c == 0:
                return 0.0
            bp = 1.0 if c > r else math.exp(1 - r / c)

            p_n = []
            for n in range(1, max_n + 1):
                if c < n:
                    p_n.append(0.0)
                    continue
                cand_ngrams = [
                    tuple(cand_tokens[i : i + n]) for i in range(len(cand_tokens) - n + 1)
                ]
                ref_ngrams = [tuple(ref_tokens[i : i + n]) for i in range(len(ref_tokens) - n + 1)]

                from collections import Counter

                cand_counts = Counter(cand_ngrams)
                ref_counts = Counter(ref_ngrams)

                clipped = sum(
                    min(count, ref_counts.get(ng, 0)) for ng, count in cand_counts.items()
                )
                total = len(cand_ngrams)
                p_n.append(clipped / total if total > 0 else 0.0)

            if any(p == 0.0 for p in p_n):
                return 0.0
            log_precisions = sum(math.log(p) for p in p_n) / max_n
            return bp * math.exp(log_precisions)

        ref = "the cat is sitting on the mat".split()
        cand_perfect = "the cat is sitting on the mat".split()
        cand_short = "the cat is".split()
        cand_disjoint = "dog barked outside loudly".split()

        self.assertAlmostEqual(compute_bleu(ref, cand_perfect), 1.0, places=4)
        self.assertEqual(compute_bleu(ref, cand_disjoint), 0.0)
        self.assertLess(compute_bleu(ref, cand_short), 0.5)

    def test_l23_l24_bellman_contraction_and_value_iteration(self):
        """L23 & L24: Bellman Contraction Mapping & Value Iteration convergence."""
        num_states = 16
        num_actions = 4
        gamma = 0.9

        np.random.seed(42)
        P = np.zeros((num_states, num_actions, num_states))
        R = np.random.randn(num_states, num_actions)

        for s in range(num_states):
            for a in range(num_actions):
                next_s = (s + a + 1) % num_states
                P[s, a, next_s] = 1.0

        def bellman_operator(V):
            Q = np.zeros((num_states, num_actions))
            for a in range(num_actions):
                Q[:, a] = R[:, a] + gamma * np.dot(P[:, a, :], V)
            return np.max(Q, axis=1)

        V1 = np.random.randn(num_states)
        V2 = np.random.randn(num_states)
        TV1 = bellman_operator(V1)
        TV2 = bellman_operator(V2)

        dist_TV = np.max(np.abs(TV1 - TV2))
        dist_V = np.max(np.abs(V1 - V2))
        self.assertLessEqual(
            dist_TV, gamma * dist_V + 1e-9, "Bellman operator must be a gamma-contraction"
        )

        V = np.zeros(num_states)
        for _ in range(500):
            V_new = bellman_operator(V)
            if np.max(np.abs(V_new - V)) < 1e-7:
                break
            V = V_new

        TV = bellman_operator(V)
        self.assertLess(np.max(np.abs(TV - V)), 1e-6)

    def test_l26_reinforce_policy_gradient_monotonic_improvement(self):
        """L26: REINFORCE Policy Gradient step updates policy in correct direction."""
        torch.manual_seed(42)
        true_rewards = torch.tensor([1.0, 2.0, 10.0])
        theta = torch.zeros(3, requires_grad=True)

        optimizer = torch.optim.SGD([theta], lr=0.1)

        initial_probs = F.softmax(theta, dim=0).detach()
        self.assertTrue(torch.allclose(initial_probs, torch.tensor([1 / 3, 1 / 3, 1 / 3])))

        for _ in range(30):
            optimizer.zero_grad()
            probs = F.softmax(theta, dim=0)
            dist = torch.distributions.Categorical(probs)
            action = dist.sample()
            reward = true_rewards[action]

            loss = -dist.log_prob(action) * reward
            loss.backward()
            optimizer.step()

        final_probs = F.softmax(theta, dim=0).detach()
        self.assertGreater(
            final_probs[2].item(),
            0.65,
            "REINFORCE must increase probability of highest reward action",
        )

    def test_l27_gae_advantage_identities(self):
        """L27: Generalized Advantage Estimation (GAE) edge case identities."""
        rewards = [1.0, 0.0, 2.0, 5.0]
        values = [0.5, 1.2, 1.8, 4.0, 0.0]
        gamma = 0.99

        deltas = [rewards[t] + gamma * values[t + 1] - values[t] for t in range(len(rewards))]

        def calc_gae(lam):
            advantages = []
            for t in range(len(rewards)):
                a_t = sum((gamma * lam) ** l * deltas[t + l] for l in range(len(rewards) - t))
                advantages.append(a_t)
            return advantages

        gae_0 = calc_gae(0.0)
        for t in range(len(rewards)):
            self.assertAlmostEqual(gae_0[t], deltas[t], places=5)

        gae_1 = calc_gae(1.0)
        returns = []
        G = 0
        for r in reversed(rewards):
            G = r + gamma * G
            returns.insert(0, G)
        mc_advantages = [returns[t] - values[t] for t in range(len(rewards))]
        for t in range(len(rewards)):
            self.assertAlmostEqual(gae_1[t], mc_advantages[t], places=5)


if __name__ == "__main__":
    unittest.main(verbosity=2)
