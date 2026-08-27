# План реализации: Комплексная модернизация платформы «Методы ИИ» (ГУУ 2026)

> **Для исполнителей:** ТРЕБУЕМЫЙ ПОДХОД: TDD, пошаговая реализация с непрерывной верификацией тестами (`uv run pytest tests/`), сохранение обратной совместимости с 200 существующими тестами.

**Цель:** Превратить статический портал курса «Методы ИИ» в интерактивную EdTech-платформу с симулятором устного экзамена (рандомайзер билетов 1–25, 3-минутный таймер, flashcards, банк задач), трекингом прогресса в LocalStorage, живым поиском/фильтрами, DRY-рефакторингом CSS/JS, Anki-экспортером и pre-commit автоматизацией.

**Архитектура:** Единая дизайн-система `style.css` с поддержкой Dark/Light тем и `@media print`, модульные Vanilla JS скрипты (`js/tracker.js`, `js/lecture.js`, `js/simulator.js`, `js/app.js`), инструмент `tools/export_anki.py` для генерации колод Anki, и расширенный тестовый комплекс `tests/`.

**Спецификация:** [`docs/superpowers/specs/2026-08-27-platform-and-org-enhancements-design.md`](../specs/2026-08-27-platform-and-org-enhancements-design.md)

---

## Задачи реализации

### Task 1: Дизайн-система, темы и стили (`style.css`)
- Поддержка тем `[data-theme="light"]` и `[data-theme="dark"]`.
- Стили для симулятора экзамена, таймера, флешкарт, прогресс-баров, бейджей, тултипов и кнопок копирования.
- `@media print` стили.
- Тест: `tests/test_theme_and_styles.py`.

### Task 2: Ядро сохранения состояния (`js/tracker.js`)
- LocalStorage API: `getCompletedLectures()`, `toggleLecture()`, `getCheckedQAs()`, `toggleQA()`, `getCheckedTasks()`, `toggleTask()`, `getTheme()`, `setTheme()`.
- Вычисление суммарной статистики и экспорт/импорт JSON.
- Тест: `tests/test_js_assets_and_tracker.py`.

### Task 3: Внутристраничный интерактив лекций (`js/lecture.js`)
- Полоса прогресса чтения, кнопка копирования кода, чекбоксы в блоках QA и задач, кнопка «Наверх», переключатель темы.
- Тест: `tests/test_lecture_interactivity.py`.

### Task 4: Экзаменационный тренажер и банк задач (`js/simulator.js`)
- Рандомайзер билетов 1–25 с тезисами 3-минутного ответа.
- Интерактивный 3-минутный таймер со звуком гонга/бипа через Web Audio API.
- Режим Flashcards для 280+ вопросов преподавателя.
- Банк 170+ задач с фильтрацией по темам.
- Кнопки скачивания Anki колод.
- Тест: `tests/test_exam_simulator.py`.

### Task 5: Главная страница, живой поиск и фильтрация (`index.html` + `js/app.js`)
- Контейнер симулятора экзамена на главной странице.
- Виджет общего прогресса курса с живым обновлением.
- Живой поиск с подсветкой и теги (CV, NLP, RL, Math, Optimization).
- Тест: `tests/test_portal_ui.py`.

### Task 6: Генератор колод Anki (`tools/export_anki.py`)
- Извлечение всех QA, задач и шпаргалок из 28 HTML-файлов.
- Экспорт в `anki_decks/*.tsv`.
- Тест: `tests/test_anki_exporter.py`.

### Task 7: DRY CSS/JS Рефакторинг 28 лекций (`lectures/*.html`)
- Замена встроенных тегов `<style>` на `<link rel="stylesheet" href="../style.css">`.
- Подключение `<script src="../js/tracker.js"></script>` и `<script src="../js/lecture.js"></script>`.
- Тест: `tests/test_dry_css_refactor.py` и полный прогон 200 существующих тестов.

### Task 8: Инженерная инфраструктура, Git Hooks и CI/CD
- `.pre-commit-config.yaml` с `ruff`, проверкой синтаксиса и гигиены.
- Обновление `tests/run_all_tests.py`, `.github/workflows/ci.yml`, `README.md`, `PROJECT.md`.
- Полный прогон `pytest tests/`.
