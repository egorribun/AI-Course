# E2E Test Infra: Deep Learning Course Verification

## Test Philosophy
- Opaque-box, requirement-driven automated verification suite covering Requirements R1, R2, R3, R4.
- Methodology: Category-Partition, Boundary Value Analysis, Syntax Checking, Static & Dynamic Code Validation, Graph Link Verification.

## Test Architecture
- Test Runner: Python test scripts located in `tests/`
- Test Categories:
  * `test_r1_coverage.py`: Verifies all 25 exam tickets from `dl_guu-dl_26/` are covered and `index.html` mapping table is synchronized.
  * `test_r2_math_latex.py`: Verifies LaTeX delimiter balance (`$$`, `$`), brace matching, formula syntax, absence of malformed entities.
  * `test_r3_code_exec.py`: Extracts all Python/PyTorch code blocks from HTML files, verifies AST syntax, executes snippets with tensor assertions where applicable.
  * `test_r4_structure_nav.py`: Verifies all 28 lectures have $\ge 10$ QA (`<details class="qa">`), $\ge 6$ tasks (`.task`) with solutions (`.sol`), cheat-sheet (`.cheat`), and checks 100% of relative links, anchors, and prev/next chains.
  * `run_all_tests.py`: Master test harness executing all 4 suites and reporting unified summary.

## Coverage Goals
- Tier 1: 100% Lecture and Ticket coverage (all 28 lectures, 25 tickets).
- Tier 2: Boundary & Corner cases (edge tickets, duplicate numbering in raw source, first/last lecture navigation bounds).
- Tier 3: Code execution validity (zero AST syntax errors, zero runtime crashes).
- Tier 4: Structural integrity ($\ge 10$ QA in all 28 lectures, $\ge 6$ tasks with solutions, zero dead links/anchors).
