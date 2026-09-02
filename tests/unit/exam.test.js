/**
 * Unit Test Suite for js/exam.js
 * Comprehensive 100% Lines, Branches, Functions Coverage via Node.js Native Runner.
 */

const { describe, it, beforeEach, afterEach } = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const { setupMockBrowser, MockElement } = require('../harness/mock_browser');

const EXAM_PATH = path.resolve(__dirname, '../../js/exam.js');
const TRACKER_PATH = path.resolve(__dirname, '../../js/tracker.js');
const EXAM_DATA_PATH = path.resolve(__dirname, '../../js/exam_data.js');

function loadExamData() {
  delete require.cache[require.resolve(EXAM_DATA_PATH)];
  require(EXAM_DATA_PATH);
}

function loadTracker() {
  delete require.cache[require.resolve(TRACKER_PATH)];
  require(TRACKER_PATH);
  return global.window.CourseTracker;
}

function loadExam(options = {}) {
  delete require.cache[require.resolve(EXAM_PATH)];
  require(EXAM_PATH);
  return global.window.ExamSimulator;
}

describe('Exam Simulator Suite', () => {
  let intervalCallbacks = [];
  const origSetInterval = global.setInterval;

  beforeEach(() => {
    setupMockBrowser({ pathname: '/exam.html' });
    loadTracker();
    loadExamData();
    intervalCallbacks = [];
    global.setInterval = (fn, ms) => {
      intervalCallbacks.push(fn);
      return origSetInterval(fn, ms);
    };
  });

  afterEach(() => {
    global.setInterval = origSetInterval;
    if (global.window.ExamSimulator) {
      global.window.ExamSimulator.resetTimer();
    }
  });

  describe('Classification and Helper Functions', () => {
    it('should classify lecture blocks and topics accurately', () => {
      const sim = loadExam();
      // Blocks
      assert.strictEqual(sim.getLectureBlock('00'), 'block-a');
      assert.strictEqual(sim.getLectureBlock('07'), 'block-a');
      assert.strictEqual(sim.getLectureBlock('08'), 'block-b');
      assert.strictEqual(sim.getLectureBlock('13'), 'block-b');
      assert.strictEqual(sim.getLectureBlock('14'), 'block-c');
      assert.strictEqual(sim.getLectureBlock('21'), 'block-c');
      assert.strictEqual(sim.getLectureBlock('22'), 'block-d');
      assert.strictEqual(sim.getLectureBlock('27'), 'block-d');
      assert.strictEqual(sim.getLectureBlock('invalid'), 'block-a');

      // Topics
      assert.strictEqual(sim.getLectureTopic('00'), 'cv');
      assert.strictEqual(sim.getLectureTopic('10'), 'cv');
      assert.strictEqual(sim.getLectureTopic('16'), 'nlp');
      assert.strictEqual(sim.getLectureTopic('25'), 'rl');
      assert.strictEqual(sim.getLectureTopic('invalid'), 'cv');
    });

    it('should test readyState loading branch on script load', () => {
      setupMockBrowser({ pathname: '/exam.html' });
      global.document.readyState = 'loading';
      loadTracker();
      loadExamData();
      const sim = loadExam();
      assert.ok(sim);
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));
    });
  });

  describe('Oral Exam Timer 3:00', () => {
    it('should start, pause, resume, reset, and tick down timer to 0 (warn and danger states)', () => {
      const sim = loadExam();

      const container = global.document.createElement('div');
      container.id = 'exam-simulator-container';
      global.document.body.appendChild(container);

      sim.init();

      // Render a ticket so the timer area is created
      sim.renderRandomTicket(global.window.EXAM_DATA[1]);

      const timerVal = global.document.getElementById('timer-val');
      const toggleBtn = global.document.getElementById('timer-toggle-btn');
      const resetBtn = global.document.getElementById('timer-reset-btn');
      assert.ok(toggleBtn);
      assert.ok(resetBtn);

      // Start timer
      toggleBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(toggleBtn.textContent, '⏸ Пауза');

      // Pause timer
      toggleBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(toggleBtn.textContent, '▶ Продолжить');

      // Resume timer
      toggleBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(toggleBtn.textContent, '⏸ Пауза');

      // Execute timer interval ticks
      assert.ok(intervalCallbacks.length > 0);
      const timerTick = intervalCallbacks[intervalCallbacks.length - 1];

      // Tick down 150 times -> timerSecondsLeft = 30 (warn state)
      for (let i = 0; i < 150; i++) {
        timerTick();
      }
      assert.ok(timerVal.classList.contains('warn'));

      // Tick down remaining 30 times -> timerSecondsLeft = 0 (danger state + gong)
      for (let i = 0; i < 30; i++) {
        timerTick();
      }
      assert.ok(timerVal.classList.contains('danger'));
      assert.strictEqual(toggleBtn.textContent, '🔄 Сначала');

      // Start again when secondsLeft === 0 resets to 180 and starts
      toggleBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(toggleBtn.textContent, '⏸ Пауза');

      // Reset timer
      resetBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(timerVal.textContent, '03:00');
      assert.strictEqual(toggleBtn.textContent, '▶ Старт 3:00');

      sim.resetTimer();
    });
  });

  describe('Exam Ticket Selector and Renderer', () => {
    it('should select tickets manually, draw random ticket, and handle edge cases', () => {
      const sim = loadExam();

      const container = global.document.createElement('div');
      container.id = 'exam-simulator-container';
      global.document.body.appendChild(container);

      sim.init();

      const selectDropdown = global.document.getElementById('ticket-select-dropdown');
      const drawBtn = global.document.getElementById('draw-ticket-btn');
      const blockFilter = global.document.getElementById('ticket-topic-filter');
      const resultArea = global.document.getElementById('ticket-result-area');

      // 1. Draw random ticket with cv topic filter
      blockFilter.value = 'cv';
      drawBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.ok(resultArea.innerHTML.includes('🎯 Выбранный билет:'));

      // 2. Draw with nlp, rl, math filters
      blockFilter.value = 'nlp';
      drawBtn.dispatchEvent(new global.window.CustomEvent('click'));
      blockFilter.value = 'rl';
      drawBtn.dispatchEvent(new global.window.CustomEvent('click'));
      blockFilter.value = 'math';
      drawBtn.dispatchEvent(new global.window.CustomEvent('click'));

      // 3. Select via dropdown
      selectDropdown.value = '01';
      const changeEvt = new global.window.CustomEvent('change');
      changeEvt.target = selectDropdown;
      selectDropdown.dispatchEvent(changeEvt);
      assert.ok(resultArea.innerHTML.includes('Билет 1'));

      // Select empty
      selectDropdown.value = '';
      selectDropdown.dispatchEvent(changeEvt);

      // 4. Change block filter
      blockFilter.value = 'block-b';
      blockFilter.dispatchEvent(new global.window.CustomEvent('change'));
      assert.ok(selectDropdown.innerHTML.includes('Блок B'));

      // 5. Render ticket with empty / minimal data
      sim.renderRandomTicket({
        id: '99',
        filename: '99-test.html',
        title: 'Тестовая лекция',
        ticket: 'Билет 99',
        module: 'D',
        qas: [],
        tasks: [],
        cheat_items: []
      });
      assert.ok(resultArea.innerHTML.includes('Билет 99'));

      // Null container or null ticket
      sim.renderRandomTicket(null);
    });
  });

  describe('Spaced Repetition SM-2 Flashcards', () => {
    it('should filter flashcards, reveal answers, and record ratings', () => {
      const sim = loadExam();

      const container = global.document.createElement('div');
      container.id = 'exam-simulator-container';
      global.document.body.appendChild(container);

      sim.init();

      // Switch to flashcards tab
      const fcTabBtn = global.document.getElementById('tab-btn-flashcards');
      fcTabBtn.dispatchEvent(new global.window.CustomEvent('click'));

      const cardWrap = global.document.getElementById('flashcard-wrap');
      assert.ok(cardWrap);

      // Reveal answer
      const revealBtn = cardWrap.querySelector('#fc-reveal-btn');
      assert.ok(revealBtn);
      revealBtn.dispatchEvent(new global.window.CustomEvent('click'));

      // Rate card (grade 5)
      const rate5Btn = cardWrap.querySelector('.sm2-rate-btn[data-grade="5"]');
      assert.ok(rate5Btn);
      const clickRateEvt = new global.window.CustomEvent('click');
      clickRateEvt.currentTarget = rate5Btn;
      rate5Btn.dispatchEvent(clickRateEvt);

      // Verify next card is displayed and rating buttons work
      const nextReveal = cardWrap.querySelector('#fc-reveal-btn');
      assert.ok(nextReveal);

      // Rate card repeatedly to test wrap-around
      for (let g = 1; g <= 5; g++) {
        const rev = cardWrap.querySelector('#fc-reveal-btn');
        if (rev) rev.dispatchEvent(new global.window.CustomEvent('click'));
        const btn = cardWrap.querySelector(`.sm2-rate-btn[data-grade="${g}"]`);
        if (btn) {
          const evt = new global.window.CustomEvent('click');
          evt.currentTarget = btn;
          btn.dispatchEvent(evt);
        }
      }
    });

    it('should filter flashcards by block and due status and handle empty queue', () => {
      const sim = loadExam();

      const container = global.document.createElement('div');
      container.id = 'exam-simulator-container';
      global.document.body.appendChild(container);

      sim.init();

      // Click tab
      global.document.getElementById('tab-btn-flashcards').dispatchEvent(new global.window.CustomEvent('click'));

      const cardWrap = global.document.getElementById('flashcard-wrap');
      assert.ok(cardWrap);

      // Filter by due
      const dueChip = global.document.querySelector('[data-fc-filter="due"]');
      assert.ok(dueChip);
      dueChip.dispatchEvent(new global.window.CustomEvent('click'));

      // Filter by block A
      const blockAChip = global.document.querySelector('[data-fc-topic="block-a"]');
      assert.ok(blockAChip);
      blockAChip.dispatchEvent(new global.window.CustomEvent('click'));

      // Advance index in All, then switch to small block queue
      const allTopicChip = global.document.querySelector('[data-fc-topic="all"]');
      if (allTopicChip) allTopicChip.dispatchEvent(new global.window.CustomEvent('click'));
      for (let i = 0; i < 25; i++) {
        const rev = cardWrap.querySelector('#fc-reveal-btn');
        if (rev) rev.dispatchEvent(new global.window.CustomEvent('click'));
        const btn = cardWrap.querySelector('.sm2-rate-btn[data-grade="4"]');
        if (btn) {
          const evt = new global.window.CustomEvent('click');
          evt.currentTarget = btn;
          btn.dispatchEvent(evt);
        }
      }
      // Now filter to block D (which has fewer cards) to trigger index wrap
      const blockDChip2 = global.document.querySelector('[data-fc-topic="block-d"]');
      if (blockDChip2) blockDChip2.dispatchEvent(new global.window.CustomEvent('click'));

      // Filter by block B
      const blockBChip = global.document.querySelector('[data-fc-topic="block-b"]');
      if (blockBChip) blockBChip.dispatchEvent(new global.window.CustomEvent('click'));

      // Filter by block C
      const blockCChip = global.document.querySelector('[data-fc-topic="block-c"]');
      if (blockCChip) blockCChip.dispatchEvent(new global.window.CustomEvent('click'));

      // Filter by block D
      const blockDChip = global.document.querySelector('[data-fc-topic="block-d"]');
      if (blockDChip) blockDChip.dispatchEvent(new global.window.CustomEvent('click'));

      // Empty queue simulation (when all reviewed)
      const allCards = {};
      global.window.EXAM_DATA.forEach(lec => {
        (lec.qas || []).forEach((qa, i) => {
          allCards[`l${lec.id}_qa${i}`] = {
            cardId: `l${lec.id}_qa${i}`,
            box: 3,
            repetitions: 2,
            interval: 10,
            easeFactor: 2.5,
            lastReviewed: Date.now(),
            nextReview: Date.now() + 10 * 24 * 3600 * 1000 // future
          };
        });
      });
      global.localStorage.setItem('ai_course_sm2_cards', JSON.stringify(allCards));

      dueChip.dispatchEvent(new global.window.CustomEvent('click'));
      assert.ok(cardWrap.innerHTML.includes('Все карточки повторены'));

      // Click show all button
      const showAllBtn = cardWrap.querySelector('#fc-show-all-btn');
      assert.ok(showAllBtn);
      showAllBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.ok(cardWrap.querySelector('#fc-reveal-btn'));
    });
  });

  describe('Blitz Exam Mode', () => {
    it('should start blitz, tick timer, show answers, record answers, and render results (grades 5, 4, 3)', () => {
      const sim = loadExam();

      const container = global.document.createElement('div');
      container.id = 'exam-simulator-container';
      global.document.body.appendChild(container);

      sim.init();

      // Switch to Blitz tab
      const blitzTabBtn = global.document.getElementById('tab-btn-blitz');
      blitzTabBtn.dispatchEvent(new global.window.CustomEvent('click'));

      const startBtn = global.document.getElementById('blitz-start-btn');
      assert.ok(startBtn);

      // Start blitz session with block A topic filter
      const topicSelect = global.document.getElementById('blitz-topic-select');
      if (topicSelect) topicSelect.value = 'block-a';
      startBtn.dispatchEvent(new global.window.CustomEvent('click'));

      const blitzContainer = global.document.getElementById('blitz-container');
      assert.ok(blitzContainer.innerHTML.includes('Вопрос 1 из 10'));

      // Test blitz timer countdown tick (<=5s turns red, 0s beeps)
      assert.ok(intervalCallbacks.length > 0);
      const blitzTick = intervalCallbacks[intervalCallbacks.length - 1];
      for (let s = 0; s < 26; s++) {
        blitzTick();
      }
      const timerEl = document.getElementById('blitz-timer');
      assert.strictEqual(timerEl.style.color, '#ff5555');
      for (let s = 0; s < 5; s++) {
        blitzTick();
      }

      // Answer 10 questions with 8 correct (grade 5)
      for (let i = 0; i < 10; i++) {
        const showBtn = blitzContainer.querySelector('#blitz-show-btn');
        if (showBtn) showBtn.dispatchEvent(new global.window.CustomEvent('click'));

        if (i < 8) {
          const correctBtn = blitzContainer.querySelector('#blitz-correct-btn');
          if (correctBtn) correctBtn.dispatchEvent(new global.window.CustomEvent('click'));
        } else {
          const wrongBtn = blitzContainer.querySelector('#blitz-wrong-btn');
          if (wrongBtn) wrongBtn.dispatchEvent(new global.window.CustomEvent('click'));
        }
      }

      // Verify results screen
      assert.ok(blitzContainer.innerHTML.includes('Результаты блиц-опроса'));
      assert.ok(blitzContainer.innerHTML.includes('8 / 10'));
      assert.ok(blitzContainer.innerHTML.includes('Отлично'));

      // Test restart blitz
      const restartBtn = blitzContainer.querySelector('#blitz-restart-btn');
      assert.ok(restartBtn);
      restartBtn.dispatchEvent(new global.window.CustomEvent('click'));

      // Second blitz: score 4 (grade bad)
      const startBtn2 = global.document.getElementById('blitz-start-btn');
      startBtn2.dispatchEvent(new global.window.CustomEvent('click'));
      for (let i = 0; i < 10; i++) {
        const showBtn = blitzContainer.querySelector('#blitz-show-btn');
        if (showBtn) showBtn.dispatchEvent(new global.window.CustomEvent('click'));
        if (i < 4) {
          const correctBtn = blitzContainer.querySelector('#blitz-correct-btn');
          if (correctBtn) correctBtn.dispatchEvent(new global.window.CustomEvent('click'));
        } else {
          const wrongBtn = blitzContainer.querySelector('#blitz-wrong-btn');
          if (wrongBtn) wrongBtn.dispatchEvent(new global.window.CustomEvent('click'));
        }
      }
      assert.ok(blitzContainer.innerHTML.includes('4 / 10'));
      assert.ok(blitzContainer.innerHTML.includes('Требуется повторение'));

      // Third blitz: score 7 (grade warn 4)
      const restartBtn2 = blitzContainer.querySelector('#blitz-restart-btn');
      restartBtn2.dispatchEvent(new global.window.CustomEvent('click'));
      const startBtn3 = global.document.getElementById('blitz-start-btn');
      startBtn3.dispatchEvent(new global.window.CustomEvent('click'));
      for (let i = 0; i < 10; i++) {
        const showBtn = blitzContainer.querySelector('#blitz-show-btn');
        if (showBtn) showBtn.dispatchEvent(new global.window.CustomEvent('click'));
        if (i < 7) {
          const correctBtn = blitzContainer.querySelector('#blitz-correct-btn');
          if (correctBtn) correctBtn.dispatchEvent(new global.window.CustomEvent('click'));
        } else {
          const wrongBtn = blitzContainer.querySelector('#blitz-wrong-btn');
          if (wrongBtn) wrongBtn.dispatchEvent(new global.window.CustomEvent('click'));
        }
      }
      assert.ok(blitzContainer.innerHTML.includes('7 / 10'));
      assert.ok(blitzContainer.innerHTML.includes('Хороший уровень'));
    });
  });
});
