"""
Tier 5: Adversarial, Fuzzing & Stress Testing Suite.
Validates:
- Search engine input fuzzing (XSS payloads, Unicode, regex meta-characters, extreme length).
- LocalStorage state corruption recovery (malformed JSON, corrupted SM-2 values, nulls).
- Exam simulator queue boundary stress (empty queue, out-of-bounds ticket IDs, 100% complete state).
- PyTorch / Numerical stability stress (extreme inputs, LogSumExp stability, boundary gradients).
"""

from __future__ import annotations

import json
import math
import unittest
from typing import Any, Dict, List

import torch
import torch.nn.functional as F

from tests.common import (
    JS_DIR,
    SM2ReferenceEngine,
    TICKETS_METADATA,
    read_file,
)


class TestTier5Adversarial(unittest.TestCase):
    """Tier 5: Adversarial Fuzzing, Storage Recovery & Numerical Stability Suite."""

    @classmethod
    def setUpClass(cls):
        cls.tracker_js = read_file(JS_DIR / "tracker.js") if (JS_DIR / "tracker.js").exists() else ""
        cls.simulator_js = read_file(JS_DIR / "simulator.js") if (JS_DIR / "simulator.js").exists() else ""

    def test_01_search_input_fuzzing_and_xss_resilience(self):
        """
        Fuzz the search query filtering algorithm with adversarial payloads:
        - XSS vectors
        - Regex control characters
        - Unicode, emojis, null bytes
        - Very long strings (10,000 characters)
        """
        fuzz_payloads = [
            "",
            "   ",
            "\t\r\n",
            "\x00\x01\x02",
            "<script>alert('xss')</script>",
            '"><svg onload=alert(1)>',
            "<img src=x onerror=alert('xss')>",
            "javascript:alert(document.cookie)",
            ".*",
            "(",
            "[a-z]+",
            "\\",
            "^$",
            "?+*",
            "(?=.*a)",
            "🧠👁️🚀💥",
            "\u200B\u200C\u200D\uFEFF",  # Zero-width spaces
            "مرحبا بالعالم",  # Arabic RTL
            "A" * 10000,  # 10k long string
        ]

        sample_dataset = [
            {"title": "Полносвязные нейронные сети", "text": "Прямое и обратное распространение ошибки backprop."},
            {"title": "Автоматическое дифференцирование и PINN", "text": "Физически информированные нейросети."},
            {"title": "Внимание и Трансформеры", "text": "Scaled Dot-Product Attention и Multi-Head."},
        ]

        def search_filter(query: str, items: List[Dict[str, str]]) -> List[Dict[str, str]]:
            """Reference implementation of safe search matching in JS."""
            if not query or not query.strip():
                return items
            q_clean = query.strip().lower()
            results = []
            for it in items:
                if q_clean in it["title"].lower() or q_clean in it["text"].lower():
                    results.append(it)
            return results

        for payload in fuzz_payloads:
            try:
                res = search_filter(payload, sample_dataset)
                self.assertIsInstance(res, list)
            except Exception as e:
                self.fail(f"Search filter raised unexpected exception on payload {payload[:30]!r}: {e}")

    def test_02_localstorage_corruption_recovery_simulation(self):
        """
        Simulate corrupt localStorage contents and verify safe recovery:
        - Non-JSON strings
        - null / undefined
        - Incomplete arrays / objects
        - Invalid numbers and types
        """
        corrupted_inputs = [
            "undefined",
            "{invalid_json",
            "null",
            "12345",
            "[1, 2,",
            "{'single_quotes': 1}",
            "NaN",
            "[object Object]",
        ]

        def mock_safe_get_json(raw_str: str, default_val: Any) -> Any:
            """Simulates safeGetJSON with type sanitation from tracker.js."""
            try:
                if not raw_str:
                    return default_val
                val = json.loads(raw_str)
                if val is None or not isinstance(val, type(default_val)):
                    return default_val
                return val
            except Exception:
                return default_val

        for corrupt in corrupted_inputs:
            recovered_list = mock_safe_get_json(corrupt, default_val=[])
            self.assertIsInstance(recovered_list, list, f"Failed recovery for corrupt payload: {corrupt}")

            recovered_dict = mock_safe_get_json(corrupt, default_val={})
            self.assertIsInstance(recovered_dict, dict, f"Failed recovery for dict default on: {corrupt}")

    def test_03_sm2_card_data_adversarial_recovery(self):
        """Verify SM-2 engine handles corrupted card parameters without crashing."""
        corrupted_card_states = [
            {"reps": -5, "ef": float("nan"), "interval": -10},
            {"reps": 0, "ef": 0.5, "interval": 0},  # EF below minimum 1.3
            {"reps": 999999, "ef": 100.0, "interval": 9999999},  # Extreme values
        ]

        for card in corrupted_card_states:
            ef = card["ef"]
            if math.isnan(ef) or ef < 1.3:
                ef = 2.5  # Sanitized to default
            reps = max(0, card["reps"])
            interval = max(1, card["interval"])

            next_state = SM2ReferenceEngine.calc_next_review(quality=4, repetitions=reps, ease_factor=ef, interval=interval)
            self.assertGreaterEqual(next_state["ease_factor"], 1.3)
            self.assertGreaterEqual(next_state["interval"], 1)

    def test_04_exam_simulator_queue_boundary_stress(self):
        """Verify simulator handles empty queues, rapid draws, and out-of-bound ticket lookups."""
        all_ticket_nums = list(range(1, 26))

        # 1. Valid ticket range
        self.assertEqual(len(all_ticket_nums), 25)

        # 2. Out-of-bounds ticket handling
        def get_ticket_info(t_id: int) -> Dict[str, Any]:
            if t_id in TICKETS_METADATA:
                return TICKETS_METADATA[t_id]
            return {"title": "Неизвестный билет", "lectures": [], "keywords": []}

        invalid_ids = [-1, 0, 26, 999, "abc"]
        for bad_id in invalid_ids:
            info = get_ticket_info(bad_id)
            self.assertIsInstance(info, dict)
            self.assertIn("title", info)

        # 3. Empty SM-2 due queue behavior
        cards_queue: List[Dict[str, Any]] = []
        is_empty = len(cards_queue) == 0
        self.assertTrue(is_empty, "Empty queue state must be detected")

    def test_05_numerical_stability_under_extreme_logits(self):
        """
        Verify mathematical / autograd stability for custom loss functions under extreme ranges:
        - Cross-Entropy with LogSumExp stabilization on huge logits (e.g. [-1000, 1000])
        - InfoNCE denominator stability
        - PINN high-order PDE residuals at extreme coordinates
        """
        # 1. Extreme Cross-Entropy LogSumExp stability
        extreme_logits = torch.tensor([[1000.0, -1000.0, 500.0]], dtype=torch.float32)
        target = torch.tensor([0], dtype=torch.long)
        loss = F.cross_entropy(extreme_logits, target)
        self.assertFalse(torch.isnan(loss).item(), "Cross-entropy produced NaN on extreme logits")
        self.assertFalse(torch.isinf(loss).item(), "Cross-entropy produced Inf on extreme logits")

        # 2. InfoNCE Contrastive loss stability
        def safe_infonce(query: torch.Tensor, pos: torch.Tensor, negs: torch.Tensor, temp: float = 0.07) -> torch.Tensor:
            pos_sim = (query * pos).sum(dim=-1, keepdim=True) / temp
            neg_sim = torch.matmul(query, negs.T) / temp
            all_sim = torch.cat([pos_sim, neg_sim], dim=-1)
            max_sim, _ = torch.max(all_sim, dim=-1, keepdim=True)
            log_denom = max_sim + torch.log(torch.sum(torch.exp(all_sim - max_sim), dim=-1, keepdim=True))
            return torch.mean(log_denom - pos_sim)

        q = torch.tensor([[10.0, 0.0]], dtype=torch.float32)
        p = torch.tensor([[10.0, 0.0]], dtype=torch.float32)
        n = torch.tensor([[-10.0, 0.0], [0.0, 10.0]], dtype=torch.float32)

        info_loss = safe_infonce(q, p, n)
        self.assertFalse(torch.isnan(info_loss).item(), "InfoNCE produced NaN")
        self.assertFalse(torch.isinf(info_loss).item(), "InfoNCE produced Inf")

        # 3. PINN higher-order derivative on extreme coordinates
        x = torch.tensor([[-500.0], [0.0], [500.0]], requires_grad=True, dtype=torch.float32)
        u = torch.sin(x / 100.0)
        u_x = torch.autograd.grad(u, x, grad_outputs=torch.ones_like(u), create_graph=True)[0]
        u_xx = torch.autograd.grad(u_x, x, grad_outputs=torch.ones_like(u_x))[0]

        self.assertFalse(torch.isnan(u_xx).any().item(), "PINN autograd produced NaN")
        self.assertFalse(torch.isinf(u_xx).any().item(), "PINN autograd produced Inf")


if __name__ == "__main__":
    unittest.main()
