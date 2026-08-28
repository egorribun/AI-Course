/**
 * Adversarial Verification Harness for Service Worker (sw.js) and UI/CourseTracker
 * Challenger M1 Empirical Verification Suite
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const SW_PATH = path.join(ROOT, 'sw.js');
const INDEX_PATH = path.join(ROOT, 'index.html');
const TRACKER_PATH = path.join(ROOT, 'js', 'tracker.js');
const EXAM_DATA_PATH = path.join(ROOT, 'js', 'exam_data.js');

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

async function asyncTest(name, fn) {
  try {
    await fn();
    console.log(`  [PASS] ${name}`);
    passCount++;
  } catch (err) {
    console.error(`  [FAIL] ${name}`);
    console.error(`         ${err.message}`);
    failCount++;
  }
}

// -------------------------------------------------------------
// Mock Classes for Service Worker Environment
// -------------------------------------------------------------
class MockHeaders {
  constructor(init = {}) {
    this.map = new Map();
    if (init) {
      for (const [k, v] of Object.entries(init)) {
        this.map.set(k.toLowerCase(), v);
      }
    }
  }
  get(name) {
    return this.map.get(name.toLowerCase()) || null;
  }
  set(name, value) {
    this.map.set(name.toLowerCase(), value);
  }
}

class MockRequest {
  constructor(url, options = {}) {
    this.url = typeof url === 'string' ? url : url.url;
    this.method = options.method || (url.method) || 'GET';
    this.mode = options.mode || (url.mode) || 'cors';
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
  async has(cacheName) {
    return this.caches.has(cacheName);
  }
  async delete(cacheName) {
    return this.caches.delete(cacheName);
  }
  async keys() {
    return Array.from(this.caches.keys());
  }
}

// -------------------------------------------------------------
// Service Worker Harness Setup
// -------------------------------------------------------------
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
      skipWaiting: async () => {
        skipWaitingCalled = true;
      },
      clients: {
        claim: async () => {
          claimCalled = true;
        }
      }
    },
    caches: cacheStorage,
    fetch: mockFetch || (async (req) => new MockResponse('ok', { status: 200, type: 'basic' })),
    Request: MockRequest,
    Response: MockResponse,
    Headers: MockHeaders,
    URL: URL,
    console: {
      log: () => {},
      warn: () => {},
      error: () => {},
      debug: () => {}
    }
  };
  sandbox.self.addEventListener = sandbox.self.addEventListener.bind(sandbox.self);

  const swCode = fs.readFileSync(SW_PATH, 'utf-8');
  vm.createContext(sandbox);
  vm.runInContext(swCode, sandbox);

  return {
    sandbox,
    eventListeners,
    cacheStorage,
    getSkipWaitingCalled: () => skipWaitingCalled,
    getClaimCalled: () => claimCalled
  };
}

// -------------------------------------------------------------
// Main Test Runner
// -------------------------------------------------------------
async function runAllChallengerTests() {
  console.log('=== Starting Challenger M1 Adversarial Verification Suite ===\n');

  console.log('--- Test Suite 1: STATIC_ASSETS Inventory & Filesystem Integrity ---');
  test('All STATIC_ASSETS in sw.js exist on the filesystem', () => {
    const swCode = fs.readFileSync(SW_PATH, 'utf-8');
    const match = swCode.match(/const STATIC_ASSETS = \[\s*([\s\S]*?)\s*\];/);
    assert(match, 'STATIC_ASSETS array definition must exist in sw.js');
    const items = match[1]
      .split(',')
      .map(s => s.trim().replace(/^['"]|['"]$/g, ''))
      .filter(Boolean);

    assert(items.length >= 35, `Expected >= 35 precached assets, found ${items.length}`);

    // Verify 28 lectures
    for (let i = 0; i < 28; i++) {
      const pad = String(i).padStart(2, '0');
      const found = items.some(item => item.includes(`lectures/${pad}-`));
      assert(found, `Lecture ${pad} missing from STATIC_ASSETS`);
    }

    // Verify all files exist
    for (const item of items) {
      let relPath = item.replace(/^\.\//, '');
      if (relPath === '' || relPath === '.') relPath = 'index.html';
      const fullPath = path.join(ROOT, relPath);
      assert(fs.existsSync(fullPath), `Precached file does not exist on disk: ${item} -> ${fullPath}`);
    }
  });

  console.log('\n--- Test Suite 2: Service Worker Lifecycle (Install & Activate) ---');
  await asyncTest('Install event pre-caches all static assets into ai-course-v2 and calls skipWaiting', async () => {
    const { eventListeners, cacheStorage, getSkipWaitingCalled } = createSwSandbox();
    assert(eventListeners.install, 'Install listener must be registered');

    let waitPromise = null;
    eventListeners.install({
      waitUntil(p) {
        waitPromise = p;
      }
    });
    await waitPromise;

    const cache = await cacheStorage.open('ai-course-v2');
    const keys = Array.from(cache.store.keys());
    assert(keys.length >= 35, `Expected >= 35 cached assets in ai-course-v2, found ${keys.length}`);
    assert(getSkipWaitingCalled(), 'skipWaiting() must be called on install');
  });

  await asyncTest('Activate event purges old caches (v1, legacy, unknown) and calls clients.claim()', async () => {
    const { eventListeners, cacheStorage, getClaimCalled } = createSwSandbox();
    assert(eventListeners.activate, 'Activate listener must be registered');

    // Pre-populate old cache stores
    await cacheStorage.open('ai-course-v1');
    await cacheStorage.open('ai-course-v0');
    await cacheStorage.open('legacy-cache-xyz');
    await cacheStorage.open('ai-course-v2');

    let waitPromise = null;
    eventListeners.activate({
      waitUntil(p) {
        waitPromise = p;
      }
    });
    await waitPromise;

    const remainingKeys = await cacheStorage.keys();
    assert.deepStrictEqual(remainingKeys, ['ai-course-v2'], `Old caches must be deleted! Remaining: ${JSON.stringify(remainingKeys)}`);
    assert(getClaimCalled(), 'clients.claim() must be called on activate');
  });

  console.log('\n--- Test Suite 3: Network-First Caching & Offline Fallback ---');
  await asyncTest('Network-First: Online requests fetch fresh from network and update cache', async () => {
    let networkCallCount = 0;
    const mockFetch = async (req) => {
      networkCallCount++;
      return new MockResponse('fresh network html content', { status: 200, type: 'basic' });
    };

    const { eventListeners, cacheStorage } = createSwSandbox(mockFetch);
    const req = new MockRequest('https://example.com/index.html');

    let respondedPromise = null;
    eventListeners.fetch({
      request: req,
      respondWith(p) {
        respondedPromise = p;
      }
    });
    const res = await respondedPromise;

    assert.strictEqual(networkCallCount, 1, 'Network fetch must be called');
    assert.strictEqual(res.body, 'fresh network html content', 'Must return fresh network response');

    // Verify cache updated
    const cache = await cacheStorage.open('ai-course-v2');
    const cached = await cache.match(req);
    assert(cached, 'Cache must be updated with network response');
    assert.strictEqual(cached.body, 'fresh network html content');
  });

  await asyncTest('Network-First: Non-200 responses are returned but NOT written to cache', async () => {
    const mockFetch = async (req) => {
      return new MockResponse('404 Not Found', { status: 404, type: 'basic' });
    };

    const { eventListeners, cacheStorage } = createSwSandbox(mockFetch);
    const req = new MockRequest('https://example.com/nonexistent.html');

    let respondedPromise = null;
    eventListeners.fetch({
      request: req,
      respondWith(p) {
        respondedPromise = p;
      }
    });
    const res = await respondedPromise;
    assert.strictEqual(res.status, 404);

    const cache = await cacheStorage.open('ai-course-v2');
    const cached = await cache.match(req);
    assert.strictEqual(cached, undefined, '404 responses must not be cached');
  });

  await asyncTest('Offline Fallback: Network failure falls back to cached asset', async () => {
    const mockFetch = async (req) => {
      throw new Error('Network error: Offline');
    };

    const { eventListeners, cacheStorage } = createSwSandbox(mockFetch);
    const cache = await cacheStorage.open('ai-course-v2');
    const req = new MockRequest('https://example.com/lectures/01-fcnn.html');
    await cache.put(req, new MockResponse('cached lecture 01', { status: 200, type: 'basic' }));

    let respondedPromise = null;
    eventListeners.fetch({
      request: req,
      respondWith(p) {
        respondedPromise = p;
      }
    });
    const res = await respondedPromise;

    assert(res, 'Must return a response when offline');
    assert.strictEqual(res.body, 'cached lecture 01', 'Must return cached version when network fails');
  });

  await asyncTest('Offline Navigation Fallback: Navigation request for uncached page falls back to index.html', async () => {
    const mockFetch = async (req) => {
      throw new Error('Network error: Offline');
    };

    const { eventListeners, cacheStorage } = createSwSandbox(mockFetch);
    const cache = await cacheStorage.open('ai-course-v2');
    // Put index.html in cache under './index.html'
    await cache.put('./index.html', new MockResponse('fallback index.html content', { status: 200, type: 'basic' }));

    const req = new MockRequest('https://example.com/some/deep/page.html', {
      mode: 'navigate',
      headers: { accept: 'text/html,application/xhtml+xml' }
    });

    let respondedPromise = null;
    eventListeners.fetch({
      request: req,
      respondWith(p) {
        respondedPromise = p;
      }
    });
    const res = await respondedPromise;

    assert(res, 'Must return fallback for navigation request');
    assert.strictEqual(res.body, 'fallback index.html content');
  });

  await asyncTest('Fetch Filter: Non-GET requests and non-HTTP protocols are not intercepted', async () => {
    const { eventListeners } = createSwSandbox();

    // POST request
    let intercepted = false;
    eventListeners.fetch({
      request: new MockRequest('https://example.com/api', { method: 'POST' }),
      respondWith() {
        intercepted = true;
      }
    });
    assert(!intercepted, 'POST requests must not be intercepted');

    // chrome-extension: protocol
    intercepted = false;
    eventListeners.fetch({
      request: new MockRequest('chrome-extension://abcdefg/script.js', { method: 'GET' }),
      respondWith() {
        intercepted = true;
      }
    });
    assert(!intercepted, 'chrome-extension requests must not be intercepted');
  });

  await asyncTest('CDN SWR Strategy: External CDN requests use Stale-While-Revalidate', async () => {
    let networkFetched = false;
    const mockFetch = async (req) => {
      networkFetched = true;
      return new MockResponse('fresh cdn mathjax', { status: 200, type: 'cors' });
    };

    const { eventListeners, cacheStorage } = createSwSandbox(mockFetch);
    const cache = await cacheStorage.open('ai-course-v2');
    const req = new MockRequest('https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js');
    await cache.put(req, new MockResponse('stale cdn mathjax', { status: 200 }));

    let respondedPromise = null;
    eventListeners.fetch({
      request: req,
      respondWith(p) {
        respondedPromise = p;
      }
    });
    const res = await respondedPromise;

    assert.strictEqual(res.body, 'stale cdn mathjax', 'SWR must return cached/stale response immediately');
  });

  console.log('\n--- Test Suite 4: index.html DOM & CourseTracker Integration ---');
  test('index.html #global-progress-hub does NOT contain export button', () => {
    const indexHtml = fs.readFileSync(INDEX_PATH, 'utf-8');
    const hubStart = indexHtml.indexOf('id="global-progress-hub"');
    assert(hubStart !== -1, '#global-progress-hub must exist');
    const hubEnd = indexHtml.indexOf('id="exam-simulator-container"', hubStart);
    const hubHtml = indexHtml.substring(hubStart, hubEnd !== -1 ? hubEnd : hubStart + 1500);

    assert(!hubHtml.includes('💾 Экспорт'), '💾 Экспорт button must be completely removed from progress hub');
    assert(!hubHtml.includes('exportProgressJSON'), 'exportProgressJSON click handler must not be in progress hub');
    assert(hubHtml.includes('🔄 Сброс'), '🔄 Сброс button must be present in progress hub');
    assert(hubHtml.includes('CourseTracker.resetProgress()'), 'resetProgress handler must be attached to reset button');
    assert(hubHtml.includes('id="global-progress-fill"'), 'global-progress-fill must be present');
    assert(hubHtml.includes('id="stat-lecs-val"'), 'stat-lecs-val must be present');
    assert(hubHtml.includes('id="stat-qas-val"'), 'stat-qas-val must be present');
    assert(hubHtml.includes('id="stat-tasks-val"'), 'stat-tasks-val must be present');
  });

  test('CourseTracker methods: exportProgressJSON, importProgressJSON, resetProgress, and SM-2 operate cleanly', () => {
    const trackerCode = fs.readFileSync(TRACKER_PATH, 'utf-8');
    const localStorageStore = new Map();
    const mockLocalStorage = {
      getItem: (k) => localStorageStore.get(k) || null,
      setItem: (k, v) => localStorageStore.set(k, String(v)),
      removeItem: (k) => localStorageStore.delete(k),
      clear: () => localStorageStore.clear()
    };

    const sandbox = {
      window: {
        dispatchEvent: () => {},
        addEventListener: () => {},
        location: { pathname: '/', reload: () => {} }
      },
      document: {
        addEventListener: () => {},
        querySelectorAll: () => [],
        documentElement: { setAttribute: () => {} }
      },
      localStorage: mockLocalStorage,
      CustomEvent: class {},
      console: { warn: () => {}, error: () => {}, log: () => {} },
      navigator: { serviceWorker: { register: () => Promise.resolve() } }
    };
    sandbox.window.CourseTracker = undefined;

    vm.createContext(sandbox);
    vm.runInContext(trackerCode, sandbox);

    const CourseTracker = sandbox.CourseTracker || sandbox.window.CourseTracker;
    assert(CourseTracker, 'CourseTracker must be exported');

    // Test setting progress
    CourseTracker.setLectureCompleted('00-intro-ml', true);
    CourseTracker.setLectureCompleted('01-fcnn', true);
    CourseTracker.setQAChecked('qa-00-1', true);
    CourseTracker.setTaskChecked('task-00-1', true);

    const stats = CourseTracker.getOverallStats();
    assert.strictEqual(stats.completedLectures, 2);
    assert.strictEqual(stats.checkedQAs, 1);
    assert.strictEqual(stats.checkedTasks, 1);
    assert(stats.overallPercent > 0, 'overallPercent should be > 0');

    // Test export JSON
    const exportedStr = CourseTracker.exportProgressJSON();
    assert(typeof exportedStr === 'string');
    const parsed = JSON.parse(exportedStr);
    assert(Array.isArray(parsed.completedLectures));
    assert(parsed.completedLectures.includes('00-intro-ml'));
    assert(parsed.completedLectures.includes('01-fcnn'));

    // Test Reset
    CourseTracker.resetProgress();
    const resetStats = CourseTracker.getOverallStats();
    assert.strictEqual(resetStats.completedLectures, 0);
    assert.strictEqual(resetStats.checkedQAs, 0);
    assert.strictEqual(resetStats.checkedTasks, 0);

    // Test Import roundtrip
    const importSuccess = CourseTracker.importProgressJSON(exportedStr);
    assert.strictEqual(importSuccess, true);
    const restoredStats = CourseTracker.getOverallStats();
    assert.strictEqual(restoredStats.completedLectures, 2);

    // Test Import with malformed / adversarial input (should fail gracefully and return false)
    assert.strictEqual(CourseTracker.importProgressJSON('invalid { json'), false);
    assert.strictEqual(CourseTracker.importProgressJSON('null'), false);
    assert.strictEqual(CourseTracker.importProgressJSON('12345'), true); // non-object without properties won't crash
  });

  console.log('\n======================================================');
  console.log(`Challenger M1 Results: ${passCount} passed, ${failCount} failed`);
  console.log('======================================================\n');

  if (failCount > 0) {
    process.exit(1);
  }
}

runAllChallengerTests().catch((err) => {
  console.error('Unhandled test suite error:', err);
  process.exit(1);
});
