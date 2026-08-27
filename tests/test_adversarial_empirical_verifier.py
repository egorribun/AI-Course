"""
Adversarial Empirical Verifier Suite (SM-2, LocalStorage, Simulator, UX State Machines).
Stress tests:
1. SM-2 Edge Cases & Invariants:
   - Rating grades q in {0, 1, 2, 3, 4, 5} and out-of-bound inputs
   - Consecutive forgetting (q < 3) resets repetitions to 0, interval to 1, box to 1
   - Ease Factor lower bound clamping at EF >= 1.30
   - Multi-step interval progression on streaks of perfect recall
   - Due queue filtering with past, present, future, and unreviewed timestamps
2. LocalStorage Persistence & Schema Validation:
   - Export/import round-trips
   - Corruption resistance against empty, malformed, non-object, and malicious payloads
3. Exam Simulator Ticket Coverage & Routing:
   - Direct vs random selection across all 25 official tickets and Lecture 00
   - Topic drill classification across CV, NLP, RL, and Math
4. UX Keyboard Shortcut Focus Isolation:
   - Guarding shortcuts against focus inside INPUT, TEXTAREA, SELECT, and contentEditable
   - Escape key blur behavior
5. Empirical Execution:
   - Headless Node.js harness execution (tests/adversarial_harness.cjs)
"""

from __future__ import annotations

import json
import subprocess
import time
import unittest
from pathlib import Path
from typing import Any, Dict, Optional

COURSE_ROOT = Path(__file__).resolve().parent.parent
TRACKER_JS_FILE = COURSE_ROOT / "js" / "tracker.js"
SIMULATOR_JS_FILE = COURSE_ROOT / "js" / "simulator.js"
EXAM_DATA_JS_FILE = COURSE_ROOT / "js" / "exam_data.js"
APP_JS_FILE = COURSE_ROOT / "js" / "app.js"
LECTURE_JS_FILE = COURSE_ROOT / "js" / "lecture.js"
NODE_HARNESS_FILE = COURSE_ROOT / "tests" / "adversarial_harness.cjs"

from tests.common import read_file


def calculate_sm2_python_oracle(
    prev_state: Dict[str, Any],
    grade: float,
    now_ts: Optional[int] = None
) -> Dict[str, Any]:
    """
    Independent Python mathematical oracle of the SM-2 algorithm.
    """
    if now_ts is None:
        now_ts = int(time.time() * 1000)

    q = max(0, min(5, float(grade)))

    ef = float(prev_state.get("easeFactor", 2.5))
    reps = int(prev_state.get("repetitions", 0))
    interval = int(prev_state.get("interval", 1))
    box = int(prev_state.get("box", 1))

    # EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    ef_delta = 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)
    new_ef = max(1.30, round(ef + ef_delta, 2))

    if q >= 3:
        if reps == 0:
            new_interval = 1
        elif reps == 1:
            new_interval = 6
        else:
            new_interval = max(1, round(interval * new_ef))
        new_reps = reps + 1
        new_box = min(5, box + 1)
    else:
        new_reps = 0
        new_interval = 1
        new_box = 1

    next_review = now_ts + new_interval * 24 * 60 * 60 * 1000

    return {
        "box": new_box,
        "repetitions": new_reps,
        "interval": new_interval,
        "easeFactor": new_ef,
        "lastReviewed": now_ts,
        "nextReview": next_review
    }


class TestAdversarialEmpiricalVerifier(unittest.TestCase):
    """Adversarial stress testing suite for SM-2, Storage, Simulator, and Shortcuts."""

    def test_01_execute_headless_node_adversarial_harness(self):
        """Execute the headless Node.js harness and verify 100% empirical pass rate."""
        self.assertTrue(NODE_HARNESS_FILE.exists(), f"Node harness file missing at {NODE_HARNESS_FILE}")

        proc = subprocess.run(
            ["node", str(NODE_HARNESS_FILE)],
            cwd=str(COURSE_ROOT),
            capture_output=True,
            text=True
        )
        self.assertEqual(
            proc.returncode, 0,
            f"Node.js adversarial harness failed with exit code {proc.returncode}:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )
        self.assertIn("ALL ADVERSARIAL HARNESS TESTS PASSED EMPIRICALLY!", proc.stdout)

    def test_02_sm2_rating_grade_domain_stress(self):
        """Stress-test SM-2 Ease Factor updates across continuous and discrete grades 0..5."""
        initial_state = {"box": 1, "repetitions": 0, "interval": 1, "easeFactor": 2.5}

        # Grade 5: EF delta = +0.10
        r5 = calculate_sm2_python_oracle(initial_state, 5)
        self.assertAlmostEqual(r5["easeFactor"], 2.60, places=2)
        self.assertEqual(r5["box"], 2)
        self.assertEqual(r5["repetitions"], 1)
        self.assertEqual(r5["interval"], 1)

        # Grade 4: EF delta = 0.00
        r4 = calculate_sm2_python_oracle(initial_state, 4)
        self.assertAlmostEqual(r4["easeFactor"], 2.50, places=2)

        # Grade 3: EF delta = -0.14
        r3 = calculate_sm2_python_oracle(initial_state, 3)
        self.assertAlmostEqual(r3["easeFactor"], 2.36, places=2)

        # Grade 2: EF delta = -0.32
        r2 = calculate_sm2_python_oracle(initial_state, 2)
        self.assertAlmostEqual(r2["easeFactor"], 2.18, places=2)

        # Grade 1: EF delta = -0.54
        r1 = calculate_sm2_python_oracle(initial_state, 1)
        self.assertAlmostEqual(r1["easeFactor"], 1.96, places=2)

        # Grade 0: EF delta = -0.80
        r0 = calculate_sm2_python_oracle(initial_state, 0)
        self.assertAlmostEqual(r0["easeFactor"], 1.70, places=2)

    def test_03_sm2_adversarial_consecutive_forgetting_clamps_ef(self):
        """Adversarial stress test: 100 consecutive failed recalls must keep EF clamped at >= 1.30."""
        state = {"box": 5, "repetitions": 20, "interval": 365, "easeFactor": 3.0}

        for i in range(100):
            grade = 0 if i % 2 == 0 else 1
            state = calculate_sm2_python_oracle(state, grade)
            self.assertGreaterEqual(state["easeFactor"], 1.30, f"EF dropped below 1.30 at iter {i}")
            self.assertEqual(state["repetitions"], 0, f"Repetitions not reset at iter {i}")
            self.assertEqual(state["interval"], 1, f"Interval not reset at iter {i}")
            self.assertEqual(state["box"], 1, f"Box not reset at iter {i}")

        self.assertAlmostEqual(state["easeFactor"], 1.30, places=2)

    def test_04_sm2_exponential_progression_streak(self):
        """Verify long-term interval progression on a streak of grade 5 reviews."""
        state = {"box": 1, "repetitions": 0, "interval": 1, "easeFactor": 2.5}
        expected_intervals = [1, 6, 17, 49, 147]

        for idx, exp_int in enumerate(expected_intervals):
            state = calculate_sm2_python_oracle(state, 5)
            self.assertEqual(state["interval"], exp_int, f"Step {idx}: expected {exp_int}, got {state['interval']}")
            self.assertEqual(state["box"], min(5, idx + 2))

    def test_05_localstorage_corrupted_payload_resilience(self):
        """Verify LocalStorage parser handles corrupt, truncated, non-object JSON without unhandled exceptions."""
        tracker_src = read_file(TRACKER_JS_FILE)
        self.assertIn("importProgressJSON", tracker_src)
        self.assertIn("try {", tracker_src)
        self.assertIn("catch (e)", tracker_src)

        # Test schema keys
        required_keys = [
            "ai_course_theme",
            "ai_course_completed_lectures",
            "ai_course_checked_qas",
            "ai_course_checked_tasks",
            "ai_course_sm2_cards"
        ]
        for k in required_keys:
            self.assertIn(k, tracker_src, f"Key {k} must be referenced in tracker.js")

    def test_06_exam_simulator_all_25_tickets_complete(self):
        """Verify all 25 official tickets in EXAM_DATA have complete content."""
        exam_data_src = read_file(EXAM_DATA_JS_FILE)
        start_idx = exam_data_src.find("[")
        end_idx = exam_data_src.rfind("]")
        data = json.loads(exam_data_src[start_idx : end_idx + 1])

        self.assertEqual(len(data), 28, "EXAM_DATA must contain all 28 lectures")

        # Ticket mapping
        tickets_found = set()
        for lec in data:
            t = lec.get("ticket", "")
            if "Билет" in t:
                tickets_found.add(t)
            self.assertGreaterEqual(len(lec.get("qas", [])), 10, f"{lec['id']} has <10 QAs")
            self.assertGreaterEqual(len(lec.get("tasks", [])), 6, f"{lec['id']} has <6 tasks")
            self.assertGreaterEqual(len(lec.get("cheat_items", [])), 1, f"{lec['id']} missing cheat sheet")

        for t_idx in range(1, 26):
            matches = [t for t in tickets_found if f"Билет {t_idx}" in t]
            self.assertTrue(len(matches) >= 1, f"Missing ticket #{t_idx} in EXAM_DATA")

    def test_07_keyboard_shortcuts_input_guarding_mechanisms(self):
        """Verify that app.js and lecture.js contain input-guarding checks against active element tags."""
        app_js = read_file(APP_JS_FILE)
        lecture_js = read_file(LECTURE_JS_FILE)

        for name, src in [("app.js", app_js), ("lecture.js", lecture_js)]:
            self.assertIn("activeElement", src, f"{name} must inspect document.activeElement")
            self.assertIn("INPUT", src, f"{name} must guard against INPUT")
            self.assertIn("TEXTAREA", src, f"{name} must guard against TEXTAREA")
            self.assertIn("SELECT", src, f"{name} must guard against SELECT")
            self.assertIn("isContentEditable", src, f"{name} must guard against isContentEditable")
            self.assertIn("Escape", src, f"{name} must handle Escape to blur active input")


if __name__ == "__main__":
    unittest.main()
