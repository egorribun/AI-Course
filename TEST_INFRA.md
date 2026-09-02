# E2E Test Infra: Deep Learning Course (GUU 2026)

## Test Philosophy
- Multi-tier requirement-driven & opaque-box verification.
- Zero-tolerance for unverified assertions; strict 100% line/branch/function coverage across Python and JavaScript.
- Methodology: Category-Partition + Boundary Value Analysis + Pairwise Combinatorial + Real-World Workload Testing + Adversarial Stress Testing.

## Feature Inventory & Test Mapping
| # | Feature | Source | Tier 1 (Unit/Tool) | Tier 2 (Static/AST) | Tier 3 (Client/DOM) | Tier 4 (Layout/Responsive) | Tier 5 (Adversarial) |
|---|---------|--------|:------------------:|:-------------------:|:-------------------:|:--------------------------:|:--------------------:|
| 1 | Content Block A (00-07) | R1 | ✓ | ✓ (AST/LaTeX/ё) | ✓ | ✓ | ✓ |
| 2 | Content Block B (08-13) | R1 | ✓ | ✓ (AST/LaTeX/ё) | ✓ | ✓ | ✓ |
| 3 | Content Block C (14-21) | R1 | ✓ | ✓ (AST/LaTeX/ё) | ✓ | ✓ | ✓ |
| 4 | Content Block D (22-27) | R1 | ✓ | ✓ (AST/LaTeX/ё) | ✓ | ✓ | ✓ |
| 5 | Python Tools 100% Cov | R2 | ✓ (pytest-cov 100%) | ✓ (Ruff 0 errs) | — | — | ✓ |
| 6 | Frontend Node 100% Cov | R2 | ✓ (Node cov 100%) | ✓ (tsc 0 errs) | ✓ | — | ✓ (Fuzzing) |
| 7 | CSS & WCAG 2.1 AA | R2 | ✓ (Stylelint 0 errs)| ✓ (HTML5) | ✓ | ✓ (320-2560px) | ✓ |
| 8 | Exam Simulator & PWA v3 | R3 | ✓ | ✓ | ✓ (SM-2, timer) | ✓ | ✓ (Offline/Corrupt) |

## Test Architecture
- **Master Runner**: `tests/run_all_tests.py` orchestrating 5 tiers:
  - Tier 1: Core Python tools, dataset freshness, schema validation.
  - Tier 2: Static AST parse, LaTeX delimiter balancing, Russian 'ё' audit.
  - Tier 3: DOM events, SM-2 spaced repetition state transitions, timer accuracy, blitz mode.
  - Tier 4: Viewport responsiveness across 320px, 375px, 768px, 1024px, 1440px, 1920px, 2560px with 0 horizontal overflow.
  - Tier 5: Adversarial state corruption, localStorage fuzzing, XSS injection immunity, ServiceWorker offline caching resilience.
- **Python Coverage**: `pytest tests/ -v --cov=tools --cov-branch --cov-fail-under=100`.
- **Node.js Coverage**: `node --test --experimental-test-coverage` targeting 100% lines/branches/functions on `js/*.js` and `sw.js`.
- **Static Typing**: `tsc --noEmit --checkJs` with zero errors.
- **Linters**: `ruff check .`, `ruff format --check .`, `stylelint style.css`.

## Coverage Thresholds
- Python `tools/`: strictly 100% line coverage, 100% branch coverage.
- JavaScript `js/*.js`, `sw.js`: strictly 100% line, branch, and function coverage.
- Content: 28/28 lectures with all 8 invariant sections, 296/296 questions, 170/170 tasks, 25/25 exam tickets.
- Viewports: 7 standard breakpoints (320px to 2560px) with 0 horizontal overflow on all 30 HTML pages.
