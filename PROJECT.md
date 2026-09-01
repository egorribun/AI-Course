# Project: «Методы ИИ» Educational Web Course Modernization & Forensic Audit

## Architecture
- **Web App**: Static HTML5 + Vanilla ES6 JavaScript + Modern CSS3 with CSS variables and responsive flex/grid layouts.
- **PWA Capabilities**: Service Worker (`sw.js`, cache name `ai-course-v3`), Web App Manifest (`manifest.json`), offline-first content delivery.
- **Data Layer**: Generated `js/exam_data.js` containing the unified catalog of 25 exam tickets, 28 lectures, 296+ defense Q&As, and 170+ micro-tasks with SM-2 spaced repetition state in `localStorage`.
- **Tooling**: Pure Python 3 CLI tool `tools/build_exam_data.py` (tested with `pytest` / `uv run pytest`) that parses lecture HTML files and emits validated JSON/JS data.
- **Testing Architecture**: 5-tier test suite executed via `pytest` and `tests/run_all_tests.py` verifying Python coverage, HTML/AST/LaTeX syntax, DOM/PWA mechanics, responsive viewport constraints (320px–2560px), and adversarial fuzzing.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | De-sprintization & 4 Modular Blocks | Eliminate sprint terminology across repo, organize curriculum into 4 Blocks: A (Foundations & CV), B (Representations, GenAI & CV Tasks), C (NLP & Transformers), D (Reinforcement Learning). | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Navigation & UI Foundation | Update index.html, syllabus, search, exam simulator navigation to 4-block layout, modernize dark/light theme, typography. | M1 | ORIGINAL_REQUEST §R1, §R4 |
| 3 | Mobile-First UI & Responsive Layout | Implement Quick Action Bar on mobile (<768px), safe-area-insets (top/bottom), touch targets >=44px, isolated horizontal scroll containers for math/tables, 0 page overflow on 320px-2560px. | M1 | ORIGINAL_REQUEST §R4 |
| 4 | Legacy Anki Removal & Exam Data Builder | Delete `anki_decks/`, `tools/export_anki.py`, and legacy Anki tests. Implement `tools/build_exam_data.py` producing `js/exam_data.js`. | M1 | ORIGINAL_REQUEST §R3 |
| 5 | Block A Lectures Modernization (00–07) | Reformat lectures 00–07 into 8-Step High-Yield structure mapped to tickets 1–7 (ML basics, FCNN, Autodiff, Losses/MLE, CNN layers, Architectures, Optimizers, Validation/Optuna). | M2-A | ORIGINAL_REQUEST §R2 |
| 6 | Block B Lectures Modernization (08–13) | Reformat lectures 08–13 into 8-Step High-Yield structure mapped to tickets 8–12 (Metric learning, SSL/CLIP, VAE, GAN, Diffusion DDPM, CV Tasks YOLO/U-Net). | M2-B | ORIGINAL_REQUEST §R2 |
| 7 | Block C Lectures Modernization (14–21) | Reformat lectures 14–21 into 8-Step High-Yield structure mapped to tickets 13–20 (RNN/LSTM, Seq2Seq Attention, Transformers, Self-Attention, Tokenization/Word2Vec, Translation/BLEU, LLM architectures). | M2-C | ORIGINAL_REQUEST §R2 |
| 8 | Block D Lectures Modernization (22–27) | Reformat lectures 22–27 into 8-Step High-Yield structure mapped to tickets 21–25 (MDP, Bellman equations, Monte Carlo/Value Iteration, TD/Q-learning/SARSA, Policy Gradient, Actor-Critic). | M2-D | ORIGINAL_REQUEST §R2 |
| 9 | 5-Tier Test Suite Implementation | Build Tier 1 (100% Python coverage for build tool), Tier 2 (AST/LaTeX/HTML validation), Tier 3 (DOM/PWA/SM-2), Tier 4 (Responsive Viewports 320-2560px), Tier 5 (Adversarial Fuzzing). | E2E-Track | ORIGINAL_REQUEST §R5 |
| 10 | Final E2E Test Suite Pass & Adversarial Hardening | Verify 100% pass of all 5 tiers of E2E test suite, perform adversarial whitebox hardening against edge cases and audit integrity. | M-Final | ORIGINAL_REQUEST §R5 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Core Architecture, De-sprintization, UI Modernization & Exam Tool | Restructure into Blocks A-D, update index/nav, mobile-first CSS/JS, Quick Action Bar, delete Anki, implement `tools/build_exam_data.py` -> `js/exam_data.js` | none | DONE |
| M2-A | Block A Content Modernization | Lectures 00–07 mapped to Tickets 1–7 with 8-Step High-Yield structure | M1 | DONE |
| M2-B | Block B Content Modernization | Lectures 08–13 mapped to Tickets 8–12 with 8-Step High-Yield structure | M1 | DONE |
| M2-C | Block C Content Modernization | Lectures 14–21 mapped to Tickets 13–20 with 8-Step High-Yield structure | M1 | DONE |
| M2-D | Block D Content Modernization | Lectures 22–27 mapped to Tickets 21–25 with 8-Step High-Yield structure | M1 | DONE |
| E2E | E2E Testing Suite (Tiers 1–5) | Implement complete 5-tier test suite in `tests/`, standalone runner `tests/run_all_tests.py`, and publish `TEST_READY.md` | none | DONE |
| M-Final | Final Acceptance, 100% Test Pass & Adversarial Hardening | Run 100% of E2E tests across all modernised lectures & tools, adversarial edge cases, forensic integrity audit | M2-A, M2-B, M2-C, M2-D, E2E | DONE |

## Interface Contracts
### 8-Step High-Yield Lecture Structure
Every lecture HTML file (`00-intro-ml.html` .. `27-actor-critic.html`) strictly follows this 8-step structure:
1. `## 1. Интуиция и мотивация` (High-level motivation, practical metaphor, real-world relevance)
2. `## 2. Архитектура и схема` (Visual conceptual ASCII/SVG/HTML diagram, workflow pipeline)
3. `## 3. Математический аппарат` (Formal equations, rigorous derivations, KaTeX/MathJax formatting, parameter definitions)
4. `## 4. Пошаговый числовой пример` (Concrete calculation with numerical inputs and step-by-step tensor/matrix arithmetic)
5. `## 5. Преимущества, недостатки и применимость` (Comparison table, trade-offs, when to use / when not to use)
6. `## 6. 🎯 Препод спросит` (Minimum 10 comprehensive Q&As covering deep theoretical caveats and common defense traps)
7. `## 7. 📝 Микро-задачи с решениями` (Minimum 6 practice problems with hidden/revealed detailed solutions)
8. `## 8. ⚡ Скелет ответа по билету` (Cheat-sheet structured outline: 3-5 key bullets for a 5-minute flawless exam answer)

### Exam Data Interface (`js/exam_data.js`)
- Exposes `window.EXAM_DATA = { tickets: [...], lectures: [...], questions: [...], tasks: [...] }`.
- Generated deterministically by `python tools/build_exam_data.py`.
- No Anki dependencies or leftover references.

### Mobile-First UI & Responsive Requirements
- Quick Action Bar fixed at bottom on mobile viewports (< 768px) with safe-area padding: `padding-bottom: env(safe-area-inset-bottom)`.
- All interactive buttons/links have touch targets $\ge 44 \times 44\text{ px}$.
- Mathematical formulas and tables enclosed in `.math-scroll-wrapper` or `.table-scroll-wrapper` with `overflow-x: auto; max-width: 100%;` preventing viewport horizontal overflow.
- 0 horizontal scroll overflow at document root across `320px`, `375px`, `414px`, `768px`, `1024px`, `1440px`, `2560px`.

## Code Layout
- `index.html`: Main landing & course dashboard (Blocks A–D).
- `exam.html`: Interactive exam simulator & SM-2 flashcards trainer.
- `lectures/*.html` or root `*.html`: The 28 modernized lecture files (`00-intro-ml.html` .. `27-actor-critic.html`).
- `css/`: `style.css`, `mobile.css`, `exam.css` (or unified modular stylesheets).
- `js/`: `app.js`, `exam.js`, `exam_data.js`, `sw.js`.
- `tools/`: `build_exam_data.py`.
- `tests/`: 5-tier test suite (`test_tier1_tools.py`, `test_tier2_static_ast.py`, `test_tier3_pwa_dom.py`, `test_tier4_viewport_responsive.py`, `test_tier5_adversarial.py`, `common.py`, `run_all_tests.py`).
