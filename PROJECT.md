# Project: Deep Learning Exam Course (AI-Course) UI/UX, Quality & 100% Verification

## Architecture
- **Static Portal & Multi-page Educational Platform**:
  - `index.html`: Portal overview, 28 lecture cards, search filter & 4-block classification, progress hub, desktop header action button, mobile bottom navigation.
  - `exam.html`: Autonomous oral exam simulator, 25 official tickets, 3:00 countdown timer, blitz quiz, SM-2 flashcards deck, mobile bottom navigation.
  - `lectures/00-intro-ml.html` .. `lectures/27-actor-critic.html`: 28 structured lectures (8 standardized sections per lecture, MathJax LaTeX formulas, interactive Q&A defenses, micro-tasks with solutions, cheat outlines, mobile bottom navigation).
  - `css/style.css`: Unified dark/light design system, responsive breakpoints (768px desktop/mobile boundary), WCAG 2.1 AA focus rings, Safe Area Inset support (`env(safe-area-inset-bottom)`), print styles.
  - `js/tracker.js`: Universal state management (`CourseTracker`) for theme, completed lectures, checked Q&As, checked tasks, SM-2 spaced repetition, progress modal, and corrupted localStorage resiliency.
  - `js/app.js`: Portal search engine, block/tag filters, back-to-top, shortcuts, mobile navigation bindings.
  - `js/exam.js`: Standalone oral exam simulator, timer, SM-2 flashcard UI, blitz quiz.
  - `js/lecture.js`: Lecture reader bar, spoiler reveal, checkmarks, keyboard navigation.
  - `sw.js`: PWA Service Worker with offline precaching for all 30 HTML pages, styles, scripts, fonts, and assets.
  - `tools/build_exam_data.py`: CLI compiler extracting questions/tasks/cheats from 28 lectures into `js/exam_data.js`.

## Feature Inventory
| # | Feature | Description | Milestone | Source | Status |
|---|---------|-------------|-----------|--------|--------|
| 1 | Desktop Exam Header Button | «🎲 Тренажёр экзамена» button in `header.top .inner` on `index.html` (>=768px) | M1 | ORIGINAL_REQUEST R1 | DONE |
| 2 | Simulator Removal from Body | Remove `#exam-simulator-container` and `js/simulator.js` from `index.html` body | M1 | ORIGINAL_REQUEST R1 | DONE |
| 3 | Portal Bottom Navigation Bar | 4-item dock (`[🔍 Поиск, 🎲 Тренажёр, 📊 Прогресс, 🌓 Тема]`) on `index.html` & `exam.html` (<768px) | M1 | ORIGINAL_REQUEST R1 | DONE |
| 4 | Lectures Bottom Navigation Bar | 4-item dock (`[🔍 Поиск, 🎲 Тренажёр, 📊 Прогресс, 🌓 Тема]`) across all 28 `lectures/*.html` (<768px) | M1 | ORIGINAL_REQUEST R1 | DONE |
| 5 | Safe Area Inset Layout | CSS rules for notch padding (`env(safe-area-inset-bottom)`), body padding, floating back-to-top | M1 | ORIGINAL_REQUEST R1 | DONE |
| 6 | Universal Progress Modal | Modal dialog showing lecture/QA/task stats with reset action, ARIA dialog, and Esc dismiss | M1 | ORIGINAL_REQUEST R1 | DONE |
| 7 | Synchronized Theme Toggling | Instant theme toggle synced across header, bottom bar, `CourseTracker`, and localStorage | M1 | ORIGINAL_REQUEST R1 | DONE |
| 8 | Service Worker Precache Parity | Precache `exam.html` and `js/exam.js` in `sw.js` `STATIC_ASSETS` for 100% offline access | M2 | ORIGINAL_REQUEST R2 | DONE |
| 9 | LocalStorage Type Guarding | Harden `tracker.js:safeGetJSON` against corrupted primitive/non-array types | M2 | ORIGINAL_REQUEST R2 | DONE |
| 10 | JS Redundancy Consolidation | Unify `js/simulator.js` and `js/exam.js` into single maintainable module | M2 | ORIGINAL_REQUEST R2 | DONE |
| 11 | Lecture Heading Hierarchy | Fix heading skips (`<h4>` to `<h3>` in Section 4) across 12 lecture files for WCAG 2.1 AA | M2 | ORIGINAL_REQUEST R2 | DONE |
| 12 | Python 100% Line & Branch Coverage | Add `pytest-cov>=5.0.0` to `pyproject.toml` and verify 100% line & branch coverage on `tools/` | M3 / E2E Track | ORIGINAL_REQUEST R3 | DONE |
| 13 | JS & DOM Unit Tests | Automated headless tests for `CourseTracker`, SM-2 algorithm, 3:00 timer, ticket generator | M3 / E2E Track | ORIGINAL_REQUEST R3 | DONE |
| 14 | Adversarial Fuzzing Suite | Test suite for corrupted localStorage, extreme search queries, timer edge cases, offline SW | M3 / E2E Track | ORIGINAL_REQUEST R3 | DONE |
| 15 | HTML5 & Asset Conformance | Conformance tests for all 28 lectures, `exam.html`, `index.html`, internal anchors, MathJax balance | M3 / E2E Track | ORIGINAL_REQUEST R3 | DONE |
| 16 | CI/CD Workflow Pipeline | Update `.github/workflows/ci.yml` to run ruff, 100% coverage, adversarial node suites, pytest | M3 / E2E Track | ORIGINAL_REQUEST R3 | DONE |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 0 | E2E Testing Track | Independent multi-tier test suite design (Tiers 1-4) publishing `TEST_READY.md` | none | DONE |
| 1 | M1: UI/UX & Responsive Navigation | Remove simulator from index.html body, add desktop header button, add 4-item bottom nav bar to index/exam/28 lectures, progress modal, Safe Area Insets in CSS | none | DONE |
| 2 | M2: Code Quality, PWA & JS Hardening | sw.js precache parity, tracker.js safeGetJSON type guards, exam.js consolidation, lecture heading normalization, WCAG AA & MathJax audit | none | DONE |
| 3 | M3: Final Milestone (100% Verification & Adversarial Hardening) | Phase 1: Pass 100% of E2E test suite (Tiers 1-4) with 100% Python line/branch coverage and CI workflow. Phase 2: Adversarial Coverage Hardening (Tier 5) with Challenger loop | M1, M2, E2E | DONE |

## Interface Contracts
### Header Actions ↔ Responsive Viewport
- **Desktop (>= 768px)**: `.header-actions` displays `.btn-header-exam` and `.theme-toggle`. `.bottom-nav-bar` has `display: none`.
- **Mobile (< 768px)**: `.header-actions .btn-header-exam` has `display: none`. `.bottom-nav-bar` has `display: flex; position: fixed; bottom: 0; left: 0; right: 0;`.
- **Body Padding**: `body` on mobile has `padding-bottom: calc(72px + env(safe-area-inset-bottom, 0px))`.

### Bottom Navigation Bar ↔ Page Routing
- **Search Item**:
  - On `index.html`: Focuses `#lecture-search-input` and scrolls into view.
  - On `exam.html`: Navigates to `index.html?focus=search`.
  - On `lectures/*.html`: Navigates to `../index.html?focus=search`.
- **Exam Item**:
  - On `index.html`: Navigates to `exam.html`.
  - On `exam.html`: Active item (`aria-current="page"`).
  - On `lectures/*.html`: Navigates to `../exam.html`.
- **Progress Item**:
  - Universal across all 30 pages: Opens `#course-progress-modal` dialog displaying `CourseTracker.getOverallStats()`.
- **Theme Item**:
  - Universal across all 30 pages: Invokes `CourseTracker.toggleTheme()`, updating `[data-theme]` on `<html>` and syncing icon/text on both header and bottom nav buttons.

### Safe Area Insets Contract
- `.bottom-nav-bar`: `padding-bottom: max(8px, env(safe-area-inset-bottom, 0px));`
- `.back-to-top`: `bottom: calc(80px + env(safe-area-inset-bottom, 0px)) !important;`

### CourseTracker Schema Contract
- `ai_course_completed_lectures`: JSON Array of strings `["00", "01", ...]`. Safe fallback: `[]`.
- `ai_course_checked_qas`: JSON Array of strings `["qa-00-1", ...]`. Safe fallback: `[]`.
- `ai_course_checked_tasks`: JSON Array of strings `["task-00-1", ...]`. Safe fallback: `[]`.
- `ai_course_sm2_cards`: JSON Object of `{ [cardId: string]: { box: number, reps: number, interval: number, easeFactor: number, nextReview: number } }`. Safe fallback: `{}`.
- `ai_course_theme`: String `'dark' | 'light'`. Safe fallback: `'dark'`.

## Code Layout & Write Ownership
- **Track 0 (E2E Testing Track)**: Owns `TEST_INFRA.md`, `TEST_READY.md`, `tests/` new test files (`tests/test_e2e_*.py`, `tests/adversarial_sw_ui_stress_test.cjs`).
- **Milestone M1 Worker**: Owns `index.html`, `exam.html`, `lectures/*.html` (bottom navigation bar injection), `css/style.css` (navigation & modal styles), `js/app.js` (mobile nav & search focus bindings).
- **Milestone M2 Worker**: Owns `sw.js`, `js/tracker.js`, `js/exam.js`, `js/simulator.js`, `lectures/*.html` (heading hierarchy `<h4>` -> `<h3>` in Section 4).
- **Milestone M3 Worker**: Owns `pyproject.toml`, `.github/workflows/ci.yml`, `tools/` coverage test suites, final integration.
