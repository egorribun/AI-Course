/**
 * Challenger 1 M1 Empirical DOM & Layout Stress Testing Suite
 * Tests live DOM interactions, URL search parameter auto-focus, modal open/close/Esc,
 * theme syncing across buttons, and layout invariants across all 30 HTML documents.
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');
const assert = require('assert');

const ROOT = path.resolve(__dirname, '..');
const INDEX_HTML = path.join(ROOT, 'index.html');
const EXAM_HTML = path.join(ROOT, 'exam.html');
const LECTURES_DIR = path.join(ROOT, 'lectures');
const STYLE_CSS = path.join(ROOT, 'style.css');
const APP_JS = path.join(ROOT, 'js', 'app.js');
const TRACKER_JS = path.join(ROOT, 'js', 'tracker.js');

let passCount = 0;
let failCount = 0;

function test(name, fn) {
  try {
    fn();
    console.log(`  [PASS] ${name}`);
    passCount++;
  } catch (err) {
    console.error(`  [FAIL] ${name}`);
    console.error(`         ${err.stack || err.message}`);
    failCount++;
  }
}

async function testAsync(name, fn) {
  try {
    await fn();
    console.log(`  [PASS] ${name}`);
    passCount++;
  } catch (err) {
    console.error(`  [FAIL] ${name}`);
    console.error(`         ${err.stack || err.message}`);
    failCount++;
  }
}

// -------------------------------------------------------------------------
// Minimal DOM Mock for Headless Interactive Testing
// -------------------------------------------------------------------------
class MockElement {
  constructor(tagName, id = '', className = '') {
    this.tagName = tagName.toUpperCase();
    this.id = id;
    this.className = className;
    this.attributes = {};
    this.style = {};
    this.children = [];
    this.parentNode = null;
    this.listeners = {};
    this.textContent = '';
    this.value = '';
    this.dataset = {};
    const self = this;
    this.classList = {
      contains(cls) {
        return self.className ? self.className.split(/\s+/).includes(cls) : false;
      },
      add(cls) {
        if (!this.contains(cls)) {
          self.className = (self.className ? self.className + ' ' : '') + cls;
        }
      },
      remove(cls) {
        if (self.className) {
          self.className = self.className.split(/\s+/).filter(c => c !== cls).join(' ');
        }
      },
      toggle(cls, force) {
        if (typeof force === 'boolean') {
          if (force) this.add(cls);
          else this.remove(cls);
        } else {
          if (this.contains(cls)) this.remove(cls);
          else this.add(cls);
        }
      }
    };
  }

  setAttribute(name, val) {
    this.attributes[name] = String(val);
  }
  getAttribute(name) {
    return this.attributes.hasOwnProperty(name) ? this.attributes[name] : null;
  }
  removeAttribute(name) {
    delete this.attributes[name];
  }
  hasAttribute(name) {
    return this.attributes.hasOwnProperty(name);
  }

  appendChild(child) {
    child.parentNode = this;
    this.children.push(child);
    return child;
  }

  querySelector(selector) {
    const list = this.querySelectorAll(selector);
    return list.length > 0 ? list[0] : null;
  }

  querySelectorAll(selector) {
    const results = [];
    const selectors = selector.split(',').map(s => s.trim());
    function matchSingle(el, sel) {
      if (sel.startsWith('#')) {
        return el.id === sel.slice(1);
      } else if (sel.startsWith('.')) {
        const cls = sel.slice(1);
        return el.classList && el.classList.contains(cls);
      } else if (sel.includes('.')) {
        const parts = sel.split('.');
        const tag = parts[0].toUpperCase();
        const cls = parts[1];
        return (!tag || el.tagName === tag) && el.classList && el.classList.contains(cls);
      } else {
        return el.tagName === sel.toUpperCase();
      }
    }
    function match(el) {
      if (selectors.some(sel => matchSingle(el, sel))) {
        results.push(el);
      }
      for (const ch of el.children) match(ch);
    }
    for (const ch of this.children) match(ch);
    return results;
  }

  addEventListener(event, handler) {
    if (!this.listeners[event]) this.listeners[event] = [];
    this.listeners[event].push(handler);
  }

  dispatchEvent(event) {
    const handlers = this.listeners[event.type] || [];
    for (const h of handlers) h(event);
  }

  click() {
    this.dispatchEvent({ type: 'click', target: this, preventDefault: () => {} });
  }

  focus() {
    let root = this;
    while (root.parentNode) root = root.parentNode;
    root.activeElement = this;
  }

  select() {
    this.selected = true;
  }

  scrollIntoView() {
    this.scrolled = true;
  }
}

class MockLocalStorage {
  constructor() { this.store = {}; }
  getItem(k) { return this.store.hasOwnProperty(k) ? this.store[k] : null; }
  setItem(k, v) { this.store[k] = String(v); }
  removeItem(k) { delete this.store[k]; }
  clear() { this.store = {}; }
}

function createFreshEnvironment() {
  const storage = new MockLocalStorage();
  const doc = new MockElement('document');
  const html = new MockElement('html');
  const body = new MockElement('body');
  doc.appendChild(html);
  html.appendChild(body);
  doc.documentElement = html;
  doc.body = body;
  doc.activeElement = null;
  doc.createElement = function(tagName) { return new MockElement(tagName); };
  doc.getElementById = function(id) {
    function find(el) {
      if (el.id === id) return el;
      for (const ch of el.children) {
        const res = find(ch);
        if (res) return res;
      }
      return null;
    }
    return find(doc.documentElement);
  };

  const win = {
    document: doc,
    localStorage: storage,
    location: { search: '?focus=search', pathname: '/index.html' },
    scrollTo: () => {},
    addEventListener: (evt, fn) => doc.addEventListener(evt, fn),
    dispatchEvent: (evt) => doc.dispatchEvent(evt),
    CustomEvent: class { constructor(type, detail) { this.type = type; this.detail = detail; } },
    navigator: {
      serviceWorker: {
        register: () => Promise.resolve()
      }
    },
    console: console
  };

  return { doc, html, body, storage, win };
}

(async () => {
  console.log('=== Starting Challenger 1 M1 Empirical DOM Stress Suite ===\n');

  // -----------------------------------------------------------------------
  // Test 1: All 30 HTML Files Verification
  // -----------------------------------------------------------------------
  test('HTML Conformance: All 30 pages contain Bottom Navigation Bar & Progress Modal', () => {
    const lectureFiles = fs.readdirSync(LECTURES_DIR).filter(f => f.endsWith('.html'));
    assert.strictEqual(lectureFiles.length, 28, 'Must find 28 lecture files');

    const allPages = [
      { name: 'index.html', path: INDEX_HTML, isRoot: true, isExam: false },
      { name: 'exam.html', path: EXAM_HTML, isRoot: true, isExam: true },
      ...lectureFiles.map(f => ({ name: f, path: path.join(LECTURES_DIR, f), isRoot: false, isExam: false }))
    ];

    assert.strictEqual(allPages.length, 30, 'Total verified pages must be 30');

    allPages.forEach(p => {
      const raw = fs.readFileSync(p.path, 'utf-8');
      
      // 1. Bottom nav bar
      assert(raw.includes('class="bottom-nav-bar"'), `${p.name} missing bottom-nav-bar`);
      assert(raw.includes('id="nav-search-btn"'), `${p.name} missing nav-search-btn`);
      assert(raw.includes('id="nav-exam-btn"'), `${p.name} missing nav-exam-btn`);
      assert(raw.includes('id="nav-progress-btn"'), `${p.name} missing nav-progress-btn`);

      // 2. Progress modal
      assert(raw.includes('id="course-progress-modal"'), `${p.name} missing course-progress-modal`);
      assert(raw.includes('id="modal-progress-close"'), `${p.name} missing modal-progress-close`);
      assert(raw.includes('id="modal-reset-progress-btn"'), `${p.name} missing modal-reset-progress-btn`);
      assert(raw.includes('role="dialog"'), `${p.name} modal missing role=dialog`);
      assert(raw.includes('aria-modal="true"'), `${p.name} modal missing aria-modal=true`);

      // 3. Routing paths
      if (p.isRoot) {
        if (p.isExam) {
          assert(raw.includes('href="index.html?focus=search"'), `${p.name} search href must be index.html?focus=search`);
          assert(raw.includes('aria-current="page"'), `${p.name} exam item must have aria-current=page`);
          assert(raw.includes('class="bottom-nav-item active"'), `${p.name} exam item must have active class`);
        }
      } else {
        assert(raw.includes('href="../index.html?focus=search"'), `${p.name} search href must be ../index.html?focus=search`);
        assert(raw.includes('href="../exam.html"'), `${p.name} exam href must be ../exam.html`);
      }
    });
  });

  // -----------------------------------------------------------------------
  // Test 2: CSS Stylesheet Conformance
  // -----------------------------------------------------------------------
  test('CSS Conformance: Responsive breakpoints, safe area insets, and touch targets', () => {
    const css = fs.readFileSync(STYLE_CSS, 'utf-8');

    // Desktop rule
    assert(css.includes('.bottom-nav-bar {\n  display: none;\n}'), 'Base bottom-nav-bar must be display: none');
    assert(css.includes('.header-actions'), 'Must define .header-actions');
    assert(css.includes('.btn-header-exam'), 'Must define .btn-header-exam');

    // Mobile media query
    assert(css.includes('@media (max-width: 767px)'), 'Must define @media (max-width: 767px)');
    assert(css.includes('display: none !important'), 'btn-header-exam must be hidden on mobile');
    assert(css.includes('display: flex !important'), 'bottom-nav-bar must be flex on mobile');

    // Safe area insets
    assert(css.includes('padding-bottom: max(8px, env(safe-area-inset-bottom, 0px));'), 'bottom-nav-bar must use max(8px, env(safe-area-inset-bottom, 0px))');
    assert(css.includes('padding-bottom: calc(72px + env(safe-area-inset-bottom, 0px))'), 'body must have padding-bottom calc(72px + env(safe-area-inset-bottom, 0px))');
    assert(css.includes('bottom: calc(80px + env(safe-area-inset-bottom, 0px)) !important;'), 'back-to-top must be elevated above bottom bar');

    // Touch targets >= 44px
    assert(css.includes('min-width: 44px'), 'Touch targets must define min-width: 44px');
    assert(css.includes('min-height: 48px') || css.includes('min-height: 44px'), 'Touch targets must define min-height >= 44px');
  });

  // -----------------------------------------------------------------------
  // Test 3: Interactive JS DOM Execution: URL search query focus
  // -----------------------------------------------------------------------
  await testAsync('Interactive JS: ?focus=search automatically focuses and selects search input', async () => {
    const env = createFreshEnvironment();
    const searchInput = new MockElement('input', 'lecture-search-input', 'search-input');
    env.body.appendChild(searchInput);

    const context = vm.createContext({
      window: env.win,
      document: env.doc,
      navigator: env.win.navigator,
      localStorage: env.storage,
      URLSearchParams: class {
        get(param) { return param === 'focus' ? 'search' : null; }
      },
      setTimeout: (fn, delay) => { fn(); },
      clearTimeout: () => {},
      CustomEvent: env.win.CustomEvent,
      console: console
    });

    const appCode = fs.readFileSync(APP_JS, 'utf-8');
    vm.runInContext(appCode, context);

    // Trigger DOMContentLoaded
    env.doc.dispatchEvent({ type: 'DOMContentLoaded' });

    assert.strictEqual(env.doc.activeElement, searchInput, 'Search input should be focused on ?focus=search');
    assert.strictEqual(searchInput.selected, true, 'Search input should be selected on ?focus=search');
    assert.strictEqual(searchInput.scrolled, true, 'Search input should be scrolled into view');
  });

  // -----------------------------------------------------------------------
  // Test 4: Interactive JS DOM Execution: Modal Open/Close & Escape Key
  // -----------------------------------------------------------------------
  await testAsync('Interactive JS: Modal opens, updates stats, closes via button, overlay, and Escape key', async () => {
    const env = createFreshEnvironment();
    const modal = new MockElement('div', 'course-progress-modal', 'progress-modal-overlay');
    modal.setAttribute('hidden', '');
    const navProgressBtn = new MockElement('button', 'nav-progress-btn', 'bottom-nav-item');
    const closeBtn = new MockElement('button', 'modal-progress-close', 'modal-close-btn');
    const closeActionBtn = new MockElement('button', 'modal-close-action-btn', 'btn btn-primary');
    const resetBtn = new MockElement('button', 'modal-reset-progress-btn', 'btn btn-secondary');
    
    const fill = new MockElement('div', 'modal-progress-fill');
    const percent = new MockElement('div', 'modal-progress-percent');
    const lecs = new MockElement('div', 'modal-stat-lecs');
    const qas = new MockElement('div', 'modal-stat-qas');
    const tasks = new MockElement('div', 'modal-stat-tasks');

    modal.appendChild(closeBtn);
    modal.appendChild(closeActionBtn);
    modal.appendChild(resetBtn);
    modal.appendChild(fill);
    modal.appendChild(percent);
    modal.appendChild(lecs);
    modal.appendChild(qas);
    modal.appendChild(tasks);

    env.body.appendChild(modal);
    env.body.appendChild(navProgressBtn);

    const context = vm.createContext({
      window: env.win,
      document: env.doc,
      navigator: env.win.navigator,
      localStorage: env.storage,
      CustomEvent: env.win.CustomEvent,
      confirm: () => true,
      setTimeout: (fn) => fn(),
      clearTimeout: () => {},
      console: console
    });

    const trackerCode = fs.readFileSync(TRACKER_JS, 'utf-8');
    vm.runInContext(trackerCode, context);

    // Trigger DOMContentLoaded to initialize CourseTracker
    env.doc.dispatchEvent({ type: 'DOMContentLoaded' });

    // 1. Open modal via nav button
    assert(modal.hasAttribute('hidden'), 'Modal must start hidden');
    navProgressBtn.click();
    assert(!modal.hasAttribute('hidden'), 'Modal must become visible after clicking nav-progress-btn');
    assert.strictEqual(percent.textContent, 'Общий прогресс: 0%', 'Modal stats must render initial percentage');

    // 2. Close modal via close button
    closeBtn.click();
    assert(modal.hasAttribute('hidden'), 'Modal must hide after closeBtn click');

    // 3. Open and close via action button
    navProgressBtn.click();
    assert(!modal.hasAttribute('hidden'));
    closeActionBtn.click();
    assert(modal.hasAttribute('hidden'), 'Modal must hide after closeActionBtn click');

    // 4. Open and close via Escape key
    navProgressBtn.click();
    assert(!modal.hasAttribute('hidden'));
    env.doc.dispatchEvent({ type: 'keydown', key: 'Escape', preventDefault: () => {} });
    assert(modal.hasAttribute('hidden'), 'Modal must hide after Escape keydown');

    // 5. Open and close via backdrop click
    navProgressBtn.click();
    assert(!modal.hasAttribute('hidden'));
    modal.dispatchEvent({ type: 'click', target: modal });
    assert(modal.hasAttribute('hidden'), 'Modal must hide after backdrop click');
  });

  // -----------------------------------------------------------------------
  // Test 5: Interactive JS DOM Execution: Theme Toggle Synchronization
  // -----------------------------------------------------------------------
  await testAsync('Interactive JS: Theme toggle updates <html> data-theme and syncs header & bottom nav buttons', async () => {
    const env = createFreshEnvironment();
    const headerToggle = new MockElement('button', 'header-theme-toggle', 'theme-toggle');
    const headerIcon = new MockElement('span', '', 'theme-icon');
    const headerText = new MockElement('span', '', 'theme-text');
    headerToggle.appendChild(headerIcon);
    headerToggle.appendChild(headerText);

    const bottomToggle = new MockElement('button', 'nav-theme-btn', 'bottom-nav-item theme-toggle');
    const bottomIcon = new MockElement('span', '', 'bottom-nav-icon theme-icon');
    const bottomLabel = new MockElement('span', '', 'bottom-nav-label theme-label');
    bottomToggle.appendChild(bottomIcon);
    bottomToggle.appendChild(bottomLabel);

    env.body.appendChild(headerToggle);
    env.body.appendChild(bottomToggle);

    const context = vm.createContext({
      window: env.win,
      document: env.doc,
      navigator: env.win.navigator,
      localStorage: env.storage,
      CustomEvent: env.win.CustomEvent,
      console: console
    });

    const trackerCode = fs.readFileSync(TRACKER_JS, 'utf-8');
    vm.runInContext(trackerCode, context);

    env.doc.dispatchEvent({ type: 'DOMContentLoaded' });

    // Initial state: dark theme -> shows sun icon to switch to light
    assert.strictEqual(env.doc.documentElement.getAttribute('data-theme'), 'dark');
    assert.strictEqual(headerIcon.textContent, '☀️');
    assert.strictEqual(bottomIcon.textContent, '☀️');

    // Click bottom toggle -> should switch to light -> shows moon icon to switch to dark
    bottomToggle.click();
    assert.strictEqual(env.doc.documentElement.getAttribute('data-theme'), 'light');
    assert.strictEqual(headerIcon.textContent, '🌙');
    assert.strictEqual(bottomIcon.textContent, '🌙');

    // Click header toggle -> should switch back to dark -> shows sun icon
    headerToggle.click();
    assert.strictEqual(env.doc.documentElement.getAttribute('data-theme'), 'dark');
    assert.strictEqual(headerIcon.textContent, '☀️');
    assert.strictEqual(bottomIcon.textContent, '☀️');
  });

  console.log('======================================================');
  console.log(`Challenger 1 Results: ${passCount} passed, ${failCount} failed`);
  console.log('======================================================');

  if (failCount > 0) process.exit(1);
})();
