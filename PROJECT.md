# Project: Deep Learning Course Full Audit & Modernization

## Architecture
- Static Educational Web Application & PWA (GitHub Pages deployable).
- 28 Interactive Lecture HTML Modules (`lectures/00-intro-ml.html` .. `lectures/27-actor-critic.html`).
- Core Portal UI (`index.html`, `style.css`, `app.js`).
- Interactive Components (`js/tracker.js`, `js/simulator.js`, `js/exam_data.js`).
- Service Worker (`sw.js`) with Network-First caching strategy for local assets and Stale-While-Revalidate for external CDNs (MathJax).
- Anki Export Tooling (`tools/export_anki.py`, `anki_decks/*.tsv`).
- Automated Testing Framework (`tests/` running 271+ pytest suites, `tests/run_all_tests.py`, `tests/adversarial_harness.cjs`).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | R1: UI Progress Hub Export Removal | Remove `<button ...>💾 Экспорт</button>` from `#global-progress-hub` in `index.html` while preserving Reset button and tracker logic | M1 | ORIGINAL_REQUEST §R1 |
| 2 | R2: Service Worker Network-First Strategy | Upgrade `sw.js` cache name to `ai-course-v2`, implement Network-First with cache fallback for local files, ensure clean purge of outdated caches on activate | M1 | ORIGINAL_REQUEST §R2 |
| 3 | R3: 28 Lectures Comprehensive Audit | Thorough audit of all 28 lectures for math/LaTeX correctness, PyTorch code AST, Russian grammar/terminology, QA/task counters, and navigation links | M3 | ORIGINAL_REQUEST §R3 |
| 4 | R4: Exam Data & Anki Deck Sync | Ensure `tools/export_anki.py` generates accurate TSVs in `anki_decks/` and `js/exam_data.js` matching all 28 lectures and 25 exam tickets | M2 | ORIGINAL_REQUEST §R4 |
| 5 | R5: Final Audit Report & E2E Test Suite Pass | Generate exhaustive `AUDIT_REPORT.md` / `walkthrough.md` documenting all audit items, and run full test suites (`uv run pytest`) ensuring 0 failures / 0 errors | M4 | ORIGINAL_REQUEST §R5 |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | UI & PWA Modernization | R1 (index.html button removal) & R2 (sw.js Network-First & cache version bump) + UI/PWA test updates | none | COMPLETED |
| M2 | Exam Simulator & Anki Sync | R4 (export_anki.py verification, anki_decks/*.tsv, js/exam_data.js sync) | M1 | COMPLETED |
| M3 | 28 Lectures Forensic Audit Verification | R3 (Verification of formulas, AST, counters, nav links, Russian text across all 28 lectures) | none | COMPLETED |
| M4 | Final Report & Master Verification | R5 (Generate AUDIT_REPORT.md, full pytest suite 296 tests, node adversarial harness) | M1, M2, M3 | COMPLETED |

## Code Layout
- `index.html`: Portal homepage and Progress Hub. Owned by M1 Worker.
- `sw.js`: Service Worker for PWA caching & offline support. Owned by M1 Worker.
- `tests/test_portal_ui.py`, `tests/test_pwa_and_ux_e2e.py`, `tests/test_pwa_web_platform_m1.py`: PWA & UI tests. Owned by M1 Worker.
- `tools/export_anki.py`, `js/exam_data.js`, `anki_decks/`: Anki tools & decks. Owned by M2 Worker.
- `lectures/*.html`: 28 lecture files. Owned by M3 Worker.
- `AUDIT_REPORT.md`: Comprehensive audit report. Owned by M4 Worker.

## Interface Contracts
### `index.html` ↔ `js/tracker.js`
- `CourseTracker.resetProgress()` invoked on Reset button click.
- Progress counters read `CourseTracker.getProgress()` and update DOM cards.
- `CourseTracker.exportProgressJSON()` remains available programmatically for tests and exam simulator.

### `sw.js` ↔ Browser / GitHub Pages
- Cache name: `const CACHE_NAME = 'ai-course-v2';`
- Local assets: Network-First (`fetch(req)` -> fallback `caches.match(req)`).
- Activate handler: `caches.keys()` -> delete keys `!== CACHE_NAME` -> `self.clients.claim()`.

### `lectures/*.html` ↔ `tools/export_anki.py` ↔ `js/exam_data.js`
- 28 lectures with `<details class="qa">` and `<div class="task">` parsed by BeautifulSoup.
- Generates 3 TSV files with exact column structure and `js/exam_data.js` with `window.EXAM_DATA`.
