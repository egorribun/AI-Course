/**
 * Unit Test Suite for js/tracker.js
 * Comprehensive 100% Lines, Branches, Functions Coverage via Node.js Native Runner.
 */

const { describe, it, beforeEach } = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const { setupMockBrowser, MockElement } = require('../harness/mock_browser');

const TRACKER_PATH = path.resolve(__dirname, '../../js/tracker.js');

function loadTracker(options = {}) {
  delete require.cache[require.resolve(TRACKER_PATH)];
  require(TRACKER_PATH);
  return global.window.CourseTracker;
}

describe('CourseTracker Suite', () => {
  beforeEach(() => {
    setupMockBrowser();
  });

  describe('Theme Management', () => {
    it('should get default dark theme and set/toggle themes', () => {
      const tracker = loadTracker();
      assert.strictEqual(tracker.getTheme(), 'dark');

      tracker.setTheme('light');
      assert.strictEqual(tracker.getTheme(), 'light');
      assert.strictEqual(global.document.documentElement.getAttribute('data-theme'), 'light');

      const toggled = tracker.toggleTheme();
      assert.strictEqual(toggled, 'dark');
      assert.strictEqual(tracker.getTheme(), 'dark');

      tracker.setTheme('custom-unknown');
      assert.strictEqual(tracker.getTheme(), 'dark');
    });

    it('should handle localStorage getTheme / setTheme exceptions gracefully', () => {
      const tracker = loadTracker();
      const origGetItem = global.localStorage.getItem;
      global.localStorage.getItem = () => { throw new Error('Storage disabled'); };
      assert.strictEqual(tracker.getTheme(), 'dark');

      const origSetItem = global.localStorage.setItem;
      global.localStorage.setItem = () => { throw new Error('Quota exceeded'); };
      tracker.setTheme('light');
      assert.strictEqual(global.document.documentElement.getAttribute('data-theme'), 'light');

      global.localStorage.getItem = origGetItem;
      global.localStorage.setItem = origSetItem;
    });

    it('should update theme toggle buttons with various DOM variations', () => {
      const tracker = loadTracker();

      // Case 1: Standard button with .theme-icon and .theme-text
      const btn1 = new MockElement('button');
      btn1.className = 'theme-toggle';
      const icon1 = new MockElement('span');
      icon1.className = 'theme-icon';
      const text1 = new MockElement('span');
      text1.className = 'theme-text';
      btn1.appendChild(icon1);
      btn1.appendChild(text1);
      global.document.body.appendChild(btn1);

      // Case 2: Bottom nav item with .theme-icon and .theme-label
      const btn2 = new MockElement('button');
      btn2.className = 'theme-toggle bottom-nav-item';
      const icon2 = new MockElement('span');
      icon2.className = 'theme-icon';
      const label2 = new MockElement('span');
      label2.className = 'theme-label';
      btn2.appendChild(icon2);
      btn2.appendChild(label2);
      global.document.body.appendChild(btn2);

      // Case 3: Empty standard button
      const btn3 = new MockElement('button');
      btn3.className = 'theme-toggle';
      global.document.body.appendChild(btn3);

      // Case 4: Empty bottom-nav button
      const btn4 = new MockElement('button');
      btn4.className = 'theme-toggle bottom-nav-item';
      global.document.body.appendChild(btn4);

      tracker.setTheme('light');
      tracker.updateThemeButtons();
      assert.strictEqual(icon1.textContent, '🌙');
      assert.strictEqual(text1.textContent, 'Тёмная тема');
      assert.strictEqual(icon2.textContent, '🌙');
      assert.strictEqual(label2.textContent, 'Тема');
      assert.ok(btn3.innerHTML.includes('Тёмная тема'));
      assert.ok(btn4.innerHTML.includes('bottom-nav-label'));

      tracker.setTheme('dark');
      tracker.updateThemeButtons();
      assert.strictEqual(icon1.textContent, '☀️');
      assert.strictEqual(text1.textContent, 'Светлая тема');
    });
  });

  describe('Lectures Progress Tracking', () => {
    it('should track completed lectures and toggle correctly', () => {
      const tracker = loadTracker();
      assert.deepStrictEqual(tracker.getCompletedLectures(), []);
      assert.strictEqual(tracker.isLectureCompleted('00'), false);

      assert.strictEqual(tracker.setLectureCompleted('00', true), true);
      assert.strictEqual(tracker.isLectureCompleted('00'), true);
      assert.deepStrictEqual(tracker.getCompletedLectures(), ['00']);

      // Duplicate add
      tracker.setLectureCompleted('00', true);
      assert.deepStrictEqual(tracker.getCompletedLectures(), ['00']);

      // Toggle
      assert.strictEqual(tracker.toggleLecture('00'), false);
      assert.strictEqual(tracker.isLectureCompleted('00'), false);

      assert.strictEqual(tracker.toggleLecture('01'), true);
      assert.strictEqual(tracker.isLectureCompleted('01'), true);

      // Remove lecture
      tracker.setLectureCompleted('01', false);
      assert.strictEqual(tracker.isLectureCompleted('01'), false);
    });

    it('should handle corrupted localStorage array data and safeSetJSON errors', () => {
      const tracker = loadTracker();
      global.localStorage.setItem('ai_course_completed_lectures', JSON.stringify('corrupted-string'));
      assert.deepStrictEqual(tracker.getCompletedLectures(), []);

      global.localStorage.setItem('ai_course_completed_lectures', JSON.stringify({ not: 'array' }));
      assert.deepStrictEqual(tracker.getCompletedLectures(), []);

      // Test safeSetJSON catch branch
      const origSetItem = global.localStorage.setItem;
      global.localStorage.setItem = () => { throw new Error('Storage write failed'); };
      tracker.setLectureCompleted('05', true);
      global.localStorage.setItem = origSetItem;

      tracker.setLectureCompleted('05', true);
      assert.strictEqual(tracker.isLectureCompleted('05'), true);
    });
  });

  describe('QA Items Tracking', () => {
    it('should track checked QA questions', () => {
      const tracker = loadTracker();
      assert.deepStrictEqual(tracker.getCheckedQAs(), []);
      assert.strictEqual(tracker.isQAChecked('l00_qa1'), false);

      tracker.setQAChecked('l00_qa1', true);
      assert.strictEqual(tracker.isQAChecked('l00_qa1'), true);

      // Duplicate add
      tracker.setQAChecked('l00_qa1', true);
      assert.deepStrictEqual(tracker.getCheckedQAs(), ['l00_qa1']);

      // Toggle
      assert.strictEqual(tracker.toggleQA('l00_qa1'), false);
      assert.strictEqual(tracker.isQAChecked('l00_qa1'), false);

      assert.strictEqual(tracker.toggleQA('l02_qa3'), true);
      assert.strictEqual(tracker.isQAChecked('l02_qa3'), true);

      tracker.setQAChecked('l02_qa3', false);
      assert.strictEqual(tracker.isQAChecked('l02_qa3'), false);
    });

    it('should handle corrupted QA state in localStorage', () => {
      const tracker = loadTracker();
      global.localStorage.setItem('ai_course_checked_qas', 'invalid json string');
      assert.deepStrictEqual(tracker.getCheckedQAs(), []);

      tracker.setQAChecked('l01_qa0', true);
      assert.strictEqual(tracker.isQAChecked('l01_qa0'), true);
    });
  });

  describe('Task Items Tracking', () => {
    it('should track checked practical tasks', () => {
      const tracker = loadTracker();
      assert.deepStrictEqual(tracker.getCheckedTasks(), []);
      assert.strictEqual(tracker.isTaskChecked('l00_t1'), false);

      tracker.setTaskChecked('l00_t1', true);
      assert.strictEqual(tracker.isTaskChecked('l00_t1'), true);

      // Duplicate add
      tracker.setTaskChecked('l00_t1', true);
      assert.deepStrictEqual(tracker.getCheckedTasks(), ['l00_t1']);

      // Toggle
      assert.strictEqual(tracker.toggleTask('l00_t1'), false);
      assert.strictEqual(tracker.isTaskChecked('l00_t1'), false);

      assert.strictEqual(tracker.toggleTask('l05_t2'), true);
      assert.strictEqual(tracker.isTaskChecked('l05_t2'), true);

      tracker.setTaskChecked('l05_t2', false);
      assert.strictEqual(tracker.isTaskChecked('l05_t2'), false);
    });

    it('should handle corrupted Task state in localStorage', () => {
      const tracker = loadTracker();
      global.localStorage.setItem('ai_course_checked_tasks', '12345');
      assert.deepStrictEqual(tracker.getCheckedTasks(), []);

      tracker.setTaskChecked('l01_t0', true);
      assert.strictEqual(tracker.isTaskChecked('l01_t0'), true);
    });
  });

  describe('SuperMemo SM-2 Spaced Repetition Engine', () => {
    it('should calculate initial SM-2 review transitions correctly', () => {
      const tracker = loadTracker();

      // Grade 5 on fresh card (box 1 -> 2)
      const res5 = tracker.calcSM2(5, 0, 2.5, 1);
      assert.strictEqual(res5.repetitions, 1);
      assert.strictEqual(res5.interval, 1);
      assert.strictEqual(res5.box, 2);
      assert.strictEqual(res5.easeFactor, 2.6);

      // Grade 4 on 2nd repetition via calcSM2 (box 1 -> 2)
      const res4 = tracker.calcSM2(4, 1, 2.6, 1);
      assert.strictEqual(res4.repetitions, 2);
      assert.strictEqual(res4.interval, 6);
      assert.strictEqual(res4.box, 2);
      assert.strictEqual(res4.easeFactor, 2.6);

      // Grade 3 on 3rd repetition with existing prevState (box 3 -> 4)
      const res3 = tracker.sm2.calculateNextState({
        cardId: 'c1',
        box: 3,
        repetitions: 2,
        easeFactor: 2.6,
        interval: 6,
        lastReviewed: null,
        nextReview: null
      }, 3);
      assert.strictEqual(res3.repetitions, 3);
      assert.strictEqual(res3.interval, Math.round(6 * 2.46));
      assert.strictEqual(res3.box, 4);

      // Grade 2 (failure) resets to box 1 and interval 1
      const resFail = tracker.calcSM2(2, 3, 2.46, 15);
      assert.strictEqual(resFail.repetitions, 0);
      assert.strictEqual(resFail.interval, 1);
      assert.strictEqual(resFail.box, 1);
    });

    it('should enforce EF minimum clamp at 1.30', () => {
      const tracker = loadTracker();
      // Repeated low grades
      let state = tracker.calcSM2(0, 0, 1.35, 1);
      assert.strictEqual(state.easeFactor, 1.3);
      state = tracker.calcSM2(0, 0, 1.3, 1);
      assert.strictEqual(state.easeFactor, 1.3);
    });

    it('should handle recordReview, isCardDue, getStats, and resetSM2', () => {
      const tracker = loadTracker();

      let eventDetail = null;
      global.window.addEventListener('sm2-card-reviewed', (e) => {
        eventDetail = e.detail;
      });

      const card1 = tracker.sm2.recordReview('card_test_1', 5);
      assert.strictEqual(card1.cardId, 'card_test_1');
      assert.strictEqual(card1.box, 2);
      assert.ok(eventDetail);
      assert.strictEqual(eventDetail.cardId, 'card_test_1');

      // Check card state getter
      const fetched = tracker.sm2.getCard('card_test_1');
      assert.strictEqual(fetched.box, 2);

      // Check default card getter for unreviewed
      const unreviewed = tracker.sm2.getCard('unreviewed_card');
      assert.strictEqual(unreviewed.repetitions, 0);
      assert.strictEqual(unreviewed.box, 1);
      assert.strictEqual(tracker.sm2.isCardDue('unreviewed_card'), true);

      // Card due check
      assert.strictEqual(tracker.sm2.isCardDue('card_test_1'), false); // next review in future

      // Stats
      const stats = tracker.sm2.getStats();
      assert.strictEqual(stats.totalReviewed, 1);
      assert.strictEqual(stats.boxCounts[2], 1);
      assert.strictEqual(stats.dueCount, 0);
      assert.strictEqual(stats.matureCount, 0);

      // Add a mature card (box 4)
      const allCards = tracker.sm2.getCards();
      allCards['card_mature'] = {
        cardId: 'card_mature',
        box: 4,
        repetitions: 4,
        interval: 30,
        easeFactor: 2.6,
        lastReviewed: Date.now() - 40 * 24 * 3600 * 1000,
        nextReview: Date.now() - 10 * 24 * 3600 * 1000
      };
      global.localStorage.setItem('ai_course_sm2_cards', JSON.stringify(allCards));

      const stats2 = tracker.sm2.getStats();
      assert.strictEqual(stats2.totalReviewed, 2);
      assert.strictEqual(stats2.dueCount, 1);
      assert.strictEqual(stats2.matureCount, 1);

      // Reset SM2
      tracker.sm2.resetSM2();
      assert.deepStrictEqual(tracker.sm2.getCards(), {});
    });

    it('should handle safeGetJSON type checking edge cases in SM2 and storage', () => {
      const tracker = loadTracker();
      // Corrupted non-object for SM2
      global.localStorage.setItem('ai_course_sm2_cards', '1234');
      assert.deepStrictEqual(tracker.sm2.getCards(), {});

      global.localStorage.setItem('ai_course_sm2_cards', JSON.stringify(['array', 'not', 'dict']));
      assert.deepStrictEqual(tracker.sm2.getCards(), {});

      // calculateNextState with null prevState and grade bounds
      const next1 = tracker.sm2.calculateNextState(null, 10);
      assert.strictEqual(next1.repetitions, 1); // grade clamped to 5
      const next2 = tracker.sm2.calculateNextState(null, -5);
      assert.strictEqual(next2.repetitions, 0); // grade clamped to 0
    });
  });

  describe('safeGetJSON Type Guards and Storage Hardening', () => {
    it('should validate string defaultVal and type check parsed values', () => {
      const tracker = loadTracker();
      global.localStorage.setItem('k_str_valid', JSON.stringify('hello world'));
      assert.strictEqual(tracker._safeGetJSON('k_str_valid', 'default'), 'hello world');

      global.localStorage.setItem('k_str_invalid', JSON.stringify(12345));
      assert.strictEqual(tracker._safeGetJSON('k_str_invalid', 'default'), 'default');

      global.localStorage.setItem('k_str_obj', JSON.stringify({ a: 1 }));
      assert.strictEqual(tracker._safeGetJSON('k_str_obj', 'default'), 'default');
    });

    it('should validate number defaultVal and reject NaN / Infinity / non-numbers', () => {
      const tracker = loadTracker();
      global.localStorage.setItem('k_num_valid', JSON.stringify(42.5));
      assert.strictEqual(tracker._safeGetJSON('k_num_valid', 0), 42.5);

      global.localStorage.setItem('k_num_invalid_str', JSON.stringify('42'));
      assert.strictEqual(tracker._safeGetJSON('k_num_invalid_str', 0), 0);

      global.localStorage.setItem('k_num_nan', 'NaN');
      assert.strictEqual(tracker._safeGetJSON('k_num_nan', 0), 0);

      global.localStorage.setItem('k_num_inf', 'Infinity');
      assert.strictEqual(tracker._safeGetJSON('k_num_inf', 0), 0);
    });

    it('should validate boolean defaultVal and reject non-booleans', () => {
      const tracker = loadTracker();
      global.localStorage.setItem('k_bool_true', JSON.stringify(true));
      assert.strictEqual(tracker._safeGetJSON('k_bool_true', false), true);

      global.localStorage.setItem('k_bool_false', JSON.stringify(false));
      assert.strictEqual(tracker._safeGetJSON('k_bool_false', true), false);

      global.localStorage.setItem('k_bool_invalid', JSON.stringify('true'));
      assert.strictEqual(tracker._safeGetJSON('k_bool_invalid', false), false);

      global.localStorage.setItem('k_bool_num', JSON.stringify(1));
      assert.strictEqual(tracker._safeGetJSON('k_bool_num', false), false);
    });

    it('should validate array and object defaults and handle fallback and errors', () => {
      const tracker = loadTracker();
      // Array
      global.localStorage.setItem('k_arr_valid', JSON.stringify([1, 2, 3]));
      assert.deepStrictEqual(tracker._safeGetJSON('k_arr_valid', []), [1, 2, 3]);

      global.localStorage.setItem('k_arr_invalid', JSON.stringify({ length: 3 }));
      assert.deepStrictEqual(tracker._safeGetJSON('k_arr_invalid', []), []);

      // Object
      global.localStorage.setItem('k_obj_valid', JSON.stringify({ a: 1 }));
      assert.deepStrictEqual(tracker._safeGetJSON('k_obj_valid', {}), { a: 1 });

      global.localStorage.setItem('k_obj_arr', JSON.stringify([1, 2]));
      assert.deepStrictEqual(tracker._safeGetJSON('k_obj_arr', {}), {});

      global.localStorage.setItem('k_obj_null', 'null');
      assert.deepStrictEqual(tracker._safeGetJSON('k_obj_null', { fallback: true }), { fallback: true });

      // Fallback path when defaultVal is null
      global.localStorage.setItem('k_raw_val', JSON.stringify('some_val'));
      assert.strictEqual(tracker._safeGetJSON('k_raw_val', null), 'some_val');

      global.localStorage.setItem('k_raw_null', 'null');
      assert.strictEqual(tracker._safeGetJSON('k_raw_null', null), null);

      // Missing item
      assert.strictEqual(tracker._safeGetJSON('missing_key', 'fallback'), 'fallback');

      // Syntax error
      global.localStorage.setItem('k_bad_json', '{not-json');
      assert.strictEqual(tracker._safeGetJSON('k_bad_json', 'fallback'), 'fallback');
    });
  });

  describe('Overall Statistics and Progress Metrics', () => {
    it('should compute weighted progress statistics accurately', () => {
      const tracker = loadTracker();
      const initial = tracker.getOverallStats();
      assert.strictEqual(initial.totalLectures, 28);
      assert.strictEqual(initial.completedLectures, 0);
      assert.strictEqual(initial.lecturePercent, 0);
      assert.strictEqual(initial.overallPercent, 0);

      // 14 of 28 lectures = 50% lec (40% weight -> 20%)
      for (let i = 0; i < 14; i++) {
        tracker.setLectureCompleted(String(i).padStart(2, '0'), true);
      }
      // 148 of 296 QAs = 50% qa (35% weight -> 17.5%)
      for (let i = 0; i < 148; i++) {
        tracker.setQAChecked(`l00_qa${i}`, true);
      }
      // 85 of 170 tasks = 50% task (25% weight -> 12.5%)
      for (let i = 0; i < 85; i++) {
        tracker.setTaskChecked(`l00_t${i}`, true);
      }

      const halfStats = tracker.getOverallStats();
      assert.strictEqual(halfStats.lecturePercent, 50);
      assert.strictEqual(halfStats.qaPercent, 50);
      assert.strictEqual(halfStats.taskPercent, 50);
      assert.strictEqual(halfStats.overallPercent, 50);
    });

    it('should export and import progress JSON correctly with edge cases', () => {
      const tracker = loadTracker();
      tracker.setTheme('light');
      tracker.setLectureCompleted('00', true);
      tracker.setQAChecked('l00_qa0', true);
      tracker.setTaskChecked('l00_t0', true);
      tracker.sm2.recordReview('l00_qa0', 5);

      const jsonStr = tracker.exportProgressJSON();
      assert.ok(jsonStr.includes('"theme": "light"'));
      assert.ok(jsonStr.includes('"completedLectures"'));

      // Clear
      tracker.resetProgress();
      assert.strictEqual(tracker.getCompletedLectures().length, 0);

      // Import back
      const imported = tracker.importProgressJSON(jsonStr);
      assert.strictEqual(imported, true);
      assert.strictEqual(tracker.getTheme(), 'light');
      assert.strictEqual(tracker.isLectureCompleted('00'), true);
      assert.strictEqual(tracker.isQAChecked('l00_qa0'), true);
      assert.strictEqual(tracker.isTaskChecked('l00_t0'), true);

      // Partial object imports
      assert.strictEqual(tracker.importProgressJSON('{}'), true);
      assert.strictEqual(tracker.importProgressJSON(JSON.stringify({ theme: 123 })), true);

      // Bad import
      assert.strictEqual(tracker.importProgressJSON('invalid json'), false);
      assert.strictEqual(tracker.importProgressJSON('null'), false);
    });
  });

  describe('Universal Progress Modal & DOM Binding', () => {
    it('should initialize and control progress modal', () => {
      // Build mock modal elements
      const modal = new MockElement('div');
      modal.id = 'course-progress-modal';
      modal.setAttribute('hidden', '');

      const openBtn = new MockElement('button');
      openBtn.id = 'nav-progress-btn';

      const closeBtn = new MockElement('button');
      closeBtn.id = 'modal-progress-close';

      const closeActionBtn = new MockElement('button');
      closeActionBtn.id = 'modal-close-action-btn';

      const resetBtn = new MockElement('button');
      resetBtn.id = 'modal-reset-progress-btn';

      const fill = new MockElement('div');
      fill.id = 'modal-progress-fill';

      const percent = new MockElement('div');
      percent.id = 'modal-progress-percent';

      const lecs = new MockElement('div');
      lecs.id = 'modal-stat-lecs';

      const qas = new MockElement('div');
      qas.id = 'modal-stat-qas';

      const tasks = new MockElement('div');
      tasks.id = 'modal-stat-tasks';

      modal.appendChild(closeBtn);
      modal.appendChild(closeActionBtn);
      modal.appendChild(resetBtn);
      modal.appendChild(fill);
      modal.appendChild(percent);
      modal.appendChild(lecs);
      modal.appendChild(qas);
      modal.appendChild(tasks);

      global.document.body.appendChild(modal);
      global.document.body.appendChild(openBtn);

      const tracker = loadTracker();

      // Trigger DOMContentLoaded
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      // Open modal via button
      openBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(modal.hasAttribute('hidden'), false);

      // Close modal via closeBtn
      closeBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(modal.hasAttribute('hidden'), true);

      // Open again and close via closeActionBtn
      openBtn.dispatchEvent(new global.window.CustomEvent('click'));
      closeActionBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(modal.hasAttribute('hidden'), true);

      // Open again and close via background click
      openBtn.dispatchEvent(new global.window.CustomEvent('click'));
      const bgClickEvent = new global.window.CustomEvent('click');
      bgClickEvent.target = modal;
      modal.dispatchEvent(bgClickEvent);
      assert.strictEqual(modal.hasAttribute('hidden'), true);

      // Click on inner element should not close modal
      openBtn.dispatchEvent(new global.window.CustomEvent('click'));
      const innerClickEvent = new global.window.CustomEvent('click');
      innerClickEvent.target = fill;
      modal.dispatchEvent(innerClickEvent);
      assert.strictEqual(modal.hasAttribute('hidden'), false);

      // Open and close via Escape keydown
      const escEvent = new global.window.CustomEvent('keydown');
      escEvent.key = 'Escape';
      global.document.dispatchEvent(escEvent);
      assert.strictEqual(modal.hasAttribute('hidden'), true);

      // Escape when modal already hidden does nothing
      global.document.dispatchEvent(escEvent);

      // Reset progress from modal (with confirm)
      openBtn.dispatchEvent(new global.window.CustomEvent('click'));
      tracker.setLectureCompleted('01', true);
      resetBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(tracker.isLectureCompleted('01'), false);

      // Reset progress with confirm=false
      const origConfirm = global.confirm;
      global.confirm = () => false;
      tracker.setLectureCompleted('02', true);
      resetBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(tracker.isLectureCompleted('02'), true);
      global.confirm = origConfirm;
    });

    it('should test DOM theme button click listener on DOMContentLoaded', () => {
      const toggleBtn = new MockElement('button');
      toggleBtn.className = 'theme-toggle';
      global.document.body.appendChild(toggleBtn);

      const tracker = loadTracker();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      assert.strictEqual(tracker.getTheme(), 'dark');
      toggleBtn.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(tracker.getTheme(), 'light');
    });

    it('should handle ServiceWorker registration from root and subpage, plus error paths', () => {
      const tracker = loadTracker();

      // Trigger controllerchange twice to verify refreshing guard
      const controllerchangeHandlers = global.navigator.serviceWorker._listeners['controllerchange'] || [];
      controllerchangeHandlers.forEach(cb => cb());
      assert.strictEqual(global.window.location._reloaded, true);
      global.window.location._reloaded = false;
      controllerchangeHandlers.forEach(cb => cb());
      assert.strictEqual(global.window.location._reloaded, false);

      // Root path registration
      global.window.dispatchEvent(new global.window.CustomEvent('load'));
      assert.strictEqual(global.navigator.serviceWorker._lastRegisteredPath, './sw.js');

      // Subpage (/lectures/) registration with reg.update error and register error
      setupMockBrowser({ pathname: '/lectures/00-intro-ml.html' });
      global.navigator.serviceWorker.register = (swPath) => {
        global.navigator.serviceWorker._lastRegisteredPath = swPath;
        return Promise.resolve({
          update: () => Promise.reject(new Error('Update failed'))
        });
      };
      loadTracker();
      global.window.dispatchEvent(new global.window.CustomEvent('load'));
      assert.strictEqual(global.navigator.serviceWorker._lastRegisteredPath, '../sw.js');

      // Registration failure branch
      setupMockBrowser({ pathname: '/index.html' });
      global.navigator.serviceWorker.register = () => Promise.reject(new Error('Reg failed'));
      loadTracker();
      global.window.dispatchEvent(new global.window.CustomEvent('load'));
    });
  });
});
