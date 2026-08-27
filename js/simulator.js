/**
 * ExamSimulator - Interactive Exam Hub, 3-minute Timer, Leitner/SM-2 Flashcards,
 * Ticket Selector, Blitz Exam Mode, and Anki Export.
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
  let currentFlashcardTopic = 'all';  // 'all' | 'cv' | 'nlp' | 'rl' | 'math'

  // Blitz mode state
  let blitzQuestions = [];
  let blitzCurrentIndex = 0;
  let blitzScore = 0;
  let blitzAnswers = [];
  let blitzTimerInterval = null;
  let blitzSecondsLeft = 30;

  // Topic classification helper
  function getLectureTopic(lecId) {
    const num = parseInt(lecId, 10);
    if ([4, 5, 8, 9, 13].includes(num)) return 'cv';
    if ([14, 15, 16, 17, 18, 19, 20, 21].includes(num)) return 'nlp';
    if ([22, 23, 24, 25, 26, 27].includes(num)) return 'rl';
    return 'math';
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

      <!-- 3-Min Cheat Skeleton -->
      ${ticketData.cheat_items && ticketData.cheat_items.length > 0 ? `
        <div class="cheat" style="margin: 20px 0;">
          <div class="bt">⚡ Скелет ответа за 3 минуты</div>
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
    const selectEl = document.getElementById('ticket-select-dropdown');
    const drawBtn = document.getElementById('draw-ticket-btn');
    const topicSelect = document.getElementById('ticket-topic-filter');
    const data = window.EXAM_DATA || [];

    if (selectEl && data.length > 0) {
      selectEl.innerHTML = '<option value="">-- Выберите билет вручную (Билеты 1–25) --</option>' +
        data.map((lec) => {
          return `<option value="${lec.id}">${lec.ticket}: ${lec.title.replace(/^Лекция\s*\d+\.\s*/, '')}</option>`;
        }).join('');

      selectEl.addEventListener('change', (e) => {
        const val = e.target.value;
        if (!val) return;
        const chosen = data.find(d => d.id === val);
        if (chosen) renderRandomTicket(chosen);
      });
    }

    if (drawBtn) {
      drawBtn.addEventListener('click', () => {
        if (data.length === 0) return;
        const topic = topicSelect ? topicSelect.value : 'all';
        let candidates = data.filter(d => d.id !== '00');
        if (topic !== 'all') {
          candidates = candidates.filter(d => getLectureTopic(d.id) === topic);
        }
        if (candidates.length === 0) candidates = data;
        const chosen = candidates[Math.floor(Math.random() * candidates.length)];
        if (selectEl) selectEl.value = chosen.id;
        renderRandomTicket(chosen);
      });
    }

    if (topicSelect) {
      topicSelect.addEventListener('change', () => {
        const topic = topicSelect.value;
        if (selectEl) {
          let filtered = data;
          if (topic !== 'all') {
            filtered = data.filter(d => getLectureTopic(d.id) === topic);
          }
          selectEl.innerHTML = '<option value="">-- Выберите билет из выбранной темы --</option>' +
            filtered.map((lec) => {
              return `<option value="${lec.id}">${lec.ticket}: ${lec.title.replace(/^Лекция\s*\d+\.\s*/, '')}</option>`;
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
      const topic = getLectureTopic(lec.id);
      (lec.qas || []).forEach((qa, idx) => {
        allCardsList.push({
          id: `l${lec.id}_qa${idx}`,
          lectureId: lec.id,
          lectureTitle: lec.title,
          ticket: lec.ticket,
          topic: topic,
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
      // 1. Topic filter
      if (currentFlashcardTopic !== 'all' && card.topic !== currentFlashcardTopic) {
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
        <div class="flashcard" style="text-align:center; padding:40px 20px;">
          <div style="font-size:36px; margin-bottom:12px;">🎉</div>
          <h3>Все карточки в этом режиме повторены!</h3>
          <p style="color:var(--text-dim); max-width:480px; margin:0 auto 20px;">
            В очереди нет карточек, требующих повторения прямо сейчас. Вы можете переключиться в режим «Все карточки» для сквозного повторения.
          </p>
          <button type="button" class="btn btn-primary" id="fc-switch-all-btn">Показать все карточки (${allCardsList.length})</button>
        </div>
      `;
      const switchBtn = document.getElementById('fc-switch-all-btn');
      if (switchBtn) {
        switchBtn.addEventListener('click', () => {
          currentFlashcardFilter = 'all';
          const filterBtnAll = document.querySelector('[data-fc-filter="all"]');
          if (filterBtnAll) filterBtnAll.click();
        });
      }
      return;
    }

    if (currentCardIndex >= activeCardsQueue.length) {
      currentCardIndex = 0;
    }

    const card = activeCardsQueue[currentCardIndex];
    const cardState = window.CourseTracker ? window.CourseTracker.sm2.getCard(card.id) : { box: 1, repetitions: 0, interval: 1 };

    const boxPillClass = cardState.box >= 4 ? 'good' : (cardState.box >= 2 ? 'warn' : 'gray');

    cardWrap.innerHTML = `
      <div class="flashcard" role="region" aria-label="Карточка вопроса">
        <div>
          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:12px;">
            <span style="font-size:12px; font-weight:700; color:var(--accent); font-family:var(--mono);">
              ${card.ticket} · Карточка ${currentCardIndex + 1} из ${activeCardsQueue.length}
            </span>
            <div style="display:flex; gap:6px;">
              <span class="pill ${boxPillClass}" style="font-size:11px; padding:2px 8px;">📦 Коробка ${cardState.box}</span>
              <span class="pill gray" style="font-size:11px; padding:2px 8px;">Повторений: ${cardState.repetitions} (интервал ${cardState.interval} дн.)</span>
            </div>
          </div>
          <div class="flashcard-q" id="flashcard-question-text">${card.question}</div>
          <div class="flashcard-a" id="flashcard-answer" aria-live="polite">${card.answer}</div>
        </div>

        <div class="flashcard-actions">
          <button type="button" class="btn btn-secondary" id="fc-show-ans-btn" aria-label="Показать ответ">👁️ Показать ответ</button>
          
          <div class="rating-btns" id="fc-rating-btns" style="display:none;" aria-label="Оценка знания карточки">
            <button type="button" class="btn btn-good" id="fc-know-btn" title="Ответ известен уверенно (интервал увеличится)">🟢 Знаю (5)</button>
            <button type="button" class="btn btn-warn" id="fc-unsure-btn" title="Вспомнил с трудом (интервал умеренный)">🟡 Сомневаюсь (3)</button>
            <button type="button" class="btn btn-bad" id="fc-forgot-btn" title="Не помню (сброс в Коробку 1)">🔴 Не помню (1)</button>
          </div>

          <div style="display:flex; gap:6px;">
            <button type="button" class="btn btn-secondary" id="fc-prev-btn" ${currentCardIndex === 0 ? 'disabled' : ''} aria-label="Предыдущая карточка">← Назад</button>
            <button type="button" class="btn btn-primary" id="fc-next-btn" aria-label="Следующая карточка">Следующий →</button>
          </div>
        </div>
      </div>
    `;

    // Show answer handler
    const showAnsBtn = document.getElementById('fc-show-ans-btn');
    if (showAnsBtn) {
      showAnsBtn.addEventListener('click', () => {
        const ansEl = document.getElementById('flashcard-answer');
        if (ansEl) ansEl.classList.add('revealed');
        showAnsBtn.style.display = 'none';
        const ratingWrap = document.getElementById('fc-rating-btns');
        if (ratingWrap) ratingWrap.style.display = 'flex';
        if (window.MathJax && window.MathJax.typesetPromise && ansEl) {
          window.MathJax.typesetPromise([ansEl]);
        }
      });
    }

    // Navigation buttons
    const nextBtn = document.getElementById('fc-next-btn');
    if (nextBtn) {
      nextBtn.addEventListener('click', () => {
        if (currentCardIndex < activeCardsQueue.length - 1) {
          currentCardIndex++;
          renderFlashcard();
        } else {
          currentCardIndex = 0;
          renderFlashcard();
        }
      });
    }

    const prevBtn = document.getElementById('fc-prev-btn');
    if (prevBtn) {
      prevBtn.addEventListener('click', () => {
        if (currentCardIndex > 0) {
          currentCardIndex--;
          renderFlashcard();
        }
      });
    }

    // Rating (SM-2) action handler
    const handleRating = (grade) => {
      if (window.CourseTracker) {
        window.CourseTracker.sm2.recordReview(card.id, grade);
      }
      renderFlashcardStats();

      // If in due mode and card is no longer due, advance or re-filter
      if (currentFlashcardFilter === 'due') {
        activeCardsQueue.splice(currentCardIndex, 1);
        if (currentCardIndex >= activeCardsQueue.length) {
          currentCardIndex = 0;
        }
        renderFlashcard();
      } else {
        if (currentCardIndex < activeCardsQueue.length - 1) {
          currentCardIndex++;
        } else {
          currentCardIndex = 0;
        }
        renderFlashcard();
      }
    };

    const knowBtn = document.getElementById('fc-know-btn');
    if (knowBtn) knowBtn.addEventListener('click', () => handleRating(5));

    const unsureBtn = document.getElementById('fc-unsure-btn');
    if (unsureBtn) unsureBtn.addEventListener('click', () => handleRating(3));

    const forgotBtn = document.getElementById('fc-forgot-btn');
    if (forgotBtn) forgotBtn.addEventListener('click', () => handleRating(1));

    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([cardWrap]).catch(err => console.warn(err));
    }
  }

  function setupFlashcardFilters() {
    document.querySelectorAll('[data-fc-filter]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-fc-filter]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFlashcardFilter = btn.getAttribute('data-fc-filter') || 'all';
        updateFlashcardsQueue();
      });
    });

    document.querySelectorAll('[data-fc-topic]').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-fc-topic]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFlashcardTopic = btn.getAttribute('data-fc-topic') || 'all';
        updateFlashcardsQueue();
      });
    });
  }

  // ==========================================================
  // 4. Blitz Exam Mode (Tab 3)
  // ==========================================================
  function startBlitzSession(topic = 'all') {
    buildAllCardsList();
    let pool = allCardsList;
    if (topic !== 'all') {
      pool = allCardsList.filter(c => c.topic === topic);
    }
    if (pool.length === 0) pool = allCardsList;

    // Shuffle and pick 10 questions
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

    const q = blitzQuestions[blitzCurrentIndex];
    clearInterval(blitzTimerInterval);
    blitzSecondsLeft = 30;

    container.innerHTML = `
      <div class="box exambox" style="margin-top:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <span class="pill" style="font-weight:700;">Вопрос ${blitzCurrentIndex + 1} из ${blitzQuestions.length}</span>
          <span id="blitz-timer" class="timer-display" style="font-size:24px;">00:30</span>
        </div>

        <div style="font-size:12px; color:var(--text-dim); margin-bottom:6px;">${q.ticket}</div>
        <h3 style="margin:4px 0 16px; color:var(--text); line-height:1.4;">${q.question}</h3>

        <div id="blitz-answer-area" class="flashcard-a" style="display:none; margin:16px 0;">
          ${q.answer}
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; margin-top:20px; flex-wrap:wrap; gap:10px;">
          <button type="button" class="btn btn-secondary" id="blitz-show-btn">👁️ Показать ответ</button>
          <div id="blitz-action-btns" style="display:none; gap:8px;">
            <button type="button" class="btn btn-good" id="blitz-correct-btn">🟢 Знаю (+1 балл)</button>
            <button type="button" class="btn btn-bad" id="blitz-wrong-btn">🔴 Не знаю (0 баллов)</button>
          </div>
        </div>
      </div>
    `;

    const timerEl = document.getElementById('blitz-timer');
    blitzTimerInterval = setInterval(() => {
      blitzSecondsLeft--;
      if (timerEl) {
        timerEl.textContent = `00:${String(blitzSecondsLeft).padStart(2, '0')}`;
        if (blitzSecondsLeft <= 10) timerEl.classList.add('warn');
        if (blitzSecondsLeft === 0) {
          timerEl.classList.add('danger');
          playBeep(440, 0.2);
        }
      }
      if (blitzSecondsLeft <= 0) {
        clearInterval(blitzTimerInterval);
      }
    }, 1000);

    const showBtn = document.getElementById('blitz-show-btn');
    const ansArea = document.getElementById('blitz-answer-area');
    const actBtns = document.getElementById('blitz-action-btns');

    if (showBtn) {
      showBtn.addEventListener('click', () => {
        if (ansArea) ansArea.style.display = 'block';
        showBtn.style.display = 'none';
        if (actBtns) actBtns.style.display = 'flex';
        if (window.MathJax && window.MathJax.typesetPromise && ansArea) {
          window.MathJax.typesetPromise([ansArea]);
        }
      });
    }

    const answerQuestion = (isCorrect) => {
      clearInterval(blitzTimerInterval);
      if (isCorrect) blitzScore++;
      blitzAnswers.push({
        question: q.question,
        ticket: q.ticket,
        isCorrect: isCorrect
      });

      // Record SM-2 review
      if (window.CourseTracker) {
        window.CourseTracker.sm2.recordReview(q.id, isCorrect ? 5 : 1);
      }

      blitzCurrentIndex++;
      renderBlitzActiveQuestion();
    };

    const correctBtn = document.getElementById('blitz-correct-btn');
    if (correctBtn) correctBtn.addEventListener('click', () => answerQuestion(true));

    const wrongBtn = document.getElementById('blitz-wrong-btn');
    if (wrongBtn) wrongBtn.addEventListener('click', () => answerQuestion(false));

    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([container]).catch(err => console.warn(err));
    }
  }

  function renderBlitzResults() {
    clearInterval(blitzTimerInterval);
    const container = document.getElementById('blitz-container');
    if (!container) return;

    const percent = Math.round((blitzScore / blitzQuestions.length) * 100);
    let gradeLabel = 'Отлично! Отличная готовность к экзамену 🎓';
    let gradeClass = 'good';
    if (percent < 60) {
      gradeLabel = 'Нужно повторить материал. Рекомендуем проработать конспекты 📚';
      gradeClass = 'warn';
    } else if (percent < 80) {
      gradeLabel = 'Хорошо! Подтяните сложные темы перед комиссией 👍';
      gradeClass = 'good';
    }

    container.innerHTML = `
      <div class="box exambox" style="margin-top:16px; text-align:center; padding:32px 20px;">
        <div style="font-size:40px; margin-bottom:10px;">🏆</div>
        <h2>Результаты Блиц-опроса</h2>
        <div style="font-size:48px; font-weight:800; color:var(--accent); font-family:var(--mono); margin:10px 0;">
          ${blitzScore} / ${blitzQuestions.length} (${percent}%)
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

        <button type="button" class="btn btn-primary" id="blitz-restart-btn" style="font-size:15px; padding:10px 24px;">
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
          <select id="blitz-topic-select" class="search-input" style="max-width:260px; padding:6px 12px;">
            <option value="all">Все темы (28 лекций)</option>
            <option value="cv">👁️ Компьютерное зрение</option>
            <option value="nlp">📝 Языковые модели & Трансформеры</option>
            <option value="rl">🤖 Обучение с подкреплением</option>
            <option value="math">📐 Математика & Оптимизация</option>
          </select>
          <button type="button" class="btn btn-exam" id="blitz-start-btn" style="font-size:15px; padding:10px 22px;">
            🚀 Начать блиц-опрос (10 вопросов)
          </button>
        </div>
      </div>
    `;

    const startBtn = document.getElementById('blitz-start-btn');
    const topicSelect = document.getElementById('blitz-topic-select');
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
      <div class="sim-container" role="region" aria-label="Интерактивный симулятор экзамена">
        <div class="sim-header">
          <div class="sim-title">🎓 Интерактивный симулятор экзамена</div>
          <div class="sim-nav-tabs" role="tablist" aria-label="Вкладки симулятора">
            <button type="button" class="sim-tab-btn active" role="tab" id="tab-btn-ticket" aria-selected="true" aria-controls="tab-ticket" data-tab="tab-ticket">
              🎲 Экзаменационный билет
            </button>
            <button type="button" class="sim-tab-btn" role="tab" id="tab-btn-blitz" aria-selected="false" aria-controls="tab-blitz" data-tab="tab-blitz">
              ⚡ Блиц-опрос (10 вопросов)
            </button>
            <button type="button" class="sim-tab-btn" role="tab" id="tab-btn-flashcards" aria-selected="false" aria-controls="tab-flashcards" data-tab="tab-flashcards">
              🗂️ Карточки (интервальное повторение)
            </button>
            <button type="button" class="sim-tab-btn" role="tab" id="tab-btn-anki" aria-selected="false" aria-controls="tab-anki" data-tab="tab-anki">
              📥 Экспорт в Anki
            </button>
          </div>
        </div>

        <!-- Tab 1: Ticket Randomizer & Direct Selection -->
        <div class="sim-panel active" role="tabpanel" id="tab-ticket" aria-labelledby="tab-btn-ticket">
          <p style="color:var(--text-dim); margin-top:0;">Вытяните случайный билет или выберите конкретный номер билета для устного ответа у доски (таймер 3 минуты, каверзные вопросы и микро-задача):</p>
          
          <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin-bottom:16px;">
            <button type="button" class="btn btn-primary" id="draw-ticket-btn" style="font-size:15px; padding:10px 20px;">
              🎲 Случайный билет
            </button>
            <select id="ticket-topic-filter" class="search-input" style="max-width:220px; padding:8px 12px;" aria-label="Фильтр темы билета">
              <option value="all">Все темы</option>
              <option value="cv">👁️ Компьютерное зрение</option>
              <option value="nlp">📝 Языковые модели</option>
              <option value="rl">🤖 Обучение с подкреплением</option>
              <option value="math">📐 Математика & Оптимизация</option>
            </select>
            <select id="ticket-select-dropdown" class="search-input" style="flex:1; min-width:240px; padding:8px 12px;" aria-label="Прямой выбор билета"></select>
          </div>

          <div id="ticket-result-area"></div>
        </div>

        <!-- Tab 2: Blitz Mode -->
        <div class="sim-panel" role="tabpanel" id="tab-blitz" aria-labelledby="tab-btn-blitz">
          <div id="blitz-container"></div>
        </div>

        <!-- Tab 3: Leitner / SM-2 Flashcards -->
        <div class="sim-panel" role="tabpanel" id="tab-flashcards" aria-labelledby="tab-btn-flashcards">
          <p style="color:var(--text-dim); margin-top:0;">Система интервальных повторений: повторяйте вопросы по алгоритму Лейтнера, распределяя карточки по коробкам памяти 1–5.</p>
          
          <div id="flashcard-stats-bar"></div>

          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom:12px;">
            <div class="filter-chips" style="margin:0;">
              <span class="tag-chip active" data-fc-filter="all">Все карточки (296)</span>
              <span class="tag-chip" data-fc-filter="due">📅 К повторению</span>
            </div>
            <div class="filter-chips" style="margin:0;">
              <span class="tag-chip active" data-fc-topic="all">Все темы</span>
              <span class="tag-chip" data-fc-topic="cv">👁️ Компьютерное зрение</span>
              <span class="tag-chip" data-fc-topic="nlp">📝 Языковые модели</span>
              <span class="tag-chip" data-fc-topic="rl">🤖 Обучение с подкреплением</span>
              <span class="tag-chip" data-fc-topic="math">📐 Математика</span>
            </div>
          </div>

          <div id="flashcard-wrap"></div>
        </div>

        <!-- Tab 4: Anki Export -->
        <div class="sim-panel" role="tabpanel" id="tab-anki" aria-labelledby="tab-btn-anki">
          <p style="color:var(--text-dim); margin-top:0;">Скачайте готовые колоды для импорта в приложение Anki (Desktop / iOS / Android):</p>
          <div style="display:flex; flex-direction:column; gap:12px; margin:18px 0;">
            <a class="btn btn-secondary" href="anki_decks/ai_course_exam_qas.tsv" download>
              📥 Скачать колоду: «Препод спросит» (296 вопросов с ответами) .tsv
            </a>
            <a class="btn btn-secondary" href="anki_decks/ai_course_microtasks.tsv" download>
              📥 Скачать колоду: «Микро-задачи у доски» (170 задач с решениями) .tsv
            </a>
            <a class="btn btn-secondary" href="anki_decks/ai_course_3min_cheatsheets.tsv" download>
              📥 Скачать колоду: «Шпаргалки: Ответ за 3 минуты» (28 билетов) .tsv
            </a>
          </div>
          <div class="box idea" style="margin-top:14px;">
            <div class="bt">💡 Инструкция по импорту в Anki</div>
            <p>В приложении Anki выберите <strong>Файл → Импорт</strong>, укажите скачанный <code>.tsv</code> файл, выберите разделитель <strong>Tab</strong> и разрешите HTML-разметку для корректного рендеринга формул MathJax.</p>
          </div>
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

  document.addEventListener('DOMContentLoaded', initSimulator);
})();
