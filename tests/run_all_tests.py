"""
Master Test Runner for Deep Learning Course Verification Suite.
Executes Requirements R1, R2, R3, and R4 test suites and outputs structured report.
"""

from __future__ import annotations

import sys
import time
import unittest
from io import StringIO
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure course root is on python path
COURSE_ROOT = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))

# Import test suites
from tests.test_r1_coverage import TestR1Coverage
from tests.test_r2_math_latex import TestR2MathLatex
from tests.test_r3_code_exec import TestR3CodeExec
from tests.test_r4_structure_nav import TestR4StructureNav
from tests.test_r5_summary_styling import TestR5SummaryStyling
from tests.test_adversarial_challenges import TestAdversarialChallenges
from tests.test_syllabus_mathematical_forensics import TestSyllabusForensics
from tests.test_qa_pill_sync import TestQAPillSync
from tests.test_adversarial_challenger_2 import (
    TestDOMAndPillInvariants,
    TestLinkGraphAndAnchors,
    TestAdversarialDynamicCodeExecution,
)
from tests.test_challenger1_forensics import (
    TestChallenger1MicroTasksAndQAs,
    TestSyllabusTicketAlignmentGUU26,
)
from tests.verify_deep_microtasks_arithmetic import TestDeepMicrotasksForensics
from tests.verify_all_170_tasks_oracle import TestAll170MicroTasksOracle


class DetailedTestResult(unittest.TestResult):
    """Custom TestResult collecting granular status and failure info."""

    def __init__(self):
        super().__init__()
        self.successes: List[unittest.TestCase] = []

    def addSuccess(self, test: unittest.TestCase):
        super().addSuccess(test)
        self.successes.append(test)


def run_suite_and_gather_stats(suite_class, suite_name: str) -> Dict:
    """Run a single test suite class and extract statistics."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(suite_class)
    result = DetailedTestResult()

    start_time = time.time()
    suite.run(result)
    duration = time.time() - start_time

    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = len(result.successes)
    success_rate = (passed / total * 100) if total > 0 else 0.0

    failure_details = []
    for test, trace in result.failures:
        failure_details.append({"test": test.id().split(".")[-1], "error": trace.strip()})
    for test, trace in result.errors:
        failure_details.append({"test": test.id().split(".")[-1], "error": trace.strip()})

    return {
        "name": suite_name,
        "class": suite_class.__name__,
        "total": total,
        "passed": passed,
        "failed": failures,
        "errors": errors,
        "skipped": skipped,
        "duration": duration,
        "success_rate": success_rate,
        "failure_details": failure_details,
    }


def main():
    print("=" * 80)
    print("    DEEP LEARNING COURSE E2E VERIFICATION SUITE (GUU 2026)")
    print("=" * 80)

    suites_to_run = [
        (TestR1Coverage, "R1: Syllabus & Coverage Audit"),
        (TestR2MathLatex, "R2: Math & LaTeX Verification"),
        (TestR3CodeExec, "R3: Code & Implementation Check"),
        (TestR4StructureNav, "R4: Structure & Navigation Integrity"),
        (TestR5SummaryStyling, "R5: Summary Marker & Arrow Polish"),
        (TestAdversarialChallenges, "Adversarial Stress & Boundary Suite"),
        (TestSyllabusForensics, "Syllabus Mathematical Forensic Suite"),
        (TestQAPillSync, "QA Pill Badge Exact Sync Suite"),
        (TestDOMAndPillInvariants, "Challenger 2: DOM & Pill Invariants"),
        (TestLinkGraphAndAnchors, "Challenger 2: Link Graph & Dead Anchors"),
        (TestAdversarialDynamicCodeExecution, "Challenger 2: Dynamic Code Edge Tests"),
        (TestChallenger1MicroTasksAndQAs, "Challenger 1: Micro-Tasks & Q&A Suite"),
        (TestSyllabusTicketAlignmentGUU26, "Challenger 1: GUU 2026 Syllabus Tickets"),
        (TestDeepMicrotasksForensics, "Challenger 1: Deep Microtasks Completeness"),
        (TestAll170MicroTasksOracle, "Challenger 1: All 170 Tasks Oracle"),
    ]

    results = []
    total_tests = 0
    total_passed = 0
    total_failed = 0
    total_errors = 0
    total_skipped = 0
    total_duration = 0.0

    for suite_cls, suite_name in suites_to_run:
        stats = run_suite_and_gather_stats(suite_cls, suite_name)
        results.append(stats)
        total_tests += stats["total"]
        total_passed += stats["passed"]
        total_failed += stats["failed"]
        total_errors += stats["errors"]
        total_skipped += stats["skipped"]
        total_duration += stats["duration"]

    # Print summary table
    print("\nSUMMARY OF REQUIREMENTS VERIFICATION:")
    print("-" * 80)
    header = f"{'Requirement Suite':<38} | {'Total':<6} | {'Pass':<6} | {'Fail':<6} | {'Err':<5} | {'Rate':<7}"
    print(header)
    print("-" * 80)

    for st in results:
        status_line = (
            f"{st['name']:<38} | {st['total']:<6} | {st['passed']:<6} | "
            f"{st['failed']:<6} | {st['errors']:<5} | {st['success_rate']:>5.1f}%"
        )
        print(status_line)

    print("-" * 80)
    overall_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0.0
    total_line = (
        f"{'TOTAL COURSE VERIFICATION':<38} | {total_tests:<6} | {total_passed:<6} | "
        f"{total_failed:<6} | {total_errors:<5} | {overall_rate:>5.1f}%"
    )
    print(total_line)
    print(f"Elapsed Time: {total_duration:.3f}s")
    print("=" * 80)

    # Print detailed failures if any
    has_failures = total_failed > 0 or total_errors > 0
    if has_failures:
        print("\nIDENTIFIED ISSUES & REMEDIATION BACKLOG:")
        print("=" * 80)
        for st in results:
            if st["failure_details"]:
                print(f"\n>>> {st['name']} ({len(st['failure_details'])} failure(s)):")
                for item in st["failure_details"]:
                    print(f"\n  [FAIL] {item['test']}:")
                    # Print first 5 lines of error for clarity
                    lines = item["error"].splitlines()
                    for line in lines[-6:]:
                        print(f"    {line}")
        print("\n" + "=" * 80)

    print("\nVerification status: " + ("ALL TESTS PASSED" if not has_failures else "FAILURES DETECTED (EXPECTED AT BASELINE)"))
    return 1 if has_failures else 0


if __name__ == "__main__":
    sys.exit(main())
