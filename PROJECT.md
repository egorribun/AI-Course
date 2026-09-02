# Project: AI-Course Full-Scale Audit and Verification

## Architecture
AI-Course is a modern, static web educational platform featuring 28 AI/ML lectures, interactive tests, exams, Anki export tools, tracker logic, and offline PWA capabilities.
- **Frontend / Content**: HTML5 (`index.html`, `exam.html`, `lectures/*.html` [28 lectures]), CSS3 (`style.css`), Vanilla JS with JSDoc types (`js/tracker.js`, `js/exam.js`, `js/lecture.js`, `js/app.js`), Service Worker (`sw.js`).
- **Backend / Tooling**: Python 3 tooling (`tools/build_exam_data.py`, `tools/export_anki.py`, `tools/sync_from_repo.py`).
- **Tests**: Pytest unit & coverage suite (`tests/`), JS unit tests (`tests/*.test.js`), Node adversarial harness (`tests/adversarial_harness.cjs`), Orchestrated test runner (`tests/run_all_tests.py`).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Content & HTML Invariants | 28 lectures 8-section invariant, valid tags, valid links, LaTeX/MathJax 3, AST-parsed Python, Russian spelling & ё consistency | M1 | Survey |
| 2 | Code Quality & Type Safety | Zero console.log, strict error handling, tsc --checkJs 0 errors, stylelint 0 errors, ruff clean | M2 | Survey |
| 3 | Python Tools & Coverage | 100% line & branch coverage for tools/build_exam_data.py & tools/export_anki.py | M3 | Survey |
| 4 | Test Suites Execution | 100% 314/314 tests passed in run_all_tests.py, npm test, adversarial harness | M4 | Survey |
| 5 | PWA & Offline Support | Service worker registration, cache management, offline fallback | M5 | Survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Content & HTML Audit | All HTML files, lectures, LaTeX, Python blocks, Russian spelling | none | DONE |
| 2 | M2: Code, Types & Lint Audit | JS/CSS/Python code quality, type checks, lint checks | none | DONE |
| 3 | M3: Tests & Coverage Audit | Pytest 100% branch cov, npm test, adversarial harness, run_all_tests.py | none | DONE |
| 4 | M4: PWA & Offline Audit | sw.js, manifest, offline capabilities | none | DONE |
| 5 | M5: Multi-Agent Gate Verification | Reviewers (2/2 APPROVE), Challengers (2/2 APPROVE), Forensic Auditor (CLEAN) | M1, M2, M3, M4 | DONE |

## Code Layout
- `lectures/` — 28 lecture HTML files (lecture00 to lecture27)
- `js/` — Client-side JavaScript (`app.js`, `exam.js`, `lecture.js`, `tracker.js`, `exam_data.js`)
- `tools/` — Python build and export utilities (`build_exam_data.py`, `export_anki.py`, `sync_from_repo.py`)
- `tests/` — Test suites and harness files
- `sw.js` — Service worker
- `style.css` — Global styles
- `index.html`, `exam.html` — Main portal and examination pages
