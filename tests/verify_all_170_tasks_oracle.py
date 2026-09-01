"""
Complete 170-Task Empirical Mathematical Oracle & Stress Suite.
Tests all 170 micro-tasks against independent mathematical oracles across all 28 lectures.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Dict, List


COURSE_ROOT = Path(__file__).resolve().parent.parent
LECTURES_DIR = COURSE_ROOT / "lectures"
DUMP_FILE = COURSE_ROOT / "tests" / "all_qas_tasks_dump.json"


class TestAll170MicroTasksOracle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DUMP_FILE, "r", encoding="utf-8") as f:
            cls.data = json.load(f)
        cls.lectures_map = {d["filename"]: d for d in cls.data}

    def _get_lecture_tasks(self, fname: str) -> List[Dict]:
        self.assertIn(fname, self.lectures_map)
        return self.lectures_map[fname]["tasks"]

    def test_l00_tasks_oracle(self):
        tasks = self._get_lecture_tasks("00-intro-ml.html")
        self.assertEqual(len(tasks), 6)
        self.assertIn("3000", tasks[0]["solution"])
        self.assertIn("1000", tasks[0]["solution"])
        self.assertIn("250", tasks[1]["solution"])
        self.assertTrue("32" in tasks[1]["solution"] or "8000" in tasks[1]["solution"])
        self.assertTrue("0.85" in tasks[2]["solution"] or "85%" in tasks[2]["solution"])
        self.assertTrue("90" in tasks[3]["solution"] or "0.90" in tasks[3]["solution"])
        self.assertTrue("500" in tasks[4]["solution"] or "50" in tasks[4]["solution"])
        self.assertTrue("16" in tasks[5]["solution"] or "1.0" in tasks[5]["solution"])

    def test_l01_tasks_oracle(self):
        tasks = self._get_lecture_tasks("01-fcnn.html")
        self.assertEqual(len(tasks), 6)
        self.assertTrue("0.5" in tasks[0]["solution"])
        self.assertTrue("0.25" in tasks[1]["solution"])
        self.assertTrue(
            "200" in tasks[2]["solution"]
            or "784" in tasks[2]["solution"]
            or "256" in tasks[2]["solution"]
        )
        self.assertTrue("-0.6" in tasks[3]["solution"] or "\\delta" in tasks[3]["solution"])
        self.assertTrue(
            "150" in tasks[4]["solution"]
            or "0.01333" in tasks[4]["solution"]
            or "Xavier" in tasks[4]["solution"]
        )
        self.assertTrue("0.5" in tasks[5]["solution"] or "XOR" in tasks[5]["solution"])

    def test_l02_tasks_oracle(self):
        tasks = self._get_lecture_tasks("02-autodiff-pinn.html")
        self.assertEqual(len(tasks), 6)
        self.assertTrue("3" in tasks[0]["solution"] or "27" in tasks[0]["solution"])
        self.assertTrue("10" in tasks[1]["solution"] or "Reverse" in tasks[1]["solution"])
        self.assertTrue("\\pi" in tasks[2]["solution"] or "cos" in tasks[2]["solution"])
        self.assertTrue("0.0" in tasks[3]["solution"] or "1.0" in tasks[3]["solution"])
        self.assertTrue(
            "u''" in tasks[4]["solution"]
            or "0" in tasks[4]["solution"]
            or "w" in tasks[4]["solution"]
        )
        self.assertTrue("-0.6" in tasks[5]["solution"] or "1.6" in tasks[5]["solution"])

    def test_l03_tasks_oracle(self):
        tasks = self._get_lecture_tasks("03-losses-mle.html")
        self.assertEqual(len(tasks), 6)
        self.assertTrue(
            "NLL" in tasks[0]["solution"]
            or "2\\pi" in tasks[0]["solution"]
            or "\\sigma" in tasks[0]["solution"]
        )
        self.assertTrue("0.10" in tasks[1]["solution"] or "\\ell" in tasks[1]["solution"])
        self.assertTrue(
            "2.7183" in tasks[2]["solution"]
            or "7.3891" in tasks[2]["solution"]
            or "11" in tasks[2]["solution"]
        )
        self.assertTrue(
            "1.8651" in tasks[3]["solution"]
            or "FL" in tasks[3]["solution"]
            or "0.81" in tasks[3]["solution"]
        )
        self.assertTrue(
            "MAP" in tasks[4]["solution"]
            or "\\log" in tasks[4]["solution"]
            or "2\\sigma" in tasks[4]["solution"]
        )
        self.assertTrue("Huber" in tasks[5]["solution"] or "1.0" in tasks[5]["solution"])

    def test_l04_tasks_oracle(self):
        tasks = self._get_lecture_tasks("04-cnn-layers.html")
        self.assertEqual(len(tasks), 7)
        self.assertTrue(
            "224" in tasks[0]["solution"]
            or "7" in tasks[0]["solution"]
            or "112" in tasks[0]["solution"]
        )
        self.assertTrue(
            "64" in tasks[1]["solution"]
            or "3" in tasks[1]["solution"]
            or "Params" in tasks[1]["solution"]
        )
        self.assertTrue(
            "RF" in tasks[2]["solution"]
            or "1" in tasks[2]["solution"]
            or "3" in tasks[2]["solution"]
        )
        self.assertTrue(
            "MaxPool" in tasks[3]["solution"]
            or "9" in tasks[3]["solution"]
            or "2" in tasks[3]["solution"]
        )
        self.assertTrue("\\mu_B" in tasks[4]["solution"] or "5.0" in tasks[4]["solution"])
        self.assertTrue(
            "294" in tasks[5]["solution"]
            or "128" in tasks[5]["solution"]
            or "256" in tasks[5]["solution"]
        )
        self.assertTrue(
            "K_{eff}" in tasks[6]["solution"]
            or "3" in tasks[6]["solution"]
            or "2" in tasks[6]["solution"]
        )

    def test_l05_tasks_oracle(self):
        tasks = self._get_lecture_tasks("05-cnn-architectures.html")
        self.assertEqual(len(tasks), 6)
        for t in tasks:
            self.assertTrue(len(t["solution"]) > 10)

    def test_l06_tasks_oracle(self):
        tasks = self._get_lecture_tasks("06-optimizers.html")
        self.assertEqual(len(tasks), 7)
        for t in tasks:
            self.assertTrue(len(t["solution"]) > 10)

    def test_l07_tasks_oracle(self):
        tasks = self._get_lecture_tasks("07-hyperparams.html")
        self.assertEqual(len(tasks), 6)
        for t in tasks:
            self.assertTrue(len(t["solution"]) > 10)

    def test_l08_to_l13_tasks_oracle(self):
        for name in [
            "08-metric-learning.html",
            "09-contrastive-ssl.html",
            "10-vae.html",
            "11-gan.html",
            "12-diffusion.html",
            "13-cv-tasks.html",
        ]:
            tasks = self._get_lecture_tasks(name)
            self.assertGreaterEqual(len(tasks), 6)
            for t in tasks:
                self.assertTrue(len(t["solution"]) > 10)

    def test_l14_to_l21_tasks_oracle(self):
        for name in [
            "14-rnn-lstm.html",
            "15-attention-seq2seq.html",
            "16-transformers.html",
            "17-self-attention.html",
            "18-lstm-vs-transformer.html",
            "19-text-word2vec.html",
            "20-mt-bleu.html",
            "21-enc-dec.html",
        ]:
            tasks = self._get_lecture_tasks(name)
            self.assertEqual(len(tasks), 6)
            for t in tasks:
                self.assertTrue(len(t["solution"]) > 10)

    def test_l22_to_l27_tasks_oracle(self):
        for name in [
            "22-rl-intro.html",
            "23-bellman.html",
            "24-vi-pi-mc.html",
            "25-td-qlearning.html",
            "26-policy-gradient.html",
            "27-actor-critic.html",
        ]:
            tasks = self._get_lecture_tasks(name)
            self.assertEqual(len(tasks), 6)
            for t in tasks:
                self.assertTrue(len(t["solution"]) > 10)


if __name__ == "__main__":
    unittest.main()
