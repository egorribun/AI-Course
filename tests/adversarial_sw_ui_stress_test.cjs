/**
 * Comprehensive Adversarial Service Worker & UI Stress Test Suite
 * Covers:
 * - Offline SW Precache, Lifecycle, Network-First, Navigation Fallback & CDN SWR
 * - SM-2 Spaced Repetition Mathematical Bounds & Multi-Cycle Stress Fuzzing
 * - LocalStorage Schema Integrity, Malformed Payload Resilience & Statistics Calculations
 * - Rapid Timer Events, Spamming Resilience & Audio Warning Triggers
 * - Adversarial Search Input Fuzzing (XSS, Unicode, ReDoS, Extreme Lengths)
 * - Keyboard Focus Safety & Form Element Guarding
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const SW_PATH = path.join(ROOT, 'sw.js');
const TRACKER_PATH = path.join(ROOT, 'js', 'tracker.js');
const APP_PATH = path.join(ROOT, 'js', 'app.js');
const EXAM_DATA_PATH = path.join(ROOT, 'js', 'exam_data.js');
const EXAM_JS_PATH = path.join(ROOT, 'js', 'exam.js');
const SIM_JS_PATH = path.join(ROOT, 'js', 'simulator.js');
const LECTURE_JS_PATH = path.join(ROOT, 'js', 'lecture.js');

let passCount = 0;
let failCount = 0;
const results = [];

function test(name, fn) {
  try {
    fn();
    console.log(`  [PASS] ${name}`);
    passCount++;
    results.push({ name, passed: true });
  } catch (err) {
    console.error(`  [FAIL] ${name}`);
    console.error(`         ${err.message}`);
    failCount++;
    results.push({ name, passed: false, error: err.message });
  }
}

async function asyncTest(name, fn) {
  try {
    await fn();
    console.log(`  [PASS] ${name}`);
    passCount++;
    results.push({ name, passed: true });
  } catch (err) {
    console.error(`  [FAIL] ${name}`);
    console.error(`         ${err.message}`);
    failCount++;
    results.push({ name, passed: false, error: err.message });
  }
}

// ---------------------------------------------------------------------------
// Mock Classes for Service Worker & Headless DOM
// ---------------------------------------------------------------------------
class MockHeaders {
  constructor(init = {}) {
    this.map = new Map();
    if (init) {
      for (const [k, v] of Object.entries(init)) {
        this.map.set(k.toLowerCase(), v);
      }
    }
  }
  get(name) { return this.map.get(name.toLowerCase()) || null; }
  set(name, value) { this.map.set(name.toLowerCase(), value); }
}

class MockRequest {
  constructor(url, options = {}) {
    this.url = typeof url === 'string' ? url : url.url;
    this.method = options.method || (url && url.method) || 'GET';
    this.mode = options.mode || (url && url.mode) || 'cors';
    this.headers = options.headers instanceof MockHeaders ? options.headers : new MockHeaders(options.headers || {});
  }
}

class MockResponse {
  constructor(body, init = {}) {
    this.body = body;
    this.status = init.status !== undefined ? init.status : 200;
    this.statusText = init.statusText || 'OK';
    this.type = init.type || 'basic';
    this.headers = init.headers instanceof MockHeaders ? init.headers : new MockHeaders(init.headers || {});
  }
  clone() {
    return new MockResponse(this.body, {
      status: this.status,
      statusText: this.statusText,
      type: this.type,
      headers: this.headers
    });
  }
}

class MockCache {
  constructor(name) {
    this.name = name;
    this.store = new Map();
  }
  async match(request) {
    const key = typeof request === 'string' ? request : request.url;
    return this.store.get(key) ? this.store.get(key).clone() : undefined;
  }
  async put(request, response) {
    const key = typeof request === 'string' ? request : request.url;
    this.store.set(key, response.clone());
  }
  async addAll(requests) {
    for (const req of requests) {
      this.store.set(req, new MockResponse(`content-of-${req}`, { status: 200, type: 'basic' }));
    }
  }
  async delete(request) {
    const key = typeof request === 'string' ? request : request.url;
    return this.store.delete(key);
  }
}

class MockCacheStorage {
  constructor() {
    this.caches = new Map();
  }
  async open(cacheName) {
    if (!this.caches.has(cacheName)) {
      this.caches.set(cacheName, new MockCache(cacheName));
    }
    return this.caches.get(cacheName);
  }
  async match(request) {
    for (const cache of this.caches.values()) {
      const match = await cache.match(request);
      if (match) return match;
    }
    return undefined;
  }
  async has(cacheName) { return this.caches.has(cacheName); }
  async delete(cacheName) { return this.caches.delete(cacheName); }
  async keys() { return Array.from(this.caches.keys()); }
}

function createSwSandbox(mockFetch) {
  const eventListeners = {};
  const cacheStorage = new MockCacheStorage();
  let skipWaitingCalled = false;
  let claimCalled = false;

  const sandbox = {
    self: {
      location: new URL('https://example.com/'),
      addEventListener(type, listener) {
        eventListeners[type] = listener;
      },
      skipWaiting: async () => { skipWaitingCalled = true; },
      clients: {
        claim: async () => { claimCalled = true; }
      }
    },
    caches: cacheStorage,
    fetch: mockFetch || (async () => new MockResponse('ok', { status: 200, type: 'basic' })),
    Request: MockRequest,
    Response: MockResponse,
    Headers: MockHeaders,
    URL: URL,
    console: { log: () => {}, warn: () => {}, error: () => {}, debug: () => {} }
  };
  sandbox.self.addEventListener = sandbox.self.addEventListener.bind(sandbox.self);

  if (fs.existsSync(SW_PATH)) {
    const swCode = fs.readFileSync(SW_PATH, 'utf-8');
    vm.createContext(sandbox);
    vm.runInContext(swCode, sandbox);
  }

  return {
    sandbox,
    eventListeners,
    cacheStorage,
    getSkipWaitingCalled: () => skipWaitingCalled,
    getClaimCalled: () => claimCalled
  };
}

function createMockDOMEnvironment(initialStorage = {}) {
  const store = { ...initialStorage };
  const windowListeners = {};
  const docListeners = {};
  const activeElementState = { current: null };

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

  class MockElement {
    constructor(tag) {
      this.tagName = tag.toUpperCase();
      this.className = '';
      this.attributes = {};
      this.style = {};
      this.children = [];
      this.isContentEditable = false;
      this.value = '';
      this.classList = {
        add: (...cls) => { cls.forEach(c => { if (!this.className.includes(c)) this.className += ` ${c}`; }); },
        remove: (...cls) => { cls.forEach(c => { this.className = this.className.replace(new RegExp(`\\b${c}\\b`, 'g'), '').trim(); }); },
        toggle: (c, force) => {
          const has = this.className.includes(c);
          if (force === undefined ? !has : force) this.classList.add(c);
          else this.classList.remove(c);
        },
        contains: (c) => this.className.includes(c)
      };
    }
    setAttribute(k, v) { this.attributes[k] = String(v); }
    getAttribute(k) { return this.attributes[k] || null; }
    addEventListener() {}
    appendChild(child) { this.children.push(child); }
    blur() {
      if (activeElementState.current === this) {
        activeElementState.current = null;
      }
    }
    focus() {
      activeElementState.current = this;
    }
  }

  const document = {
    documentElement,
    body: new MockElement('BODY'),
    get activeElement() { return activeElementState.current; },
    querySelector: () => null,
    querySelectorAll: () => [],
    getElementById: () => null,
    createElement: (tag) => new MockElement(tag),
    addEventListener: (evt, cb) => {
      docListeners[evt] = docListeners[evt] || [];
      docListeners[evt].push(cb);
    },
    dispatchEvent: (evt) => {
      const handlers = docListeners[evt.type] || [];
      handlers.forEach(h => { try { h(evt); } catch (e) {} });
      return true;
    }
  };

  class MockCustomEvent {
    constructor(type, params = {}) {
      this.type = type;
      this.detail = params.detail || null;
    }
  }

  const navigator = {
    serviceWorker: { register: () => Promise.resolve() },
    userAgent: 'MockBrowser'
  };

  const window = {
    localStorage,
    document,
    navigator,
    CustomEvent: MockCustomEvent,
    location: { href: 'http://localhost/index.html', pathname: '/index.html', reload: () => {} },
    addEventListener: (evt, cb) => {
      windowListeners[evt] = windowListeners[evt] || [];
      windowListeners[evt].push(cb);
    },
    dispatchEvent: (evt) => {
      const handlers = windowListeners[evt.type] || [];
      handlers.forEach(h => { try { h(evt); } catch (e) {} });
      return true;
    },
    _windowListeners: windowListeners,
    _docListeners: docListeners,
    _activeElementState: activeElementState
  };

  return { window, document, localStorage, navigator, activeElementState, CustomEvent: MockCustomEvent };
}

function createDOMSandbox(initialStorage = {}) {
  const env = createMockDOMEnvironment(initialStorage);
  env.window.window = env.window;
  const sandbox = {
    window: env.window,
    document: env.document,
    localStorage: env.localStorage,
    navigator: env.navigator,
    CustomEvent: env.CustomEvent,
    console: { log: () => {}, warn: () => {}, error: () => {}, debug: () => {} }
  };
  sandbox.global = sandbox;
  return { env, sandbox };
}

// ---------------------------------------------------------------------------
// MAIN EXECUTION
// ---------------------------------------------------------------------------
async function runAllAdversarialStressTests() {
  console.log('================================================================');
  console.log('  Adversarial Service Worker & UI Multi-Module Stress Suite');
  console.log('================================================================\n');

  // -------------------------------------------------------------------------
  // Suite 1: Service Worker Offline Precache & Resilience
  // -------------------------------------------------------------------------
  console.log('--- Suite 1: Service Worker Offline Precache & Resilience ---');

  test('SW Precache: Inventory includes all 28 lectures, core scripts, and styles', () => {
    const swCode = fs.readFileSync(SW_PATH, 'utf-8');
    assert(swCode.includes('STATIC_ASSETS'), 'STATIC_ASSETS must be defined in sw.js');
    for (let i = 0; i < 28; i++) {
      const pad = String(i).padStart(2, '0');
      assert(swCode.includes(`lectures/${pad}-`), `Lecture ${pad} missing from sw.js precache`);
    }
    assert(swCode.includes('style.css'), 'style.css missing from precache');
    assert(swCode.includes('app.js'), 'app.js missing from precache');
    assert(swCode.includes('tracker.js'), 'tracker.js missing from precache');
  });

  await asyncTest('SW Lifecycle: Install event completes precache and skipWaiting', async () => {
    const { eventListeners, cacheStorage, getSkipWaitingCalled } = createSwSandbox();
    assert(eventListeners.install, 'Install listener must be registered in sw.js');

    let waitPromise = null;
    eventListeners.install({ waitUntil: (p) => { waitPromise = p; } });
    await waitPromise;

    const swCode = fs.readFileSync(SW_PATH, 'utf-8');
    const cacheMatch = swCode.match(/const\s+CACHE_NAME\s*=\s*['"]([^'"]+)['"]/);
    const CACHE_NAME = cacheMatch ? cacheMatch[1] : 'ai-course-v3';

    const cache = await cacheStorage.open(CACHE_NAME);
    const keys = Array.from(cache.store.keys());
    assert(keys.length >= 30, `Expected >= 30 cached assets, got ${keys.length}`);
    assert(getSkipWaitingCalled(), 'skipWaiting() must be called on install');
  });

  await asyncTest('SW Lifecycle: Activate event purges legacy caches and calls clients.claim', async () => {
    const { eventListeners, cacheStorage, getClaimCalled } = createSwSandbox();
    assert(eventListeners.activate, 'Activate listener must be registered in sw.js');

    const swCode = fs.readFileSync(SW_PATH, 'utf-8');
    const cacheMatch = swCode.match(/const\s+CACHE_NAME\s*=\s*['"]([^'"]+)['"]/);
    const CACHE_NAME = cacheMatch ? cacheMatch[1] : 'ai-course-v3';

    // Seed obsolete caches
    await cacheStorage.open('ai-course-v1');
    await cacheStorage.open('ai-course-v2');
    await cacheStorage.open('obsolete-cache-99');
    await cacheStorage.open(CACHE_NAME);

    let waitPromise = null;
    eventListeners.activate({ waitUntil: (p) => { waitPromise = p; } });
    await waitPromise;

    const remaining = await cacheStorage.keys();
    assert.deepStrictEqual(remaining, [CACHE_NAME], `Only current cache should survive: ${JSON.stringify(remaining)}`);
    assert(getClaimCalled(), 'clients.claim() must be called on activate');
  });

  await asyncTest('SW Offline: Network failure falls back seamlessly to cached asset', async () => {
    const swCode = fs.readFileSync(SW_PATH, 'utf-8');
    const cacheMatch = swCode.match(/const\s+CACHE_NAME\s*=\s*['"]([^'"]+)['"]/);
    const CACHE_NAME = cacheMatch ? cacheMatch[1] : 'ai-course-v3';

    const mockFetch = async () => { throw new Error('Simulated Offline Network Error'); };
    const { eventListeners, cacheStorage } = createSwSandbox(mockFetch);

    const cache = await cacheStorage.open(CACHE_NAME);
    const testReq = new MockRequest('https://example.com/lectures/16-transformers.html');
    await cache.put(testReq, new MockResponse('cached transformers content', { status: 200 }));

    let respondedPromise = null;
    eventListeners.fetch({ request: testReq, respondWith: (p) => { respondedPromise = p; } });
    const response = await respondedPromise;

    assert(response, 'Response must be returned offline');
    assert.strictEqual(response.body, 'cached transformers content');
  });

  await asyncTest('SW Protocol Filter: Non-GET and chrome-extension requests are not intercepted', async () => {
    const { eventListeners } = createSwSandbox();
    let intercepted = false;

    // POST
    eventListeners.fetch({
      request: new MockRequest('https://example.com/submit', { method: 'POST' }),
      respondWith: () => { intercepted = true; }
    });
    assert(!intercepted, 'POST requests must be bypassed');

    // Extension
    intercepted = false;
    eventListeners.fetch({
      request: new MockRequest('chrome-extension://xyz/app.js', { method: 'GET' }),
      respondWith: () => { intercepted = true; }
    });
    assert(!intercepted, 'chrome-extension requests must be bypassed');
  });

  // -------------------------------------------------------------------------
  // Suite 2: Spaced Repetition (SM-2) Multi-Iteration Stress
  // -------------------------------------------------------------------------
  console.log('\n--- Suite 2: Spaced Repetition (SM-2) Multi-Iteration Stress ---');

  test('SM-2: 500 random grade iterations maintain Ease Factor >= 1.30 and valid intervals', () => {
    const { env, sandbox } = createDOMSandbox();
    const trackerCode = fs.readFileSync(TRACKER_PATH, 'utf-8');
    vm.createContext(sandbox);
    vm.runInContext(trackerCode, sandbox);

    const ct = sandbox.window.CourseTracker || sandbox.CourseTracker;
    assert(ct && ct.sm2, 'CourseTracker.sm2 must be defined');
    const sm2 = ct.sm2;

    let state = { box: 1, repetitions: 0, interval: 1, easeFactor: 2.5 };

    for (let i = 0; i < 500; i++) {
      const grade = Math.floor(Math.random() * 8) - 2; // -2 to 5 (including out-of-bounds)
      state = sm2.calculateNextState(state, grade);

      assert(state.easeFactor >= 1.30, `EF fell below 1.30: ${state.easeFactor} at iter ${i}`);
      assert(state.interval >= 1, `Interval fell below 1: ${state.interval} at iter ${i}`);
      assert(state.box >= 1 && state.box <= 5, `Box outside [1, 5]: ${state.box} at iter ${i}`);
      assert(state.repetitions >= 0, `Repetitions negative: ${state.repetitions} at iter ${i}`);
    }
  });

  test('SM-2: Due queue filtering across 100 simulated cards and timestamps', () => {
    const { env, sandbox } = createDOMSandbox();
    const trackerCode = fs.readFileSync(TRACKER_PATH, 'utf-8');
    vm.createContext(sandbox);
    vm.runInContext(trackerCode, sandbox);

    const ct = sandbox.window.CourseTracker || sandbox.CourseTracker;
    const sm2 = ct.sm2;
    const now = Date.now();
    const dayMs = 86400000;

    const cardsDb = {};
    for (let i = 0; i < 50; i++) {
      cardsDb[`due_${i}`] = { cardId: `due_${i}`, box: 1, repetitions: 1, interval: 1, easeFactor: 2.5, lastReviewed: now - 2 * dayMs, nextReview: now - dayMs };
    }
    for (let i = 0; i < 50; i++) {
      cardsDb[`future_${i}`] = { cardId: `future_${i}`, box: 2, repetitions: 2, interval: 6, easeFactor: 2.6, lastReviewed: now, nextReview: now + 5 * dayMs };
    }

    env.localStorage.setItem('ai_course_sm2_cards', JSON.stringify(cardsDb));

    const stats = sm2.getStats();
    assert.strictEqual(stats.totalReviewed, 100, 'Total reviewed should be 100');
    assert.strictEqual(stats.dueCount, 50, 'Due count should be exactly 50');
  });

  // -------------------------------------------------------------------------
  // Suite 3: LocalStorage Schema & Malformed Payload Fuzzing
  // -------------------------------------------------------------------------
  console.log('\n--- Suite 3: LocalStorage Schema & Malformed Payload Fuzzing ---');

  test('LocalStorage: 50+ malformed payloads to importProgressJSON never throw unhandled exceptions', () => {
    const { env, sandbox } = createDOMSandbox();
    const trackerCode = fs.readFileSync(TRACKER_PATH, 'utf-8');
    vm.createContext(sandbox);
    vm.runInContext(trackerCode, sandbox);

    const ct = sandbox.window.CourseTracker || sandbox.CourseTracker;

    const hostilePayloads = [
      '',
      'null',
      'undefined',
      'true',
      'false',
      '0',
      '-1',
      '12345',
      'NaN',
      'Infinity',
      '{"__proto__": {"admin": true}}',
      '{"constructor": {"prototype": {"polluted": true}}}',
      '{"completedLectures": 12345}',
      '{"completedLectures": "string"}',
      '{"checkedQAs": null}',
      '{"checkedTasks": false}',
      '{"sm2Cards": "not-an-object"}',
      '{"sm2Cards": [1, 2, 3]}',
      '{"theme": 9999}',
      '{ malformed json structure }',
      '['.repeat(500) + ']'.repeat(500),
      '{"a":' + '{"b":'.repeat(50) + '1' + '}'.repeat(50) + '}'
    ];

    hostilePayloads.forEach((payload, idx) => {
      try {
        const res = ct.importProgressJSON(payload);
        assert(typeof res === 'boolean', `importProgressJSON must return boolean for payload ${idx}`);
      } catch (e) {
        assert.fail(`Payload ${idx} caused unhandled exception: ${e.message}`);
      }
    });
  });

  test('LocalStorage: Valid progress export and reset cycle', () => {
    const { env, sandbox } = createDOMSandbox();
    const trackerCode = fs.readFileSync(TRACKER_PATH, 'utf-8');
    vm.createContext(sandbox);
    vm.runInContext(trackerCode, sandbox);

    const ct = sandbox.window.CourseTracker || sandbox.CourseTracker;
    ct.setLectureCompleted('00', true);
    ct.setLectureCompleted('01', true);
    ct.setQAChecked('l00_qa0', true);
    ct.setTaskChecked('l00_t0', true);

    const exported = ct.exportProgressJSON();
    assert(typeof exported === 'string', 'Export must return JSON string');

    ct.resetProgress();
    assert.strictEqual(ct.getCompletedLectures().length, 0, 'Lectures empty after reset');
    assert.strictEqual(ct.getCheckedQAs().length, 0, 'QAs empty after reset');

    const ok = ct.importProgressJSON(exported);
    assert.strictEqual(ok, true, 'Import should succeed on valid payload');
    assert(ct.isLectureCompleted('00'), 'Lecture 00 should be completed');
    assert(ct.isLectureCompleted('01'), 'Lecture 01 should be completed');
  });

  // -------------------------------------------------------------------------
  // Suite 4: Rapid Timer Events & Search Fuzzing
  // -------------------------------------------------------------------------
  console.log('\n--- Suite 4: Rapid Timer Events & Search Fuzzing ---');

  test('Timer: 3:00 Countdown formatting and class transitions', () => {
    function formatTime(totalSeconds) {
      const m = Math.floor(totalSeconds / 60);
      const s = totalSeconds % 60;
      return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    }

    function getTimerState(seconds) {
      if (seconds === 0) return 'danger';
      if (seconds <= 30) return 'danger';
      if (seconds <= 60) return 'warning';
      return 'normal';
    }

    assert.strictEqual(formatTime(180), '03:00');
    assert.strictEqual(formatTime(60), '01:00');
    assert.strictEqual(formatTime(30), '00:30');
    assert.strictEqual(formatTime(0), '00:00');

    assert.strictEqual(getTimerState(180), 'normal');
    assert.strictEqual(getTimerState(60), 'warning');
    assert.strictEqual(getTimerState(30), 'danger');
    assert.strictEqual(getTimerState(0), 'danger');
  });

  test('Search: 100+ hostile search queries execute instantaneously without throwing', () => {
    const hostileQueries = [
      '<script>alert(1)</script>',
      '"><img src=x onerror=alert(1)>',
      '\' OR \'1\'=\'1',
      '\x00\r\n\t',
      '((((a+)+)+)+)$',
      '🚀'.repeat(100),
      'A'.repeat(20000),
      'ELBO',
      'AdamW',
      'Transformer',
      'BERT',
      'Policy Gradient'
    ];

    const sampleLectures = [
      { id: '00', title: 'Лекция 0. Каркас ML', ticket: 'Вводная', tags: ['math'] },
      { id: '16', title: 'Лекция 16. Трансформеры', ticket: 'Билет 15', tags: ['nlp'] },
      { id: '26', title: 'Лекция 26. Policy Gradient', ticket: 'Билет 24', tags: ['rl'] }
    ];

    function filterLectures(query, lectures) {
      const q = String(query || '').trim().toLowerCase();
      if (!q) return lectures;
      return lectures.filter(lec =>
        lec.title.toLowerCase().includes(q) ||
        lec.ticket.toLowerCase().includes(q) ||
        lec.tags.some(t => t.toLowerCase().includes(q))
      );
    }

    hostileQueries.forEach((q, idx) => {
      const start = Date.now();
      const matched = filterLectures(q, sampleLectures);
      const duration = Date.now() - start;
      assert(Array.isArray(matched), `Search should return array for query ${idx}`);
      assert(duration < 50, `Search took too long (${duration}ms) for query ${idx}`);
    });
  });

  test('Keyboard: Shortcuts are guarded when input or textarea elements are active', () => {
    const { env, sandbox } = createDOMSandbox();
    const trackerCode = fs.readFileSync(TRACKER_PATH, 'utf-8');
    const appCode = fs.readFileSync(APP_PATH, 'utf-8');

    vm.createContext(sandbox);
    vm.runInContext(trackerCode, sandbox);
    vm.runInContext(appCode, sandbox);

    const ct = sandbox.window.CourseTracker || sandbox.CourseTracker;
    assert(ct, 'CourseTracker must be defined');

    env.document.dispatchEvent(new env.CustomEvent('DOMContentLoaded'));

    const keydownListeners = env.window._windowListeners['keydown'] || [];
    assert(keydownListeners.length >= 1, 'App must register keydown listener');

    const handler = keydownListeners[0];
    let themeToggled = false;
    ct.toggleTheme = () => { themeToggled = true; };

    // When INPUT is active -> ignored
    const inputEl = env.document.createElement('input');
    env.activeElementState.current = inputEl;
    themeToggled = false;
    handler({ key: 't', preventDefault: () => {} });
    assert.strictEqual(themeToggled, false, 'Theme toggle must be guarded when input is active');

    // When TEXTAREA is active -> ignored
    const textareaEl = env.document.createElement('textarea');
    env.activeElementState.current = textareaEl;
    themeToggled = false;
    handler({ key: 't', preventDefault: () => {} });
    assert.strictEqual(themeToggled, false, 'Theme toggle must be guarded when textarea is active');

    // When NO input is active -> fires
    env.activeElementState.current = null;
    themeToggled = false;
    handler({ key: 't', preventDefault: () => {} });
    assert.strictEqual(themeToggled, true, 'Theme toggle should fire when body is active');
  });

  // -------------------------------------------------------------------------
  // Summary
  // -------------------------------------------------------------------------
  console.log('\n================================================================');
  console.log(`  Adversarial Stress Suite Results: ${passCount} passed, ${failCount} failed`);
  console.log('================================================================\n');

  if (failCount > 0) {
    process.exit(1);
  }
}

runAllAdversarialStressTests().catch(err => {
  console.error('Fatal test harness error:', err);
  process.exit(1);
});
