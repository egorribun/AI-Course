"""
Master 5-Tier Test Runner for Deep Learning Course Verification Suite (GUU 2026).
Orchestrates Tier 1 to Tier 5 execution with structured visual reporting, timing, and pass/fail summary.
"""

from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path
from typing import Any, Dict, List, Tuple

COURSE_ROOT = Path(__file__).resolve().parent.parent
if str(COURSE_ROOT) not in sys.path:
    sys.path.insert(0, str(COURSE_ROOT))

# Tier 1 Imports
from tests.test_tier1_tools import TestTier1ToolsCoverage
from tests.test_build_exam_data import TestBuildExamData
from tests.test_export_anki import TestExportAnki

# Tier 2 Imports
from tests.test_tier2_static_ast import TestTier2StaticAST
from tests.test_r1_coverage import TestR1Coverage
from tests.test_r2_math_latex import TestR2MathLatex
from tests.test_r3_code_exec import TestR3CodeExec
from tests.test_r4_structure_nav import TestR4StructureNav
from tests.test_all_28_lectures_html_conformance import TestAll28LecturesHTMLConformance
from tests.test_syllabus_mathematical_forensics import TestSyllabusForensics

# Tier 3 Imports
from tests.test_tier3_pwa_dom import TestTier3PWADOM
from tests.test_js_assets_and_tracker import TestJSAssetsAndTracker
from tests.test_exam_simulator import TestExamSimulator
from tests.test_qa_pill_sync import TestQAPillSync
from tests.test_pwa_and_ux_e2e import (
    TestPwaManifestAndServiceWorker,
    TestKeyboardShortcutsAndInteraction,
)

# Tier 4 Imports
from tests.test_tier4_viewport_responsive import TestTier4ViewportResponsive
from tests.test_r5_summary_styling import TestR5SummaryStyling
from tests.test_theme_and_styles import TestThemeAndStyles
from tests.test_portal_ui import TestPortalUI
from tests.test_adversarial_challenger_2 import TestDOMAndPillInvariants
from tests.test_m1_responsive_nav_comprehensive import TestMilestone1ResponsiveNav
from tests.test_lighthouse_and_web_vitals import TestLighthouseAndWebVitals
from tests.test_e2e_requirements import TestE2EPlatformRequirements

# Tier 5 Imports
from tests.test_tier5_adversarial import TestTier5Adversarial
from tests.test_adversarial_challenges import TestAdversarialChallenges
from tests.test_adversarial_challenger_2 import (
    TestLinkGraphAndAnchors,
    TestAdversarialDynamicCodeExecution,
)
from tests.test_adversarial_empirical_challenger2 import (
    TestDynamicPyTorchExecutionRandomized,
    TestLatexBalanceAndASTCheckingExhaustive,
    TestServiceWorkerPrecacheResolution,
)
from tests.test_challenger1_forensics import (
    TestChallenger1MicroTasksAndQAs,
    TestSyllabusTicketAlignmentGUU26,
)
from tests.verify_deep_microtasks_arithmetic import TestDeepMicrotasksForensics
from tests.verify_all_170_tasks_oracle import TestAll170MicroTasksOracle
from tests.test_challenger_m1_adversarial import TestChallengerM1NodeHarnessExecution


class DetailedTestResult(unittest.TestResult):
    """Custom TestResult collecting granular status and failure info."""

    def __init__(self):
        super().__init__()
        self.successes: List[unittest.TestCase] = []

    def addSuccess(self, test: unittest.TestCase):
        super().addSuccess(test)
        self.successes.append(test)


def run_suite_and_gather_stats(suite_class, suite_name: str) -> Dict[str, Any]:
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


TIER_DEFINITIONS: List[Tuple[str, List[Tuple[Any, str]]]] = [
    (
        "TIER 1: Python Tooling & CLI Coverage (100% target)",
        [
            (TestTier1ToolsCoverage, "Tier 1: build_exam_data & Common Utilities"),
            (TestBuildExamData, "Tier 1: Exam Data Builder Integration"),
            (TestExportAnki, "Tier 1: Anki TSV Exporter Coverage"),
        ],
    ),
    (
        "TIER 2: Static Analysis, Math Rigor & 8-Step High-Yield Structure",
        [
            (TestTier2StaticAST, "Tier 2: 8-Step Structure, AST & Derivations"),
            (TestR1Coverage, "R1: Syllabus & Ticket Coverage Audit"),
            (TestR2MathLatex, "R2: Mathematical Derivations & LaTeX Rigor"),
            (TestR3CodeExec, "R3: PyTorch Snippets AST & Execution"),
            (TestR4StructureNav, "R4: Navigation Graph & Section Integrity"),
            (TestAll28LecturesHTMLConformance, "HTML Conformance across 28 Lectures"),
            (TestSyllabusForensics, "Syllabus Mathematical Forensics"),
        ],
    ),
    (
        "TIER 3: DOM, PWA, Service Worker & State Persistence",
        [
            (TestTier3PWADOM, "Tier 3: SW Precache, SM-2 Math & LocalStorage"),
            (TestJSAssetsAndTracker, "Platform: CourseTracker State Engine"),
            (TestExamSimulator, "Platform: Simulator & Flashcards Engine"),
            (TestQAPillSync, "UI: QA Pill Badge Dynamic Sync"),
            (TestPwaManifestAndServiceWorker, "PWA: Manifest & SW Cache Strategies"),
            (TestKeyboardShortcutsAndInteraction, "UX: Keyboard Shortcuts & Focus Visible"),
            (TestLighthouseAndWebVitals, "Quality: Lighthouse CI & Web Vitals Invariants"),
            (TestMilestone1ResponsiveNav, "UI/UX: Universal 3-Item Bottom Nav Bar across 30 Pages"),
            (
                TestE2EPlatformRequirements,
                "Architecture: Comprehensive 16-Feature E2E Requirements",
            ),
        ],
    ),
    (
        "TIER 4: Viewport & Responsive Layout (320px – 2560px)",
        [
            (TestTier4ViewportResponsive, "Tier 4: 7 Viewports, Touch Targets & Overflow"),
            (TestR5SummaryStyling, "R5: Summary Marker Styling & DRY CSS"),
            (TestThemeAndStyles, "Platform: Theme Engine & Accessible Widgets"),
            (TestPortalUI, "Platform: Portal UI & Quick Action Bar"),
            (TestDOMAndPillInvariants, "Challenger 2: DOM & Pill Invariants"),
        ],
    ),
    (
        "TIER 5: Adversarial Fuzzing, Storage Recovery & Stress Testing",
        [
            (TestTier5Adversarial, "Tier 5: Search Fuzzing & Corrupt Storage Recovery"),
            (TestAdversarialChallenges, "Adversarial Stress & Boundary Suite"),
            (TestLinkGraphAndAnchors, "Challenger 2: Link Graph & Anchor Integrity"),
            (TestAdversarialDynamicCodeExecution, "Challenger 2: Dynamic Code Edge Tests"),
            (TestDynamicPyTorchExecutionRandomized, "Challenger 2: Dynamic PyTorch Randomized"),
            (TestLatexBalanceAndASTCheckingExhaustive, "Challenger 2: LaTeX Delimiters & AST"),
            (TestServiceWorkerPrecacheResolution, "Challenger 2: SW Precache Resolution"),
            (TestChallenger1MicroTasksAndQAs, "Challenger 1: Micro-Tasks & Q&A Integrity"),
            (TestSyllabusTicketAlignmentGUU26, "Challenger 1: GUU 2026 Ticket Alignment"),
            (TestDeepMicrotasksForensics, "Challenger 1: Deep Microtasks Completeness"),
            (TestAll170MicroTasksOracle, "Challenger 1: All 170 Tasks Oracle"),
            (TestChallengerM1NodeHarnessExecution, "Challenger M1: Node.js SW Adversarial Harness"),
        ],
    ),
]


def main() -> int:
    print("=" * 80)
    print("    DEEP LEARNING COURSE 5-TIER VERIFICATION SUITE (GUU 2026)")
    print("=" * 80)

    grand_total = 0
    grand_passed = 0
    grand_failed = 0
    grand_errors = 0
    grand_skipped = 0
    start_all = time.time()

    all_failures = []

    for tier_title, suite_list in TIER_DEFINITIONS:
        print(f"\n{'-' * 80}")
        print(f"  {tier_title}")
        print(f"{'-' * 80}")

        tier_total = 0
        tier_passed = 0
        tier_failed = 0
        tier_errors = 0

        for suite_cls, suite_name in suite_list:
            stats = run_suite_and_gather_stats(suite_cls, suite_name)
            tier_total += stats["total"]
            tier_passed += stats["passed"]
            tier_failed += stats["failed"]
            tier_errors += stats["errors"]

            grand_total += stats["total"]
            grand_passed += stats["passed"]
            grand_failed += stats["failed"]
            grand_errors += stats["errors"]
            grand_skipped += stats["skipped"]

            status = "PASS" if (stats["failed"] == 0 and stats["errors"] == 0) else "FAIL"
            print(
                f"  [{status:4s}] {suite_name:<55s} "
                f"({stats['passed']}/{stats['total']} in {stats['duration']:.2f}s)"
            )

            if stats["failure_details"]:
                for f in stats["failure_details"]:
                    all_failures.append((suite_name, f["test"], f["error"]))

        tier_status = "PASSED" if (tier_failed == 0 and tier_errors == 0) else "FAILED"
        print(f"  --> {tier_title[:30]} Result: {tier_status} ({tier_passed}/{tier_total} tests)")

    total_duration = time.time() - start_all

    print("\n" + "=" * 80)
    print("    5-TIER TEST SUITE EXECUTION SUMMARY")
    print("=" * 80)
    print(f"  Total Test Cases : {grand_total}")
    print(f"  Passed           : {grand_passed}")
    print(f"  Failed           : {grand_failed}")
    print(f"  Errors           : {grand_errors}")
    print(f"  Skipped          : {grand_skipped}")
    print(f"  Total Duration   : {total_duration:.2f}s")
    print(f"  Success Rate     : {(grand_passed / grand_total * 100):.1f}%")
    print("=" * 80)

    if all_failures:
        print("\nFAILURE DETAILS:")
        for suite, test, err in all_failures:
            print(f"\n[FAIL] {suite} -> {test}:")
            print(f"  {err[:300]}")
        return 1

    print("\n[SUCCESS] 100% of tests in all 5 tiers PASSED cleanly!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
