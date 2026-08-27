# Методы искусственного интеллекта и глубокого обучения (Deep Learning Exam Course)

<div align="center">

[![GitHub Release](https://img.shields.io/github/v/release/egorribun/AI-Course?style=for-the-badge&logo=github&color=58a6ff)](https://github.com/egorribun/AI-Course/releases)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Portal-58a6ff?style=for-the-badge&logo=github&logoColor=white)](https://egorribun.github.io/AI-Course/)
[![CI / Tests](https://img.shields.io/badge/CI%20Pytest-271%20Passed-3fb950?style=for-the-badge&logo=pytest&logoColor=white)](https://github.com/egorribun/AI-Course/actions)
[![Linter](https://img.shields.io/badge/Ruff-0%20Errors-46e3b7?style=for-the-badge&logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![uv](https://img.shields.io/badge/uv-Astral%20Fast%20Env-de5fe9?style=for-the-badge&logo=astral&logoColor=white)](https://github.com/astral-sh/uv)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-3776ab?style=for-the-badge&logo=python&logoColor=white)](pyproject.toml)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.x%20Ready-ee4c2c?style=for-the-badge&logo=pytorch&logoColor=white)](https://pytorch.org)
[![PWA Ready](https://img.shields.io/badge/PWA-Offline%20Ready-8957e5?style=for-the-badge&logo=pwa&logoColor=white)](manifest.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-d29922.svg?style=for-the-badge)](LICENSE)

[![Lectures](https://img.shields.io/badge/Lectures-28%20Interactive%20Modules-79c0ff?style=flat-square)](#3-модульный-интерактивный-учебный-план)
[![Exam QA](https://img.shields.io/badge/Exam%20QA-296%20Defense%20Items-56d364?style=flat-square)](#3-модульный-интерактивный-учебный-план)
[![Microtasks](https://img.shields.io/badge/Microtasks-170%20Step--by--Step-f0883e?style=flat-square)](#3-модульный-интерактивный-учебный-план)
[![Anki Cards](https://img.shields.io/badge/Anki%20Decks-494%20Cards-d2a8ff?style=flat-square)](anki_decks/)
[![Tickets](https://img.shields.io/badge/GUU%20Tickets-25%20Fully%20Covered-bc8cff?style=flat-square)](#3-модульный-интерактивный-учебный-план)

**Официальный академический паспорт и интерактивный портал подготовки к устному экзамену по курсу «Методы искусственного интеллекта» (ГУУ 2026).**

[🌐 Открыть интерактивный портал курса](https://egorribun.github.io/AI-Course/) • [📑 Оглавление и матрица билетов](#3-модульный-интерактивный-учебный-план) • [🧪 Запуск и тестирование](#локальный-запуск-и-верификация)

</div>

---

## 📌 О курсе и паспорте программы

Учебно-методический комплекс спроектирован для интенсивной подготовки к государственному устному экзамену и коллоквиумам по направлению «Методы искусственного интеллекта» (Государственный университет управления, 2026).

Курс охватывает сквозную траекторию современного машинного и глубокого обучения: от базовых принципов эмпирической минимизации риска и дифференцирования до современных генеративных диффузионных процессов, архитектур Трансформеров и алгоритмов глубокого обучения с подкреплением (Deep RL).

### 🎯 Целевые компетенции и результаты освоения

1. **Математический аппарат DL:** Владение строгими аналитическими выводами (Backpropagation, PINN/autograd, MLE/MAP, VAE ELBO, GAN Minimax, DDPM Forward/Reverse SDE/ODE, Уравнения Беллмана, Policy Gradient Theorem, GAE).
2. **Архитектурная грамотность:** Понимание размерностей тензоров, рецептивных полей, потоков градиентов, механизмов нормализации (BatchNorm, LayerNorm) и внимания (Self-Attention, Cross-Attention, FlashAttention).
3. **Практический инжиниринг:** Умение реализовывать ключевые блоки нейронных сетей на чистом Python / PyTorch без высокоуровневых абстракций.
4. **Устная академическая защита:** Навык экспресс-формулирования ответов у доски за 3 минуты и решения практических микро-задач при перекрестном опросе экзаменационной комиссией.

---

## 🏛️ Педагогическая архитектура лекции

Каждый лекционный модуль `lectures/*.html` спроектирован как изолированный, самодостаточный интерактивный учебный паспорт со строгим структурным контрактом:

1. **💡 Интуиция и физический смысл:** Мотивация, почему предыдущих методов было недостаточно, и какую проблему решает концепт.
2. **📐 Архитектурная схема:** Наглядные ASCII-графы и диаграммы вычислительных графов и потоков данных.
3. **🔬 Строгий математический аппарат:** Формулы в нотации LaTeX MathJax с посимвольной расшифровкой каждой переменной, оператора и размерности тензора.
4. **🔢 Сквозной числовой пример:** Пошаговый расчет матричных умножений, градиентов и вероятностей вручную с проверкой чисел.
5. **⚖️ Анализ компромиссов (Trade-offs):** Плюсы, минусы, вычислительная сложность $\mathcal{O}(\cdot)$, ограничения по памяти и условия применимости.
6. **🎯 Блок «Препод спросит» (10–12 вопросов с ответами):** Разбор провокационных вопросов с подвохом, граничных случаев и тонкостей реализации.
7. **📝 Блок «Микро-задачи у доски» (6+ задач с пошаговыми решениями):** Практические расчетные упражнения с раскрывающимися блоками `<details>`.
8. **⚡ Блок «Ответ за 3 минуты»:** Скелет и тезисный конспект для 100% уверенного устного ответа по билету.

---

## 📚 3-модульный интерактивный учебный план

Курс разбит на 3 интенсивных учебных модуля (дня), покрывающих все 25 экзаменационных билетов:

### Модуль 1: Фундамент нейросетей и компьютерное зрение (День 1)

| Лекция | Файл лекции | Экзаменационный билет ГУУ | Ключевые концепции и темы | Акад. часы |
|:---|:---|:---:|:---|:---:|
| **Лекция 00** | [`00-intro-ml.html`](lectures/00-intro-ml.html) | — | Каркас ML, Train/Val/Test, Overfitting, Регуляризация $L_1/L_2$, Data Leakage | 1.0 ч |
| **Лекция 01** | [`01-fcnn.html`](lectures/01-fcnn.html) | **Билет 1** | Полносвязные сети (FCNN), функции активации (ReLU, GELU, Swish), Backpropagation | 2.5 ч |
| **Лекция 02** | [`02-autodiff-pinn.html`](lectures/02-autodiff-pinn.html) | **Билет 2** | Графы автодифференцирования, Forward/Reverse mode, Физически-информированные сети (PINN) | 1.5 ч |
| **Лекция 03** | [`03-losses-mle.html`](lectures/03-losses-mle.html) | **Билет 3** | Функции потерь (MSE, MAE, Huber, BCE, CE), Принцип максимального правдоподобия (MLE) | 2.0 ч |
| **Лекция 04** | [`04-cnn-layers.html`](lectures/04-cnn-layers.html) | **Билет 4** | Свёрточные слои, Stride, Padding, Dilation, Receptive Field, Pooling, Batch Normalization | 2.0 ч |
| **Лекция 05** | [`05-cnn-architectures.html`](lectures/05-cnn-architectures.html) | **Билет 5** | Эволюция CNN: LeNet, AlexNet, VGG, ResNet (Skip-connections), Transfer Learning, Fine-tuning | 2.0 ч |
| **Лекция 06** | [`06-optimizers.html`](lectures/06-optimizers.html) | **Билет 6** | Оптимизаторы: SGD, Momentum, Nesterov, AdaGrad, RMSProp, Adam, AdamW, матричные производные | 2.5 ч |
| **Лекция 07** | [`07-hyperparams.html`](lectures/07-hyperparams.html) | **Билет 7** | Аугментация данных, тюнинг гиперпараметров, Grid/Random Search, Hyperband, Optuna | 2.0 ч |

### Модуль 2: Представления, генеративные модели и последовательности (День 2)

| Лекция | Файл лекции | Экзаменационный билет ГУУ | Ключевые концепции и темы | Акад. часы |
|:---|:---|:---:|:---|:---:|
| **Лекция 08** | [`08-metric-learning.html`](lectures/08-metric-learning.html) | **Билет 8** | Metric Learning, Сиамские сети, Contrastive Loss, Triplet Loss, Hard Negative Mining | 1.5 ч |
| **Лекция 09** | [`09-contrastive-ssl.html`](lectures/09-contrastive-ssl.html) | **Билет 9** | Self-Supervised Learning (SSL), Контрастивное обучение, InfoNCE Loss, SimCLR, MoCo, BYOL | 1.5 ч |
| **Лекция 10** | [`10-vae.html`](lectures/10-vae.html) | **Билет 10** | Автоэнкодеры: Vanilla AE, Вариационный автоэнкодер (VAE), вывод ELBO, Reparameterization Trick, CVAE | 2.0 ч |
| **Лекция 11** | [`11-gan.html`](lectures/11-gan.html) | **Билет 11** | Генеративно-состязательные сети (GAN), Minimax игра, Оптимальный дискриминатор, Mode Collapse, WGAN-GP | 2.0 ч |
| **Лекция 12** | [`12-diffusion.html`](lectures/12-diffusion.html) | **Билет 12** | Диффузионные вероятностные модели (DDPM), Прямой и обратный процесс, Скор-функция, U-Net шумоподавление | 2.0 ч |
| **Лекция 13** | [`13-cv-tasks.html`](lectures/13-cv-tasks.html) | **Билет 12** | Задачи Computer Vision: Детекция (YOLO, Faster R-CNN), Сегментация (U-Net, Mask R-CNN), IoU, mAP | 2.0 ч |
| **Лекция 14** | [`14-rnn-lstm.html`](lectures/14-rnn-lstm.html) | **Билет 13** | Рекуррентные сети (RNN), Затухание градиентов, BPTT, Ячейки LSTM и GRU, Двунаправленные biLSTM | 2.5 ч |
| **Лекция 15** | [`15-attention-seq2seq.html`](lectures/15-attention-seq2seq.html) | **Билет 14** | Seq2Seq архитектуры, Bottleneck вектор, Механизмы аддитивного (Bahdanau) и мультипликативного (Luong) внимания | 1.5 ч |

### Модуль 3: Трансформеры, обработка текстов и обучение с подкреплением (День 3)

| Лекция | Файл лекции | Экзаменационный билет ГУУ | Ключевые концепции и темы | Акад. часы |
|:---|:---|:---:|:---|:---:|
| **Лекция 16** | [`16-transformers.html`](lectures/16-transformers.html) | **Билет 15** | Архитектура Transformer («Attention Is All You Need»), Multi-Head Attention, Feed-Forward, LayerNorm | 2.0 ч |
| **Лекция 17** | [`17-self-attention.html`](lectures/17-self-attention.html) | **Билет 16** | Scaled Dot-Product Attention ($Q, K, V$), Причинные (Causal) маски, Позиционное кодирование (Sinusoidal, RoPE) | 2.0 ч |
| **Лекция 18** | [`18-lstm-vs-transformer.html`](lectures/18-lstm-vs-transformer.html) | **Билет 17** | Детальное сравнение LSTM и Transformer: Вычислительная сложность $\mathcal{O}(N^2)$ vs $\mathcal{O}(N)$, параллелизм, память | 1.0 ч |
| **Лекция 19** | [`19-text-word2vec.html`](lectures/19-text-word2vec.html) | **Билет 18** | NLP препроцессинг, Токенизация (BPE, WordPiece), Векторные представления Word2Vec (CBOW, Skip-gram, Neg. Sampling) | 1.5 ч |
| **Лекция 20** | [`20-mt-bleu.html`](lectures/20-mt-bleu.html) | **Билет 19** | Машинный перевод, Языковое моделирование (Perplexity), Декодирование (Greedy, Beam Search), Метрика BLEU | 1.5 ч |
| **Лекция 21** | [`21-enc-dec.html`](lectures/21-enc-dec.html) | **Билет 20** | Семейства трансформеров: Encoder-only (BERT, RoBERTa), Decoder-only (GPT-серия), Encoder-Decoder (T5, BART) | 1.25 ч |
| **Лекция 22** | [`22-rl-intro.html`](lectures/22-rl-intro.html) | **Билет 21** | Основы Reinforcement Learning: Среда, Агент, Марковский процесс принятия решений (MDP), Политическая функция $\pi$, Reward, Discount $\gamma$ | 1.75 ч |
| **Лекция 23** | [`23-bellman.html`](lectures/23-bellman.html) | **Билет 22** | Уравнение Беллмана для $V(s)$ и $Q(s,a)$, Оператор Беллмана, Уравнение оптимальности Беллмана (Bellman Optimality) | 1.5 ч |
| **Лекция 24** | [`24-vi-pi-mc.html`](lectures/24-vi-pi-mc.html) | **Билет 22** | Динамическое программирование в RL: Итерация по ценностям (Value Iteration), Итерация по стратегиям (Policy Iteration), Методы Монте-Карло | 2.0 ч |
| **Лекция 25** | [`25-td-qlearning.html`](lectures/25-td-qlearning.html) | **Билет 23** | Бессмодельное обучение (Model-Free): Temporal Difference TD(0), On-policy SARSA, Off-policy Q-Learning, Deep Q-Networks (DQN) | 2.0 ч |
| **Лекция 26** | [`26-policy-gradient.html`](lectures/26-policy-gradient.html) | **Билет 24** | Методы оптимизации стратегии: Метод кросс-энтропии (CEM), Теорема о градиенте стратегии (Policy Gradient Theorem), Алгоритм REINFORCE | 2.0 ч |
| **Лекция 27** | [`27-actor-critic.html`](lectures/27-actor-critic.html) | **Билет 25** | Сравнение Value-based vs Policy-based, Архитектуры Актор-Критик (Actor-Critic), Advantage ($A(s,a)$), A2C/A3C, PPO, SAC | 1.75 ч |

---

## 🚀 Интерактивная платформа и возможности

Веб-портал включает полный набор современных EdTech-инструментов для интенсивной подготовки:

1. **📱 Zero-build PWA и оффлайн-доступ (`sw.js`, `manifest.json`):**
   - **Progressive Web App:** Возможность установки платформы как нативного Standalone-приложения на iOS, Android, macOS и Windows.
   - **Оффлайн-режим (Service Worker):** Двухуровневое кэширование (Cache-First для страниц `lectures/*.html`, стилей `style.css`, скриптов `js/` и TSV-колод; Stale-While-Revalidate для MathJax CDN) — все 28 лекций и симулятор работают без подключения к сети.
   - **Манифест и иконки:** Файл `manifest.json` с темами оформления и векторный ассет `icon.svg`.

2. **🎲 Продвинутый симулятор экзамена (`js/simulator.js`):**
   - **Выбор билета (1–25) и рандомайзер:** Прямой выбор конкретного экзаменационного билета или случайная жеребьевка билета по официальной программе ГУУ.
   - **⏱️ 3-минутный таймер ответа:** 180-секундный таймер обратного отсчета с визуальным оповещением и звуковым гонгом (Web Audio API) для тренировки устного ответа у доски.
   - **⚡ Блиц-тестирование (Blitz Mode):** Экспресс-опрос из 10 случайных вопросов по всей программе курса для быстрой самопроверки.
   - **🎯 Тематический дриллинг (Topic Drill):** Выборка вопросов и задач по разделам (*Foundations*, *Computer Vision*, *Generative Models*, *NLP & Transformers*, *Reinforcement Learning*).
   - **🗂️ Flashcards (296 вопросов):** Карточки для самопроверки с каверзными вопросами и раскрывающимися ответами.
   - **📝 Банк микро-задач (170 задач):** Практические расчетные упражнения с пошаговыми решениями.

3. **🧠 Интервальные повторения (Leitner / SM-2 Spaced Repetition):**
   - **Алгоритм SuperMemo-2:** Расчет фактора легкости ($EF \ge 1.3$), интервалов повторения ($I$) и счетчика повторений ($n$).
   - **Очередь повторения (Due Queue):** Автоматическая фильтрация карточек, требующих повторения на текущую дату.
   - **Градация ответов:** Оценка качества ответа (0–5 / Снова, Трудно, Хорошо, Легко) с сохранением состояния в `LocalStorage` (`ai_course_sm2_cards`).

4. **⌨️ Эргономичные горячие клавиши (Keyboard Shortcuts):**
   - `[` / `]` — Быстрый переход к предыдущей / следующей лекции курса.
   - `T` — Мгновенное переключение тёмной и светлой темы оформления.
   - `/` — Фокус на строку живого поиска (с защитой от ложных срабатываний при активном вводе в текстовых полях).
   - `Alt + O` — Мгновенное раскрытие или закрытие всех скрытых спойлеров и решений `<details>` на странице.

5. **📊 Бессерверный трекинг прогресса (LocalStorage):**
   - Живой прогресс-бар курса (процент изученных лекций, проверенных вопросов и решенных задач).
   - Чекбоксы «Выучено / Решено» у каждого вопроса и задачи внутри лекций.
   - Экспорт и импорт прогресса в формате JSON (`ai_course_backup_*.json`).

6. **🔍 Живой поиск и фильтрация:**
   - Мгновенный клиентский поиск по 28 лекциям, билетам, формулам и терминам (например, `AdamW`, `ELBO`, `RoPE`, `BLEU`, `PPO`, `WGAN-GP`).
   - Быстрые теги фильтрации: *Computer Vision*, *NLP & Transformers*, *Reinforcement Learning*, *Math & Optimization*.

7. **📋 Инжиниринг UX и печать:**
   - Кнопки копирования блоков кода PyTorch с моментальной визуальной анимацией («Скопировано!»).
   - Оптимизированные стили печати (`@media print`) с авто-раскрытием спойлеров (`beforeprint`) для генерации аккуратных PDF-шпаргалок.

8. **📥 Экспорт колод в Anki (`tools/export_anki.py`):**
   - Готовые `.tsv` колоды для Anki Desktop/Mobile: `anki_decks/ai_course_exam_qas.tsv` (296 карточек), `anki_decks/ai_course_microtasks.tsv` (170 карточек), `anki_decks/ai_course_3min_cheatsheets.tsv` (28 шпаргалок).
   - Датасет `js/exam_data.js` для мгновенной работы симулятора в браузере.

---

## 🛠️ Локальный запуск и верификация

В репозитории настроено современное окружение на базе пакетного менеджера **Astral `uv`** и стандарта **PEP 621**.

### 1. Предварительные требования
- Установленный [Astral `uv`](https://docs.astral.sh/uv/getting-started/installation/) (рекомендуется) или Python $\ge 3.10$.

### 2. Установка окружения и зависимостей
```bash
# Клонирование репозитория
git clone https://github.com/egorribun/AI-Course.git
cd AI-Course

# Автоматическая синхронизация виртуального окружения (Python 3.10 + PyTorch + NumPy + Pytest + Ruff)
uv sync
```

### 3. Локальный просмотр портала
```bash
# Запуск локального HTTP-сервера для просмотра интерактивного портала
uv run python -m http.server 8000
```
После запуска откройте в браузере: [`http://localhost:8000`](http://localhost:8000) или откройте `index.html` напрямую.

### 4. Запуск автоматизированного тестового комплекса
Репозиторий защищен исчерпывающим сквозным набором из **254 тестов** (`tests/`), проверяющих математические выводы, целостность ссылок, баланс LaTeX-тегов, синтаксис AST, PWA и выполнение PyTorch тензорных операций:

```bash
# Запуск полного набора E2E тестов (254 теста)
uv run pytest tests/

# Проверка качества кода и линтинг (Ruff)
uv run ruff check .
```

---

## 📂 Структура репозитория

```text
AI-Course/
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Автоматический CI: uv sync + ruff check + pytest
│       └── deploy-pages.yml       # Автоматический деплой портала на GitHub Pages
├── .editorconfig                  # Стандарты форматирования, отступов и кодировки UTF-8
├── .gitattributes                 # Нормализация LF-окончаний строк и linguist-определения
├── .gitignore                     # Исключения кэшей, .venv, артефактов тестирования
├── .python-version                # Фиксация базовой версии Python (3.10)
├── LICENSE                        # Официальная лицензия MIT (Copyright 2026 Egor Ribun)
├── pyproject.toml                 # Стандарт PEP 621: метаданные, зависимости PyTorch/NumPy, pytest/ruff
├── uv.lock                        # Детерминированный lockfile зависимостей Astral uv
├── README.md                      # Академический паспорт курса и руководство разработчика
├── PROJECT.md                     # Архитектурный манифест, спецификация и дорожная карта
├── index.html                     # Главный интерактивный веб-портал и навигационная карта курса
├── sw.js                          # PWA Service Worker (офлайн-кэширование всех лекций и ассетов)
├── manifest.json                  # PWA Web App Manifest (standalone установка, иконки, цвета)
├── icon.svg                       # Векторная PWA-иконка приложения
├── style.css                      # Глобальная темная дизайн-система и адаптивные стили
├── js/                            # Модульный JavaScript-движок платформы
│   ├── app.js                     # Логика главной страницы, поиск, фильтры, горячие клавиши
│   ├── lecture.js                 # Интерактив лекций: копирование кода, спойлеры, хоткеи
│   ├── tracker.js                 # Локальный трекер прогресса (LocalStorage, экспорт/импорт)
│   ├── simulator.js               # Экзаменационный симулятор, 3-мин таймер, SM-2 интервальные повторения
│   └── exam_data.js               # Прекомпилированный датасет вопросов, билетов и микро-задач
├── anki_decks/                    # Готовые колоды Anki (.tsv)
│   ├── ai_course_exam_qas.tsv     # 296 карточек с вопросами экзаменатора и ответами
│   ├── ai_course_microtasks.tsv   # 170 расчетных задач с пошаговыми решениями
│   └── ai_course_3min_cheatsheets.tsv # 28 конспектов для 3-минутного ответа у доски
├── tools/
│   └── export_anki.py             # Парсер лекций для генерации Anki TSV и js/exam_data.js
├── lectures/                      # 28 интерактивных лекций со строгим структурным контрактом
│   ├── 00-intro-ml.html
│   ├── 01-fcnn.html
│   ├── ...
│   └── 27-actor-critic.html
├── dl_guu-dl_26/                  # Исходные экзаменационные материалы и задания ГУУ 2026
└── tests/                         # Автоматизированный E2E комплекс верификации курса (254 теста)
    ├── __init__.py
    ├── common.py                  # Общие утилиты парсинга DOM, LaTeX, AST
    ├── test_r1_coverage.py        # Проверка 100% покрытия билетов и тем
    ├── test_r2_math_latex.py      # Проверка LaTeX формул и математических инвариантов
    ├── test_r3_code_exec.py       # Исполнение и проверка PyTorch тензорного кода
    ├── test_r4_structure_nav.py   # Проверка структуры лекций, графа ссылок, QA/Task счетчиков
    ├── test_r5_summary_styling.py # Проверка HTML тегов, CSS стилей и summary маркеров
    ├── test_pwa_web_platform_m1.py # Верификация PWA, sw.js, manifest.json, a11y, Print CSS
    ├── test_sm2_and_simulator_e2e.py # Верификация SM-2 алгоритма, таймера и режимов симулятора
    └── ...                        # Форензик и состязательные валидаторы целостности
```

---

## 📖 Академические источники и литература

1. **Goodfellow, I., Bengio, Y., Courville, A.** *Deep Learning.* MIT Press, 2016.
2. **Sutton, R. S., Barto, A. G.** *Reinforcement Learning: An Introduction.* 2nd Edition, MIT Press, 2018.
3. **Vaswani, A. et al.** *Attention Is All You Need.* Advances in Neural Information Processing Systems (NeurIPS), 2017.
4. **Ho, J., Jain, A., Abbeel, P.** *Denoising Diffusion Probabilistic Models (DDPM).* NeurIPS, 2020.
5. **He, K., Zhang, X., Ren, S., Sun, J.** *Deep Residual Learning for Image Recognition (ResNet).* CVPR, 2016.
6. **Kingma, D. P., Welling, M.** *Auto-Encoding Variational Bayes (VAE).* ICLR, 2014.
7. **Goodfellow, I. et al.** *Generative Adversarial Nets (GAN).* NeurIPS, 2014.
8. **Schulman, J. et al.** *Proximal Policy Optimization Algorithms (PPO).* arXiv:1707.06347, 2017.

---

<div align="center">
  <sub>Лицензировано под <a href="LICENSE">MIT License</a> • Copyright © 2026 Egor Ribun. Все права защищены.</sub>
</div>
