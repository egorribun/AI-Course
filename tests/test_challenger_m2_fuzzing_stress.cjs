/**
 * Challenger M2 Empirical Fuzzing & Service Worker Stress Harness
 * Milestone M2: Code Quality, PWA Offline, JS Hardening & Heading Hierarchy
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

let passedTests = 0;
let failedTests = 0;

function logPass(msg) {
  console.log(`  [PASS] ${msg}`);
  passedTests++;
}

function logFail(msg, err) {
  console.error(`  [FAIL] ${msg}`);
  if (err) console.error('         ', err.message || err);
  failedTests++;
}

function createDOMContext(initialStorage = {}) {
  const store = { ...initialStorage };
  const listeners = {};

  const localStorage = {
    getItem: (k) => (k in store ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: (k) => { delete store[k]; },
    clear: () => { Object.keys(store).forEach(k => delete store[k]); },
    _dump: () => store
  };

  const document = {
    documentElement: {
      setAttribute: (k, v) => {},
      getAttribute: (k) => 'dark'
    },
    querySelectorAll: (selector) => [],
    getElementById: (id) => null,
    addEventListener: (event, handler) => {
      listeners[event] = listeners[event] || [];
      listeners[event].push(handler);
    }
  };

  const window = {
    localStorage,
    document,
    location: { pathname: '/index.html' },
    addEventListener: (event, handler) => {
      listeners[event] = listeners[event] || [];
      listeners[event].push(handler);
    },
    dispatchEvent: (evt) => {
      const handlers = listeners[evt.type] || [];
      handlers.forEach(fn => {
        try { fn(evt); } catch(e) {}
      });
      return true;
    }
  };

  global.CustomEvent = class CustomEvent {
    constructor(type, params) {
      this.type = type;
      this.detail = params ? params.detail : null;
    }
  };

  const sandbox = {
    window,
    document,
    localStorage,
    console: {
      log: () => {},
      warn: () => {},
      error: () => {},
      debug: () => {}
    },
    setTimeout,
    clearTimeout,
    Date,
    Math,
    Array,
    Object,
    Number,
    String,
    Boolean,
    JSON,
    CustomEvent: global.CustomEvent,
    navigator: {}
  };

  vm.createContext(sandbox);
  const trackerCode = fs.readFileSync(path.join(__dirname, '../js/tracker.js'), 'utf8');
  vm.runInContext(trackerCode, sandbox);

  return { sandbox, store, localStorage, window };
}

console.log('=== Starting Challenger M2 Adversarial Fuzzing & SW Stress Harness ===\n');

// ---------------------------------------------------------------------------
// SUITE 1: Extreme LocalStorage Fuzzing & Type Guarding
// ---------------------------------------------------------------------------
console.log('--- Suite 1: CourseTracker & safeGetJSON Exhaustive Fuzzing ---');

const FUZZ_PAYLOADS = [
  // Corrupted / malformed JSON strings
  '{invalid_json',
  '[1, 2, ',
  '{"key": undefined}',
  '{"a": 1,}',
  '',
  '   ',
  'undefined',
  'NaN',
  'Infinity',
  '-Infinity',
  '{"__proto__": {"polluted": true}}',
  '{"constructor": {"prototype": {"polluted": true}}}',
  // Unexpected JSON primitive types
  '12345',
  '-999.99',
  '0',
  '"plain string payload"',
  '""',
  'true',
  'false',
  'null',
  // Unexpected structural JSON types
  '[]',
  '{}',
  '{"0": "00", "1": "01", "length": 2}',
  '["valid", 123, null, undefined, true, false, {"nested": true}, [1, 2]]',
  '[[[[1]]]]',
  // Special characters & XSS payloads
  '<script>alert("xss")</script>',
  '\u0000\u0001\u0002\u001f',
  '🔥🚀💡🧠📚',
  'A'.repeat(10000)
];

const KEYS = [
  'ai_course_theme',
  'ai_course_completed_lectures',
  'ai_course_checked_qas',
  'ai_course_checked_tasks',
  'ai_course_sm2_cards'
];

try {
  let fuzzRunCount = 0;
  for (const key of KEYS) {
    for (const payload of FUZZ_PAYLOADS) {
      const { sandbox } = createDOMContext({ [key]: payload });
      const CT = sandbox.window.CourseTracker;

      // 1. getCompletedLectures must ALWAYS return an Array
      const completed = CT.getCompletedLectures();
      assert(Array.isArray(completed), `getCompletedLectures returned non-array for ${key}=${payload.slice(0, 20)}`);

      // 2. isLectureCompleted must ALWAYS return boolean
      const isComp = CT.isLectureCompleted('00');
      assert(typeof isComp === 'boolean', 'isLectureCompleted returned non-boolean');

      // 3. getCheckedQAs must ALWAYS return an Array
      const qas = CT.getCheckedQAs();
      assert(Array.isArray(qas), 'getCheckedQAs returned non-array');

      // 4. isQAChecked must ALWAYS return boolean
      const isQA = CT.isQAChecked('qa-00-1');
      assert(typeof isQA === 'boolean', 'isQAChecked returned non-boolean');

      // 5. getCheckedTasks must ALWAYS return an Array
      const tasks = CT.getCheckedTasks();
      assert(Array.isArray(tasks), 'getCheckedTasks returned non-array');

      // 6. isTaskChecked must ALWAYS return boolean
      const isTask = CT.isTaskChecked('task-00-1');
      assert(typeof isTask === 'boolean', 'isTaskChecked returned non-boolean');

      // 7. getTheme must return string
      const theme = CT.getTheme();
      assert(typeof theme === 'string', 'getTheme returned non-string');

      // 8. sm2.getCards must ALWAYS return non-null, non-array object
      const cards = CT.sm2.getCards();
      assert(typeof cards === 'object' && cards !== null && !Array.isArray(cards), 'sm2.getCards invalid');

      // 9. sm2.getCard must return valid card structure
      const card = CT.sm2.getCard('card-1');
      assert(card && typeof card === 'object', 'sm2.getCard invalid');
      assert(typeof card.box === 'number' && card.box >= 1 && card.box <= 5, 'card.box out of bounds');
      assert(typeof card.easeFactor === 'number' && card.easeFactor >= 1.3, 'card.easeFactor < 1.3');

      // 10. getOverallStats must return strictly valid finite numbers [0, 100]
      const stats = CT.getOverallStats();
      assert(typeof stats.overallPercent === 'number' && !isNaN(stats.overallPercent) && isFinite(stats.overallPercent), 'overallPercent is NaN/non-finite');
      assert(stats.overallPercent >= 0 && stats.overallPercent <= 100, `overallPercent out of range: ${stats.overallPercent}`);
      assert(stats.lecturePercent >= 0 && stats.lecturePercent <= 100, 'lecturePercent out of range');
      assert(stats.qaPercent >= 0 && stats.qaPercent <= 100, 'qaPercent out of range');
      assert(stats.taskPercent >= 0 && stats.taskPercent <= 100, 'taskPercent out of range');

      // 11. sm2.getStats must return valid object without throwing when cards are valid objects
      const sm2Stats = CT.sm2.getStats();
      assert(typeof sm2Stats.totalReviewed === 'number' && !isNaN(sm2Stats.totalReviewed), 'sm2Stats invalid');

      fuzzRunCount++;
    }
  }
  logPass(`Exhaustive LocalStorage fuzzing: ${fuzzRunCount} corrupt state combinations recovered without crash`);
} catch (e) {
  logFail('Exhaustive LocalStorage fuzzing crashed', e);
}

// ---------------------------------------------------------------------------
// SUITE 2: State Mutation, JSON Import/Export & SM-2 Edge Fuzzing
// ---------------------------------------------------------------------------
console.log('\n--- Suite 2: State Mutation, JSON Import/Export & SM-2 Edge Fuzzing ---');

try {
  const { sandbox } = createDOMContext();
  const CT = sandbox.window.CourseTracker;

  // Test setLectureCompleted / toggleLecture with diverse types
  [null, undefined, 0, 12, '27', true, false, {}, []].forEach(input => {
    CT.setLectureCompleted(input, true);
    assert(CT.isLectureCompleted(input) === true, `Failed to mark lecture ${input} as completed`);
    CT.toggleLecture(input);
    assert(CT.isLectureCompleted(input) === false, `Failed to toggle lecture ${input}`);
  });
  logPass('setLectureCompleted / toggleLecture handle arbitrary input types cleanly');

  // Test calcSM2 mathematical boundary invariants across 1,000 random trials
  let sm2TrialsPassed = 0;
  for (let i = 0; i < 1000; i++) {
    const randomGrade = (Math.random() * 20) - 5; // -5 to 15
    const randomReps = Math.floor((Math.random() * 20) - 5);
    const randomEf = (Math.random() * 5) - 1;
    const randomInterval = Math.floor((Math.random() * 100) - 10);

    const nextState = CT.calcSM2(randomGrade, randomReps, randomEf, randomInterval);
    assert(nextState.easeFactor >= 1.3, `calcSM2 produced EF < 1.3: ${nextState.easeFactor}`);
    assert(nextState.box >= 1 && nextState.box <= 5, `calcSM2 produced box out of bounds: ${nextState.box}`);
    assert(nextState.interval >= 1, `calcSM2 produced interval < 1: ${nextState.interval}`);
    assert(nextState.repetitions >= 0, `calcSM2 produced reps < 0: ${nextState.repetitions}`);
    sm2TrialsPassed++;
  }
  logPass(`calcSM2 passed 1,000 randomized fuzzing iterations with strict invariant maintenance (EF >= 1.3, Box 1-5)`);

  // Test importProgressJSON with adversarial fuzz payloads
  for (const payload of FUZZ_PAYLOADS) {
    const res = CT.importProgressJSON(payload);
    assert(typeof res === 'boolean', `importProgressJSON returned non-boolean for ${payload}`);
  }
  logPass('importProgressJSON successfully intercepted all malformed payloads without unhandled exceptions');

  // Test valid export/import round-trip
  CT.setLectureCompleted('00', true);
  CT.setLectureCompleted('05', true);
  CT.setQAChecked('qa-00-1', true);
  CT.setTaskChecked('task-00-1', true);
  CT.sm2.recordReview('card-1', 4);

  const exported = CT.exportProgressJSON();
  assert(typeof exported === 'string' && exported.length > 50, 'exportProgressJSON failed');

  const parsedExport = JSON.parse(exported);
  assert(parsedExport.completedLectures.includes('00'), 'Export missing completed lecture 00');
  assert(parsedExport.checkedQAs.includes('qa-00-1'), 'Export missing QA');
  assert(parsedExport.checkedTasks.includes('task-00-1'), 'Export missing Task');

  CT.resetProgress();
  assert(CT.getCompletedLectures().length === 0, 'resetProgress did not clear lectures');
  assert(CT.getCheckedQAs().length === 0, 'resetProgress did not clear QAs');
  assert(CT.getCheckedTasks().length === 0, 'resetProgress did not clear tasks');

  const importSuccess = CT.importProgressJSON(exported);
  assert(importSuccess === true, 'importProgressJSON failed on valid export');
  assert(CT.isLectureCompleted('00') === true, 'Import did not restore lecture 00');
  assert(CT.isLectureCompleted('05') === true, 'Import did not restore lecture 05');
  assert(CT.isQAChecked('qa-00-1') === true, 'Import did not restore QA');
  assert(CT.isTaskChecked('task-00-1') === true, 'Import did not restore Task');
  logPass('Export -> Reset -> Import round-trip verified with 100% fidelity');

} catch (e) {
  logFail('State mutation and SM-2 fuzzing failed', e);
}

// ---------------------------------------------------------------------------
// SUITE 3: Service Worker Offline Simulation for exam.html and js/exam.js
// ---------------------------------------------------------------------------
console.log('\n--- Suite 3: Service Worker Offline Simulation & Precache Parity ---');

function normalizeUrlKey(urlStr) {
  if (!urlStr) return '';
  try {
    const parsed = new URL(urlStr, 'https://ai-course.local');
    return parsed.pathname.replace(/^\//, '');
  } catch (e) {
    return String(urlStr).replace(/^\.\//, '').replace(/^\//, '');
  }
}

class MockCache {
  constructor(name) {
    this.name = name;
    this.store = new Map();
  }
  async match(request) {
    const rawKey = typeof request === 'string' ? request : (request.url || request);
    if (this.store.has(rawKey)) return this.store.get(rawKey).clone();
    const normKey = normalizeUrlKey(rawKey);
    for (const [k, v] of this.store.entries()) {
      if (normalizeUrlKey(k) === normKey) return v.clone();
    }
    return undefined;
  }
  async put(request, response) {
    const key = typeof request === 'string' ? request : (request.url || request);
    this.store.set(key, response.clone());
  }
  async addAll(requests) {
    for (const req of requests) {
      this.store.set(req, new MockResponse(`Mocked content for ${req}`, { status: 200 }));
    }
  }
  async delete(request) {
    const key = typeof request === 'string' ? request : (request.url || request);
    return this.store.delete(key);
  }
}

class MockResponse {
  constructor(body, init = {}) {
    this.body = body;
    this.status = init.status !== undefined ? init.status : 200;
    this.type = init.type || 'basic';
    this.headers = new Map(Object.entries(init.headers || {}));
  }
  clone() {
    return new MockResponse(this.body, {
      status: this.status,
      type: this.type,
      headers: Object.fromEntries(this.headers.entries())
    });
  }
}

class MockRequest {
  constructor(url, init = {}) {
    this.url = typeof url === 'string' ? url : url.url;
    this.method = init.method || 'GET';
    this.mode = init.mode || 'navigate';
    this.headers = {
      get: (k) => (init.headers && init.headers[k.toLowerCase()]) || null
    };
  }
}

function createSWContext() {
  const cacheMap = new Map();
  const eventListeners = {};

  const caches = {
    open: async (name) => {
      if (!cacheMap.has(name)) {
        cacheMap.set(name, new MockCache(name));
      }
      return cacheMap.get(name);
    },
    keys: async () => Array.from(cacheMap.keys()),
    delete: async (name) => cacheMap.delete(name),
    match: async (request) => {
      for (const cache of cacheMap.values()) {
        const res = await cache.match(request);
        if (res) return res;
      }
      return undefined;
    }
  };

  const selfObj = {
    addEventListener: (event, handler) => {
      eventListeners[event] = eventListeners[event] || [];
      eventListeners[event].push(handler);
    },
    skipWaiting: () => Promise.resolve(),
    clients: {
      claim: () => Promise.resolve()
    },
    location: {
      origin: 'https://ai-course.local'
    }
  };

  const sandbox = {
    self: selfObj,
    caches,
    URL,
    console: {
      log: () => {},
      warn: () => {},
      error: () => {},
      debug: () => {}
    }
  };

  vm.createContext(sandbox);
  const swCode = fs.readFileSync(path.join(__dirname, '../sw.js'), 'utf8');
  vm.runInContext(swCode, sandbox);

  return { sandbox, caches, cacheMap, eventListeners, selfObj };
}

(async () => {
  try {
    const { sandbox, caches, cacheMap, eventListeners, selfObj } = createSWContext();

    // 1. Trigger Install Event
    assert(eventListeners['install'] && eventListeners['install'].length > 0, 'SW missing install listener');
    let installPromise;
    const installEvent = {
      waitUntil: (p) => { installPromise = p; }
    };
    eventListeners['install'][0](installEvent);
    await installPromise;

    const cacheV3 = cacheMap.get('ai-course-v3');
    assert(cacheV3, 'Cache ai-course-v3 was not created');
    logPass('Service Worker install: precached assets into ai-course-v3');

    // 2. Verify exam.html and js/exam.js are precached
    const examHtmlCached = await cacheV3.match('./exam.html');
    const examJsCached = await cacheV3.match('./js/exam.js');
    assert(examHtmlCached !== undefined, 'exam.html is MISSING from precache');
    assert(examJsCached !== undefined, 'js/exam.js is MISSING from precache');
    logPass('Service Worker precache contains ./exam.html and ./js/exam.js');

    // 3. Verify all 28 lectures are precached
    for (let i = 0; i <= 27; i++) {
      const pad = String(i).padStart(2, '0');
      const key = Array.from(cacheV3.store.keys()).find(k => k.includes(`lectures/${pad}-`));
      assert(key, `Lecture ${pad} missing from SW precache`);
    }
    logPass('Service Worker precache contains all 28 lectures (00-intro-ml to 27-actor-critic)');

    // 4. Test Activate Event (Purges old caches)
    cacheMap.set('ai-course-v1', new MockCache('ai-course-v1'));
    cacheMap.set('ai-course-v2', new MockCache('ai-course-v2'));
    cacheMap.set('obsolete-cache', new MockCache('obsolete-cache'));

    let activatePromise;
    const activateEvent = {
      waitUntil: (p) => { activatePromise = p; }
    };
    eventListeners['activate'][0](activateEvent);
    await activatePromise;

    assert(!cacheMap.has('ai-course-v1'), 'Failed to delete ai-course-v1');
    assert(!cacheMap.has('ai-course-v2'), 'Failed to delete ai-course-v2');
    assert(!cacheMap.has('obsolete-cache'), 'Failed to delete obsolete-cache');
    assert(cacheMap.has('ai-course-v3'), 'Active cache ai-course-v3 was erroneously deleted');
    logPass('Service Worker activate: purged outdated caches and preserved ai-course-v3');

    // 5. Simulate Offline Fetch Event for exam.html and js/exam.js
    const fetchListener = eventListeners['fetch'][0];
    assert(fetchListener, 'SW missing fetch listener');

    sandbox.fetch = async () => {
      throw new TypeError('Failed to fetch (offline simulation)');
    };

    async function simulateFetch(url, mode = 'navigate', headers = { accept: 'text/html' }) {
      const req = new MockRequest(url, { mode, headers });
      let responsePromise;
      const evt = {
        request: req,
        respondWith: (p) => { responsePromise = p; }
      };
      fetchListener(evt);
      return await responsePromise;
    }

    const offlineExamHtml = await simulateFetch('https://ai-course.local/exam.html');
    assert(offlineExamHtml && offlineExamHtml.status === 200, 'Offline fetch for exam.html failed');
    assert(offlineExamHtml.body.includes('exam.html'), 'Offline exam.html body corrupted');

    const offlineExamJs = await simulateFetch('https://ai-course.local/js/exam.js', 'no-cors', { accept: '*/*' });
    assert(offlineExamJs && offlineExamJs.status === 200, 'Offline fetch for js/exam.js failed');
    assert(offlineExamJs.body.includes('js/exam.js'), 'Offline js/exam.js body corrupted');

    logPass('Offline Simulation: exam.html and js/exam.js successfully served from cache when network fails');

    // 6. Simulate Navigation Fallback for unvisited URL
    const unvisitedOfflineNav = await simulateFetch('https://ai-course.local/unvisited-nonexistent-page.html');
    assert(unvisitedOfflineNav && unvisitedOfflineNav.status === 200, 'Navigation fallback failed');
    assert(unvisitedOfflineNav.body.includes('index.html'), 'Navigation fallback did not return index.html');
    logPass('Offline Navigation Fallback: uncached route falls back to ./index.html gracefully');

  } catch (e) {
    logFail('Service Worker offline simulation failed', e);
  }

  // ---------------------------------------------------------------------------
  // SUITE 4: js/exam.js and js/simulator.js Redundancy & Ast Parity
  // ---------------------------------------------------------------------------
  console.log('\n--- Suite 4: JS Redundancy Consolidation (exam.js vs simulator.js) ---');

  try {
    const examCode = fs.readFileSync(path.join(__dirname, '../js/exam.js'), 'utf8');
    const simCode = fs.readFileSync(path.join(__dirname, '../js/simulator.js'), 'utf8');

    const examNorm = examCode.replace(/\r\n/g, '\n');
    const simNorm = simCode.replace(/\r\n/g, '\n');

    assert.strictEqual(examNorm, simNorm, 'js/exam.js and js/simulator.js must be identical');
    logPass('js/exam.js and js/simulator.js have 100% normalized code identity (0 drift)');

    const sandbox = {
      window: {
        CourseTracker: {
          sm2: { recordReview: () => {} },
          calcSM2: () => ({ easeFactor: 2.5, box: 1, interval: 1, repetitions: 0 })
        }
      },
      document: {
        addEventListener: () => {},
        getElementById: () => null,
        querySelectorAll: () => []
      },
      setInterval: () => {},
      clearInterval: () => {},
      console: { log: () => {}, warn: () => {}, error: () => {} }
    };
    vm.createContext(sandbox);
    vm.runInContext(examCode, sandbox);
    logPass('js/exam.js runs in VM sandbox without runtime syntax or initialization errors');
  } catch (e) {
    logFail('JS Redundancy Consolidation check failed', e);
  }

  console.log('\n======================================================');
  console.log(`Challenger M2 Fuzzing Results: ${passedTests} passed, ${failedTests} failed`);
  console.log('======================================================');

  if (failedTests > 0) {
    process.exit(1);
  }
})();
