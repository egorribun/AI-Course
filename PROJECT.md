# Project: Deep Learning Educational Platform

## Architecture
- **Web Platform**: Zero-build Static HTML5 / CSS3 / Vanilla JavaScript. 100% GitHub Pages compatible.
- **PWA & Offline**: Root `sw.js` (Cache-First strategy for local HTML/CSS/JS/Anki, Stale-While-Revalidate for MathJax CDN), `manifest.json`, standalone web app installation support.
- **EdTech Engines**:
  - `js/tracker.js`: Course completion, lecture visits, and global progress tracking with LocalStorage persistence.
  - `js/simulator.js`: Exam simulator (tickets 1-25, 3-min countdown timer, blitz mode, topic drill), Leitner / SM-2 spaced repetition engine (`ai_course_sm2_cards`).
  - `js/app.js` & `js/lecture.js`: Live search, topic filtering, keyboard shortcuts dispatcher (`[`, `]`, `T`, `/`, `Alt+O`), code copy buttons, print handling.
- **Content & Rigor**: 28 complete HTML lectures (`lectures/00-*.html` .. `lectures/27-*.html`) covering 25 exam tickets with 300 Q&A blocks, 170 micro-tasks, and 28 cheat-sheets.
- **Verification & Tooling**: `tests/` (254 pytest suites covering DOM, Math, Code AST, Links, Anki, UI, PWA, SM-2), `tools/export_anki.py` (generates TSV decks and `js/exam_data.js`), `ruff` linter, GitHub Actions CI/CD.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Zero-build PWA & Service Worker | Root `sw.js` offline caching for all 28 lectures, assets, MathJax | M1 | survey |
| 2 | Web App Manifest & App Icons | `manifest.json`, theme colors, standalone display mode, SVG/PNG icons | M1 | survey |
| 3 | Spaced Repetition (Leitner / SM-2) | LocalStorage SM-2 interval scheduling ($EF, I, n$), due queue filtering | M1 | survey |
| 4 | Exam Simulator: Ticket Selector | Direct selection of tickets 1-25 in addition to random draw | M1 | survey |
| 5 | Exam Simulator: 3-Min Timer | 180s countdown timer with audio gong and visual alerts | M1 | survey |
| 6 | Exam Simulator: Blitz & Drill Modes | Rapid-fire 10-question blitz test and topic category drill modes | M1 | survey |
| 7 | Global Keyboard Shortcuts | `[` / `]` navigation, `T` theme, `/` search, `Alt+O` spoilers with input protection | M1 | survey |
| 8 | Code Snippet Copy Buttons | Pre-block copy buttons with visual feedback and clipboard fallback | M1 | survey |
| 9 | Print CSS & WCAG 2.1 AA a11y | `beforeprint` auto-expand `<details>`, `:focus-visible`, ARIA tab attributes | M1 | survey |
| 10 | 28 Lectures Academic Rigor | 8 core proofs (Backprop, ELBO, Bellman, Policy Gradient, SDPA, InfoNCE, WGAN, DDPM) | M2 | survey |
| 11 | EdTech Q&A and Micro-Tasks | $\ge 10$ Q&A (300 total) and $\ge 6$ micro-tasks (170 total) + 28 cheat-sheets | M2 | survey |
| 12 | LaTeX Delimiter & Syntax Fixes | Clean CutMix `$$` in L07 and unescaped `%` in L09 | M2 | survey |
| 13 | PyTorch 2.x Modernization | Replace `.data` with `nn.init.uniform_` in L19; add `# [B, C, H, W]` shape comments | M2 | survey |
| 14 | Anki TSV Exporter & Sync | Export 3 TSV decks (494 cards) and `js/exam_data.js` via `export_anki.py` | M3 | survey |
| 15 | Repository & Documentation Sync | Update `README.md` test counter badges, sync `PROJECT.md`, verify `ruff` 0 errors | M3 | survey |
| 16 | E2E Verification & Adversarial Gate | Pass 100% pytest suite (Tiers 1-4) + Tier 5 adversarial hardening | M-Final | survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Web Platform, PWA & EdTech UX | PWA (`sw.js`, `manifest.json`), SM-2 algorithm, ticket selector, blitz/drill, hotkeys, print/a11y | none | DONE |
| M2 | Content Rigor & PyTorch Snippets Polish | LaTeX delimiter fixes, PyTorch `.data` modernization, tensor shape annotations | none | DONE |
| M3 | Tooling, Anki & Documentation Sync | `export_anki.py` deck generation, `README.md` test counts, ruff lint clean | M1, M2 | DONE |
| M-Final | E2E Test Pass & Adversarial Hardening | 100% E2E test pass (Tiers 1-4), Tier 5 adversarial stress verification | M1, M2, M3 | DONE |

## Interface Contracts
### `sw.js` ↔ Web Platform
- Scope: `/` (repository root).
- Strategy: Cache-First for static assets (`/`, `index.html`, `lectures/*.html`, `style.css`, `js/*.js`, `manifest.json`), Network-First / Stale-While-Revalidate for CDN assets.
- Fallback: Offline fallback to cached `index.html`.

### `js/tracker.js` / `js/simulator.js` ↔ LocalStorage
- `ai_course_sm2_cards`: Object mapping `cardId` $\to$ `{ box: 1..5, repetitions: int, interval: int, easeFactor: float, lastReviewed: int, nextReview: int }`.
- `ai_course_checked_qas`: Array of checked Q&A IDs.
- `ai_course_checked_tasks`: Array of checked task IDs.
- `ai_course_visited_lectures`: Array of visited lecture slugs.

### `tools/export_anki.py` ↔ `js/exam_data.js` & `anki_decks/*.tsv`
- `anki_decks/ai_course_exam_qas.tsv`: 4 columns (`Ticket`, `Question`, `Answer`, `Tags`).
- `anki_decks/ai_course_microtasks.tsv`: 4 columns (`Lecture`, `Task`, `Solution`, `Type`).
- `anki_decks/ai_course_3min_cheatsheets.tsv`: 3 columns (`Lecture`, `Title`, `CheatSheet`).
- `js/exam_data.js`: `window.EXAM_DATA = { tickets: [...], qas: [...], tasks: [...] }`.

## Code Layout
- `index.html` : Main course portal, lecture grid, live search, global progress bar.
- `lectures/00-intro-ml.html` .. `lectures/27-actor-critic.html` : 28 interactive course lectures.
- `style.css` : Design system, dark/light themes, layout, print styles (`@media print`).
- `js/app.js` : Portal logic, search, category filters, hotkeys dispatcher.
- `js/lecture.js` : Lecture interaction, copy buttons, spoiler toggles, hotkeys.
- `js/tracker.js` : Progress tracking, LocalStorage persistence, progress export/import.
- `js/simulator.js` : Exam simulator, 3-minute timer, Leitner-SM2 flashcard engine.
- `sw.js` : Service Worker for offline PWA caching.
- `manifest.json` : Web App Manifest for PWA installation.
- `tools/export_anki.py` : Parser generating TSV decks and `js/exam_data.js`.
- `tests/` : Comprehensive pytest test suites and forensic verification scripts.
- `.github/workflows/` : CI test workflow and GitHub Pages deployment workflow.
