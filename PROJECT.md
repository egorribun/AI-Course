# Project: Deep Learning Course (GUU 2026) Audit & Crystallization

## Architecture
- **Client Architecture**: Vanilla JS + CSS, zero runtime external libraries, offline-first PWA (`sw.js` with `ai-course-v3` cache).
- **Content Architecture**: 28 lectures (`00-intro-ml.html` .. `27-actor-critic.html`) with strict 8-section layout, 296 questions, 170 micro-tasks, LaTeX MathJax 3 formulas, and executable Python snippets.
- **Tools & Compilers**: Python toolchain (`tools/build_exam_data.py`, `tools/export_anki.py`) compiling content to `js/exam_data.js` and `anki_decks/` TSVs.
- **Testing Multi-Stack**:
  - Python: `pytest` with strictly 100% line and branch coverage on `tools/` (`--cov=tools --cov-branch --cov-fail-under=100`, 523/523 passed).
  - JavaScript: Native Node.js test runner (`node --test --experimental-test-coverage`) with 100% line coverage on `js/tracker.js`, `js/exam.js`, `js/lecture.js`, `js/app.js`, `js/exam_data.js`, and `sw.js` (54/54 passed).
  - Static Typing: TypeScript JSDoc (`tsc --noEmit --checkJs`) with 0 errors via `jsconfig.json` and `types/globals.d.ts`.
  - CSS & HTML: `stylelint style.css` with 0 errors, HTML5 semantic validation, WCAG 2.1 AA compliance, and responsive viewport validation (320px–2560px with 0 overflow).
  - Master Runner: `tests/run_all_tests.py` orchestrating 5 verification tiers with 100% success rate (314/314 passed).

## Feature Inventory
| # | Feature | Description | Milestone | Status |
|---|---------|-------------|-----------|--------|
| 1 | High-Yield Compression Block A | Lectures 00–07 compressed by 32.5%, invariant 8 sections, formulas, AST, ё | M1-A | DONE |
| 2 | High-Yield Compression Block B | Lectures 08–13 compressed by 30.7%, invariant 8 sections, formulas, AST, ё | M1-B | DONE |
| 3 | High-Yield Compression Block C | Lectures 14–21 compressed by 31.1%, header fixes (6,7,8), formulas, AST, ё | M1-C | DONE |
| 4 | High-Yield Compression Block D | Lectures 22–27 compressed by 30.6%, invariant 8 sections, formulas, AST, ё | M1-D | DONE |
| 5 | Python 100% Coverage & Tools | `tools/` 100% line/branch cov (246/246 stmts, 74/74 branches), `tools/export_anki.py`, Ruff 0 errs | M2 | DONE |
| 6 | Frontend Node 100% Coverage & TS | `js/*.js` & `sw.js` 100% coverage, `tsc --checkJs` 0 errs, Stylelint 0 errs | M3 | DONE |
| 7 | Responsive, WCAG 2.1 AA & PWA v3 | 320px-2560px no overflow, WCAG 2.1 AA, `sw.js` `ai-course-v3` precache | M4 | DONE |
| 8 | Exam Simulator, Anki & CI Polish | `exam.html` SM-2/blitz, Anki TSV sync, 5-tier master-runner & CI workflow | M5 | DONE |
| 9 | Final Verification & Audit | Full 5-tier master runner, forensic audit, acceptance criteria sign-off | M6 | DONE |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1-A | Content Block A (00-07) | 8-section layout, 32.5% compression, 89 Q&As, 50 tasks, formulas, AST, ё | none | DONE |
| M1-B | Content Block B (08-13) | 8-section layout, 30.7% compression, 64 Q&As, 36 tasks, formulas, AST, ё | none | DONE |
| M1-C | Content Block C (14-21) | 8-section layout, 31.1% compression, 82 Q&As, 48 tasks, header fixes, AST, ё | none | DONE |
| M1-D | Content Block D (22-27) | 8-section layout, 30.6% compression, 60 Q&As, 36 tasks, formulas, AST, ё | none | DONE |
| M2 | Python Tools & 100% Coverage | `pytest --cov=tools --cov-branch --cov-fail-under=100`, Ruff check & format | none | DONE |
| M3 | Frontend 100% Test Coverage & TS | `package.json`, headless test harness, 100% Node cov on `js/` and `sw.js`, `tsc` 0 err | none | DONE |
| M4 | CSS, WCAG 2.1 AA & PWA Cache v3 | Stylelint, WCAG 2.1 AA contrast/ARIA, responsive 320-2560px, `sw.js` v3 | M3 | DONE |
| M5 | Exam Simulator, Anki & CI | `exam.html` SM-2 timer/blitz, `build_exam_data.py --check`, `export_anki.py`, 5 tiers, CI | M1, M2, M3 | DONE |
| M6 | Final Verification & Audit | Full 5-tier master runner, forensic audit, acceptance criteria sign-off | M1-M5 | DONE |

## Interface Contracts
### `tools/build_exam_data.py` ↔ `js/exam_data.js` ↔ `js/exam.js`
- `tools/build_exam_data.py` extracts Q&A (`.qa`), tasks (`.task`), and cheatsheet items (`.cheat li`) from all 28 HTML lectures.
- Generates `js/exam_data.js` defining `window.EXAM_DATA = { version: "3.0", lectures: [...], total_qa: 296, total_tasks: 170, total_cheats: 231 }`.
- `js/exam.js` consumes `window.EXAM_DATA` for flashcards, oral defense (3:00 timer), SM-2 intervals, and blitz mode.

### `tools/export_anki.py` ↔ `anki_decks/`
- Exports TSV decks formatted for Anki import (`questions.tsv`, `microtasks.tsv`, `cheatsheets.tsv`) without embedding broken links in client HTML.

### `tests/harness/mock_browser.js` ↔ `tests/unit/*.test.js` ↔ `js/*.js`
- Clean zero-dependency browser globals (`window`, `document`, `localStorage`, `CustomEvent`, `caches`, `AudioContext`) injected before requiring client JS files for 100% line coverage under `node --test --experimental-test-coverage`.

## Code Layout
- `lectures/` (or root `*.html`): 28 lecture files (`00-intro-ml.html` .. `27-actor-critic.html`), `index.html`, `exam.html`.
- `js/`: `tracker.js`, `exam.js`, `simulator.js`, `lecture.js`, `app.js`, `exam_data.js`.
- `sw.js`: Service worker (`ai-course-v3`).
- `style.css`: Unified stylesheet.
- `tools/`: `build_exam_data.py`, `export_anki.py`.
- `tests/`: Unit tests (`tests/unit/`), tier tests, adversarial harnesses, `run_all_tests.py`.
- `types/`: `globals.d.ts`.
- `jsconfig.json`, `tsconfig.json`, `package.json`, `pyproject.toml`, `.stylelintrc.json`.
- `.github/workflows/ci.yml`.
