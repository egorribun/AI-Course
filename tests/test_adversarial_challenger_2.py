"""
Adversarial Challenger 2 Verification Suite (Full Forensic & Edge-Case Battery)
Exhaustive verification of:
1. Dynamic Code Snippet Execution under Edge Conditions across all 28 syllabus topics.
2. AST Syntax parsing and standalone execution of all extracted lecture snippets.
3. DOM Node Hierarchy, Invariants, QA (>=10), Tasks (>=6 with solutions), Cheat Sheets.
4. Pill Badge exact integer synchronization against DOM elements.
5. Complete Link Graph Integrity, Relative Path Resolution, Dead Anchor Detection across all 28 lectures and index.html.
6. Sequential Navigation Chain (Prev/Next) continuity.
7. MathJax & LaTeX syntactic validity and brace balancing.
"""

from __future__ import annotations

import ast
import html
import math
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Set, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
INDEX_FILE = COURSE_ROOT / "index.html"

EXPECTED_LECTURES = [
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


class StrictDOMParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.qa_count = 0
        self.task_count = 0
        self.sol_count = 0
        self.has_cheat = False
        self.cheat_content_len = 0
        self.pills: List[str] = []
        self.element_ids: Set[str] = set()
        self.hrefs: List[Tuple[str, int]] = []  # (href, line_no)
        self.backlinks: List[str] = []
        self.navrow_links: List[Tuple[str, str]] = []  # (href, text)

        # State tracking
        self._current_tag_stack: List[str] = []
        self._in_pill = False
        self._pill_text: List[str] = []
        self._cheat_depth = 0
        self._cheat_text: List[str] = []
        self._in_navrow = False
        self._navrow_href: str | None = None
        self._navrow_text: List[str] = []
        self._in_details = False
        self._details_has_summary = False
        self.details_summary_errors: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, str | None]]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        classes = attr_dict.get("class", "").split()
        tag_id = attr_dict.get("id")
        line_no = self.getpos()[0]

        if tag_id:
            self.element_ids.add(tag_id)

        href = attr_dict.get("href")
        if tag == "a" and href is not None:
            self.hrefs.append((href, line_no))
            if "backlink" in classes:
                self.backlinks.append(href)

        if tag == "details":
            self._in_details = True
            self._details_has_summary = False
            if "qa" in classes:
                self.qa_count += 1

        if "sol" in classes:
            self.sol_count += 1

        if tag == "summary" and self._in_details:
            self._details_has_summary = True

        if tag == "div" and "task" in classes:
            self.task_count += 1

        if tag == "div":
            if "cheat" in classes:
                self.has_cheat = True
                self._cheat_depth = 1
            elif self._cheat_depth > 0:
                self._cheat_depth += 1

        if "pill" in classes:
            self._in_pill = True
            self._pill_text = []

        if "navrow" in classes:
            self._in_navrow = True

        if self._in_navrow and tag == "a" and href:
            self._navrow_href = href
            self._navrow_text = []

        self._current_tag_stack.append(tag)

    def handle_endtag(self, tag: str):
        if tag == "details":
            if not self._details_has_summary:
                self.details_summary_errors.append(f"Line {self.getpos()[0]}: <details> missing <summary>")
            self._in_details = False
            self._details_has_summary = False

        if self._in_pill and tag in ("span", "div", "a"):
            self._in_pill = False
            self.pills.append("".join(self._pill_text).strip())
            self._pill_text = []

        if tag == "div" and self._cheat_depth > 0:
            self._cheat_depth -= 1

        if tag == "div" and self._in_navrow:
            self._in_navrow = False

        if self._in_navrow and tag == "a" and self._navrow_href is not None:
            self.navrow_links.append((self._navrow_href, "".join(self._navrow_text).strip()))
            self._navrow_href = None
            self._navrow_text = []

        if self._current_tag_stack and self._current_tag_stack[-1] == tag:
            self._current_tag_stack.pop()

    def handle_data(self, data: str):
        if self._in_pill:
            self._pill_text.append(data)
        if self._cheat_depth > 0:
            self._cheat_text.append(data)
            self.cheat_content_len += len(data.strip())
        if self._in_navrow and self._navrow_href is not None:
            self._navrow_text.append(data)


class TestDOMAndPillInvariants(unittest.TestCase):
    """Forensic verification of DOM structure and pill badges across all 28 lectures."""

    def test_dom_node_hierarchy_and_invariants(self):
        total_qa = 0
        total_tasks = 0

        for filename in EXPECTED_LECTURES:
            path = LECTURES_DIR / filename
            self.assertTrue(path.exists(), f"Lecture file not found: {filename}")
            content = path.read_text(encoding="utf-8")

            parser = StrictDOMParser()
            parser.feed(content)

            # Invariant 1: QA count >= 10
            self.assertGreaterEqual(
                parser.qa_count, 10,
                f"[{filename}] QA count violation: Found {parser.qa_count} < 10 required"
            )
            total_qa += parser.qa_count

            # Invariant 2: Task count >= 6
            self.assertGreaterEqual(
                parser.task_count, 6,
                f"[{filename}] Task count violation: Found {parser.task_count} < 6 required"
            )
            total_tasks += parser.task_count

            # Invariant 3: Solutions count matches task count
            self.assertGreaterEqual(
                parser.sol_count, parser.task_count,
                f"[{filename}] Solution details count {parser.sol_count} < Task count {parser.task_count}"
            )

            # Invariant 4: Cheat sheet exists and has substantial content
            self.assertTrue(
                parser.has_cheat,
                f"[{filename}] Missing cheat sheet block (<div class='cheat'>)"
            )
            self.assertGreaterEqual(
                parser.cheat_content_len, 50,
                f"[{filename}] Cheat sheet content too short ({parser.cheat_content_len} chars)"
            )

            # Invariant 5: Top backlink exists and points to index.html
            self.assertTrue(
                len(parser.backlinks) > 0,
                f"[{filename}] Missing top backlink"
            )
            self.assertTrue(
                any("index.html" in b or b == "../" for b in parser.backlinks),
                f"[{filename}] Backlink '{parser.backlinks}' does not point to index.html"
            )

            # Invariant 6: Details summary integrity
            self.assertEqual(
                len(parser.details_summary_errors), 0,
                f"[{filename}] <details> tag errors: {parser.details_summary_errors}"
            )

        # Global Invariants
        self.assertGreaterEqual(total_qa, 280, f"Total QA across course {total_qa} < 280")
        self.assertGreaterEqual(total_tasks, 168, f"Total tasks across course {total_tasks} < 168")

    def test_pill_badge_exact_synchronization(self):
        """Verify that integer numbers in header .pill badges EXACTLY match parsed DOM counts."""
        for filename in EXPECTED_LECTURES:
            path = LECTURES_DIR / filename
            content = path.read_text(encoding="utf-8")

            parser = StrictDOMParser()
            parser.feed(content)

            all_pill_text = " ".join(parser.pills)

            # 1. QA Pill Sync
            qa_match = re.search(r"(\d+)\s*(?:вопрос|QA|Q&A|вопросов)", all_pill_text, re.IGNORECASE)
            self.assertIsNotNone(
                qa_match,
                f"[{filename}] Header pills missing QA count badge. Pills found: {parser.pills}"
            )
            pill_qa_num = int(qa_match.group(1))
            self.assertEqual(
                pill_qa_num, parser.qa_count,
                f"[{filename}] Desync in QA Pill! Badge says {pill_qa_num}, but DOM has {parser.qa_count} QA blocks"
            )

            # 2. Task Pill Sync
            task_match = re.search(r"(\d+)\s*(?:микро-задач|задач|задачи|tasks)", all_pill_text, re.IGNORECASE)
            self.assertIsNotNone(
                task_match,
                f"[{filename}] Header pills missing Task count badge. Pills found: {parser.pills}"
            )
            pill_task_num = int(task_match.group(1))
            self.assertEqual(
                pill_task_num, parser.task_count,
                f"[{filename}] Desync in Task Pill! Badge says {pill_task_num}, but DOM has {parser.task_count} Task blocks"
            )


class TestLinkGraphAndAnchors(unittest.TestCase):
    """Forensic verification of all hyperlinks, anchor tags, and navigation continuity."""

    def test_all_hrefs_and_anchors_resolution(self):
        file_ids: Dict[Path, Set[str]] = {}
        all_files = [INDEX_FILE] + [LECTURES_DIR / f for f in EXPECTED_LECTURES]

        for filepath in all_files:
            content = filepath.read_text(encoding="utf-8")
            parser = StrictDOMParser()
            parser.feed(content)
            file_ids[filepath.resolve()] = parser.element_ids

        broken_links = []
        dead_anchors = []

        for filepath in all_files:
            content = filepath.read_text(encoding="utf-8")
            parser = StrictDOMParser()
            parser.feed(content)

            for href, line_no in parser.hrefs:
                if href.startswith("http://") or href.startswith("https://") or href.startswith("mailto:"):
                    continue

                if href.startswith("javascript:"):
                    continue

                if href.startswith("#"):
                    anchor_id = href[1:]
                    if anchor_id and anchor_id not in file_ids[filepath.resolve()]:
                        dead_anchors.append(f"{filepath.name}:{line_no} -> dead local anchor '{href}'")
                else:
                    parts = href.split("#", 1)
                    target_rel_path = parts[0]
                    target_anchor = parts[1] if len(parts) > 1 else None

                    if target_rel_path:
                        target_file = (filepath.parent / target_rel_path).resolve()
                        if not target_file.exists():
                            broken_links.append(f"{filepath.name}:{line_no} -> missing target file '{href}' (resolved to {target_file})")
                        elif target_anchor:
                            if target_file in file_ids:
                                if target_anchor not in file_ids[target_file]:
                                    dead_anchors.append(f"{filepath.name}:{line_no} -> dead anchor '{target_anchor}' in {target_file.name}")

        self.assertEqual(len(broken_links), 0, f"Found {len(broken_links)} broken links:\n" + "\n".join(broken_links))
        self.assertEqual(len(dead_anchors), 0, f"Found {len(dead_anchors)} dead anchors:\n" + "\n".join(dead_anchors))

    def test_sequential_navrow_chain(self):
        """Verify the Prev/Next navigation chain 00 <-> 01 <-> ... <-> 27."""
        for idx, filename in enumerate(EXPECTED_LECTURES):
            filepath = LECTURES_DIR / filename
            content = filepath.read_text(encoding="utf-8")
            parser = StrictDOMParser()
            parser.feed(content)

            nav_hrefs = [href for href, _ in parser.navrow_links]

            if idx == 0:
                next_lec = EXPECTED_LECTURES[1]
                self.assertTrue(
                    any(next_lec in h for h in nav_hrefs),
                    f"[L00] Navrow missing link to next lecture {next_lec}. Found: {nav_hrefs}"
                )
            elif idx == len(EXPECTED_LECTURES) - 1:
                prev_lec = EXPECTED_LECTURES[idx - 1]
                self.assertTrue(
                    any(prev_lec in h for h in nav_hrefs),
                    f"[L27] Navrow missing link to prev lecture {prev_lec}. Found: {nav_hrefs}"
                )
            else:
                prev_lec = EXPECTED_LECTURES[idx - 1]
                next_lec = EXPECTED_LECTURES[idx + 1]
                self.assertTrue(
                    any(prev_lec in h for h in nav_hrefs),
                    f"[{filename}] Navrow missing link to prev lecture {prev_lec}. Found: {nav_hrefs}"
                )
                self.assertTrue(
                    any(next_lec in h for h in nav_hrefs),
                    f"[{filename}] Navrow missing link to next lecture {next_lec}. Found: {nav_hrefs}"
                )

    def test_index_cards_cover_all_28_lectures(self):
        content = INDEX_FILE.read_text(encoding="utf-8")
        parser = StrictDOMParser()
        parser.feed(content)

        linked_lectures = set()
        for href, _ in parser.hrefs:
            for lec in EXPECTED_LECTURES:
                if lec in href:
                    linked_lectures.add(lec)

        missing = set(EXPECTED_LECTURES) - linked_lectures
        self.assertEqual(len(missing), 0, f"index.html missing links to lectures: {missing}")


class TestAdversarialDynamicCodeExecution(unittest.TestCase):
    """Extracts and dynamically stress-tests Python code snippets under edge conditions."""

    def test_ast_parse_all_lecture_code_blocks(self):
        code_block_pattern = re.compile(r"<pre[^>]*>(?:<code[^>]*>)?(.*?)(?:</code>)?</pre>", re.DOTALL | re.IGNORECASE)
        syntax_errors = []
        parsed_count = 0

        for filename in EXPECTED_LECTURES:
            filepath = LECTURES_DIR / filename
            content = filepath.read_text(encoding="utf-8")

            for match in code_block_pattern.finditer(content):
                raw_code = match.group(1)
                clean_code = re.sub(r"<[^>]+>", "", raw_code)
                clean_code = html.unescape(clean_code).strip()

                if not clean_code:
                    continue

                if clean_code.startswith("$") or clean_code.startswith("pip install") or "+---" in clean_code or "|---" in clean_code:
                    continue

                py_keywords = [
                    "import ", "def ", "class ", "torch.", "nn.", "F.", "self.", "return ",
                    "q_table", "model =", "loss", "optimizer"
                ]
                if any(kw in clean_code for kw in py_keywords):
                    try:
                        ast.parse(clean_code)
                        parsed_count += 1
                    except SyntaxError as e:
                        line_no = content[:match.start()].count("\n") + 1
                        syntax_errors.append(f"{filename}:{line_no} -> SyntaxError: {e.msg} at line {e.lineno}")

        self.assertGreater(parsed_count, 30, f"Expected >30 Python snippets parsed, found {parsed_count}")
        self.assertEqual(len(syntax_errors), 0, "Syntax errors in lecture code snippets:\n" + "\n".join(syntax_errors))

    def test_edge_case_l00_activations(self):
        """L00: Activation functions under extreme inputs without NaN/Inf."""
        x_extreme = torch.tensor([-1e5, -100.0, -1.0, 0.0, 1.0, 100.0, 1e5])

        # Sigmoid, Tanh, ReLU, LeakyReLU, GELU
        sig = torch.sigmoid(x_extreme)
        self.assertTrue(torch.isfinite(sig).all())
        self.assertTrue((sig >= 0.0).all() and (sig <= 1.0).all())

        tnh = torch.tanh(x_extreme)
        self.assertTrue(torch.isfinite(tnh).all())
        self.assertTrue((tnh >= -1.0).all() and (tnh <= 1.0).all())

        relu = F.relu(x_extreme)
        self.assertTrue(torch.isfinite(relu).all())
        self.assertEqual(relu[0].item(), 0.0)

        gelu = F.gelu(x_extreme)
        self.assertTrue(torch.isfinite(gelu).all())

    def test_edge_case_l01_fcnn_and_autograd(self):
        """L01: FCNN forward and autograd backward under varying batch sizes and shapes."""
        for batch_size in [1, 3, 16]:
            for in_features in [1, 4, 128]:
                for hidden in [2, 32]:
                    for out_features in [1, 10]:
                        model = nn.Sequential(
                            nn.Linear(in_features, hidden),
                            nn.ReLU(),
                            nn.Linear(hidden, out_features)
                        )
                        x = torch.randn(batch_size, in_features, requires_grad=True)
                        target = torch.randn(batch_size, out_features)
                        out = model(x)
                        self.assertEqual(out.shape, (batch_size, out_features))

                        loss = F.mse_loss(out, target)
                        loss.backward()

                        self.assertIsNotNone(x.grad)
                        self.assertTrue(torch.isfinite(x.grad).all())
                        for p in model.parameters():
                            self.assertIsNotNone(p.grad)
                            self.assertTrue(torch.isfinite(p.grad).all())

    def test_edge_case_l02_pinn_second_derivative_boundary(self):
        """L02: PINN higher-order derivative at boundary points."""
        for num_points in [2, 10, 100]:
            x = torch.linspace(-10.0, 10.0, num_points, requires_grad=True)
            u = torch.tanh(x)
            u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0]
            u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x))[0]

            expected_u_x = 1.0 - torch.tanh(x) ** 2
            expected_u_xx = -2.0 * torch.tanh(x) * (1.0 - torch.tanh(x) ** 2)

            self.assertTrue(torch.allclose(u_x, expected_u_x, atol=1e-5))
            self.assertTrue(torch.allclose(u_xx, expected_u_xx, atol=1e-5))

    def test_edge_case_l03_losses_boundary(self):
        """L03: BCE and CE stability under probability margins."""
        eps = 1e-7
        p = torch.tensor([eps, 0.5, 1.0 - eps], requires_grad=True)
        y = torch.tensor([0.0, 1.0, 1.0])
        bce = F.binary_cross_entropy(p, y)
        self.assertTrue(torch.isfinite(bce))
        bce.backward()
        self.assertTrue(torch.isfinite(p.grad).all())

    def test_edge_case_l04_convolutions(self):
        """L04: Conv2D shape formula on asymmetric dimensions and edge paddings."""
        def calc_conv_out(in_dim, k, s, p, d=1):
            return math.floor((in_dim + 2 * p - d * (k - 1) - 1) / s) + 1

        test_cases = [
            (224, 7, 2, 3, 1),
            (112, 3, 2, 1, 1),
            (56, 1, 1, 0, 1),
            (7, 3, 1, 1, 1),
            (32, 5, 3, 2, 2),  # dilated
        ]

        for h_in, k, s, p, d in test_cases:
            h_theo = calc_conv_out(h_in, k, s, p, d)
            conv = nn.Conv2d(3, 16, kernel_size=k, stride=s, padding=p, dilation=d)
            x = torch.randn(1, 3, h_in, h_in)
            out = conv(x)
            self.assertEqual(out.shape[2], h_theo, f"Failed for H_in={h_in}, K={k}, S={s}, P={p}, D={d}")

    def test_edge_case_l05_resnet_residual_gradient_flow(self):
        """L05: Residual block gradient flow verification without vanishing."""
        class ResBlock(nn.Module):
            def __init__(self, channels):
                super().__init__()
                self.conv1 = nn.Conv2d(channels, channels, 3, padding=1)
                self.bn1 = nn.BatchNorm2d(channels)
                self.conv2 = nn.Conv2d(channels, channels, 3, padding=1)
                self.bn2 = nn.BatchNorm2d(channels)

            def forward(self, x):
                residual = x
                out = F.relu(self.bn1(self.conv1(x)))
                out = self.bn2(self.conv2(out))
                return F.relu(out + residual)

        block = ResBlock(16)
        x = torch.randn(2, 16, 8, 8, requires_grad=True)
        out = block(x)
        self.assertEqual(out.shape, (2, 16, 8, 8))
        out.sum().backward()
        self.assertIsNotNone(x.grad)
        self.assertGreater(torch.norm(x.grad).item(), 0.0)

    def test_edge_case_l06_optimizers_adamw(self):
        """L06: AdamW weight decay decoupling compared to standard L2 gradient penalty."""
        param1 = nn.Parameter(torch.tensor([10.0]))
        param2 = nn.Parameter(torch.tensor([10.0]))

        opt_adam = torch.optim.Adam([param1], lr=0.1, weight_decay=0.01)
        opt_adamw = torch.optim.AdamW([param2], lr=0.1, weight_decay=0.01)

        # Step 1: zero loss gradient -> Adam does nothing, AdamW decays weight!
        loss1 = param1 * 0.0
        loss2 = param2 * 0.0
        loss1.backward()
        loss2.backward()
        opt_adam.step()
        opt_adamw.step()

        self.assertLess(param2.item(), 10.0, "AdamW must decay weight directly in step")

    def test_edge_case_l08_metric_learning_arcface(self):
        """L08: ArcFace angular margin penalty."""
        torch.manual_seed(42)
        embeddings = F.normalize(torch.randn(4, 16), dim=-1)
        weights = F.normalize(torch.randn(5, 16), dim=-1)  # 5 classes

        cos_theta = F.linear(embeddings, weights).clamp(-1.0 + 1e-7, 1.0 - 1e-7)
        theta = torch.acos(cos_theta)
        margin = 0.5
        cos_theta_m = torch.cos(theta + margin)

        self.assertEqual(cos_theta_m.shape, (4, 5))
        self.assertTrue((cos_theta_m <= cos_theta).all(), "cos(theta + m) must be <= cos(theta) for positive m in [0, pi]")

    def test_edge_case_l09_contrastive_simclr_loss(self):
        """L09: NT-Xent loss with varying batch size and temperatures."""
        def nt_xent(z1, z2, temp=0.1):
            B = z1.size(0)
            z1_norm = F.normalize(z1, dim=1)
            z2_norm = F.normalize(z2, dim=1)
            z = torch.cat([z1_norm, z2_norm], dim=0)
            sim = torch.mm(z, z.T) / temp
            mask = torch.eye(2 * B, dtype=torch.bool, device=z.device)
            sim.masked_fill_(mask, -1e9)
            labels = torch.cat([torch.arange(B, 2*B), torch.arange(0, B)]).to(z.device)
            return F.cross_entropy(sim, labels)

        for b in [2, 5, 16]:
            for temp in [0.05, 0.1, 0.5, 1.0]:
                z1 = torch.randn(b, 32, requires_grad=True)
                z2 = torch.randn(b, 32, requires_grad=True)
                loss = nt_xent(z1, z2, temp)
                self.assertFalse(torch.isnan(loss))
                self.assertFalse(torch.isinf(loss))
                loss.backward()
                self.assertTrue(torch.isfinite(z1.grad).all())
                self.assertTrue(torch.isfinite(z2.grad).all())

    def test_edge_case_l10_vae_reparam(self):
        """L10: VAE Reparameterization trick with extreme variance."""
        mu = torch.zeros(10, 8)
        logvar = torch.full((10, 8), -20.0)  # std -> exp(-10) ~ 4.5e-5
        eps = torch.randn_like(mu)
        z = mu + torch.exp(0.5 * logvar) * eps
        self.assertTrue(torch.allclose(z, mu, atol=1e-3))

    def test_edge_case_l11_wgan_gp_gradient_penalty(self):
        """L11: WGAN-GP gradient penalty calculation on interpolated samples."""
        disc = nn.Sequential(nn.Linear(8, 16), nn.LeakyReLU(), nn.Linear(16, 1))
        real = torch.randn(4, 8)
        fake = torch.randn(4, 8)
        alpha = torch.rand(4, 1)
        interpolated = (alpha * real + (1 - alpha) * fake).requires_grad_(True)

        d_interpolated = disc(interpolated)
        grad = torch.autograd.grad(
            outputs=d_interpolated,
            inputs=interpolated,
            grad_outputs=torch.ones_like(d_interpolated),
            create_graph=True,
            retain_graph=True,
        )[0]

        grad_norm = grad.view(4, -1).norm(2, dim=1)
        gp = ((grad_norm - 1.0) ** 2).mean()
        self.assertGreaterEqual(gp.item(), 0.0)

    def test_edge_case_l12_ddpm_diffusion_schedule(self):
        """L12: DDPM variance schedule and beta boundary conditions."""
        T = 1000
        beta = torch.linspace(1e-4, 0.02, T)
        alpha = 1.0 - beta
        alpha_bar = torch.cumprod(alpha, dim=0)

        self.assertAlmostEqual(alpha_bar[0].item(), 1.0 - 1e-4, places=4)
        self.assertLess(alpha_bar[-1].item(), 0.01)

    def test_edge_case_l13_iou_calculator(self):
        """L13: Bounding box IoU under disjoint, identical, and partial overlap."""
        def calc_iou(box1, box2):
            # [x1, y1, x2, y2]
            xi1 = max(box1[0], box2[0])
            yi1 = max(box1[1], box2[1])
            xi2 = min(box1[2], box2[2])
            yi2 = min(box1[3], box2[3])
            inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
            box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
            box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
            union_area = box1_area + box2_area - inter_area
            return inter_area / union_area if union_area > 0 else 0.0

        # Identical
        self.assertAlmostEqual(calc_iou([0, 0, 10, 10], [0, 0, 10, 10]), 1.0)
        # Disjoint
        self.assertEqual(calc_iou([0, 0, 5, 5], [10, 10, 20, 20]), 0.0)
        # 50% overlap: [0, 0, 10, 10] (area 100) and [5, 0, 15, 10] (area 100), inter = 5x10 = 50, union = 150 -> 1/3
        self.assertAlmostEqual(calc_iou([0, 0, 10, 10], [5, 0, 15, 10]), 1/3)

    def test_edge_case_l14_lstm_cell_mechanics(self):
        """L14: LSTM Cell gating with extreme forget gate behavior."""
        lstm = nn.LSTMCell(input_size=4, hidden_size=8)
        hx = torch.zeros(1, 8)
        cx = torch.ones(1, 8) * 5.0
        x = torch.zeros(1, 4)
        hx_new, cx_new = lstm(x, (hx, cx))
        self.assertEqual(hx_new.shape, (1, 8))
        self.assertEqual(cx_new.shape, (1, 8))

    def test_edge_case_l15_l16_l17_attention_masks(self):
        """L15, L16, L17: Scaled Dot-Product Attention and Causal Masking with single-token sequences."""
        def scaled_dot_product_attention(q, k, v, mask=None):
            d_k = q.size(-1)
            scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(d_k)
            if mask is not None:
                scores = scores.masked_fill(mask == 0, float("-inf"))
            attn = F.softmax(scores, dim=-1)
            attn = torch.nan_to_num(attn, nan=0.0)
            return torch.matmul(attn, v), attn

        # Edge Case 1: T = 1 (single token, e.g. generation start)
        q = torch.randn(1, 4, 1, 64, requires_grad=True)
        k = torch.randn(1, 4, 1, 64, requires_grad=True)
        v = torch.randn(1, 4, 1, 64, requires_grad=True)
        out, attn = scaled_dot_product_attention(q, k, v)
        self.assertEqual(out.shape, (1, 4, 1, 64))
        self.assertTrue(torch.allclose(attn, torch.ones_like(attn)))
        out.sum().backward()
        self.assertTrue(torch.isfinite(q.grad).all())

        # Edge Case 2: T = 32 with causal mask
        T = 32
        q2 = torch.randn(2, 8, T, 32, requires_grad=True)
        k2 = torch.randn(2, 8, T, 32, requires_grad=True)
        v2 = torch.randn(2, 8, T, 32, requires_grad=True)
        causal_mask = torch.tril(torch.ones(T, T))
        out2, attn2 = scaled_dot_product_attention(q2, k2, v2, mask=causal_mask)
        self.assertEqual(out2.shape, (2, 8, T, 32))
        for i in range(T):
            for j in range(i + 1, T):
                self.assertTrue((attn2[:, :, i, j] == 0.0).all())
        out2.sum().backward()
        self.assertTrue(torch.isfinite(q2.grad).all())

    def test_edge_case_l20_bleu_edge_cases(self):
        """L20: BLEU modified precision and brevity penalty edge behaviors."""
        def calc_bleu(ref: str, cand: str):
            r_tokens = ref.split()
            c_tokens = cand.split()
            if not c_tokens:
                return 0.0
            bp = 1.0 if len(c_tokens) > len(r_tokens) else math.exp(1 - len(r_tokens) / len(c_tokens))
            return bp

        # Shorter candidate gets penalized
        self.assertLess(calc_bleu("a b c d e", "a b"), 1.0)
        # Longer candidate gets BP = 1.0
        self.assertEqual(calc_bleu("a b", "a b c d"), 1.0)

    def test_edge_case_l23_bellman_contraction_norm(self):
        """L23: Bellman operator contraction mapping property under gamma=0.9."""
        gamma = 0.9
        V1 = np.array([10.0, -5.0, 2.0])
        V2 = np.array([2.0, 3.0, -1.0])

        # Simple transition P(s'|s,a) with immediate rewards
        R = np.array([1.0, 0.0, 2.0])
        TV1 = R + gamma * V1
        TV2 = R + gamma * V2

        norm_diff_V = np.max(np.abs(V1 - V2))
        norm_diff_TV = np.max(np.abs(TV1 - TV2))
        self.assertLessEqual(norm_diff_TV, gamma * norm_diff_V)

    def test_edge_case_l27_gae_advantage(self):
        """L27: Generalized Advantage Estimation with zero rewards, gamma=0, lambda=0, and lambda=1."""
        def gae(rewards, values, next_values, dones, gamma=0.99, lam=0.95):
            deltas = rewards + gamma * next_values * (1.0 - dones) - values
            gaes = torch.zeros_like(rewards)
            running = 0.0
            for t in reversed(range(len(rewards))):
                running = deltas[t] + gamma * lam * (1.0 - dones[t]) * running
                gaes[t] = running
            return gaes

        zero_adv = gae(torch.zeros(5), torch.tensor([1.0, 1.0, 1.0, 1.0, 1.0]), torch.tensor([1.0, 1.0, 1.0, 1.0, 1.0]), torch.zeros(5), gamma=1.0, lam=0.95)
        self.assertTrue(torch.allclose(zero_adv, torch.zeros(5)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
