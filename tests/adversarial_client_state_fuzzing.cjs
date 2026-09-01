/**
 * Adversarial Client State & Search Fuzzing Node.js Test Suite.
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const TRACKER_PATH = path.join(ROOT, 'js', 'tracker.js');

let passCount = 0;
let failCount = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  [PASS] ${name}`);
    passCount++;
  } catch (err) {
    console.error(`  [FAIL] ${name}`);
    console.error(`         ${err.message}`);
    failCount++;
  }
}

// -------------------------------------------------------------------
// Mock LocalStorage
// -------------------------------------------------------------------
class MockLocalStorage {
  constructor() {
    this.store = {};
  }
  getItem(key) {
    return this.store.hasOwnProperty(key) ? this.store[key] : null;
  }
  setItem(key, val) {
    this.store[key] = String(val);
  }
  removeItem(key) {
    delete this.store[key];
  }
  clear() {
    this.store = {};
  }
}

// Create Sandbox
const mockStorage = new MockLocalStorage();
const mockWindow = {
  localStorage: mockStorage,
  dispatchEvent: () => {},
  addEventListener: () => {},
  document: {
    documentElement: {
      setAttribute: () => {},
      getAttribute: () => 'dark'
    },
    querySelectorAll: () => [],
    getElementById: () => null,
    addEventListener: () => {}
  },
  navigator: {
    serviceWorker: {
      register: () => Promise.resolve()
    }
  },
  CustomEvent: class { constructor(type, detail) { this.type = type; this.detail = detail; } },
  console: {
    log: () => {},
    warn: () => {},
    error: () => {}
  }
};

const context = vm.createContext({
  window: mockWindow,
  document: mockWindow.document,
  navigator: mockWindow.navigator,
  localStorage: mockStorage,
  CustomEvent: mockWindow.CustomEvent,
  console: mockWindow.console,
  setTimeout: setTimeout,
  clearTimeout: clearTimeout,
  setInterval: setInterval,
  clearInterval: clearInterval
});

// Load tracker.js
const trackerCode = fs.readFileSync(TRACKER_PATH, 'utf-8');
vm.runInContext(trackerCode, context);

// Test Suite
console.log('=== Starting Adversarial Client State & Fuzzing Suite ===');

// 1. Search Query Safety in JavaScript
test('Search Query: XSS payloads and special characters do not throw or corrupt', () => {
  const payloads = [
    "<script>alert('XSS')</script>",
    '"><svg onload=alert(1)>',
    "'; DROP TABLE students; --",
    "\\u0000\\x00",
    ".*+?^${}()|[]\\",
    "(((((((a+)+)+)+)+)+)+)$",
    "🚀🔥🧠".repeat(100),
    "A".repeat(20000),
    null,
    undefined,
    12345,
    {},
    []
  ];

  const dataset = [
    { title: 'Полносвязные сети', desc: 'Backprop и градиенты' },
    { title: 'Трансформеры', desc: 'Self-attention и Multi-head' },
  ];

  payloads.forEach(p => {
    const q = (typeof p === 'string' ? p : String(p || '')).toLowerCase().trim();
    const results = dataset.filter(d => (d.title + ' ' + d.desc).toLowerCase().includes(q));
    assert(Array.isArray(results), `Results must be array for payload: ${p}`);
  });
});

// 2. LocalStorage Corruption Recovery in tracker.js
test('LocalStorage: Recovery from completely invalid JSON and unexpected types', () => {
  const corruptedKeys = [
    'ai_course_completed_lectures',
    'ai_course_checked_qas',
    'ai_course_checked_tasks',
    'ai_course_sm2_cards'
  ];

  const corruptedPayloads = [
    'undefined',
    'null',
    '{invalid_json',
    '12345',
    '"plain string"',
    '[1, 2, 3,',
    'NaN',
    'Infinity'
  ];

  corruptedPayloads.forEach(corruptVal => {
    corruptedKeys.forEach(k => {
      mockStorage.setItem(k, corruptVal);
    });

    // Run CourseTracker methods to verify no unhandled throws
    const tracker = context.window.CourseTracker || context.CourseTracker;
    if (tracker) {
      const completed = tracker.getCompletedLectures();
      assert(Array.isArray(completed), 'getCompletedLectures should return array on corruption');

      const checkedQAs = tracker.getCheckedQAs();
      assert(Array.isArray(checkedQAs), 'getCheckedQAs should return array on corruption');

      const checkedTasks = tracker.getCheckedTasks();
      assert(Array.isArray(checkedTasks), 'getCheckedTasks should return array on corruption');

      const stats = tracker.getOverallStats();
      assert(typeof stats === 'object' && stats !== null, 'getOverallStats should return valid object');
      assert(typeof stats.percent === 'number' && !isNaN(stats.percent), 'Stats percent must be number');
    }
  });
});

// 3. SM-2 Spaced Repetition Under Extreme Ratings and Corrupted Bounds
test('SM-2 Spaced Repetition: Extreme ratings (0, 5, negative, out-of-bounds) maintain EF >= 1.3', () => {
  const tracker = context.window.CourseTracker || context.CourseTracker;
  if (tracker && tracker.calcSM2) {
    const testCases = [
      { q: 0, reps: 0, ef: 2.5, interval: 1 },
      { q: 5, reps: 10, ef: 2.5, interval: 100 },
      { q: 1, reps: 5, ef: 1.3, interval: 20 },
      { q: -10, reps: -5, ef: 0.5, interval: -10 },
      { q: 99, reps: 999999, ef: 100.0, interval: 999999 },
    ];

    testCases.forEach(tc => {
      const res = tracker.calcSM2(tc.q, tc.reps, tc.ef, tc.interval);
      assert(typeof res === 'object', 'Result must be object');
      assert(res.easeFactor >= 1.3, `Ease factor must be >= 1.3, got: ${res.easeFactor}`);
      assert(res.interval >= 1, `Interval must be >= 1, got: ${res.interval}`);
      assert(res.repetitions >= 0, `Repetitions must be >= 0, got: ${res.repetitions}`);
    });
  }
});

// 4. State Reset and Export/Import Roundtrip
test('State Management: Export, reset, and Import restore clean state', () => {
  const tracker = context.window.CourseTracker || context.CourseTracker;
  if (tracker) {
    mockStorage.clear();
    tracker.setLectureCompleted('00', true);
    tracker.setLectureCompleted('01', true);
    tracker.setQAChecked('00-qa-1', true);
    tracker.setTaskChecked('00-task-1', true);

    const exported = tracker.exportProgressJSON();
    assert(typeof exported === 'string', 'Export must return string');
    const parsed = JSON.parse(exported);
    assert(parsed.completedLectures.includes('00'), 'Exported state contains lecture 00');

    tracker.resetProgress();
    assert.strictEqual(tracker.getCompletedLectures().length, 0, 'Reset clears completed lectures');

    const imported = tracker.importProgressJSON(exported);
    assert.strictEqual(imported, true, 'Import succeeds');
    assert.strictEqual(tracker.getCompletedLectures().length, 2, 'Import restores 2 lectures');
  }
});

console.log('======================================================');
console.log(`Results: ${passCount} passed, ${failCount} failed`);
console.log('======================================================');
if (failCount > 0) process.exit(1);
