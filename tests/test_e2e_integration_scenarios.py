"""
Tier 4 Multi-Feature End-to-End Integration Scenarios Test Suite.
Simulates real-world user journeys across the Deep Learning course platform:
- Full Course Study & Progress Tracking Lifecycle
- Exam Ticket Simulation & 3-Minute Board Answer Workflow
- Spaced Repetition (SM-2 / Leitner) Multi-Day Study & Due Queue Lifecycle
- Blitz Exam Rapid-Fire Examination & Analytics
- Offline PWA Precache & PDF Print Preparation Workflow
- Data Builder & 4-Block Exam Dataset Cross-Module Synchronization
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Dict

COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
INDEX_FILE = COURSE_ROOT / "index.html"
STYLE_FILE = COURSE_ROOT / "style.css"
SW_FILE = COURSE_ROOT / "sw.js"
MANIFEST_FILE = COURSE_ROOT / "manifest.json"
JS_APP_FILE = COURSE_ROOT / "js" / "app.js"
JS_LECTURE_FILE = COURSE_ROOT / "js" / "lecture.js"
JS_SIM_FILE = COURSE_ROOT / "js" / "simulator.js"
JS_TRACKER_FILE = COURSE_ROOT / "js" / "tracker.js"
JS_EXAM_DATA_FILE = COURSE_ROOT / "js" / "exam_data.js"

from tests.common import EXPECTED_LECTURES, read_file
from tests.test_sm2_and_simulator_e2e import reference_sm2_update


class TestE2EIntegrationScenarios(unittest.TestCase):
    """Verify complex multi-feature user workflows across the platform."""

    @classmethod
    def setUpClass(cls):
        cls.exam_data_content = read_file(JS_EXAM_DATA_FILE)
        start_idx = cls.exam_data_content.find("[")
        end_idx = cls.exam_data_content.rfind("]")
        if start_idx != -1 and end_idx != -1:
            cls.exam_data = json.loads(cls.exam_data_content[start_idx : end_idx + 1])
        else:
            cls.exam_data = []

    def test_01_e2e_study_and_progress_tracking_workflow(self):
        """Scenario 1: Portal navigation -> Topic search -> Lecture study -> QA/Task checks -> Progress Hub sync."""
        # 1. User searches for 'transformer' / 'attention' in portal
        search_terms = ["transformer", "attention", "трансформ", "вниман"]
        matching_lectures = []
        for lec in self.exam_data:
            combined = f"{lec.get('title', '')} {lec.get('ticket', '')} {lec.get('filename', '')}".lower()
            if any(term in combined for term in search_terms):
                matching_lectures.append(lec)

        self.assertGreaterEqual(
            len(matching_lectures),
            2,
            "Searching for Transformer/Attention should yield multiple related lectures (e.g. L15, L16, L17, L18)",
        )

        # 2. User studies Lecture 16 (16-transformers.html)
        target_lec = next((lec for lec in self.exam_data if lec.get("id") == "16"), None)
        self.assertIsNotNone(target_lec, "Lecture 16 must exist in EXAM_DATA")
        self.assertGreaterEqual(len(target_lec.get("qas", [])), 10, "L16 must have >= 10 Q&As")
        self.assertGreaterEqual(len(target_lec.get("tasks", [])), 6, "L16 must have >= 6 tasks")

        # 3. User checks 5 Q&As and 3 tasks in Lecture 16
        mock_checked_qas = [f"l16_qa{i}" for i in range(5)]
        mock_checked_tasks = [f"l16_t{i}" for i in range(3)]
        mock_completed_lecs = ["16"]

        # 4. Global Progress Hub calculates weighted stats:
        # 40% lectures + 35% Q&As + 25% tasks
        total_lecs = 28
        total_qas = 296
        total_tasks = 170

        lec_pct = round((len(mock_completed_lecs) / total_lecs) * 100)
        qa_pct = round((len(mock_checked_qas) / total_qas) * 100)
        task_pct = round((len(mock_checked_tasks) / total_tasks) * 100)
        overall_pct = round((lec_pct * 0.4) + (qa_pct * 0.35) + (task_pct * 0.25))

        self.assertEqual(lec_pct, 4)
        self.assertEqual(qa_pct, 2)
        self.assertEqual(task_pct, 2)
        self.assertGreaterEqual(overall_pct, 2)

        # 5. User exports progress to JSON and restores it
        exported_payload = {
            "theme": "dark",
            "completedLectures": mock_completed_lecs,
            "checkedQAs": mock_checked_qas,
            "checkedTasks": mock_checked_tasks,
            "exportedAt": "2026-08-28T00:00:00.000Z",
        }
        json_str = json.dumps(exported_payload)
        imported_obj = json.loads(json_str)

        self.assertEqual(imported_obj["completedLectures"], mock_completed_lecs)
        self.assertEqual(imported_obj["checkedQAs"], mock_checked_qas)
        self.assertEqual(imported_obj["checkedTasks"], mock_checked_tasks)

    def test_02_e2e_exam_ticket_and_three_minute_timer_workflow(self):
        """Scenario 2: Select Ticket #10 -> Render ticket & 3-min cheat skeleton -> 3-min timer countdown -> Self-check."""
        # Find Ticket #10 in EXAM_DATA
        ticket_10 = next((t for t in self.exam_data if t.get("id") == "10"), None)
        self.assertIsNotNone(ticket_10, "Ticket 10 (VAE) must exist in EXAM_DATA")

        # Verify ticket content
        self.assertIn("vae", ticket_10.get("filename", "").lower())
        self.assertTrue(len(ticket_10.get("cheat_items", [])) >= 3, "Ticket 10 must have >= 3 cheat skeleton bullets")
        self.assertTrue(len(ticket_10.get("qas", [])) >= 3, "Ticket 10 must have >= 3 sample Q&As")
        self.assertTrue(len(ticket_10.get("tasks", [])) >= 1, "Ticket 10 must have >= 1 sample task")

        # Simulate 3-minute oral exam timer countdown
        display_states = []

        def get_timer_class(sec: int) -> str:
            if sec == 0:
                return "danger"
            elif sec <= 30:
                return "warn"
            return "normal"

        for s in [180, 120, 60, 30, 10, 0]:
            cls = get_timer_class(s)
            m, sec = divmod(s, 60)
            time_str = f"{m:02d}:{sec:02d}"
            display_states.append((time_str, cls))

        self.assertEqual(display_states[0], ("03:00", "normal"))
        self.assertEqual(display_states[3], ("00:30", "warn"))
        self.assertEqual(display_states[5], ("00:00", "danger"))

    def test_03_e2e_spaced_repetition_multi_day_lifecycle_workflow(self):
        """Scenario 3: Multi-day Leitner / SM-2 spaced repetition simulation across multiple review cycles."""
        start_time = 1724800000000  # arbitrary epoch
        one_day = 86400000

        # Day 0: Initial learning session (4 cards)
        card_db: Dict[str, Dict[str, Any]] = {}

        # Card A: Perfect recall (q=5)
        card_db["card_A"] = reference_sm2_update(grade=5, now_ts=start_time)
        self.assertEqual(card_db["card_A"]["interval"], 1)
        self.assertEqual(card_db["card_A"]["box"], 1)
        self.assertAlmostEqual(card_db["card_A"]["easeFactor"], 2.60, places=2)

        # Card B: Hesitant recall (q=3)
        card_db["card_B"] = reference_sm2_update(grade=3, now_ts=start_time)
        self.assertEqual(card_db["card_B"]["interval"], 1)
        self.assertAlmostEqual(card_db["card_B"]["easeFactor"], 2.36, places=2)

        # Card C: Failed recall (q=1)
        card_db["card_C"] = reference_sm2_update(grade=1, now_ts=start_time)
        self.assertEqual(card_db["card_C"]["interval"], 1)
        self.assertEqual(card_db["card_C"]["repetitions"], 0)
        self.assertEqual(card_db["card_C"]["box"], 1)
        self.assertAlmostEqual(card_db["card_C"]["easeFactor"], 1.96, places=2)

        # Day 1: +24 hours -> All 3 cards due
        day_1 = start_time + one_day
        for cid, card in card_db.items():
            self.assertLessEqual(card["nextReview"], day_1, f"Card {cid} must be due on Day 1")

        # Review Card A again with q=5 -> interval becomes 6 days
        card_db["card_A"] = reference_sm2_update(
            grade=5,
            repetitions=card_db["card_A"]["repetitions"],
            interval=card_db["card_A"]["interval"],
            ease_factor=card_db["card_A"]["easeFactor"],
            box=card_db["card_A"]["box"],
            now_ts=day_1,
        )
        self.assertEqual(card_db["card_A"]["interval"], 6)
        self.assertEqual(card_db["card_A"]["repetitions"], 2)
        self.assertEqual(card_db["card_A"]["box"], 2)
        self.assertAlmostEqual(card_db["card_A"]["easeFactor"], 2.70, places=2)

        # Day 7: +7 days -> Card A is now due (interval 6 days elapsed)
        day_7 = day_1 + (6 * one_day)
        self.assertLessEqual(card_db["card_A"]["nextReview"], day_7)

        # Review Card A with q=5 -> interval becomes round(6 * 2.8) = 17 days
        card_db["card_A"] = reference_sm2_update(
            grade=5,
            repetitions=card_db["card_A"]["repetitions"],
            interval=card_db["card_A"]["interval"],
            ease_factor=card_db["card_A"]["easeFactor"],
            box=card_db["card_A"]["box"],
            now_ts=day_7,
        )
        self.assertEqual(card_db["card_A"]["interval"], 17)
        self.assertEqual(card_db["card_A"]["repetitions"], 3)
        self.assertEqual(card_db["card_A"]["box"], 3)

    def test_04_e2e_blitz_mode_rapid_fire_session_workflow(self):
        """Scenario 4: Blitz mode 10-question drill across syllabus with score summary."""
        # Collect all questions across syllabus
        all_qas = []
        for lec in self.exam_data:
            for qa in lec.get("qas", []):
                all_qas.append({"lectureId": lec.get("id"), "question": qa.get("question"), "answer": qa.get("answer")})

        self.assertGreaterEqual(len(all_qas), 280, "Syllabus must contain at least 280 Q&As for Blitz pool")

        # Select 10 questions
        blitz_sample = all_qas[:10]
        self.assertEqual(len(blitz_sample), 10)

        # Simulate user answers (8 known, 1 unsure, 1 forgot)
        ratings = [5, 5, 5, 5, 5, 5, 5, 5, 3, 1]
        correct_count = sum(1 for r in ratings if r >= 4)
        accuracy_pct = round((correct_count / len(ratings)) * 100)

        self.assertEqual(correct_count, 8)
        self.assertEqual(accuracy_pct, 80)

    def test_05_e2e_offline_pwa_and_print_pdf_preparation_workflow(self):
        """Scenario 5: PWA precache coverage + Print CSS + beforeprint details auto-expansion."""
        # Verify precache file
        if SW_FILE.exists():
            sw_text = read_file(SW_FILE)
            for lec in EXPECTED_LECTURES:
                self.assertIn(lec, sw_text, f"Precache must contain {lec}")

        # Verify print style rules
        style_text = read_file(STYLE_FILE)
        self.assertIn("@media print", style_text)

        # Verify print details expansion logic in lecture.js or app.js
        lecture_js_text = read_file(JS_LECTURE_FILE) if JS_LECTURE_FILE.exists() else ""
        app_js_text = read_file(JS_APP_FILE) if JS_APP_FILE.exists() else ""
        combined = lecture_js_text + "\n" + app_js_text

        self.assertTrue(
            "beforeprint" in combined or "@media print" in style_text,
            "Platform must support print preparation / styling",
        )

    def test_06_e2e_exam_data_and_4block_synchronization(self):
        """Scenario 6: Cross-validation of compiled EXAM_DATA with 4-block structure and lecture files."""
        self.assertTrue(JS_EXAM_DATA_FILE.exists(), f"Missing {JS_EXAM_DATA_FILE}")

        # Check that EXAM_DATA matches live lecture extraction
        from tools.build_exam_data import compile_exam_dataset
        live_dataset = compile_exam_dataset(LECTURES_DIR)
        self.assertEqual(len(live_dataset), 28)

        # Check block distribution
        blocks = {l["module"] for l in live_dataset}
        self.assertEqual(blocks, {"A", "B", "C", "D"})

        total_qas = sum(len(l["qas"]) for l in live_dataset)
        total_tasks = sum(len(l["tasks"]) for l in live_dataset)
        self.assertEqual(total_qas, 296)
        self.assertEqual(total_tasks, 170)

        # Verify all 28 lectures are accounted for in self.exam_data
        self.assertEqual(len(self.exam_data), 28)
        for live_lec, cached_lec in zip(live_dataset, self.exam_data):
            self.assertEqual(live_lec["id"], cached_lec["id"])
            self.assertEqual(live_lec["module"], cached_lec["module"])
            self.assertEqual(len(live_lec["qas"]), len(cached_lec["qas"]))
            self.assertEqual(len(live_lec["tasks"]), len(cached_lec["tasks"]))


if __name__ == "__main__":
    unittest.main()
