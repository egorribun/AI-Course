# E2E Test Infra: Deep Learning Educational Platform

## Test Philosophy
- Requirement-driven, opaque-box and structural verification.
- 4-Tier test architecture + Tier 5 adversarial stress testing:
  - **Tier 1 - Feature Coverage**: Structural & functional verification of all 28 lectures, PWA, SM-2, exam simulator, hotkeys, copy buttons, Anki export.
  - **Tier 2 - Boundary & Corner Cases**: Edge conditions (navigation limits at L00/L27, shortcut focus collision in text inputs, SM-2 boundary ratings, extreme LaTeX formulas, print `<details>` states).
  - **Tier 3 - Cross-Feature Combinations**: Interactions between LocalStorage tracker, SM-2 state, exam simulator randomizer, theme switcher, and Anki data export.
  - **Tier 4 - Real-World Application Scenarios**: Complete exam preparation workflow simulation (studying lecture $\to$ solving microtasks $\to$ running 3-min timer on exam ticket $\to$ Leitner review $\to$ Anki export).
  - **Tier 5 - Adversarial Coverage Hardening**: White-box stress testing of PyTorch snippets, dynamic tensor execution, and LaTeX syntax parsers.

## Feature Inventory & Test Coverage Mapping
| # | Feature | Source (Requirement) | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---------|---------------------|:------:|:------:|:------:|:------:|
| 1 | Zero-build PWA & Service Worker (`sw.js`, `manifest.json`) | ORIGINAL_REQUEST §R1 | ✓ | ✓ | ✓ | ✓ |
| 2 | Web App Manifest & App Icons | ORIGINAL_REQUEST §R1 | ✓ | ✓ | ✓ | ✓ |
| 3 | Spaced Repetition (Leitner / SM-2) | ORIGINAL_REQUEST §R2 | ✓ | ✓ | ✓ | ✓ |
| 4 | Exam Simulator: Ticket Selector (1-25) | ORIGINAL_REQUEST §R2 | ✓ | ✓ | ✓ | ✓ |
| 5 | Exam Simulator: 3-Min Timer & Audio | ORIGINAL_REQUEST §R2 | ✓ | ✓ | ✓ | ✓ |
| 6 | Exam Simulator: Blitz & Drill Modes | ORIGINAL_REQUEST §R2 | ✓ | ✓ | ✓ | ✓ |
| 7 | Global Keyboard Shortcuts (`[`, `]`, `T`, `/`, `Alt+O`) | ORIGINAL_REQUEST §R2 | ✓ | ✓ | ✓ | ✓ |
| 8 | Code Snippet Copy Buttons & Feedback | ORIGINAL_REQUEST §R2 | ✓ | ✓ | ✓ | ✓ |
| 9 | Print CSS & WCAG 2.1 AA a11y | ORIGINAL_REQUEST §R1 | ✓ | ✓ | ✓ | ✓ |
| 10 | 28 Lectures Academic Rigor (8 Core Proofs) | ORIGINAL_REQUEST §R3 | ✓ | ✓ | ✓ | ✓ |
| 11 | EdTech Q&A ($\ge 10$) & Micro-Tasks ($\ge 6$) | ORIGINAL_REQUEST §R3 | ✓ | ✓ | ✓ | ✓ |
| 12 | LaTeX Delimiter & Syntax Integrity | ORIGINAL_REQUEST §R3 | ✓ | ✓ | ✓ | ✓ |
| 13 | PyTorch 2.x Idioms & AST Validation | ORIGINAL_REQUEST §R3 | ✓ | ✓ | ✓ | ✓ |
| 14 | Anki TSV Exporter (`tools/export_anki.py`) | ORIGINAL_REQUEST §R4 | ✓ | ✓ | ✓ | ✓ |
| 15 | Repository & Documentation Sync (`README.md`, `ruff`) | ORIGINAL_REQUEST §R5 | ✓ | ✓ | ✓ | ✓ |

## Test Architecture & Execution
- Framework: `pytest` (Python 3.10+)
- Master Test Suite: `tests/`
- Execution Command: `uv run pytest -v` (and `uv run python tests/run_all_tests.py`)
- Linter Command: `uv run ruff check .`
- Anki Generator Command: `uv run python tools/export_anki.py`
