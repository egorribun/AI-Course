
const fs = require('fs');
const path = require('path');
const assert = require('assert');

const ROOT_DIR = path.resolve(__dirname, '..');
const SW_PATH = path.join(ROOT_DIR, 'sw.js');
const INDEX_PATH = path.join(ROOT_DIR, 'index.html');
const TRACKER_PATH = path.join(ROOT_DIR, 'js', 'tracker.js');

let passCount = 0;
let failCount = 0;

function runSyncTest(name, fn) {
  try {
    fn();
    console.log('  [PASS] ' + name);
    passCount++;
  } catch (e) {
    console.error('  [FAIL] ' + name + ': ' + e.message);
    failCount++;
    throw e;
  }
}

async function runAsyncTest(name, fn) {
  try {
    await fn();
    console.log('  [PASS] ' + name);
    passCount++;
  } catch (e) {
    console.error('  [FAIL] ' + name + ': ' + e.message);
    failCount++;
    throw e;
  }
}

// Mock Response
class MockResponse {
  constructor(body, opts = {}) {
    this.body = body;
    this.status = opts.status !== undefined ? opts.status : 200;
    this.statusText = opts.statusText || 'OK';
    this.type = opts.type || 'basic';
    this.headers = new Map(Object.entries(opts.headers || {}));
    this.cloned = false;
  }

  clone() {
    this.cloned = true;
    return new MockResponse(this.body, {
      status: this.status,
      statusText: this.statusText,
      type: this.type,
      headers: Object.fromEntries(this.headers.entries())
    });
  }

  async text() {
    return String(this.body);
  }
}

// Mock Request
class MockRequest {
  constructor(url, opts = {}) {
    this.url = url;
    this.method = opts.method || 'GET';
    this.mode = opts.mode || 'cors';
    this.headers = new Map(Object.entries(opts.headers || {}));
  }

  get(h) {
    return this.headers.get(h) || null;
  }
}

// Mock Cache
class MockCache {
  constructor(name) {
    this.name = name;
    this.entries = new Map();
  }

  async addAll(items) {
    for (const item of items) {
      this.entries.set(item, new MockResponse('asset: ' + item));
    }
  }

  async put(req, res) {
    const key = typeof req === 'string' ? req : req.url;
    this.entries.set(key, res);
  }

  async match(req) {
    const key = typeof req === 'string' ? req : req.url;
    if (this.entries.has(key)) return this.entries.get(key);
    for (const [k, v] of this.entries.entries()) {
      if (k === key || key.endsWith(k.replace(/^\.\//, '')) || k.endsWith(key.replace(/^\.\//, ''))) {
        return v;
      }
    }
    return undefined;
  }
}

// Mock CacheStorage
class MockCacheStorage {
  constructor() {
    this.map = new Map();
  }

  async open(name) {
    if (!this.map.has(name)) {
      this.map.set(name, new MockCache(name));
    }
    return this.map.get(name);
  }

  async keys() {
    return Array.from(this.map.keys());
  }

  async delete(name) {
    return this.map.delete(name);
  }

  async match(req) {
    for (const c of this.map.values()) {
      const m = await c.match(req);
      if (m) return m;
    }
    return undefined;
  }
}

function createSWContext() {
  const listeners = {};
  const cacheStore = new MockCacheStorage();
  let skipWaitingCalls = 0;
  let clientsClaimCalls = 0;

  const mockSelf = {
    location: { origin: 'https://user.github.io' },
    clients: {
      claim: async () => { clientsClaimCalls++; return true; }
    },
    skipWaiting: async () => { skipWaitingCalls++; return true; },
    addEventListener: (ev, h) => { listeners[ev] = h; },
    caches: cacheStore
  };

  const swCode = fs.readFileSync(SW_PATH, 'utf-8');
  const runFn = new Function('self', 'caches', 'fetch', 'URL', swCode);

  return {
    mockSelf,
    cacheStore,
    listeners,
    getStats: () => ({ skipWaitingCalls, clientsClaimCalls }),
    init: (mockFetch) => runFn(mockSelf, cacheStore, mockFetch, URL)
  };
}

(async () => {
  console.log('=== Running Empirical Simulation of Service Worker ===\n');

  await runAsyncTest('Install: pre-caches all 40 assets and calls skipWaiting', async () => {
    const ctx = createSWContext();
    ctx.init(async () => new MockResponse('ok'));

    let waitP;
    ctx.listeners['install']({ waitUntil: (p) => { waitP = p; } });
    await waitP;

    assert.strictEqual(ctx.getStats().skipWaitingCalls, 1);
    const cache = await ctx.cacheStore.open('ai-course-v2');
    assert.strictEqual(cache.entries.size, 41);
    assert(await cache.match('./index.html'));
    assert(await cache.match('./lectures/27-actor-critic.html'));
  });

  await runAsyncTest('Activate: deletes outdated caches and invokes clients.claim()', async () => {
    const ctx = createSWContext();
    await ctx.cacheStore.open('ai-course-v1');
    await ctx.cacheStore.open('ai-course-v0-beta');
    await ctx.cacheStore.open('ai-course-v2');

    ctx.init(async () => new MockResponse('ok'));

    let waitP;
    ctx.listeners['activate']({ waitUntil: (p) => { waitP = p; } });
    await waitP;

    assert.strictEqual(ctx.getStats().clientsClaimCalls, 1);
    const keys = await ctx.cacheStore.keys();
    assert.deepStrictEqual(keys, ['ai-course-v2']);
  });

  await runAsyncTest('Fetch (Online): Network-First fetches fresh content and updates cache', async () => {
    const ctx = createSWContext();
    const cache = await ctx.cacheStore.open('ai-course-v2');
    await cache.put('https://user.github.io/index.html', new MockResponse('OLD STALE CACHE'));

    const mockFetch = async (req) => {
      return new MockResponse('FRESH NEW VERSION 2026', { status: 200, type: 'basic' });
    };

    ctx.init(mockFetch);

    let resPromise;
    ctx.listeners['fetch']({
      request: new MockRequest('https://user.github.io/index.html'),
      respondWith: (p) => { resPromise = p; }
    });

    const res = await resPromise;
    const text = await res.text();
    assert.strictEqual(text, 'FRESH NEW VERSION 2026');

    const cachedRes = await cache.match('https://user.github.io/index.html');
    assert.strictEqual(await cachedRes.text(), 'FRESH NEW VERSION 2026');
  });

  await runAsyncTest('Fetch (Offline): Falls back to cached response upon network failure', async () => {
    const ctx = createSWContext();
    const cache = await ctx.cacheStore.open('ai-course-v2');
    await cache.put('https://user.github.io/lectures/00-intro-ml.html', new MockResponse('CACHED LECTURE 00 CONTENT'));

    const mockFetch = async () => {
      throw new Error('TypeError: Failed to fetch (Offline)');
    };

    ctx.init(mockFetch);

    let resPromise;
    ctx.listeners['fetch']({
      request: new MockRequest('https://user.github.io/lectures/00-intro-ml.html'),
      respondWith: (p) => { resPromise = p; }
    });

    const res = await resPromise;
    assert.strictEqual(await res.text(), 'CACHED LECTURE 00 CONTENT');
  });

  await runAsyncTest('Fetch (Offline Navigation Fallback): Uncached navigation routes fallback to index.html', async () => {
    const ctx = createSWContext();
    const cache = await ctx.cacheStore.open('ai-course-v2');
    await cache.put('./index.html', new MockResponse('ROOT PORTAL HTML'));

    const mockFetch = async () => {
      throw new Error('TypeError: Failed to fetch (Offline)');
    };

    ctx.init(mockFetch);

    let resPromise;
    ctx.listeners['fetch']({
      request: new MockRequest('https://user.github.io/some-unknown-subroute', {
        mode: 'navigate',
        headers: { accept: 'text/html' }
      }),
      respondWith: (p) => { resPromise = p; }
    });

    const res = await resPromise;
    assert.strictEqual(await res.text(), 'ROOT PORTAL HTML');
  });

  await runAsyncTest('Fetch (Error Handling): 404 from network is returned but NOT saved to cache', async () => {
    const ctx = createSWContext();
    const cache = await ctx.cacheStore.open('ai-course-v2');

    const mockFetch = async () => {
      return new MockResponse('404 Not Found', { status: 404, type: 'basic' });
    };

    ctx.init(mockFetch);

    let resPromise;
    ctx.listeners['fetch']({
      request: new MockRequest('https://user.github.io/missing-file.js'),
      respondWith: (p) => { resPromise = p; }
    });

    const res = await resPromise;
    assert.strictEqual(res.status, 404);
    assert.strictEqual(await cache.match('https://user.github.io/missing-file.js'), undefined);
  });

  runSyncTest('Fetch (Bypass): Non-GET and chrome-extension:// requests are not intercepted', () => {
    const ctx = createSWContext();
    ctx.init(async () => new MockResponse('ok'));

    let intercepted = false;
    ctx.listeners['fetch']({
      request: new MockRequest('https://user.github.io/api', { method: 'POST' }),
      respondWith: () => { intercepted = true; }
    });
    assert.strictEqual(intercepted, false);

    let extIntercepted = false;
    ctx.listeners['fetch']({
      request: new MockRequest('chrome-extension://someextensionid/script.js'),
      respondWith: () => { extIntercepted = true; }
    });
    assert.strictEqual(extIntercepted, false);
  });

  console.log('\nSimulation Completed: ' + passCount + ' Passed, ' + failCount + ' Failed.');
})();
