# TEST_INFRA — Deep Learning Course E2E Test Infrastructure & Methodology

## 1. Test Philosophy
- **Requirement-Driven & Spec-Authoritative**: Every single test case is directly derived from `ORIGINAL_REQUEST.md` (R1: UI/UX & Responsive Navigation, R2: Code Quality & Polish, R3: 100% Test Coverage & Automated Verification) and the architectural contracts defined in `PROJECT.md`.
- **Opaque-Box & Behavioral Verification**: Tests evaluate observable outputs, DOM structures, CSS layout properties, mathematical invariants, state persistence, and offline service worker behaviors without relying on private implementation details.
- **Zero-Tolerance Quality Invariants**:
  - 0 broken internal hyperlinks or anchors across all 30 HTML pages.
  - 0 unbalanced LaTeX math delimiters or unescaped HTML entities in mathematical formulas.
  - 0 horizontal scrollbar regressions (`scrollWidth <= clientWidth`) across 7 responsive viewports (320px to 2560px).
  - 0 unhandled exceptions or NaN values under corrupted `localStorage` or adversarial search inputs.
  - 100% offline functionality through Service Worker precaching (`ai-course-v3`).
  - 100% line and branch coverage on Python tooling in `tools/`.

---

## 2. Feature Inventory Mapping

Every feature from `PROJECT.md` is mapped to its specific test files, validation tiers, and authoritative source requirements:

| # | Feature Name | Requirement Source | Primary Test Files | Validation Tiers |
|---|--------------|-------------------|-------------------|------------------|
| 1 | Desktop Exam Header Button | ORIGINAL_REQUEST R1 | `tests/test_e2e_requirements.py`<br>`tests/test_portal_ui.py` | Tier 1, Tier 4 |
| 2 | Simulator Removal from Body | ORIGINAL_REQUEST R1 | `tests/test_e2e_requirements.py`<br>`tests/test_pwa_web_platform_m1.py` | Tier 1, Tier 2 |
| 3 | Portal Bottom Navigation Bar | ORIGINAL_REQUEST R1 | `tests/test_e2e_requirements.py`<br>`tests/adversarial_sw_ui_stress_test.cjs` | Tier 1, Tier 3, Tier 4 |
| 4 | Lectures Bottom Navigation Bar | ORIGINAL_REQUEST R1 | `tests/test_e2e_requirements.py`<br>`tests/test_all_28_lectures_html_conformance.py` | Tier 1, Tier 4 |
| 5 | Safe Area Inset Layout | ORIGINAL_REQUEST R1 | `tests/test_e2e_requirements.py`<br>`tests/test_tier4_viewport_responsive.py` | Tier 1, Tier 2, Tier 4 |
| 6 | Universal Progress Modal | ORIGINAL_REQUEST R1 | `tests/test_e2e_requirements.py`<br>`tests/test_js_assets_and_tracker.py` | Tier 1, Tier 3 |
| 7 | Synchronized Theme Toggling | ORIGINAL_REQUEST R1 | `tests/test_e2e_requirements.py`<br>`tests/test_theme_and_styles.py`<br>`tests/adversarial_sw_ui_stress_test.cjs` | Tier 1, Tier 3 |
| 8 | Service Worker Precache Parity | ORIGINAL_REQUEST R2 | `tests/test_e2e_requirements.py`<br>`tests/adversarial_sw_ui_stress_test.cjs`<br>`tests/adversarial_sw_m1.cjs` | Tier 1, Tier 2, Tier 4 |
| 9 | LocalStorage Type Guarding | ORIGINAL_REQUEST R2 | `tests/test_e2e_requirements.py`<br>`tests/adversarial_sw_ui_stress_test.cjs`<br>`tests/test_tier5_adversarial.py` | Tier 2, Tier 3 |
| 10 | JS Redundancy Consolidation | ORIGINAL_REQUEST R2 | `tests/test_e2e_requirements.py`<br>`tests/test_exam_simulator.py` | Tier 1, Tier 2 |
| 11 | Lecture Heading Hierarchy | ORIGINAL_REQUEST R2 | `tests/test_e2e_requirements.py`<br>`tests/test_r4_structure_nav.py` | Tier 1, Tier 2 |
| 12 | Python 100% Line & Branch Coverage | ORIGINAL_REQUEST R3 | `tests/test_tier1_tools.py`<br>`tests/test_build_exam_data.py` | Tier 1, Tier 2 |
| 13 | JS & DOM Unit Tests | ORIGINAL_REQUEST R3 | `tests/test_e2e_requirements.py`<br>`tests/adversarial_harness.cjs` | Tier 1, Tier 2 |
| 14 | Adversarial Fuzzing Suite | ORIGINAL_REQUEST R3 | `tests/adversarial_sw_ui_stress_test.cjs`<br>`tests/test_tier5_adversarial.py` | Tier 2, Tier 3 |
| 15 | HTML5 & Asset Conformance | ORIGINAL_REQUEST R3 | `tests/test_e2e_requirements.py`<br>`tests/test_tier2_static_ast.py` | Tier 1, Tier 4 |
| 16 | CI/CD Workflow Pipeline | ORIGINAL_REQUEST R3 | `tests/test_e2e_requirements.py` | Tier 1, Tier 4 |

---

## 3. Test Architecture and Directory Layout

```
AI-Course/
├── TEST_INFRA.md                          # Test philosophy, architecture, and feature taxonomy
├── TEST_READY.md                          # Test runner manual, coverage table, and feature checklist
├── pyproject.toml                         # Pytest configuration and dependency definitions
├── sw.js                                  # Service Worker (ai-course-v3) with offline precache
├── index.html                             # Portal hub with 28 lecture cards & bottom navigation
├── exam.html                              # Standalone oral exam simulator & SM-2 flashcards
├── lectures/                              # 28 Structured High-Yield lectures (00 to 27)
│   ├── 00-intro-ml.html
│   └── ... (01 to 27)
├── js/                                    # Frontend application modules
│   ├── app.js                             # Live search, filter chips, keyboard shortcuts, mobile nav
│   ├── tracker.js                         # Universal state manager (CourseTracker), SM-2 engine
│   ├── exam.js                            # Standalone oral exam simulator, timer, SM-2 UI, blitz
│   ├── exam_data.js                       # Compiled dataset (28 lectures, 296 Q&As, 170 tasks)
│   └── lecture.js                         # Lecture reader navigation, spoiler toggles, QA/Task sync
├── tools/                                 # Build & dataset compilation scripts
│   └── build_exam_data.py                 # CLI dataset compiler (HTML -> JS dataset)
└── tests/                                 # Multi-tier test suite
    ├── common.py                          # Test fixtures, constants, HTML parsers, and oracles
    ├── run_all_tests.py                   # Master test runner orchestrating all tiers
    ├── test_e2e_requirements.py           # Comprehensive E2E Python assertions for all 16 features
    ├── test_tier1_tools.py                # Tier 1: 100% Python tooling & CLI branch coverage
    ├── test_tier2_static_ast.py           # Tier 2: Static AST, LaTeX math rigor, 8-step structure
    ├── test_tier3_pwa_dom.py              # Tier 3: DOM, PWA, Service Worker, and SM-2 persistence
    ├── test_tier4_viewport_responsive.py  # Tier 4: 7-Viewport zero horizontal overflow & touch targets
    ├── test_tier5_adversarial.py          # Tier 5: Adversarial search fuzzing & storage resilience
    ├── adversarial_sw_ui_stress_test.cjs  # Node.js E2E stress & adversarial test harness
    ├── adversarial_harness.cjs            # Headless Node.js DOM/storage/SM-2 mock verification
    ├── adversarial_sw_m1.cjs              # Headless Node.js Service Worker lifecycle verification
    └── ... (auxiliary forensics & syllabus validation suites)
```

---

## 4. 4-Tier Test Methodology

The platform verification conforms to a rigorous 4-tier testing hierarchy:

### Tier 1: Feature Coverage & Interface Contracts (Happy Path)
- **Objective**: Assert primary functional behavior and interface contracts for all 16 features under nominal operating conditions.
- **Coverage**:
  - Desktop header actions render «🎲 Тренажёр экзамена» button pointing to `exam.html`.
  - Mobile bottom navigation bar renders 4 interactive actions `[🔍 Поиск, 🎲 Тренажёр, 📊 Прогресс, 🌓 Тема]` across all 30 HTML pages (`index.html`, `exam.html`, and 28 `lectures/*.html`).
  - `CourseTracker` correctly tracks completed lectures, checked Q&As, checked micro-tasks, and theme preferences.
  - SM-2 algorithm advances repetitions and calculates intervals ($I_1=1$, $I_2=6$, $I_n = I_{n-1} \cdot EF$).
  - `tools/build_exam_data.py` compiles 28 lectures into `js/exam_data.js` containing 296 Q&As, 170 micro-tasks, and 231 cheat points.
  - Service Worker precaches all required static assets for offline readiness.

### Tier 2: Boundaries, Corners & Edge Cases
- **Objective**: Assert system resilience and mathematical bounds under extreme, zero-length, boundary, or out-of-range inputs.
- **Coverage**:
  - SM-2 ease factor lower bound clamp: $EF \ge 1.30$ under consecutive forgetting grades ($q=0, 1, 2$).
  - SM-2 out-of-bounds rating grades ($q < 0$, $q > 5$, NaN) clamped safely into $[0, 5]$.
  - 3:00 Oral Exam Timer boundary states ($180\text{s} \to 60\text{s}$ warning $\to 30\text{s}$ danger $\to 00:00$ termination with alert trigger).
  - Empty search inputs, whitespace-only queries, and missing DOM containers handled gracefully without exceptions.
  - Safe Area Insets: `max(8px, env(safe-area-inset-bottom, 0px))` applied to mobile navigation bars and floating buttons.
  - Heading hierarchy: All headings follow strictly descending hierarchy ($h1 \to h2 \to h3$) with 0 skipped levels across all 30 pages.

### Tier 3: Combinations & State Transitions
- **Objective**: Assert multi-module interactions, asynchronous events, and state mutations across the application lifecycle.
- **Coverage**:
  - Theme toggling synchronization: Toggling theme via header button or bottom nav bar updates DOM attribute `[data-theme]`, syncs button icons/text across the page, broadcasts `theme-changed` event, and persists to `localStorage`.
  - Spaced repetition due queue updates: Multi-day simulated study session transitions cards between unreviewed, learning, due, and mature states.
  - State Backup & Restore: Complete export/import round-trip of user progress with schema validation and malformed payload rejection.
  - Keyboard navigation focus isolation: Shortcuts (`/`, `T`, `[`, `]`) trigger global actions when body is active, but are strictly suppressed when focus is within `<input>`, `<textarea>`, `<select>`, or `contentEditable` elements.

### Tier 4: Real-World Scenarios & Full Platform Traversal
- **Objective**: Simulate complete end-to-end user journeys and validate full platform assets across all 30 HTML pages and 7 responsive viewport profiles.
- **Coverage**:
  - 30-Page Link Graph Integrity: 100% of internal hyperlinks, relative navigation links, and anchor tags (`#id`) resolve to valid target files and elements.
  - 7 Responsive Viewports: Automated layout validation across 320px, 375px, 414px, 768px, 1024px, 1440px, and 2560px with 0 horizontal overflow (`scrollWidth <= clientWidth`) and touch targets $\ge 44 \times 44\text{ px}$.
  - Offline PWA Simulation: Complete navigation and offline asset resolution through Service Worker network-first and cache fallback strategies.
  - 25 Exam Tickets Traversal: Complete mapping of all 25 official GUU 2026 exam tickets with full 8-section High-Yield structure.

---

## 5. Coverage Thresholds

| Metric / Scope | Minimum Target | Verification Method | Enforcement |
|---|---|---|---|
| **Python Tooling Line Coverage** | 100% | `pytest --cov=tools --cov-fail-under=100` | Mandatory in CI |
| **Python Tooling Branch Coverage** | 100% | `pytest --cov=tools --cov-branch --cov-fail-under=100` | Mandatory in CI |
| **Lecture HTML Pages Conformance** | 30/30 (100%) | `tests/test_e2e_requirements.py` | Mandatory in CI |
| **8-Section High-Yield Structure** | 28/28 (100%) | `tests/test_tier2_static_ast.py` | Mandatory in CI |
| **MathJax LaTeX Formula Balance** | 100% | `tests/test_math_balance_checker.py` | Mandatory in CI |
| **Touch Target Dimensions ($\ge 44\text{px}$)** | 100% | `tests/test_tier4_viewport_responsive.py` | Mandatory in CI |
| **Viewport Zero-Overflow (320px–2560px)** | 7/7 Viewports | `tests/test_tier4_viewport_responsive.py` | Mandatory in CI |
| **Adversarial & Fuzzing Pass Rate** | 100% | `node tests/adversarial_*.cjs` | Mandatory in CI |
| **Pytest Overall Pass Rate** | 100% (0 failures) | `uv run pytest` | Mandatory in CI |
