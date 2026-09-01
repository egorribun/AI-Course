/**
 * Adversarial Headless Verification Harness for DL Exam Platform.
 * Tests SM-2 algorithm, LocalStorage schema/corruption resistance,
 * Exam simulator ticket routing, and Keyboard focus isolation.
 */
const fs = require('fs');
const path = require('path');

const COURSE_ROOT = path.resolve(__dirname, '..');
const TRACKER_JS_PATH = path.join(COURSE_ROOT, 'js', 'tracker.js');
const SIMULATOR_JS_PATH = path.join(COURSE_ROOT, 'js', 'simulator.js');
const EXAM_DATA_JS_PATH = path.join(COURSE_ROOT, 'js', 'exam_data.js');
const APP_JS_PATH = path.join(COURSE_ROOT, 'js', 'app.js');
const LECTURE_JS_PATH = path.join(COURSE_ROOT, 'js', 'lecture.js');

class MockCustomEvent {
  constructor(type, params = {}) {
    this.type = type;
    this.detail = params.detail || null;
  }
}

// Mock Browser Environment
function createMockEnvironment() {
  const store = {};
  const windowEventListeners = {};
  const docEventListeners = {};

  const localStorage = {
    getItem: (k) => (Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: (k) => { delete store[k]; },
    clear: () => { Object.keys(store).forEach(k => delete store[k]); },
    _store: store
  };

  const documentElement = {
    attributes: {},
    setAttribute: (k, v) => { documentElement.attributes[k] = String(v); },
    getAttribute: (k) => documentElement.attributes[k] || null
  };

  const body = {
    children: [],
    prepend: () => {},
    appendChild: () => {},
    removeChild: () => {}
  };

  const activeElementState = { current: null };

  const document = {
    documentElement,
    body,
    get activeElement() { return activeElementState.current; },
    querySelectorAll: (sel) => [],
    querySelector: (sel) => null,
    getElementById: (id) => null,
    createElement: (tag) => ({
      tagName: tag.toUpperCase(),
      className: '',
      attributes: {},
      style: {},
      isContentEditable: false,
      classList: {
        add: () => {},
        remove: () => {},
        toggle: () => {}
      },
      setAttribute: function(k, v) { this.attributes[k] = String(v); },
      getAttribute: function(k) { return this.attributes[k] || null; },
      addEventListener: () => {},
      appendChild: () => {},
      blur: function() {
        if (activeElementState.current === this) {
          activeElementState.current = null;
        }
      },
      focus: function() {
        activeElementState.current = this;
      },
      select: () => {}
    }),
    addEventListener: (evt, cb) => {
      docEventListeners[evt] = docEventListeners[evt] || [];
      docEventListeners[evt].push(cb);
    },
    dispatchEvent: (evt) => {
      const handlers = docEventListeners[evt.type] || [];
      handlers.forEach(h => {
        try { h(evt); } catch(e) {}
      });
      return true;
    }
  };

  const navigator = {
    userAgent: 'NodeAdversarialTest',
    serviceWorker: undefined,
    clipboard: { writeText: () => Promise.resolve() }
  };

  const window = {
    localStorage,
    document,
    navigator,
    CustomEvent: MockCustomEvent,
    location: { href: 'http://localhost/index.html', pathname: '/index.html' },
    addEventListener: (evt, cb) => {
      windowEventListeners[evt] = windowEventListeners[evt] || [];
      windowEventListeners[evt].push(cb);
    },
    dispatchEvent: (evt) => {
      const handlers = windowEventListeners[evt.type] || [];
      handlers.forEach(h => {
        try { h(evt); } catch(e) {}
      });
      return true;
    },
    _windowEventListeners: windowEventListeners,
    _docEventListeners: docEventListeners,
    _activeElementState: activeElementState
  };

  global.window = window;
  global.document = document;
  global.localStorage = localStorage;
  global.CustomEvent = MockCustomEvent;

  return { window, document, localStorage, activeElementState, windowEventListeners, docEventListeners, CustomEvent: MockCustomEvent };
}

// Test Runner
const results = [];
function test(name, fn) {
  try {
    fn();
    results.push({ name, passed: true });
    console.log(`  [PASS] ${name}`);
  } catch (err) {
    results.push({ name, passed: false, error: err.message, stack: err.stack });
    console.error(`  [FAIL] ${name}: ${err.message}`);
  }
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

function assertEqual(actual, expected, message) {
  if (actual !== expected) {
    throw new Error(`${message || 'Mismatch'}: expected ${JSON.stringify(expected)}, got ${JSON.stringify(actual)}`);
  }
}

function assertAlmostEqual(actual, expected, delta = 0.001, message) {
  if (Math.abs(actual - expected) > delta) {
    throw new Error(`${message || 'Float mismatch'}: expected ${expected} ±${delta}, got ${actual}`);
  }
}

console.log('=== Starting Adversarial Verification Harness ===\n');

// -------------------------------------------------------------
// Suite 1: SM-2 Engine Edge Cases & Boundary Values
// -------------------------------------------------------------
console.log('--- Suite 1: SM-2 Algorithm & Boundary Invariants ---');

test('SM-2: Initial card state defaults', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));

  const sm2 = env.window.CourseTracker.sm2;
  const initial = sm2.getCard('non_existent_card');
  assertEqual(initial.box, 1, 'Default box must be 1');
  assertEqual(initial.repetitions, 0, 'Default repetitions must be 0');
  assertEqual(initial.interval, 1, 'Default interval must be 1');
  assertEqual(initial.easeFactor, 2.5, 'Default easeFactor must be 2.5');
  assertEqual(initial.lastReviewed, null, 'Default lastReviewed must be null');
  assertEqual(initial.nextReview, null, 'Default nextReview must be null');
});

test('SM-2: Grade rating domain q in {0, 1, 2, 3, 4, 5} easeFactor deltas', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));
  const sm2 = env.window.CourseTracker.sm2;

  // Grade 5: EF -> 2.5 + 0.1 = 2.6
  const s5 = sm2.calculateNextState({ box: 1, repetitions: 0, interval: 1, easeFactor: 2.5 }, 5);
  assertAlmostEqual(s5.easeFactor, 2.60, 0.001, 'Grade 5 EF should increase by 0.10');
  assertEqual(s5.box, 2, 'Grade 5 box should advance to 2');
  assertEqual(s5.repetitions, 1, 'Grade 5 reps should increment to 1');
  assertEqual(s5.interval, 1, 'First successful rep interval is 1');

  // Grade 4: EF -> 2.5 + 0.0 = 2.5
  const s4 = sm2.calculateNextState({ box: 1, repetitions: 0, interval: 1, easeFactor: 2.5 }, 4);
  assertAlmostEqual(s4.easeFactor, 2.50, 0.001, 'Grade 4 EF should remain unchanged');

  // Grade 3: EF -> 2.5 - 0.14 = 2.36
  const s3 = sm2.calculateNextState({ box: 1, repetitions: 0, interval: 1, easeFactor: 2.5 }, 3);
  assertAlmostEqual(s3.easeFactor, 2.36, 0.001, 'Grade 3 EF should decrease by 0.14');

  // Grade 2: EF -> 2.5 - 0.32 = 2.18
  const s2 = sm2.calculateNextState({ box: 1, repetitions: 0, interval: 1, easeFactor: 2.5 }, 2);
  assertAlmostEqual(s2.easeFactor, 2.18, 0.001, 'Grade 2 EF should decrease by 0.32');

  // Grade 1: EF -> 2.5 - 0.54 = 1.96
  const s1 = sm2.calculateNextState({ box: 1, repetitions: 0, interval: 1, easeFactor: 2.5 }, 1);
  assertAlmostEqual(s1.easeFactor, 1.96, 0.001, 'Grade 1 EF should decrease by 0.54');

  // Grade 0: EF -> 2.5 - 0.80 = 1.70
  const s0 = sm2.calculateNextState({ box: 1, repetitions: 0, interval: 1, easeFactor: 2.5 }, 0);
  assertAlmostEqual(s0.easeFactor, 1.70, 0.001, 'Grade 0 EF should decrease by 0.80');
});

test('SM-2: Out-of-bounds grades clamped to [0, 5]', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));
  const sm2 = env.window.CourseTracker.sm2;

  const sNegative = sm2.calculateNextState({ box: 1, repetitions: 0, interval: 1, easeFactor: 2.5 }, -10);
  assertAlmostEqual(sNegative.easeFactor, 1.70, 0.001, 'Negative grade clamped to 0');

  const sSuperHigh = sm2.calculateNextState({ box: 1, repetitions: 0, interval: 1, easeFactor: 2.5 }, 999);
  assertAlmostEqual(sSuperHigh.easeFactor, 2.60, 0.001, 'Grade > 5 clamped to 5');
});

test('SM-2: Consecutive forgetting (q < 3) resets repetitions to 0, interval to 1, box to 1, and clamps EF at >= 1.3', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));
  const sm2 = env.window.CourseTracker.sm2;

  let state = { box: 5, repetitions: 10, interval: 180, easeFactor: 2.8 };

  for (let i = 0; i < 50; i++) {
    state = sm2.calculateNextState(state, 0);
    assert(state.easeFactor >= 1.30, `EF must never fall below 1.30 (iter ${i}: ${state.easeFactor})`);
    assertEqual(state.repetitions, 0, `Repetitions must reset to 0 upon q < 3 (iter ${i})`);
    assertEqual(state.interval, 1, `Interval must reset to 1 day upon q < 3 (iter ${i})`);
    assertEqual(state.box, 1, `Box must reset to 1 upon q < 3 (iter ${i})`);
  }
  assertAlmostEqual(state.easeFactor, 1.30, 0.001, 'EF clamps precisely at 1.30');
});

test('SM-2: Multi-step progression on perfect streak (q = 5)', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));
  const sm2 = env.window.CourseTracker.sm2;

  let state = { box: 1, repetitions: 0, interval: 1, easeFactor: 2.5 };
  const intervals = [];
  const boxes = [];
  const efs = [];

  for (let i = 0; i < 6; i++) {
    state = sm2.calculateNextState(state, 5);
    intervals.push(state.interval);
    boxes.push(state.box);
    efs.push(state.easeFactor);
  }

  // Step 1: rep 0 -> interval 1, EF 2.60, box 2
  assertEqual(intervals[0], 1, 'Step 1 interval = 1');
  assertEqual(boxes[0], 2, 'Step 1 box = 2');
  assertAlmostEqual(efs[0], 2.60, 0.01);

  // Step 2: rep 1 -> interval 6, EF 2.70, box 3
  assertEqual(intervals[1], 6, 'Step 2 interval = 6');
  assertEqual(boxes[1], 3, 'Step 2 box = 3');
  assertAlmostEqual(efs[1], 2.70, 0.01);

  // Step 3: rep 2 -> interval = round(6 * 2.80) = 17, EF 2.80, box 4
  assertEqual(intervals[2], 17, 'Step 3 interval = 17');
  assertEqual(boxes[2], 4, 'Step 3 box = 4');

  // Step 4: rep 3 -> interval = round(17 * 2.90) = 49, EF 2.90, box 5
  assertEqual(intervals[3], 49, 'Step 4 interval = 49');
  assertEqual(boxes[3], 5, 'Step 4 box = 5 (max box 5)');

  // Step 5: rep 4 -> interval = round(49 * 3.00) = 147, EF 3.00, box 5
  assertEqual(intervals[4], 147, 'Step 5 interval = 147');
  assertEqual(boxes[4], 5, 'Step 5 box remains clamped at 5');
});

test('SM-2: Due queue filtering with past, future, and unreviewed timestamps', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));
  const sm2 = env.window.CourseTracker.sm2;

  const now = Date.now();
  const dayMs = 86400000;

  const cardsDb = {
    unreviewed: { cardId: 'unreviewed', box: 1, repetitions: 0, interval: 1, easeFactor: 2.5, lastReviewed: null, nextReview: null },
    due_yesterday: { cardId: 'due_yesterday', box: 2, repetitions: 1, interval: 1, easeFactor: 2.6, lastReviewed: now - 2*dayMs, nextReview: now - dayMs },
    due_now: { cardId: 'due_now', box: 1, repetitions: 0, interval: 1, easeFactor: 2.5, lastReviewed: now - dayMs, nextReview: now },
    due_tomorrow: { cardId: 'due_tomorrow', box: 3, repetitions: 2, interval: 6, easeFactor: 2.7, lastReviewed: now, nextReview: now + dayMs },
    due_next_month: { cardId: 'due_next_month', box: 5, repetitions: 5, interval: 45, easeFactor: 3.0, lastReviewed: now, nextReview: now + 30*dayMs }
  };

  env.localStorage.setItem('ai_course_sm2_cards', JSON.stringify(cardsDb));

  assert(sm2.isCardDue('unreviewed'), 'Unreviewed card must be due');
  assert(sm2.isCardDue('due_yesterday'), 'Yesterday card must be due');
  assert(sm2.isCardDue('due_now'), 'Card due now must be due');
  assert(!sm2.isCardDue('due_tomorrow'), 'Tomorrow card must NOT be due');
  assert(!sm2.isCardDue('due_next_month'), 'Next month card must NOT be due');

  const stats = sm2.getStats();
  assertEqual(stats.totalReviewed, 5, 'Total cards 5');
  assertEqual(stats.dueCount, 3, 'Due count must be 3 (unreviewed, yesterday, now)');
  assertEqual(stats.matureCount, 1, 'Mature count (box 4-5) must be 1');
});


// -------------------------------------------------------------
// Suite 2: LocalStorage Export/Import & Schema Validation
// -------------------------------------------------------------
console.log('\n--- Suite 2: LocalStorage Robustness & Schema Validation ---');

test('LocalStorage: Valid export and import round-trip', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));
  const ct = env.window.CourseTracker;

  ct.setTheme('light');
  ct.setLectureCompleted('00', true);
  ct.setLectureCompleted('05', true);
  ct.setQAChecked('l01_qa0', true);
  ct.setTaskChecked('l02_t0', true);
  ct.sm2.recordReview('l01_qa0', 5);

  const exportedJSON = ct.exportProgressJSON();
  assert(typeof exportedJSON === 'string', 'Export must return a JSON string');

  // Reset progress and verify wiped state
  ct.resetProgress();
  assertEqual(ct.getCompletedLectures().length, 0, 'Lectures should be empty after reset');
  assertEqual(ct.getCheckedQAs().length, 0, 'QAs should be empty after reset');

  // Import previously exported data
  const ok = ct.importProgressJSON(exportedJSON);
  assertEqual(ok, true, 'Import should succeed on valid payload');
  assertEqual(ct.getTheme(), 'light', 'Theme should be light');
  assertEqual(ct.isLectureCompleted('00'), true, 'Lecture 00 should be completed');
  assertEqual(ct.isLectureCompleted('05'), true, 'Lecture 05 should be completed');
  assertEqual(ct.isQAChecked('l01_qa0'), true, 'QA should be checked');
  assertEqual(ct.isTaskChecked('l02_t0'), true, 'Task should be checked');
  assert(ct.sm2.getCard('l01_qa0').repetitions >= 1, 'SM-2 card state restored');
});

test('LocalStorage: Malformed JSON attacks return false without throwing unhandled exceptions', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));
  const ct = env.window.CourseTracker;

  const maliciousPayloads = [
    '',
    '{ malformed: json, ',
    'null',
    'undefined',
    '12345',
    '"plain string"',
    '[]',
    '{"completedLectures": "not-an-array"}',
    '{"sm2Cards": "not-an-object"}',
    '{"theme": 12345}'
  ];

  // Temporarily mute console.error to keep harness output tidy
  const origErr = console.error;
  console.error = () => {};

  try {
    maliciousPayloads.forEach(payload => {
      const result = ct.importProgressJSON(payload);
      assert(typeof result === 'boolean', `Result must be boolean for payload: ${payload}`);
    });
  } finally {
    console.error = origErr;
  }
});


// -------------------------------------------------------------
// Suite 3: Exam Simulator Ticket Selection (Tickets 1-25 + L00)
// -------------------------------------------------------------
console.log('\n--- Suite 3: Exam Simulator Ticket Coverage & Routing ---');

test('Exam Simulator: EXAM_DATA contains 28 lectures with all 25 official tickets', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(EXAM_DATA_JS_PATH, 'utf-8'));

  const data = env.window.EXAM_DATA;
  assert(Array.isArray(data), 'window.EXAM_DATA must be an array');
  assertEqual(data.length, 28, 'EXAM_DATA must contain exactly 28 lectures');

  // Verify L00 exists
  const l00 = data.find(d => d.id === '00');
  assert(l00 !== undefined, 'Lecture 00 (Intro ML) must exist in EXAM_DATA');
  assert(l00.qas.length >= 10, `L00 must have >=10 QAs (found ${l00.qas.length})`);
  assert(l00.tasks.length >= 6, `L00 must have >=6 tasks (found ${l00.tasks.length})`);

  // Verify tickets 1 through 25
  for (let t = 1; t <= 25; t++) {
    const matching = data.filter(d => d.ticket && d.ticket.includes(`Билет ${t}`));
    assert(matching.length >= 1, `Ticket #${t} must be present in EXAM_DATA`);
    matching.forEach(lec => {
      assert(lec.title && lec.title.length > 5, `Ticket #${t} must have a valid title`);
      assert(lec.filename && lec.filename.endsWith('.html'), `Ticket #${t} must point to .html file`);
      assert(Array.isArray(lec.qas) && lec.qas.length >= 10, `Ticket #${t} must have >=10 QAs (found ${lec.qas.length})`);
      assert(Array.isArray(lec.tasks) && lec.tasks.length >= 6, `Ticket #${t} must have >=6 tasks (found ${lec.tasks.length})`);
      assert(Array.isArray(lec.cheat_items) && lec.cheat_items.length >= 1, `Ticket #${t} must have cheat sheet items`);
    });
  }
});

test('Exam Simulator: Direct and topic-filtered random ticket selection logic', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(EXAM_DATA_JS_PATH, 'utf-8'));
  const data = env.window.EXAM_DATA;

  // Topic classification helper
  function getLectureTopic(lecId) {
    const num = parseInt(lecId, 10);
    if ([4, 5, 8, 9, 13].includes(num)) return 'cv';
    if ([14, 15, 16, 17, 18, 19, 20, 21].includes(num)) return 'nlp';
    if ([22, 23, 24, 25, 26, 27].includes(num)) return 'rl';
    return 'math';
  }

  // Topic filter coverage
  const topics = ['cv', 'nlp', 'rl', 'math'];
  topics.forEach(top => {
    const subset = data.filter(d => d.id !== '00' && getLectureTopic(d.id) === top);
    assert(subset.length >= 3, `Topic ${top} must have at least 3 lectures (found ${subset.length})`);
  });

  // Random draw pool exclusion of L00
  const candidates = data.filter(d => d.id !== '00');
  assertEqual(candidates.length, 27, 'Random draw candidates pool must have 27 exam lectures (excluding L00)');
});


// -------------------------------------------------------------
// Suite 4: Keyboard Shortcut Safety & Form Focus Guarding
// -------------------------------------------------------------
console.log('\n--- Suite 4: Keyboard Shortcut Focus Safety ---');

test('Keyboard: Shortcuts guarded when focus is inside INPUT, TEXTAREA, SELECT, or contentEditable', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));
  eval(fs.readFileSync(APP_JS_PATH, 'utf-8'));

  // Trigger DOMContentLoaded so app.js registers window keydown listener
  env.document.dispatchEvent(new env.CustomEvent('DOMContentLoaded'));

  const keydownListeners = env.windowEventListeners['keydown'] || [];
  assert(keydownListeners.length >= 1, 'App.js must register keydown listener on window');

  const handler = keydownListeners[0];

  let themeToggled = false;
  env.window.CourseTracker.toggleTheme = () => { themeToggled = true; };

  // Case 1: Active element is INPUT
  const inputEl = env.document.createElement('input');
  env.activeElementState.current = inputEl;
  themeToggled = false;
  handler({ key: 't', preventDefault: () => {} });
  assertEqual(themeToggled, false, 'Theme toggle shortcut MUST NOT fire while input is focused');

  // Case 2: Active element is TEXTAREA
  const textareaEl = env.document.createElement('textarea');
  env.activeElementState.current = textareaEl;
  themeToggled = false;
  handler({ key: 't', preventDefault: () => {} });
  assertEqual(themeToggled, false, 'Theme toggle shortcut MUST NOT fire while textarea is focused');

  // Case 3: Active element is SELECT
  const selectEl = env.document.createElement('select');
  env.activeElementState.current = selectEl;
  themeToggled = false;
  handler({ key: 't', preventDefault: () => {} });
  assertEqual(themeToggled, false, 'Theme toggle shortcut MUST NOT fire while select is focused');

  // Case 4: Active element is contentEditable
  const editableEl = env.document.createElement('div');
  editableEl.isContentEditable = true;
  env.activeElementState.current = editableEl;
  themeToggled = false;
  handler({ key: 't', preventDefault: () => {} });
  assertEqual(themeToggled, false, 'Theme toggle shortcut MUST NOT fire while contentEditable is focused');

  // Case 5: Normal body focus -> shortcuts work
  env.activeElementState.current = null;
  themeToggled = false;
  handler({ key: 't', preventDefault: () => {} });
  assertEqual(themeToggled, true, 'Theme toggle shortcut MUST fire when no input is focused');
});

test('Keyboard: Escape key blurs active input element', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));
  eval(fs.readFileSync(APP_JS_PATH, 'utf-8'));

  // Trigger DOMContentLoaded so app.js registers window keydown listener
  env.document.dispatchEvent(new env.CustomEvent('DOMContentLoaded'));

  const keydownListeners = env.windowEventListeners['keydown'] || [];
  const handler = keydownListeners[0];

  const inputEl = env.document.createElement('input');
  env.activeElementState.current = inputEl;

  let blurred = false;
  inputEl.blur = () => { blurred = true; env.activeElementState.current = null; };

  handler({ key: 'Escape', preventDefault: () => {} });
  assertEqual(blurred, true, 'Escape key must trigger blur() on active input element');
  assertEqual(env.document.activeElement, null, 'Active element must become null after blur');
});

test('Keyboard: Lecture navigation keys [ and ] work in lecture.js with input protection', () => {
  const env = createMockEnvironment();
  eval(fs.readFileSync(TRACKER_JS_PATH, 'utf-8'));
  eval(fs.readFileSync(LECTURE_JS_PATH, 'utf-8'));

  env.document.dispatchEvent(new env.CustomEvent('DOMContentLoaded'));

  const keydownListeners = env.windowEventListeners['keydown'] || [];
  assert(keydownListeners.length >= 1, 'Lecture.js must register keydown listener on window');
  const handler = keydownListeners[0];

  let themeToggled = false;
  env.window.CourseTracker.toggleTheme = () => { themeToggled = true; };

  // Guard test in lecture.js
  const inputEl = env.document.createElement('input');
  env.activeElementState.current = inputEl;
  handler({ key: 't', preventDefault: () => {} });
  assertEqual(themeToggled, false, 'Theme toggle shortcut MUST NOT fire in lecture when input is focused');

  env.activeElementState.current = null;
  handler({ key: 't', preventDefault: () => {} });
  assertEqual(themeToggled, true, 'Theme toggle shortcut MUST fire in lecture when no input is focused');
});

// Summary
console.log('\n=== Harness Summary ===');
const failedCount = results.filter(r => !r.passed).length;
const passedCount = results.filter(r => r.passed).length;
console.log(`Total: ${results.length}, Passed: ${passedCount}, Failed: ${failedCount}`);

if (failedCount > 0) {
  console.error('\nFAILED TESTS:');
  results.filter(r => !r.passed).forEach(r => console.error(`- ${r.name}: ${r.error}`));
  process.exit(1);
} else {
  console.log('\nALL ADVERSARIAL HARNESS TESTS PASSED EMPIRICALLY!');
  process.exit(0);
}
