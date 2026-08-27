/**
 * ExamSimulator - Interactive Exam Hub, 3-minute Timer, Flashcards, and Task Bank.
 */
(function() {
  'use strict';

  let timerInterval = null;
  let timerSecondsLeft = 180; // 3 minutes
  let timerRunning = false;

  let currentCardIndex = 0;
  let filteredCards = [];

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

  function renderRandomTicket(ticketData) {
    const container = document.getElementById('ticket-result-area');
    if (!container || !ticketData) return;

    resetTimer();

    const qasSample = (ticketData.qas || []).slice(0, 3);
    const taskSample = (ticketData.tasks || [])[0];

    let html = `
      <div class="box exambox" style="margin-top:16px;">
        <div class="bt">🎯 Вытянутый билет: ${ticketData.ticket}</div>
        <h3 style="margin: 6px 0 10px; color: var(--text);">${ticketData.title}</h3>
        <p><a href="lectures/${ticketData.filename}" class="backlink" target="_blank">📖 Открыть полный конспект лекции →</a></p>
      </div>

      <!-- 3-Minute Timer -->
      <div class="timer-box">
        <div>
          <div style="font-size:13px; font-weight:700; color:var(--text-dim); text-transform:uppercase;">Таймер устного ответа у доски</div>
          <div class="timer-display" id="timer-val">03:00</div>
        </div>
        <div class="timer-controls">
          <button type="button" class="btn btn-exam" id="timer-toggle-btn">▶ Старт 3:00</button>
          <button type="button" class="btn btn-secondary" id="timer-reset-btn">🔄 Сброс</button>
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
    document.getElementById('timer-toggle-btn').addEventListener('click', toggleTimer);
    document.getElementById('timer-reset-btn').addEventListener('click', resetTimer);

    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([container]).catch(err => console.warn(err));
    }
  }

  function initFlashcards() {
    const rawData = window.EXAM_DATA || [];
    filteredCards = [];
    rawData.forEach(lec => {
      (lec.qas || []).forEach(qa => {
        filteredCards.push({
          lectureId: lec.id,
          ticket: lec.ticket,
          question: qa.question,
          answer: qa.answer
        });
      });
    });

    currentCardIndex = 0;
    renderFlashcard();
  }

  function renderFlashcard() {
    const cardWrap = document.getElementById('flashcard-wrap');
    if (!cardWrap || filteredCards.length === 0) return;

    const card = filteredCards[currentCardIndex];
    cardWrap.innerHTML = `
      <div class="flashcard">
        <div>
          <div style="font-size:12px; font-weight:700; color:var(--accent); font-family:var(--mono); margin-bottom:8px;">
            ${card.ticket} · Карточка ${currentCardIndex + 1} из ${filteredCards.length}
          </div>
          <div class="flashcard-q">${card.question}</div>
          <div class="flashcard-a" id="flashcard-answer">${card.answer}</div>
        </div>
        <div class="flashcard-actions">
          <button type="button" class="btn btn-secondary" id="fc-show-ans-btn">👁️ Показать ответ</button>
          <div class="rating-btns" id="fc-rating-btns" style="display:none;">
            <button type="button" class="btn btn-good" id="fc-know-btn">🟢 Знаю на 100%</button>
            <button type="button" class="btn btn-warn" id="fc-unsure-btn">🟡 Сомневаюсь</button>
            <button type="button" class="btn btn-bad" id="fc-forgot-btn">🔴 Не помню</button>
          </div>
          <div style="display:flex; gap:6px;">
            <button type="button" class="btn btn-secondary" id="fc-prev-btn" ${currentCardIndex === 0 ? 'disabled' : ''}>← Назад</button>
            <button type="button" class="btn btn-primary" id="fc-next-btn">Следующий →</button>
          </div>
        </div>
      </div>
    `;

    document.getElementById('fc-show-ans-btn').addEventListener('click', () => {
      document.getElementById('flashcard-answer').classList.add('revealed');
      document.getElementById('fc-show-ans-btn').style.display = 'none';
      document.getElementById('fc-rating-btns').style.display = 'flex';
      if (window.MathJax && window.MathJax.typesetPromise) {
        window.MathJax.typesetPromise([document.getElementById('flashcard-answer')]);
      }
    });

    document.getElementById('fc-next-btn').addEventListener('click', () => {
      if (currentCardIndex < filteredCards.length - 1) {
        currentCardIndex++;
        renderFlashcard();
      }
    });

    document.getElementById('fc-prev-btn').addEventListener('click', () => {
      if (currentCardIndex > 0) {
        currentCardIndex--;
        renderFlashcard();
      }
    });

    const nextCard = () => {
      if (currentCardIndex < filteredCards.length - 1) {
        currentCardIndex++;
        renderFlashcard();
      } else {
        alert('🎉 Вы завершили прогон всех флешкарт!');
      }
    };

    const knowBtn = document.getElementById('fc-know-btn');
    if (knowBtn) knowBtn.addEventListener('click', nextCard);
    const unsureBtn = document.getElementById('fc-unsure-btn');
    if (unsureBtn) unsureBtn.addEventListener('click', nextCard);
    const forgotBtn = document.getElementById('fc-forgot-btn');
    if (forgotBtn) forgotBtn.addEventListener('click', nextCard);

    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise([cardWrap]).catch(err => console.warn(err));
    }
  }

  function initSimulator() {
    const container = document.getElementById('exam-simulator-container');
    if (!container) return;

    container.innerHTML = `
      <div class="sim-container">
        <div class="sim-header">
          <div class="sim-title">🎓 Интерактивный симулятор экзамена</div>
          <div class="sim-nav-tabs">
            <button type="button" class="sim-tab-btn active" data-tab="tab-ticket">🎲 Вытянуть билет</button>
            <button type="button" class="sim-tab-btn" data-tab="tab-flashcards">🗂️ Flashcards (280+)</button>
            <button type="button" class="sim-tab-btn" data-tab="tab-anki">📥 Экспорт в Anki</button>
          </div>
        </div>

        <!-- Tab 1: Ticket Randomizer -->
        <div class="sim-panel active" id="tab-ticket">
          <p style="color:var(--text-dim); margin-top:0;">Случайный выбор одного из 25 экзаменационных билетов ГУУ с тезисами для 3-минутного ответа, каверзными вопросами и расчетной задачей:</p>
          <button type="button" class="btn btn-primary" id="draw-ticket-btn" style="font-size:15px; padding:11px 22px;">
            🎲 Вытянуть случайный билет
          </button>
          <div id="ticket-result-area"></div>
        </div>

        <!-- Tab 2: Flashcards -->
        <div class="sim-panel" id="tab-flashcards">
          <p style="color:var(--text-dim); margin-top:0;">Режим экспресс-опроса по 280+ вопросам преподавателя с самопроверкой:</p>
          <div id="flashcard-wrap"></div>
        </div>

        <!-- Tab 3: Anki Export -->
        <div class="sim-panel" id="tab-anki">
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
            <p>В приложении Anki выберите <strong>Файл → Импорт</strong>, укажите скачанный <code>.tsv</code> файл, выберите разделитель <strong>Tab</strong> и разрешите HTML-разметку для отображения формул MathJax.</p>
          </div>
        </div>
      </div>
    `;

    // Tabs switching
    container.querySelectorAll('.sim-tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        container.querySelectorAll('.sim-tab-btn').forEach(b => b.classList.remove('active'));
        container.querySelectorAll('.sim-panel').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const tabId = btn.getAttribute('data-tab');
        const targetPanel = document.getElementById(tabId);
        if (targetPanel) targetPanel.classList.add('active');
        if (tabId === 'tab-flashcards') initFlashcards();
      });
    });

    // Draw Ticket Button
    document.getElementById('draw-ticket-btn').addEventListener('click', () => {
      const data = window.EXAM_DATA || [];
      if (data.length === 0) return;
      // Skip intro lecture 00 for exam tickets 1-25 if desired or include all
      const candidates = data.filter(d => d.id !== '00');
      const chosen = candidates[Math.floor(Math.random() * candidates.length)];
      renderRandomTicket(chosen);
    });

    initFlashcards();
  }

  document.addEventListener('DOMContentLoaded', initSimulator);
})();
