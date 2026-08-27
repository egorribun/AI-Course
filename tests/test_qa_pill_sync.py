"""
Test Suite: Exact Pill Badge QA Synchronization across all 28 lectures.
"""
import glob
import os
import re
import unittest

class TestQAPillSync(unittest.TestCase):
    def test_all_qa_pills_match_exact_counts(self):
        lecture_files = sorted(glob.glob("lectures/*.html"))
        self.assertEqual(len(lecture_files), 28, "Expected 28 lecture files")
        
        for path in lecture_files:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            qa_count = len(re.findall(r'<details\s+class=["\']qa["\']', content))
            pill_match = re.search(r'(\d+)\s+вопрос', content)
            self.assertIsNotNone(pill_match, f"No question pill badge found in {path}")
            
            pill_count = int(pill_match.group(1))
            self.assertEqual(
                qa_count,
                pill_count,
                f"Pill badge mismatch in {path}: badge states {pill_count}, but found {qa_count} QA blocks"
            )
            self.assertGreaterEqual(qa_count, 10, f"QA count < 10 in {path}")

if __name__ == "__main__":
    unittest.main()
