# E2E Test Infra: «Методы ИИ» Educational Web Course

## Test Philosophy
- Requirement-driven, opaque-box and static AST verification.
- Zero tolerance for broken MathJax/KaTeX syntax, missing lecture steps, hardcoded answers, or viewport horizontal scroll regressions.
- Framework: Python `pytest` + `lxml`/`BeautifulSoup4` + Playwright/HTML DOM/CSS validator, executable via `uv run pytest` and `python tests/run_all_tests.py`.

## 5-Tier Test Architecture

### Tier 1: Python Tooling & CLI Coverage (100% target)
- `tests/test_tier1_tools.py`
- Tests for `tools/build_exam_data.py`:
  - Parsing all 28 lectures.
  - JSON and JS output format verification (`window.EXAM_DATA = ...`).
  - Error handling for malformed HTML, missing sections, invalid arguments.
  - CLI flags (`--output`, `--dry-run`, `--check`, `--verbose`).
  - 100% line and branch coverage via `pytest-cov`.

### Tier 2: Static Analysis, Math Rigor & 8-Step High-Yield Architecture
- `tests/test_tier2_static_ast.py`
- Validates all 28 lecture HTML files:
  - Strict presence of all 8 High-Yield sections (`## 1. Интуиция и мотивация` through `## 8. Скелет ответа по билету`).
  - Quantitative requirements: $\ge 10$ defense Q&As per lecture, $\ge 6$ micro-tasks per lecture.
  - Mathematical LaTeX rigor: Brace balance matching, no unescaped `&`, valid math environments (`$...$`, `$$...$$`), verification of 10 key theoretical derivations (ELBO, Bellman, MLE->Losses, Scaled Dot-Product variance normalization, Policy Gradient, Backprop chain rule, Softmax derivative, Triplet loss, GAN minimax, Diffusion reverse variance).
  - Python AST validation for all PyTorch/NumPy code blocks embedded in lectures.
  - De-sprintization compliance: 0 occurrences of sprint terms in user-facing text and navigation.

### Tier 3: DOM, PWA, Service Worker & State Persistence
- `tests/test_tier3_pwa_dom.py`
- PWA & Service Worker validation:
  - Cache version `ai-course-v3`.
  - Offline assets caching integrity (all HTML, CSS, JS, fonts included in precache list).
  - Web App Manifest conformance (`manifest.json` fields, icons, display standalone).
- Spaced Repetition (SM-2) engine tests:
  - Formula validation ($EF' = EF + (0.1 - (5 - q) \cdot (0.08 + (5 - q) \cdot 0.02))$, $EF \ge 1.3$).
  - Due date calculation and interval computation ($I_1=1, I_2=6, I_n = I_{n-1} \cdot EF$).
  - LocalStorage serialization, schema versioning, corrupt state recovery.

### Tier 4: Viewport & Responsive Layout (320px – 2560px)
- `tests/test_tier4_viewport_responsive.py`
- Tested viewports: `320px` (iPhone SE/older), `375px` (iPhone Mini/standard), `414px` (iPhone Plus/Max), `768px` (iPad Portrait), `1024px` (iPad Landscape), `1440px` (Desktop), `2560px` (Ultra-wide/4K).
- Assertions:
  - Document root horizontal overflow: `scrollWidth <= clientWidth` (0 horizontal scroll on body).
  - Touch targets: All interactive elements (`<button>`, `<a>`, `.tab`, `.card`, input controls) have dimensions $\ge 44 \times 44\text{ px}$ on mobile viewports ($<768\text{px}$).
  - Isolated formula & table containers: Every formula and table has `.math-scroll-wrapper` or `.table-scroll-wrapper` allowing internal horizontal scroll without spilling into page body.
  - Safe-area-insets: Quick Action Bar uses `padding-bottom: max(12px, env(safe-area-inset-bottom))`.

### Tier 5: Adversarial Fuzzing & Stress Testing
- `tests/test_tier5_adversarial.py`
- Adversarial search input fuzzing (XSS payloads, Unicode stress, regex injection).
- LocalStorage state corruption recovery (invalid JSON, missing fields, future timestamps).
- Exam simulator queue stress (empty queues, 1000+ items, rapid transitions).
- Edge-case mathematical expressions (nested fractions, multiline aligned matrices).

## Coverage Thresholds
- Tier 1: 100% line & branch coverage on Python scripts.
- Tier 2: 28/28 lectures passing all 8-step structure, AST, and LaTeX checks.
- Tier 3: 100% SM-2 algorithm & PWA manifest verification.
- Tier 4: 7/7 viewports with 0 page overflow and 100% $\ge 44\text{px}$ touch targets.
- Tier 5: 100% pass on all fuzzing and adversarial cases.
