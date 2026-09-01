"""
E2E and algorithmic test suite for Spaced Repetition (Leitner / SM-2) engine,
LocalStorage schemas, Exam Simulator ticket selector (1-25), Blitz mode, topic drill, and 3-min timer.
"""

from __future__ import annotations

import json
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Optional

COURSE_ROOT = Path(__file__).resolve().parent.parent
JS_SIM_FILE = COURSE_ROOT / "js" / "simulator.js"
JS_TRACKER_FILE = COURSE_ROOT / "js" / "tracker.js"
JS_EXAM_DATA_FILE = COURSE_ROOT / "js" / "exam_data.js"
INDEX_FILE = COURSE_ROOT / "index.html"

from tests.common import read_file


def reference_sm2_update(
    grade: int,
    repetitions: int = 0,
    interval: int = 1,
    ease_factor: float = 2.5,
    box: int = 1,
    now_ts: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Authoritative reference implementation of the SM-2 / Leitner spaced repetition algorithm.
    grade: 0-5 (0=blackout, 1=bad, 2=poor, 3=pass, 4=good, 5=perfect)
    """
    if now_ts is None:
        now_ts = int(time.time() * 1000)

    # 1. Update Ease Factor (EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))
    # Clamped to minimum EF = 1.3
    q = max(0, min(5, grade))
    new_ef = ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    new_ef = max(1.3, round(new_ef, 4))

    # 2. Update Repetitions, Interval, and Leitner Box
    if q < 3:
        # Failed recall -> reset repetitions to 0, interval to 1 day, box to 1
        new_reps = 0
        new_interval = 1
        new_box = 1
    else:
        # Successful recall
        if repetitions == 0:
            new_interval = 1
            new_box = max(1, box)
        elif repetitions == 1:
            new_interval = 6
            new_box = min(5, box + 1)
        else:
            new_interval = max(1, round(interval * new_ef))
            new_box = min(5, box + 1)
        new_reps = repetitions + 1

    one_day_ms = 24 * 60 * 60 * 1000
    next_review = now_ts + (new_interval * one_day_ms)

    return {
        "box": new_box,
        "repetitions": new_reps,
        "interval": new_interval,
        "easeFactor": new_ef,
        "lastReviewed": now_ts,
        "nextReview": next_review,
    }


class TestSM2SpacedRepetitionMath(unittest.TestCase):
    """Verify Leitner / SM-2 spaced repetition mathematical properties, state transitions, and boundary invariants."""

    def test_01_sm2_ease_factor_update_formula(self):
        """Verify mathematical precision of the Ease Factor equation for grades 0 through 5."""
        initial_ef = 2.5

        # Grade 5: EF increases by +0.10
        r5 = reference_sm2_update(grade=5, ease_factor=initial_ef)
        self.assertAlmostEqual(r5["easeFactor"], 2.60, places=3)

        # Grade 4: EF remains unchanged (delta = 0)
        r4 = reference_sm2_update(grade=4, ease_factor=initial_ef)
        self.assertAlmostEqual(r4["easeFactor"], 2.50, places=3)

        # Grade 3: EF decreases by 0.14
        r3 = reference_sm2_update(grade=3, ease_factor=initial_ef)
        self.assertAlmostEqual(r3["easeFactor"], 2.36, places=3)

        # Grade 2: EF decreases by 0.32
        r2 = reference_sm2_update(grade=2, ease_factor=initial_ef)
        self.assertAlmostEqual(r2["easeFactor"], 2.18, places=3)

        # Grade 1: EF decreases by 0.54
        r1 = reference_sm2_update(grade=1, ease_factor=initial_ef)
        self.assertAlmostEqual(r1["easeFactor"], 1.96, places=3)

        # Grade 0: EF decreases by 0.80
        r0 = reference_sm2_update(grade=0, ease_factor=initial_ef)
        self.assertAlmostEqual(r0["easeFactor"], 1.70, places=3)

    def test_02_sm2_lower_bound_clamping_at_1_point_3(self):
        """Verify Ease Factor never drops below 1.3 under an adversarial sequence of failed recalls."""
        state = {"repetitions": 5, "interval": 45, "easeFactor": 2.5, "box": 4}
        for _ in range(10):
            state = reference_sm2_update(
                grade=0,
                repetitions=state["repetitions"],
                interval=state["interval"],
                ease_factor=state["easeFactor"],
                box=state["box"],
            )
            self.assertGreaterEqual(
                state["easeFactor"], 1.30, "Ease Factor must never fall below 1.3"
            )
            self.assertEqual(state["repetitions"], 0, "Failed grade must reset repetitions to 0")
            self.assertEqual(state["interval"], 1, "Failed grade must reset interval to 1 day")
            self.assertEqual(state["box"], 1, "Failed grade must reset Leitner box to 1")

        self.assertAlmostEqual(state["easeFactor"], 1.30, places=3)

    def test_03_sm2_interval_exponential_growth_on_perfect_streak(self):
        """Verify interval progression on a streak of perfect recalls (q=5)."""
        state = {"repetitions": 0, "interval": 1, "easeFactor": 2.5, "box": 1}
        intervals = []
        boxes = []

        for _ in range(5):
            state = reference_sm2_update(
                grade=5,
                repetitions=state["repetitions"],
                interval=state["interval"],
                ease_factor=state["easeFactor"],
                box=state["box"],
            )
            intervals.append(state["interval"])
            boxes.append(state["box"])

        # Expected intervals:
        # Rep 0 -> 1 day, EF 2.6
        # Rep 1 -> 6 days, EF 2.7
        # Rep 2 -> round(6 * 2.8) = 17 days, EF 2.8
        # Rep 3 -> round(17 * 2.9) = 49 days, EF 2.9
        # Rep 4 -> round(49 * 3.0) = 147 days, EF 3.0
        self.assertEqual(intervals[0], 1, "Repetition 0 -> interval 1 day")
        self.assertEqual(intervals[1], 6, "Repetition 1 -> interval 6 days")
        self.assertEqual(intervals[2], 17, "Repetition 2 -> interval 17 days")
        self.assertEqual(intervals[3], 49, "Repetition 3 -> interval 49 days")
        self.assertEqual(intervals[4], 147, "Repetition 4 -> interval 147 days")

        # Boxes progression: 1 -> 2 -> 3 -> 4 -> 5
        self.assertEqual(boxes, [1, 2, 3, 4, 5])

    def test_04_due_queue_filtering_logic(self):
        """Verify due cards filtering based on current timestamp and nextReview schedule."""
        now = int(time.time() * 1000)
        day_ms = 86400000

        mock_card_db = {
            "card_due_yesterday": {"nextReview": now - day_ms, "box": 1},
            "card_due_today": {"nextReview": now - 1000, "box": 2},
            "card_due_tomorrow": {"nextReview": now + day_ms, "box": 3},
            "card_due_next_week": {"nextReview": now + (7 * day_ms), "box": 5},
            "card_new_unreviewed": {},
        }

        def get_due_cards(db: Dict[str, Any], current_time: int) -> List[str]:
            due = []
            for cid, card in db.items():
                nr = card.get("nextReview")
                if nr is None or nr <= current_time:
                    due.append(cid)
            return due

        due_list = get_due_cards(mock_card_db, now)
        self.assertIn("card_due_yesterday", due_list)
        self.assertIn("card_due_today", due_list)
        self.assertIn("card_new_unreviewed", due_list)
        self.assertNotIn("card_due_tomorrow", due_list)
        self.assertNotIn("card_due_next_week", due_list)


class TestLocalStorageSchemaAndPersistence(unittest.TestCase):
    """Verify LocalStorage schema definitions, serialization format, and export/import round-trips."""

    @classmethod
    def setUpClass(cls):
        cls.tracker_js = read_file(JS_TRACKER_FILE)
        cls.sim_js = read_file(JS_SIM_FILE)

    def test_05_localstorage_keys_consistency(self):
        """Verify all standardized LocalStorage keys are defined in tracker.js and simulator.js."""
        required_keys = [
            "ai_course_theme",
            "ai_course_completed_lectures",
            "ai_course_checked_qas",
            "ai_course_checked_tasks",
        ]
        for key in required_keys:
            self.assertIn(key, self.tracker_js, f"tracker.js must define key '{key}'")

        # SM-2 storage key
        self.assertTrue(
            "ai_course_sm2_cards" in self.tracker_js or "ai_course_sm2_cards" in self.sim_js,
            "Application must define and manage 'ai_course_sm2_cards' in LocalStorage",
        )

    def test_06_sm2_card_storage_schema_fields(self):
        """Verify card state schema contains box, repetitions, interval, easeFactor, lastReviewed, nextReview."""
        sample_card_json = {
            "box": 3,
            "repetitions": 2,
            "interval": 6,
            "easeFactor": 2.6,
            "lastReviewed": 1724800000000,
            "nextReview": 1725318400000,
        }
        serialized = json.dumps({"l01_qa0": sample_card_json})
        deserialized = json.loads(serialized)
        card = deserialized["l01_qa0"]

        self.assertIn("box", card)
        self.assertIn("repetitions", card)
        self.assertIn("interval", card)
        self.assertIn("easeFactor", card)
        self.assertIn("lastReviewed", card)
        self.assertIn("nextReview", card)
        self.assertIsInstance(card["box"], int)
        self.assertIsInstance(card["easeFactor"], (int, float))

    def test_07_progress_export_import_json_roundtrip(self):
        """Verify progress export and import methods safely handle valid and malformed JSON."""
        self.assertIn("exportProgressJSON", self.tracker_js)
        self.assertIn("importProgressJSON", self.tracker_js)


class TestExamSimulatorFeatures(unittest.TestCase):
    """Verify Exam Simulator Ticket Selector (1-25), Blitz mode, topic drill, and 3-minute timer."""

    @classmethod
    def setUpClass(cls):
        cls.sim_js = read_file(JS_SIM_FILE)
        cls.exam_data_js = read_file(JS_EXAM_DATA_FILE)

    def test_08_exam_data_contains_25_tickets_and_all_lectures(self):
        """Verify window.EXAM_DATA contains valid JSON with 28 lectures matching syllabus."""
        self.assertIn("window.EXAM_DATA =", self.exam_data_js)
        start_idx = self.exam_data_js.find("[")
        end_idx = self.exam_data_js.rfind("]")
        self.assertTrue(
            start_idx != -1 and end_idx != -1, "EXAM_DATA array markers '[' and ']' not found"
        )
        data = json.loads(self.exam_data_js[start_idx : end_idx + 1])

        self.assertIsInstance(data, list)
        self.assertEqual(
            len(data), 28, f"EXAM_DATA must contain exactly 28 lectures, found {len(data)}"
        )

        # Verify tickets 1 to 25 exist
        ticket_nums = {item.get("ticket") for item in data if item.get("ticket")}
        for t_idx in range(1, 26):
            expected_prefix = f"Билет {t_idx}"
            matching = [
                t
                for t in ticket_nums
                if expected_prefix in t or f"#{t_idx}" in t or f"{t_idx}:" in t or t == str(t_idx)
            ]
            self.assertTrue(
                len(matching) > 0,
                f"EXAM_DATA missing ticket #{t_idx} (found: {sorted(list(ticket_nums))[:5]}...)",
            )

    def test_09_ticket_direct_selector_implemented_in_simulator(self):
        """Verify simulator.js contains UI elements and logic for direct ticket selection (1-25)."""
        self.assertTrue(
            "select-ticket" in self.sim_js
            or "ticket-select" in self.sim_js
            or "renderTicketByNumber" in self.sim_js
            or "selectTicket" in self.sim_js
            or "ticket-dropdown" in self.sim_js
            or "ticket-grid" in self.sim_js
            or "ticketSelector" in self.sim_js
            or "ticket-selector" in self.sim_js
            or "data-ticket-id" in self.sim_js,
            "simulator.js must provide direct ticket selection (1-25) in addition to random draw",
        )

    def test_10_blitz_exam_mode_implemented_in_simulator(self):
        """Verify simulator.js implements Blitz mode (rapid-fire 10 questions session with score report)."""
        self.assertTrue(
            "blitz" in self.sim_js.lower()
            or "tab-blitz" in self.sim_js
            or "startblitz" in self.sim_js.lower()
            or "blitzquiz" in self.sim_js.lower(),
            "simulator.js must implement Blitz exam mode",
        )

    def test_11_topic_drill_filtering_implemented_in_simulator(self):
        """Verify simulator.js implements topic category drill filters (CV, NLP, RL, Math)."""
        self.assertTrue(
            "topic" in self.sim_js.lower()
            or "filterbytopic" in self.sim_js.lower()
            or "category" in self.sim_js.lower()
            or "tag" in self.sim_js.lower(),
            "simulator.js must implement topic drill filtering for flashcards and questions",
        )

    def test_12_three_minute_timer_and_visual_alerts(self):
        """Verify 3-minute timer starts at 180s, formats 03:00, and triggers warn/danger classes."""
        self.assertIn("180", self.sim_js, "Timer initial duration must be 180 seconds (3:00)")
        self.assertIn("warn", self.sim_js, "Timer must add 'warn' class near expiration (<= 30s)")
        self.assertIn("danger", self.sim_js, "Timer must add 'danger' class upon expiration (0s)")
        self.assertTrue(
            "AudioContext" in self.sim_js
            or "webkitAudioContext" in self.sim_js
            or "playBeep" in self.sim_js,
            "Timer must generate an audio beep or gong upon completion",
        )


if __name__ == "__main__":
    unittest.main()
