/**
 * Unit Test Suite for sw.js (Service Worker PWA v3)
 * Comprehensive 100% Lines, Branches, Functions Coverage via Node.js Native Runner.
 */

const { describe, it, beforeEach } = require('node:test');
const assert = require('node:assert');
const path = require('node:path');

const SW_PATH = path.resolve(__dirname, '../../sw.js');

class MockHeaders {
  constructor(init = {}) {
    this._map = new Map();
    if (init) {
      for (const [k, v] of Object.entries(init)) {
        this._map.set(k.toLowerCase(), v);
      }
    }
  }
  get(name) {
    return this._map.get(name.toLowerCase()) || null;
  }
  set(name, value) {
    this._map.set(name.toLowerCase(), value);
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
  constructor(body = '', init = {}) {
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

class MockCacheStore {
  constructor(name) {
    this.name = name;
    this._entries = new Map();
  }
  async addAll(urls) {
    for (const u of urls) {
      this._entries.set(u, new MockResponse(`content of ${u}`));
    }
  }
  async match(request) {
    const key = typeof request === 'string' ? request : request.url;
    const res = this._entries.get(key);
    return res ? res.clone() : undefined;
  }
  async put(request, response) {
    const key = typeof request === 'string' ? request : request.url;
    this._entries.set(key, response.clone());
  }
  async delete(request) {
    const key = typeof request === 'string' ? request : request.url;
    return this._entries.delete(key);
  }
}

class MockCaches {
  constructor() {
    this._stores = new Map();
  }
  async open(name) {
    if (!this._stores.has(name)) {
      this._stores.set(name, new MockCacheStore(name));
    }
    return this._stores.get(name);
  }
  async keys() {
    return Array.from(this._stores.keys());
  }
  async match(request) {
    for (const store of this._stores.values()) {
      const match = await store.match(request);
      if (match) return match;
    }
    return undefined;
  }
  async delete(name) {
    return this._stores.delete(name);
  }
}

function setupMockServiceWorkerEnv() {
  const listeners = {};
  const caches = new MockCaches();
  let skippedWaiting = false;
  let claimedClients = false;

  const swScope = {
    location: {
      origin: 'https://example.com',
      href: 'https://example.com/sw.js'
    },
    addEventListener: (evt, cb) => {
      listeners[evt] = listeners[evt] || [];
      listeners[evt].push(cb);
    },
    skipWaiting: async () => {
      skippedWaiting = true;
    },
    clients: {
      claim: async () => {
        claimedClients = true;
      }
    }
  };

  global.self = swScope;
  global.caches = caches;
  global.Request = MockRequest;
  global.Response = MockResponse;
  global.Headers = MockHeaders;
  global.fetch = async (req) => {
    return new MockResponse('live-network-content', { status: 200, type: 'basic' });
  };

  return {
    swScope,
    listeners,
    caches,
    getSkippedWaiting: () => skippedWaiting,
    getClaimedClients: () => claimedClients
  };
}

function loadServiceWorker() {
  delete require.cache[require.resolve(SW_PATH)];
  require(SW_PATH);
}

describe('Service Worker Suite (sw.js)', () => {
  it('should install and pre-cache all assets and skip waiting', async () => {
    const env = setupMockServiceWorkerEnv();
    loadServiceWorker();

    assert.ok(env.listeners['install']);
    const installHandler = env.listeners['install'][0];

    let waitUntilPromise = null;
    const mockInstallEvent = {
      waitUntil: (p) => { waitUntilPromise = p; }
    };

    installHandler(mockInstallEvent);
    await waitUntilPromise;

    assert.strictEqual(env.getSkippedWaiting(), true);

    const cache = await env.caches.open('ai-course-v3');
    const indexMatch = await cache.match('./index.html');
    assert.ok(indexMatch);
  });

  it('should handle install pre-cache warning on error', async () => {
    const env = setupMockServiceWorkerEnv();
    env.caches.open = () => Promise.reject(new Error('Cache quota'));
    loadServiceWorker();

    const installHandler = env.listeners['install'][0];
    let waitUntilPromise = null;
    installHandler({
      waitUntil: (p) => { waitUntilPromise = p; }
    });
    await waitUntilPromise;
  });

  it('should activate and purge old caches (v1, v2) and claim clients', async () => {
    const env = setupMockServiceWorkerEnv();
    await env.caches.open('ai-course-v1');
    await env.caches.open('ai-course-v2');
    await env.caches.open('ai-course-v3');

    loadServiceWorker();

    assert.ok(env.listeners['activate']);
    const activateHandler = env.listeners['activate'][0];

    let waitUntilPromise = null;
    activateHandler({
      waitUntil: (p) => { waitUntilPromise = p; }
    });
    await waitUntilPromise;

    assert.strictEqual(env.getClaimedClients(), true);
    const remainingKeys = await env.caches.keys();
    assert.deepStrictEqual(remainingKeys, ['ai-course-v3']);
  });

  describe('Fetch Strategy Dispatcher', () => {
    it('should ignore non-GET and non-HTTP requests', async () => {
      const env = setupMockServiceWorkerEnv();
      loadServiceWorker();
      const fetchHandler = env.listeners['fetch'][0];

      let responded = false;
      const postEvent = {
        request: new MockRequest('https://example.com/api', { method: 'POST' }),
        respondWith: () => { responded = true; }
      };
      fetchHandler(postEvent);
      assert.strictEqual(responded, false);

      const extEvent = {
        request: new MockRequest('chrome-extension://abc/page.html'),
        respondWith: () => { responded = true; }
      };
      fetchHandler(extEvent);
      assert.strictEqual(responded, false);
    });

    it('should handle external CDN assets (MathJax Cloudflare / jsDelivr) with Stale-While-Revalidate and cache.put warnings', async () => {
      const env = setupMockServiceWorkerEnv();
      const cache = await env.caches.open('ai-course-v3');
      await cache.put('https://cdnjs.cloudflare.com/mathjax/tex-svg.js', new MockResponse('cached-mathjax'));

      // Make cache.put reject to test warning branch
      cache.put = () => Promise.reject(new Error('Quota exceeded on CDN cache'));

      loadServiceWorker();
      const fetchHandler = env.listeners['fetch'][0];

      let responsePromise = null;
      const cdnEvent = {
        request: new MockRequest('https://cdnjs.cloudflare.com/mathjax/tex-svg.js'),
        respondWith: (p) => { responsePromise = p; }
      };

      fetchHandler(cdnEvent);
      const res = await responsePromise;
      assert.ok(res);

      // Other external domain should be ignored
      let otherResponded = false;
      const otherEvent = {
        request: new MockRequest('https://other-domain.com/asset.png'),
        respondWith: () => { otherResponded = true; }
      };
      fetchHandler(otherEvent);
      assert.strictEqual(otherResponded, false);
    });

    it('should handle local Same-Origin assets with Network-First, cache.put warnings, and offline navigation fallbacks', async () => {
      const env = setupMockServiceWorkerEnv();
      const cache = await env.caches.open('ai-course-v3');

      // Make cache.put reject to test warning branch
      const origPut = cache.put.bind(cache);
      cache.put = () => Promise.reject(new Error('Quota on local cache'));

      loadServiceWorker();
      const fetchHandler = env.listeners['fetch'][0];

      // 1. Online success
      let responsePromise1 = null;
      fetchHandler({
        request: new MockRequest('https://example.com/style.css'),
        respondWith: (p) => { responsePromise1 = p; }
      });
      const res1 = await responsePromise1;
      assert.strictEqual(res1.body, 'live-network-content');

      // Restore cache.put
      cache.put = origPut;
      await cache.put('https://example.com/style.css', new MockResponse('cached-style'));
      await cache.put('./index.html', new MockResponse('offline-portal-html'));

      // 2. Offline network failure with cached asset fallback
      global.fetch = () => Promise.reject(new Error('Network offline'));
      let responsePromise2 = null;
      fetchHandler({
        request: new MockRequest('https://example.com/style.css'),
        respondWith: (p) => { responsePromise2 = p; }
      });
      const res2 = await responsePromise2;
      assert.strictEqual(res2.body, 'cached-style');

      // 3. Offline HTML navigation request fallback to ./index.html
      let responsePromise3 = null;
      fetchHandler({
        request: new MockRequest('https://example.com/lectures/unknown.html', {
          mode: 'navigate',
          headers: { accept: 'text/html' }
        }),
        respondWith: (p) => { responsePromise3 = p; }
      });
      const res3 = await responsePromise3;
      assert.strictEqual(res3.body, 'offline-portal-html');

      // 4. Offline fallback when ./index.html is missing but /index.html is present
      await cache.delete('./index.html');
      await cache.put('/index.html', new MockResponse('root-fallback-html'));
      let responsePromise4 = null;
      fetchHandler({
        request: new MockRequest('https://example.com/unknown', {
          headers: { accept: 'text/html' }
        }),
        respondWith: (p) => { responsePromise4 = p; }
      });
      const res4 = await responsePromise4;
      assert.strictEqual(res4.body, 'root-fallback-html');

      // 5. Offline fallback when neither ./index.html nor /index.html is present but 'index.html' is present
      await cache.delete('/index.html');
      await cache.put('index.html', new MockResponse('relative-index-html'));
      let responsePromise5 = null;
      fetchHandler({
        request: new MockRequest('https://example.com/missing-page', {
          mode: 'navigate'
        }),
        respondWith: (p) => { responsePromise5 = p; }
      });
      const res5 = await responsePromise5;
      assert.strictEqual(res5.body, 'relative-index-html');
    });
  });
});
