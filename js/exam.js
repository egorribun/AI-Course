/**
 * ExamSimulator & Exam Hub (Vanilla ES6)
 * Interactive oral exam simulator, 3-minute timer, Leitner / SM-2 spaced repetition flashcards,
 * 4-Block modular drill, and Blitz exam mode.
 */
(function() {
  'use strict';

  // --- State Variables ---
  let timerInterval = null;
  let timerSecondsLeft = 180; // 3 minutes
  let timerRunning = false;

  // Flashcards state
  let allCardsList = [];
  let currentCardIndex = 0;
  let activeCardsQueue = [];
  let currentFlashcardFilter = 'all'; // 'all' | 'due'
  let currentFlashcardBlock = 'all';  // 'all' | 'block-a' | 'block-b' | 'block-c' | 'block-d'

  // Blitz mode state
  let blitzQuestions = [];
  let blitzCurrentIndex = 0;
  let blitzScore = 0;
  let blitzAnswers = [];
  let blitzTimerInterval = null;
  let blitzSecondsLeft = 30;

  // Block classification helper (Lectures 00-07 -> A, 08-13 -> B, 14-21 -> C, 22-27 -> D)
  function getLectureBlock(lecId) {
    const num = parseInt(lecId, 10);
    if (isNaN(num)) return 'block-a';
    if (num <= 7) return 'block-a';
    if (num <= 13) return 'block-b';
    if (num <= 21) return 'block-c';
    return 'block-d';
  }

  // Topic classification helper for backwards compatibility
  function getLectureTopic(lecId) {
    const block = getLectureBlock(lecId);
    if (block === 'block-a' || block === 'block-b') return 'cv';
    if (block === 'block-c') return 'nlp';
    return 'rl';
  }

  // Match block or topic filter
  function matchesFilter(lecId, filterVal) {
    if (!filterVal || filterVal === 'all') return true;
    const block = getLectureBlock(lecId);
    if (filterVal === block || filterVal === block.replace('block-', '')) return true;
    if (filterVal === 'cv' && (block === 'block-a' || block === 'block-b')) return true;
    if (filterVal === 'nlp' && block === 'block-c') return true;
    if (filterVal === 'rl' && block === 'block-d') return true;
    if (filterVal === 'math' && block === 'block-a') return true;
    return false;
  }

  // Web Audio Beep
  function playBeep(freq = 880, duration = 0.3) {
    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.3, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + duration);
    } catch (e) {}
  }

  function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  // ==========================================================
  // 1. 3-Minute Timer for Oral Exam Ticket
  // ==========================================================
  function updateTimerDisplay() {
    const el = document.getElementById('timer-val');
    if (!el) return;
    el.textContent = formatTime(timerSecondsLeft);
    el.classList.remove('warn', 'danger');
    if (timerSecondsLeft <= 30 && timerSecondsLeft > 0) {
      el.classList.add('warn');
    } else if (timerSecondsLeft === 0) {
      el.classList.add('danger');
    }
  }

  function resetTimer() {
    clearInterval(timerInterval);
    timerRunning = false;
    timerSecondsLeft = 180;
    updateTimerDisplay();
    const btn = document.getElementById('timer-toggle-btn');
    if (btn) btn.textContent = '▶ Старт 3:00';
  }

  function toggleTimer() {
    const btn = document.getElementById('timer-toggle-btn');
    if (timerRunning) {
      clearInterval(timerInterval);
      timerRunning = false;
      if (btn) btn.textContent = '▶ Продолжить';
    } else {
      if (timerSecondsLeft === 0) timerSecondsLeft = 180;
      timerRunning = true;
      if (btn) btn.textContent = '⏸ Пауза';
      timerInterval = setInterval(() => {
        timerSecondsLeft--;
        updateTimerDisplay();
        if (timerSecondsLeft <= 0) {
          clearInterval(timerInterval);
          timerRunning = false;
          playBeep(523.25, 0.6); // End gong
          if (btn) btn.textContent = '🔄 Сначала';
        }
      }, 1000);
    }
  }

  // ==========================================================
  // 2. Exam Ticket Renderer (Tab 1)
  // ==========================================================
  function renderRandomTicket(ticketData) {
    const container = document.getElementById('ticket-result-area');
    if (!container || !ticketData) return;

    resetTimer();

    const qasSample = (ticketData.qas || []).slice(0, 3);
    const taskSample = (ticketData.tasks || [])[0];

    const html = `
      <div class="box exambox" style="margin-top:16px;">
        <div class="bt">🎯 Выбранный билет: ${ticketData.ticket}</div>
        <h3 style="margin: 6px 0 10px; color: var(--text);">${ticketData.title}</h3>
        <p><a href="lectures/${ticketData.filename}" class="backlink" target="_blank" rel="noopener">📖 Открыть полный конспект лекции →</a></p>
      </div>

      <!-- 3-Minute Timer -->
      <div class="timer-box" role="region" aria-label="Таймер устного ответа">
        <div>
          <div style="font-size:13px; font-weight:700; color:var(--text-dim); text-transform:uppercase;">Таймер устного ответа у доски</div>
          <div class="timer-display" id="timer-val" aria-live="polite">03:00</div>
        </div>
        <div class="timer-controls">
          <button type="button" class="btn btn-exam" id="timer-toggle-btn" aria-label="Запустить или приостановить таймер">▶ Старт 3:00</button>
          <button type="button" class="btn btn-secondary" id="timer-reset-btn" aria-label="Сбросить таймер">🔄 Сброс</button>
        </div>
      </div>

      <!-- Ticket Cheat Skeleton -->
      ${ticketData.cheat_items && ticketData.cheat_items.length > 0 ? `
        <div class="cheat" style="margin: 20px 0;">
          <div class="bt">⚡ Краткий скелет ответа по билету</div>
          <ol>
            ${ticketData.cheat_items.map(it => `<li>${it}</li>`).join('')}
          </ol>
        </div>
      ` : ''}

      <!-- Sample Questions -->
      ${qasSample.length > 0 ? `
        <h4 style="margin-top:24px;">🎯 Вопросы преподавателя к этому билету:</h4>
        ${qasSample.map((qa, i) => `
          <details class="qa" style="margin:10px 0;">
            <summary>${qa.question}</summary>
            <div class="ans"><p>${qa.answer}</p></div>
          </details>
        `).join('')}
      ` : ''}

      <!-- Sample Task -->
      ${taskSample ? `
        <h4 style="margin-top:24px;">📝 Микро-задача у доски:</h4>
        <div class="task">
          <div class="tt">${taskSample.title}</div>
          <p>${taskSample.problem}</p>
          <details class="sol"><summary>Решение</summary><div class="sol">${taskSample.solution}</div></details>
        </div>
      ` : ''}
    `;

    container.innerHTML = html;

    // Bind timer buttons
    const toggleBtn = document.getElementById('timer-toggle-btn');
    const resetBtn = document.getElementById('timer-reset-btn');
    if (toggleBtn) toggleBtn.addEventListener('click', toggleTimer);
    if (resetBtn) resetBtn.addEventListener('click', resetTimer);

    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([container]).catch(err => console.warn(err));
    }
  }

  function setupTicketSelector() {
    const selectEl = /** @type {HTMLSelectElement | null} */ (document.getElementById('ticket-select-dropdown'));
    const drawBtn = document.getElementById('draw-ticket-btn');
    const blockSelect = /** @type {HTMLSelectElement | null} */ (document.getElementById('ticket-topic-filter'));
    const data = window.EXAM_DATA || [];

    if (selectEl && data.length > 0) {
      selectEl.innerHTML = '<option value="">-- Выберите билет вручную (Билеты 1–25) --</option>' +
        data.map((lec) => {
          return `<option value="${lec.id}">[Блок ${lec.module}] ${lec.ticket}: ${lec.title.replace(/^Лекция\s*\d+\.\s*/, '')}</option>`;
        }).join('');

      selectEl.addEventListener('change', (e) => {
        const val = /** @type {HTMLSelectElement} */ (e.target).value;
        if (!val) return;
        const chosen = data.find(d => d.id === val);
        if (chosen) renderRandomTicket(chosen);
      });
    }

    if (drawBtn) {
      drawBtn.addEventListener('click', () => {
        if (data.length === 0) return;
        const filterVal = blockSelect ? blockSelect.value : 'all';
        let candidates = data.filter(d => d.id !== '00');
        if (filterVal !== 'all') {
          candidates = candidates.filter(d => matchesFilter(d.id, filterVal));
        }
        if (candidates.length === 0) candidates = data;
        const chosen = candidates[Math.floor(Math.random() * candidates.length)];
        if (selectEl) selectEl.value = chosen.id;
        renderRandomTicket(chosen);
      });
    }

    if (blockSelect) {
      blockSelect.addEventListener('change', () => {
        const filterVal = blockSelect.value;
        if (selectEl) {
          let filtered = data;
          if (filterVal !== 'all') {
            filtered = data.filter(d => matchesFilter(d.id, filterVal));
          }
          selectEl.innerHTML = '<option value="">-- Выберите билет из выбранного блока --</option>' +
            filtered.map((lec) => {
              return `<option value="${lec.id}">[Блок ${lec.module}] ${lec.ticket}: ${lec.title.replace(/^Лекция\s*\d+\.\s*/, '')}</option>`;
            }).join('');
        }
      });
    }
  }

  // ==========================================================
  // 3. Spaced Repetition (Leitner / SM-2) Flashcards (Tab 2)
  // ==========================================================
  function buildAllCardsList() {
    const rawData = window.EXAM_DATA || [];
    allCardsList = [];
    rawData.forEach(lec => {
      const block = getLectureBlock(lec.id);
      (lec.qas || []).forEach((qa, idx) => {
        allCardsList.push({
          id: `l${lec.id}_qa${idx}`,
          lectureId: lec.id,
          lectureTitle: lec.title,
          ticket: lec.ticket,
          block: block,
          module: lec.module,
          question: qa.question,
          answer: qa.answer
        });
      });
    });
  }

  function updateFlashcardsQueue() {
    buildAllCardsList();

    const sm2 = window.CourseTracker ? window.CourseTracker.sm2 : null;

    activeCardsQueue = allCardsList.filter(card => {
      // 1. Block filter
      if (currentFlashcardBlock !== 'all' && !matchesFilter(card.lectureId, currentFlashcardBlock)) {
        return false;
      }
      // 2. Queue mode filter
      if (currentFlashcardFilter === 'due' && sm2) {
        return sm2.isCardDue(card.id);
      }
      return true;
    });

    currentCardIndex = 0;
    renderFlashcard();
    renderFlashcardStats();
  }

  function renderFlashcardStats() {
    const statsEl = document.getElementById('flashcard-stats-bar');
    if (!statsEl || !window.CourseTracker) return;

    const stats = window.CourseTracker.sm2.getStats();
    statsEl.innerHTML = `
      <div style="display:flex; gap:10px; flex-wrap:wrap; font-size:13px; margin-bottom:14px; color:var(--text-dim);">
        <span class="pill good">📅 К повторению: <strong>${stats.dueCount}</strong></span>
        <span class="pill gray">Всего изучено: <strong>${stats.totalReviewed} / ${allCardsList.length}</strong></span>
        <span class="pill warn">В долговременной памяти (коробки 4-5): <strong>${stats.matureCount}</strong></span>
      </div>
    `;
  }

  function renderFlashcard() {
    const cardWrap = document.getElementById('flashcard-wrap');
    if (!cardWrap) return;

    if (activeCardsQueue.length === 0) {
      cardWrap.innerHTML = `
        <div class="box okbox" style="text-align:center; padding:32px 16px;">
          <h3>🎉 Все карточки повторены!</h3>
          <p style="color:var(--text-dim); margin-bottom:16px;">На сегодня в этой категории нет карточек, требующих повторения.</p>
          <button type="button" class="btn btn-primary" id="fc-show-all-btn">Показать все карточки (296)</button>
        </div>
      `;
      const btn = document.getElementById('fc-show-all-btn');
      if (btn) {
        btn.addEventListener('click', () => {
          currentFlashcardFilter = 'all';
          document.querySelectorAll('[data-fc-filter]').forEach(el => {
            el.classList.toggle('active', el.getAttribute('data-fc-filter') === 'all');
          });
          updateFlashcardsQueue();
        });
      }
      return;
    }

    const card = activeCardsQueue[currentCardIndex];
    const sm2 = window.CourseTracker ? window.CourseTracker.sm2 : null;
    const cardState = sm2 ? sm2.getCard(card.id) : { box: 1, repetitions: 0, interval: 0, easeFactor: 2.5 };

    cardWrap.innerHTML = `
      <div class="flashcard-box" id="active-flashcard" role="region" aria-label="Карточка интервального повторения">
        <div class="fc-header">
          <span class="pill gray">Блок ${card.module} · ${card.ticket}</span>
          <span class="pill warn">Коробка ${cardState.box} / 5 (Интервал: ${cardState.interval} дн.)</span>
          <span style="font-size:12px; color:var(--text-dim); margin-left:auto;">${currentCardIndex + 1} из ${activeCardsQueue.length}</span>
        </div>

        <div class="fc-question" style="font-size:16px; font-weight:700; margin:16px 0 12px; color:var(--text);">
          ${card.question}
        </div>

        <div class="fc-answer-area" id="fc-answer-area" style="display:none; border-top:1px solid var(--line); padding-top:14px; margin-top:14px;">
          <div class="fc-answer-title" style="font-size:12px; font-weight:700; color:var(--accent); text-transform:uppercase; margin-bottom:6px;">Эталонный ответ:</div>
          <div class="fc-answer-text" style="font-size:14px; line-height:1.6; color:var(--text);">${card.answer}</div>
        </div>

        <div class="fc-actions" style="margin-top:18px;">
          <button type="button" class="btn btn-exam" id="fc-reveal-btn" style="width:100%; min-height:44px;">
            👀 Показать ответ (Пробел)
          </button>

          <div id="fc-rating-buttons" style="display:none; margin-top:14px;">
            <div style="font-size:12px; font-weight:600; color:var(--text-dim); margin-bottom:8px; text-align:center;">Оцените качество вашего ответа:</div>
            <div style="display:grid; grid-template-columns:repeat(5, 1fr); gap:6px;">
              <button type="button" class="btn btn-secondary sm2-rate-btn" data-grade="1" style="min-height:44px;" title="Не вспомнил">1: Забыл</button>
              <button type="button" class="btn btn-secondary sm2-rate-btn" data-grade="2" style="min-height:44px;" title="Трудно">2: С трудом</button>
              <button type="button" class="btn btn-secondary sm2-rate-btn" data-grade="3" style="min-height:44px;" title="Вспомнил с подсказкой">3: Неплохо</button>
              <button type="button" class="btn btn-secondary sm2-rate-btn" data-grade="4" style="min-height:44px;" title="Хорошо">4: Хорошо</button>
              <button type="button" class="btn btn-primary sm2-rate-btn" data-grade="5" style="min-height:44px;" title="Идеально">5: Отлично</button>
            </div>
          </div>
        </div>
      </div>
    `;

    const revealBtn = document.getElementById('fc-reveal-btn');
    const answerArea = document.getElementById('fc-answer-area');
    const ratingButtons = document.getElementById('fc-rating-buttons');

    if (revealBtn) {
      revealBtn.addEventListener('click', () => {
        revealBtn.style.display = 'none';
        if (answerArea) answerArea.style.display = 'block';
        if (ratingButtons) ratingButtons.style.display = 'block';

        if (window.MathJax && window.MathJax.typesetPromise) {
          window.MathJax.typesetPromise([answerArea]).catch(err => console.warn(err));
        }
      });
    }

    cardWrap.querySelectorAll('.sm2-rate-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const grade = parseInt(e.currentTarget.getAttribute('data-grade'), 10);
        if (window.CourseTracker && window.CourseTracker.sm2) {
          window.CourseTracker.sm2.recordReview(card.id, grade);
        }
        currentCardIndex++;
        renderFlashcard();
        renderFlashcardStats();
      });
    });

    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([cardWrap]).catch(err => console.warn(err));
    }
  }

  function setupFlashcardFilters() {
    document.querySelectorAll('[data-fc-filter]').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('[data-fc-filter]').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        currentFlashcardFilter = chip.getAttribute('data-fc-filter');
        updateFlashcardsQueue();
      });
    });

    document.querySelectorAll('[data-fc-topic]').forEach(chip => {
      chip.addEventListener('click', () => {
        document.querySelectorAll('[data-fc-topic]').forEach(c => c.classList.remove('active'));
        chip.classList.add('active');
        currentFlashcardBlock = chip.getAttribute('data-fc-topic');
        updateFlashcardsQueue();
      });
    });
  }

  // ==========================================================
  // 4. Blitz Exam Mode (Tab 3)
  // ==========================================================
  function startBlitzSession(filterBlock = 'all') {
    buildAllCardsList();

    let pool = allCardsList;
    if (filterBlock !== 'all') {
      pool = allCardsList.filter(c => matchesFilter(c.lectureId, filterBlock));
    }
    if (pool.length < 10) pool = allCardsList;

    // Shuffle and pick 10
    const shuffled = [...pool].sort(() => Math.random() - 0.5);
    blitzQuestions = shuffled.slice(0, 10);
    blitzCurrentIndex = 0;
    blitzScore = 0;
    blitzAnswers = [];

    renderBlitzActiveQuestion();
  }

  function renderBlitzActiveQuestion() {
    const container = document.getElementById('blitz-container');
    if (!container) return;

    if (blitzCurrentIndex >= blitzQuestions.length) {
      renderBlitzResults();
      return;
    }

    const currentQ = blitzQuestions[blitzCurrentIndex];
    blitzSecondsLeft = 30;

    container.innerHTML = `
      <div class="box exambox" style="margin-top:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <span class="pill warn">Вопрос ${blitzCurrentIndex + 1} из ${blitzQuestions.length}</span>
          <span class="pill gray">Блок ${currentQ.module} · ${currentQ.ticket}</span>
          <span class="timer-display" id="blitz-timer" style="font-size:20px; color:var(--accent);">00:30</span>
        </div>

        <div style="font-size:17px; font-weight:700; margin:16px 0; color:var(--text);">
          ${currentQ.question}
        </div>

        <div id="blitz-answer-area" style="display:none; border-top:1px solid var(--line); padding-top:12px; margin-top:12px;">
          <div style="font-size:12px; font-weight:700; color:var(--accent); text-transform:uppercase; margin-bottom:4px;">Эталон ответа:</div>
          <div style="font-size:14px; line-height:1.6; color:var(--text);">${currentQ.answer}</div>
        </div>

        <div style="margin-top:20px;" id="blitz-controls">
          <button type="button" class="btn btn-primary" id="blitz-show-btn" style="width:100%; min-height:44px;">
            👀 Показать ответ
          </button>
          
          <div id="blitz-judge-buttons" style="display:none; gap:12px; margin-top:12px; grid-template-columns:1fr 1fr;">
            <button type="button" class="btn btn-secondary" id="blitz-wrong-btn" style="background:rgba(255,85,85,0.15); border-color:#ff5555; color:#ff5555; min-height:44px;">
              ✗ Неверно / Не знал
            </button>
            <button type="button" class="btn btn-primary" id="blitz-correct-btn" style="background:rgba(80,250,123,0.2); border-color:#50fa7b; color:#50fa7b; min-height:44px;">
              ✓ Ответил верно
            </button>
          </div>
        </div>
      </div>
    `;

    // Start 30s question countdown
    clearInterval(blitzTimerInterval);
    const timerEl = document.getElementById('blitz-timer');
    blitzTimerInterval = setInterval(() => {
      blitzSecondsLeft--;
      if (timerEl) {
        timerEl.textContent = `00:${String(blitzSecondsLeft).padStart(2, '0')}`;
        if (blitzSecondsLeft <= 5) timerEl.style.color = '#ff5555';
      }
      if (blitzSecondsLeft <= 0) {
        clearInterval(blitzTimerInterval);
        playBeep(440, 0.2);
      }
    }, 1000);

    const showBtn = document.getElementById('blitz-show-btn');
    const ansArea = document.getElementById('blitz-answer-area');
    const judgeBtns = document.getElementById('blitz-judge-buttons');

    if (showBtn) {
      showBtn.addEventListener('click', () => {
        clearInterval(blitzTimerInterval);
        showBtn.style.display = 'none';
        if (ansArea) ansArea.style.display = 'block';
        if (judgeBtns) judgeBtns.style.display = 'grid';

        if (window.MathJax && window.MathJax.typesetPromise) {
          window.MathJax.typesetPromise([ansArea]).catch(err => console.warn(err));
        }
      });
    }

    const wrongBtn = document.getElementById('blitz-wrong-btn');
    const correctBtn = document.getElementById('blitz-correct-btn');

    if (wrongBtn) {
      wrongBtn.addEventListener('click', () => {
        blitzAnswers.push({ question: currentQ.question, ticket: currentQ.ticket, isCorrect: false });
        blitzCurrentIndex++;
        renderBlitzActiveQuestion();
      });
    }

    if (correctBtn) {
      correctBtn.addEventListener('click', () => {
        blitzScore++;
        blitzAnswers.push({ question: currentQ.question, ticket: currentQ.ticket, isCorrect: true });
        blitzCurrentIndex++;
        renderBlitzActiveQuestion();
      });
    }

    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([container]).catch(err => console.warn(err));
    }
  }

  function renderBlitzResults() {
    const container = document.getElementById('blitz-container');
    if (!container) return;

    clearInterval(blitzTimerInterval);

    let gradeClass = 'good';
    let gradeLabel = '🌟 Отлично! Готов к сдаче на 5';
    if (blitzScore < 6) {
      gradeClass = 'bad';
      gradeLabel = '⚠️ Требуется повторение материала';
    } else if (blitzScore < 8) {
      gradeClass = 'warn';
      gradeLabel = '👍 Хороший уровень (оценка 4)';
    }

    container.innerHTML = `
      <div class="box okbox" style="text-align:center; padding:28px 16px; margin-top:16px;">
        <h3>Результаты блиц-опроса</h3>
        <div style="font-size:48px; font-weight:800; color:var(--accent); margin:12px 0;">
          ${blitzScore} / 10
        </div>
        <p class="pill ${gradeClass}" style="font-size:15px; padding:6px 16px; margin-bottom:20px;">
          ${gradeLabel}
        </p>

        <div style="text-align:left; margin:24px 0;">
          <h4>Детализация ответов:</h4>
          ${blitzAnswers.map((ans, i) => `
            <div style="padding:8px 12px; margin:6px 0; border-radius:6px; background:var(--card); display:flex; justify-content:space-between; align-items:center;">
              <span style="font-size:14px;"><strong>#${i + 1}</strong> (${ans.ticket}): ${ans.question}</span>
              <span class="pill ${ans.isCorrect ? 'good' : 'bad'}" style="font-size:12px; padding:2px 8px;">
                ${ans.isCorrect ? '✓ Верно' : '✗ Ошибка'}
              </span>
            </div>
          `).join('')}
        </div>

        <button type="button" class="btn btn-primary" id="blitz-restart-btn" style="font-size:15px; padding:10px 24px; min-height:44px;">
          🚀 Пройти ещё один блиц
        </button>
      </div>
    `;

    const restartBtn = document.getElementById('blitz-restart-btn');
    if (restartBtn) {
      restartBtn.addEventListener('click', () => {
        initBlitzTab();
      });
    }
  }

  function initBlitzTab() {
    const container = document.getElementById('blitz-container');
    if (!container) return;

    container.innerHTML = `
      <div class="box idea" style="margin-top:16px;">
        <div class="bt">⚡ Экспресс-тренировка перед комиссией</div>
        <p>10 случайных вопросов из всех разделов курса. На каждый вопрос даётся <strong>30 секунд</strong>. Ответьте вслух, сверьтесь с ответом и оцените результат.</p>
        <div style="display:flex; gap:10px; align-items:center; margin:16px 0; flex-wrap:wrap;">
          <label for="blitz-topic-select" style="font-weight:600; font-size:14px;">Тематика блица:</label>
          <select id="blitz-topic-select" class="search-input" style="max-width:320px; padding:6px 12px; min-height:44px;" aria-label="Тематика блица">
            <option value="all">Все 4 блока (28 лекций)</option>
            <option value="block-a">🧠 Блок A · Фундамент и CV (Л00–Л07)</option>
            <option value="block-b">🎨 Блок B · Репрезентации & GenAI (Л08–Л13)</option>
            <option value="block-c">📝 Блок C · NLP & LLM (Л14–Л21)</option>
            <option value="block-d">🤖 Блок D · Обучение с подкреплением (Л22–Л27)</option>
          </select>
          <button type="button" class="btn btn-exam" id="blitz-start-btn" style="font-size:15px; padding:10px 22px; min-height:44px;">
            🚀 Начать блиц-опрос
          </button>
        </div>
      </div>
    `;

    const startBtn = document.getElementById('blitz-start-btn');
    const topicSelect = /** @type {HTMLSelectElement | null} */ (document.getElementById('blitz-topic-select'));
    if (startBtn) {
      startBtn.addEventListener('click', () => {
        const topic = topicSelect ? topicSelect.value : 'all';
        startBlitzSession(topic);
      });
    }
  }

  // ==========================================================
  // 5. Main Simulator Initialization
  // ==========================================================
  function initSimulator() {
    const container = document.getElementById('exam-simulator-container');
    if (!container) return;

    container.innerHTML = `
      <div class="sim-container tex2jax_ignore" role="region" aria-label="Интерактивный симулятор экзамена">
        <div class="sim-header">
          <div class="sim-title">🎓 Интерактивный симулятор экзамена</div>
          <div class="sim-nav-tabs tex2jax_ignore" role="tablist" aria-label="Вкладки симулятора">
            <button type="button" class="sim-tab-btn active" role="tab" id="tab-btn-ticket" aria-selected="true" aria-controls="tab-ticket" data-tab="tab-ticket">
              🎲 Экзаменационный билет
            </button>
            <button type="button" class="sim-tab-btn" role="tab" id="tab-btn-blitz" aria-selected="false" aria-controls="tab-blitz" data-tab="tab-blitz">
              ⚡ Блиц-опрос
            </button>
            <button type="button" class="sim-tab-btn" role="tab" id="tab-btn-flashcards" aria-selected="false" aria-controls="tab-flashcards" data-tab="tab-flashcards">
              🗂️ Карточки SM-2
            </button>
          </div>
        </div>

        <!-- Tab 1: Ticket Randomizer & Direct Selection -->
        <div class="sim-panel active" role="tabpanel" id="tab-ticket" aria-labelledby="tab-btn-ticket">
          <p style="color:var(--text-dim); margin-top:0;">Вытяните случайный билет или выберите конкретный номер билета для устного ответа у доски (таймер 3 минуты, каверзные вопросы и микро-задача):</p>
          
          <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin-bottom:16px;">
            <button type="button" class="btn btn-primary" id="draw-ticket-btn" style="font-size:15px; padding:10px 20px; min-height:44px;">
              🎲 Случайный билет
            </button>
            <select id="ticket-topic-filter" class="search-input" style="max-width:280px; padding:8px 12px; min-height:44px;" aria-label="Фильтр блока билета">
              <option value="all">Все 4 блока</option>
              <option value="block-a">🧠 Блок A · Фундамент & CV</option>
              <option value="block-b">🎨 Блок B · Репрезентации & GenAI</option>
              <option value="block-c">📝 Блок C · NLP & Трансформеры</option>
              <option value="block-d">🤖 Блок D · Обучение с подкреплением</option>
            </select>
            <select id="ticket-select-dropdown" class="search-input" style="flex:1; min-width:260px; padding:8px 12px; min-height:44px;" aria-label="Прямой выбор билета"></select>
          </div>

          <div id="ticket-result-area"></div>
        </div>

        <!-- Tab 2: Blitz Mode -->
        <div class="sim-panel" role="tabpanel" id="tab-blitz" aria-labelledby="tab-btn-blitz">
          <div id="blitz-container"></div>
        </div>

        <!-- Tab 3: Leitner / SM-2 Flashcards -->
        <div class="sim-panel" role="tabpanel" id="tab-flashcards" aria-labelledby="tab-btn-flashcards">
          <p style="color:var(--text-dim); margin-top:0;">Система интервальных повторений SM-2: повторяйте вопросы по алгоритму SuperMemo, распределяя карточки по коробкам памяти 1–5.</p>
          
          <div id="flashcard-stats-bar"></div>

          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
            <div class="filter-chips" style="margin:0;">
              <span class="tag-chip active" data-fc-filter="all">Все карточки (296)</span>
              <span class="tag-chip" data-fc-filter="due">📅 К повторению</span>
            </div>
            <div class="filter-chips" style="margin:0;">
              <span class="tag-chip active" data-fc-topic="all">Все 4 блока</span>
              <span class="tag-chip" data-fc-topic="block-a">🧠 Блок A</span>
              <span class="tag-chip" data-fc-topic="block-b">🎨 Блок B</span>
              <span class="tag-chip" data-fc-topic="block-c">📝 Блок C</span>
              <span class="tag-chip" data-fc-topic="block-d">🤖 Блок D</span>
            </div>
          </div>

          <div id="flashcard-wrap"></div>
        </div>
      </div>
    `;

    // Tabs switching
    container.querySelectorAll('.sim-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        container.querySelectorAll('.sim-tab-btn').forEach(b => {
          b.classList.remove('active');
          b.setAttribute('aria-selected', 'false');
        });
        container.querySelectorAll('.sim-panel').forEach(p => p.classList.remove('active'));

        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
        const tabId = btn.getAttribute('data-tab');
        const targetPanel = document.getElementById(tabId);
        if (targetPanel) targetPanel.classList.add('active');

        if (tabId === 'tab-flashcards') {
          updateFlashcardsQueue();
        } else if (tabId === 'tab-blitz') {
          initBlitzTab();
        }
      });
    });

    setupTicketSelector();
    setupFlashcardFilters();
    initBlitzTab();
    updateFlashcardsQueue();
  }

  // Export interface
  window.ExamSimulator = {
    init: initSimulator,
    renderRandomTicket: renderRandomTicket,
    toggleTimer: toggleTimer,
    resetTimer: resetTimer,
    getLectureBlock: getLectureBlock,
    getLectureTopic: getLectureTopic,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSimulator);
  } else {
    initSimulator();
  }
})();
