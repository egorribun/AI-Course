/**
 * Adversarial Challenger 2 Stress Test Suite for Milestone M1
 * Empirically tests:
 * 1. #course-progress-modal lifecycle (open, closeBtn, closeActionBtn, backdrop, Escape, resetProgress, background sync).
 * 2. Rapid Theme Toggle synchronization (500 iterations, header vs bottom nav vs documentElement vs localStorage).
 * 3. Simulator Isolation (#exam-simulator-container absent in index.html, present in exam.html, absent in 28 lectures).
 * 4. Relative navigation link graph resolution from all 28 lectures to index.html and exam.html.
 */

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const COURSE_ROOT = path.resolve(__dirname, '..');
const LECTURES_DIR = path.join(COURSE_ROOT, 'lectures');
const INDEX_HTML_PATH = path.join(COURSE_ROOT, 'index.html');
const EXAM_HTML_PATH = path.join(COURSE_ROOT, 'exam.html');
const STYLE_CSS_PATH = path.join(COURSE_ROOT, 'style.css');
const TRACKER_JS_PATH = path.join(COURSE_ROOT, 'js', 'tracker.js');
const APP_JS_PATH = path.join(COURSE_ROOT, 'js', 'app.js');

let passedTests = 0;
let failedTests = 0;

function assert(condition, message) {
  if (!condition) {
    failedTests++;
    console.error(`  [FAIL] ${message}`);
    throw new Error(message);
  }
  passedTests++;
  console.log(`  [PASS] ${message}`);
}

// -----------------------------------------------------------------------------
// DOM Node & Event Mock Helper
// -----------------------------------------------------------------------------
class MockElement {
  constructor(tagName, id = '', className = '') {
    this.tagName = tagName.toUpperCase();
    this.id = id;
    this.className = className;
    this.attributes = {};
    if (id) this.attributes.id = id;
    if (className) this.attributes.class = className;
    this.children = [];
    this.parentNode = null;
    this.listeners = {};
    this.style = {};
    this.textContent = '';
    this.innerHTMLValue = '';
    this.isContentEditable = false;
  }

  get classList() {
    const self = this;
    return {
      add: (...cls) => {
        const set = new Set((self.className || '').split(/\s+/).filter(Boolean));
        cls.forEach(c => set.add(c));
        self.className = Array.from(set).join(' ');
        self.attributes.class = self.className;
      },
      remove: (...cls) => {
        const set = new Set((self.className || '').split(/\s+/).filter(Boolean));
        cls.forEach(c => set.delete(c));
        self.className = Array.from(set).join(' ');
        self.attributes.class = self.className;
      },
      toggle: (c, force) => {
        const set = new Set((self.className || '').split(/\s+/).filter(Boolean));
        let res;
        if (typeof force === 'boolean') {
          if (force) set.add(c); else set.delete(c);
          res = force;
        } else {
          if (set.has(c)) { set.delete(c); res = false; }
          else { set.add(c); res = true; }
        }
        self.className = Array.from(set).join(' ');
        self.attributes.class = self.className;
        return res;
      },
      contains: (c) => (self.className || '').split(/\s+/).includes(c)
    };
  }

  setAttribute(k, v) {
    this.attributes[k] = String(v);
    if (k === 'class') this.className = String(v);
    if (k === 'id') this.id = String(v);
  }

  getAttribute(k) {
    return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null;
  }

  hasAttribute(k) {
    return Object.prototype.hasOwnProperty.call(this.attributes, k);
  }

  removeAttribute(k) {
    delete this.attributes[k];
    if (k === 'class') this.className = '';
    if (k === 'id') this.id = '';
  }

  appendChild(child) {
    child.parentNode = this;
    this.children.push(child);
    return child;
  }

  addEventListener(evt, cb) {
    this.listeners[evt] = this.listeners[evt] || [];
    this.listeners[evt].push(cb);
  }

  removeEventListener(evt, cb) {
    if (!this.listeners[evt]) return;
    this.listeners[evt] = this.listeners[evt].filter(f => f !== cb);
  }

  dispatchEvent(evt) {
    evt.target = evt.target || this;
    const handlers = this.listeners[evt.type] || [];
    handlers.forEach(h => {
      try { h(evt); } catch (e) { console.error('Handler error:', e); }
    });
    if (this.parentNode && !evt.propagationStopped) {
      this.parentNode.dispatchEvent(evt);
    }
    return true;
  }

  click() {
    const evt = { type: 'click', target: this, preventDefault: () => {}, propagationStopped: false };
    this.dispatchEvent(evt);
  }

  focus() {
    if (this.ownerDocument) {
      this.ownerDocument.activeElement = this;
    }
  }

  blur() {
    if (this.ownerDocument && this.ownerDocument.activeElement === this) {
      this.ownerDocument.activeElement = null;
    }
  }

  querySelector(selector) {
    return this.querySelectorAll(selector)[0] || null;
  }

  querySelectorAll(selector) {
    const results = [];
    const selectors = selector.split(',').map(s => s.trim());
    function traverse(node) {
      for (const child of node.children) {
        if (selectors.some(sel => matchesSelector(child, sel))) {
          results.push(child);
        }
        traverse(child);
      }
    }
    traverse(this);
    return results;
  }

  get innerHTML() {
    return this.innerHTMLValue;
  }

  set innerHTML(val) {
    this.innerHTMLValue = val;
    // Basic parser for innerHTML assignment of theme buttons
    this.children = [];
    if (val.includes('theme-icon') || val.includes('bottom-nav-icon')) {
      const iconMatch = val.match(/class="([^"]*theme-icon[^"]*)"[^>]*>([^<]*)<\/span>/);
      const textMatch = val.match(/class="([^"]*(?:theme-text|theme-label)[^"]*)"[^>]*>([^<]*)<\/span>/);
      if (iconMatch) {
        const iconSpan = new MockElement('span', '', iconMatch[1]);
        iconSpan.textContent = iconMatch[2];
        iconSpan.ownerDocument = this.ownerDocument;
        this.appendChild(iconSpan);
      }
      if (textMatch) {
        const textSpan = new MockElement('span', '', textMatch[1]);
        textSpan.textContent = textMatch[2];
        textSpan.ownerDocument = this.ownerDocument;
        this.appendChild(textSpan);
      }
    }
  }
}

function matchesSelector(el, selector) {
  const parts = selector.split(/\s+/);
  if (parts.length > 1) {
    // Basic descendant matching
    let current = el;
    for (let i = parts.length - 1; i >= 0; i--) {
      if (!current || !matchesSingle(current, parts[i])) return false;
      current = current.parentNode;
    }
    return true;
  }
  return matchesSingle(el, selector);
}

function matchesSingle(el, sel) {
  if (sel.startsWith('#')) return el.id === sel.slice(1);
  if (sel.startsWith('.')) return (el.className || '').split(/\s+/).includes(sel.slice(1));
  if (sel.includes('.')) {
    const [tag, cls] = sel.split('.');
    return (!tag || el.tagName === tag.toUpperCase()) && (el.className || '').split(/\s+/).includes(cls);
  }
  return el.tagName === sel.toUpperCase();
}

// -----------------------------------------------------------------------------
// Test Environment Setup
// -----------------------------------------------------------------------------
function buildBrowserSandbox(initialTheme = 'dark') {
  const storageStore = { ai_course_theme: initialTheme };
  const docListeners = {};
  const winListeners = {};

  const documentElement = new MockElement('html');
  documentElement.setAttribute('data-theme', initialTheme);

  const body = new MockElement('body');
  documentElement.appendChild(body);

  const document = {
    documentElement,
    body,
    activeElement: null,
    querySelectorAll: (sel) => documentElement.querySelectorAll(sel),
    querySelector: (sel) => documentElement.querySelector(sel),
    getElementById: (id) => {
      const all = documentElement.querySelectorAll('#' + id);
      return all[0] || null;
    },
    createElement: (tag) => {
      const el = new MockElement(tag);
      el.ownerDocument = document;
      return el;
    },
    addEventListener: (evt, cb) => {
      docListeners[evt] = docListeners[evt] || [];
      docListeners[evt].push(cb);
    },
    removeEventListener: (evt, cb) => {
      if (!docListeners[evt]) return;
      docListeners[evt] = docListeners[evt].filter(f => f !== cb);
    },
    dispatchEvent: (evt) => {
      const handlers = docListeners[evt.type] || [];
      handlers.forEach(h => { try { h(evt); } catch (e) { console.error(e); } });
      return true;
    }
  };

  documentElement.ownerDocument = document;
  body.ownerDocument = document;

  let confirmResult = true;

  const navigator = {
    serviceWorker: {
      register: () => Promise.resolve(),
      addEventListener: () => {}
    }
  };

  const window = {
    navigator,
    localStorage: {
      getItem: (k) => (Object.prototype.hasOwnProperty.call(storageStore, k) ? storageStore[k] : null),
      setItem: (k, v) => { storageStore[k] = String(v); },
      removeItem: (k) => { delete storageStore[k]; },
      clear: () => { Object.keys(storageStore).forEach(k => delete storageStore[k]); },
      _store: storageStore
    },
    document,
    confirm: (msg) => confirmResult,
    addEventListener: (evt, cb) => {
      winListeners[evt] = winListeners[evt] || [];
      winListeners[evt].push(cb);
    },
    removeEventListener: (evt, cb) => {
      if (!winListeners[evt]) return;
      winListeners[evt] = winListeners[evt].filter(f => f !== cb);
    },
    dispatchEvent: (evt) => {
      const handlers = winListeners[evt.type] || [];
      handlers.forEach(h => { try { h(evt); } catch (e) { console.error(e); } });
      return true;
    },
    CustomEvent: class {
      constructor(type, params = {}) {
        this.type = type;
        this.detail = params.detail || null;
      }
    },
    location: {
      search: '',
      pathname: '/index.html',
      reload: () => {}
    }
  };

  const context = vm.createContext({
    window,
    navigator,
    document,
    localStorage: window.localStorage,
    confirm: window.confirm,
    CustomEvent: window.CustomEvent,
    console,
    setTimeout: (fn) => fn(),
    clearTimeout: () => {},
    setConfirmResult: (val) => { confirmResult = val; }
  });

  return { window, document, context, storageStore, docListeners, winListeners };
}

// -----------------------------------------------------------------------------
// Suite 1: Progress Modal Lifecycle & Edge-Cases
// -----------------------------------------------------------------------------
function testProgressModalLifecycle() {
  console.log('\n--- Suite 1: Progress Modal Lifecycle & Edge Cases ---');

  const { window, document, context, storageStore, docListeners } = buildBrowserSandbox();

  // Create Header with actions
  const header = document.createElement('header');
  header.className = 'top';
  const headerInner = document.createElement('div');
  headerInner.className = 'inner';
  const headerActions = document.createElement('div');
  headerActions.className = 'header-actions';
  const headerThemeToggle = document.createElement('button');
  headerThemeToggle.className = 'theme-toggle';
  const hIcon = document.createElement('span');
  hIcon.className = 'theme-icon';
  hIcon.textContent = '☀️';
  const hText = document.createElement('span');
  hText.className = 'theme-text';
  hText.textContent = 'Светлая тема';
  headerThemeToggle.appendChild(hIcon);
  headerThemeToggle.appendChild(hText);
  headerActions.appendChild(headerThemeToggle);
  headerInner.appendChild(headerActions);
  header.appendChild(headerInner);
  document.body.appendChild(header);

  // Create Bottom Nav Bar
  const nav = document.createElement('nav');
  nav.className = 'bottom-nav-bar';
  const navProgressBtn = document.createElement('button');
  navProgressBtn.id = 'nav-progress-btn';
  navProgressBtn.className = 'bottom-nav-item';
  nav.appendChild(navProgressBtn);

  const navThemeBtn = document.createElement('button');
  navThemeBtn.id = 'nav-theme-btn';
  navThemeBtn.className = 'bottom-nav-item theme-toggle';
  const nIcon = document.createElement('span');
  nIcon.className = 'bottom-nav-icon theme-icon';
  nIcon.textContent = '☀️';
  const nText = document.createElement('span');
  nText.className = 'bottom-nav-label theme-label';
  nText.textContent = 'Тема';
  navThemeBtn.appendChild(nIcon);
  navThemeBtn.appendChild(nText);
  nav.appendChild(navThemeBtn);
  document.body.appendChild(nav);

  // Create Progress Modal
  const modal = document.createElement('div');
  modal.id = 'course-progress-modal';
  modal.className = 'progress-modal-overlay';
  modal.setAttribute('hidden', '');

  const modalContent = document.createElement('div');
  modalContent.className = 'progress-modal-content';

  const modalCloseBtn = document.createElement('button');
  modalCloseBtn.id = 'modal-progress-close';
  modalCloseBtn.className = 'modal-close-btn';

  const modalFill = document.createElement('div');
  modalFill.id = 'modal-progress-fill';

  const modalPercent = document.createElement('div');
  modalPercent.id = 'modal-progress-percent';

  const modalStatLecs = document.createElement('div');
  modalStatLecs.id = 'modal-stat-lecs';

  const modalStatQas = document.createElement('div');
  modalStatQas.id = 'modal-stat-qas';

  const modalStatTasks = document.createElement('div');
  modalStatTasks.id = 'modal-stat-tasks';

  const modalResetBtn = document.createElement('button');
  modalResetBtn.id = 'modal-reset-progress-btn';

  const modalCloseActionBtn = document.createElement('button');
  modalCloseActionBtn.id = 'modal-close-action-btn';

  modalContent.appendChild(modalCloseBtn);
  modalContent.appendChild(modalFill);
  modalContent.appendChild(modalPercent);
  modalContent.appendChild(modalStatLecs);
  modalContent.appendChild(modalStatQas);
  modalContent.appendChild(modalStatTasks);
  modalContent.appendChild(modalResetBtn);
  modalContent.appendChild(modalCloseActionBtn);
  modal.appendChild(modalContent);
  document.body.appendChild(modal);

  // Load tracker.js into sandbox
  const trackerCode = fs.readFileSync(TRACKER_JS_PATH, 'utf-8');
  vm.runInContext(trackerCode, context);

  // Fire DOMContentLoaded
  const domLoadedHandlers = docListeners['DOMContentLoaded'] || [];
  domLoadedHandlers.forEach(h => h());

  // 1. Initial State: Modal must be hidden
  assert(modal.hasAttribute('hidden'), 'Modal is initially hidden');

  // Seed some progress
  const CourseTracker = context.window.CourseTracker;
  CourseTracker.setLectureCompleted('00', true);
  CourseTracker.setLectureCompleted('01', true);
  CourseTracker.setQAChecked('qa-00-1', true);
  CourseTracker.setTaskChecked('task-00-1', true);

  // 2. Open via navProgressBtn
  navProgressBtn.click();
  assert(!modal.hasAttribute('hidden'), 'Clicking #nav-progress-btn removes hidden attribute');
  assert(document.activeElement === modalCloseBtn, 'Opening modal focuses #modal-progress-close button');
  assert(modalStatLecs.textContent.includes('2 / 28'), 'Modal displays correct completed lectures (2 / 28)');
  assert(modalStatQas.textContent.includes('1 / 296'), 'Modal displays correct completed QAs (1 / 296)');
  assert(modalStatTasks.textContent.includes('1 / 170'), 'Modal displays correct completed tasks (1 / 170)');

  // 3. Close via closeBtn
  modalCloseBtn.click();
  assert(modal.hasAttribute('hidden'), 'Clicking #modal-progress-close hides modal');
  assert(document.activeElement === navProgressBtn, 'Closing modal restores focus to openBtn');

  // 4. Open and close via closeActionBtn
  navProgressBtn.click();
  assert(!modal.hasAttribute('hidden'), 'Modal reopened');
  modalCloseActionBtn.click();
  assert(modal.hasAttribute('hidden'), 'Clicking #modal-close-action-btn hides modal');

  // 5. Open and close via backdrop click
  navProgressBtn.click();
  assert(!modal.hasAttribute('hidden'), 'Modal reopened');
  // Click on modal container directly (backdrop)
  modal.click();
  assert(modal.hasAttribute('hidden'), 'Clicking modal backdrop hides modal');

  // 6. Click inside modalContent should NOT close modal
  navProgressBtn.click();
  assert(!modal.hasAttribute('hidden'), 'Modal reopened');
  modalContent.click();
  assert(!modal.hasAttribute('hidden'), 'Clicking inside modal content does not close modal');

  // 7. Close via Escape key
  const escapeEvt = { key: 'Escape', preventDefault: () => {} };
  const keydownHandlers = docListeners['keydown'] || [];
  keydownHandlers.forEach(h => h(escapeEvt));
  assert(modal.hasAttribute('hidden'), 'Pressing Escape key closes modal');

  // 8. Escape key when already closed does nothing adverse
  keydownHandlers.forEach(h => h(escapeEvt));
  assert(modal.hasAttribute('hidden'), 'Pressing Escape when closed remains closed safely');

  // 9. Reset Progress with confirmation
  navProgressBtn.click();
  assert(!modal.hasAttribute('hidden'), 'Modal open for reset test');

  // Decline confirm
  context.setConfirmResult(false);
  modalResetBtn.click();
  assert(modalStatLecs.textContent.includes('2 / 28'), 'Declining reset preserves progress stats');

  // Accept confirm
  context.setConfirmResult(true);
  modalResetBtn.click();
  assert(modalStatLecs.textContent.includes('0 / 28 (0%)'), 'Accepting reset zeroes lecture stats');
  assert(modalStatQas.textContent.includes('0 / 296 (0%)'), 'Accepting reset zeroes QA stats');
  assert(modalStatTasks.textContent.includes('0 / 170 (0%)'), 'Accepting reset zeroes task stats');
  assert(modalPercent.textContent.includes('0%'), 'Modal percent updated to 0%');

  // Close modal
  modalCloseBtn.click();
  assert(modal.hasAttribute('hidden'), 'Modal closed after reset test');
}

// -----------------------------------------------------------------------------
// Suite 2: Rapid Theme Toggle & Concurrency Test
// -----------------------------------------------------------------------------
function testRapidThemeToggleSync() {
  console.log('\n--- Suite 2: Rapid Theme Toggle Synchronization (500 Iterations) ---');

  const { window, document, context, storageStore, docListeners } = buildBrowserSandbox('dark');

  // Setup DOM buttons
  const headerToggle = document.createElement('button');
  headerToggle.className = 'theme-toggle';
  const hIcon = document.createElement('span');
  hIcon.className = 'theme-icon';
  const hText = document.createElement('span');
  hText.className = 'theme-text';
  headerToggle.appendChild(hIcon);
  headerToggle.appendChild(hText);
  document.body.appendChild(headerToggle);

  const bottomToggle = document.createElement('button');
  bottomToggle.className = 'bottom-nav-item theme-toggle';
  const bIcon = document.createElement('span');
  bIcon.className = 'bottom-nav-icon theme-icon';
  const bText = document.createElement('span');
  bText.className = 'bottom-nav-label theme-label';
  bottomToggle.appendChild(bIcon);
  bottomToggle.appendChild(bText);
  document.body.appendChild(bottomToggle);

  // Load tracker.js
  const trackerCode = fs.readFileSync(TRACKER_JS_PATH, 'utf-8');
  vm.runInContext(trackerCode, context);

  // Fire DOMContentLoaded
  const domLoadedHandlers = docListeners['DOMContentLoaded'] || [];
  domLoadedHandlers.forEach(h => h());

  // Check initial state (dark)
  assert(document.documentElement.getAttribute('data-theme') === 'dark', 'Initial theme data-theme is dark');
  assert(hIcon.textContent === '☀️', 'Header toggle icon is sun in dark mode');
  assert(hText.textContent === 'Светлая тема', 'Header toggle text is "Светлая тема" in dark mode');
  assert(bIcon.textContent === '☀️', 'Bottom nav toggle icon is sun in dark mode');
  assert(bText.textContent === 'Тема', 'Bottom nav toggle text is "Тема"');

  // Run 500 rapid alternating clicks
  const iterations = 500;
  for (let i = 0; i < iterations; i++) {
    const isEven = (i % 2 === 0);
    const expectedTheme = isEven ? 'light' : 'dark';

    // Alternate clicking header and bottom nav buttons
    if (i % 2 === 0) {
      headerToggle.click();
    } else {
      bottomToggle.click();
    }

    const currentTheme = document.documentElement.getAttribute('data-theme');
    if (currentTheme !== expectedTheme) {
      throw new Error(`Iteration ${i}: Theme mismatch. Expected ${expectedTheme}, got ${currentTheme}`);
    }

    const storedTheme = storageStore['ai_course_theme'];
    if (storedTheme !== expectedTheme) {
      throw new Error(`Iteration ${i}: LocalStorage mismatch. Expected ${expectedTheme}, got ${storedTheme}`);
    }

    const expectedIcon = expectedTheme === 'light' ? '🌙' : '☀️';
    const expectedHeaderText = expectedTheme === 'light' ? 'Тёмная тема' : 'Светлая тема';

    if (hIcon.textContent !== expectedIcon || bIcon.textContent !== expectedIcon) {
      throw new Error(`Iteration ${i}: Icon mismatch. Header: ${hIcon.textContent}, Bottom: ${bIcon.textContent}`);
    }

    if (hText.textContent !== expectedHeaderText) {
      throw new Error(`Iteration ${i}: Header text mismatch. Expected ${expectedHeaderText}, got ${hText.textContent}`);
    }
  }

  assert(true, `Successfully completed ${iterations} rapid theme toggle operations with 100% synchronization`);
}

// -----------------------------------------------------------------------------
// Suite 3: Exam Simulator Isolation & Removal Invariants
// -----------------------------------------------------------------------------
function testExamSimulatorIsolation() {
  console.log('\n--- Suite 3: Exam Simulator Container Isolation ---');

  const indexHtml = fs.readFileSync(INDEX_HTML_PATH, 'utf-8');
  const examHtml = fs.readFileSync(EXAM_HTML_PATH, 'utf-8');

  // 1. index.html must NOT contain #exam-simulator-container or js/simulator.js
  assert(!indexHtml.includes('id="exam-simulator-container"'), 'index.html does NOT contain #exam-simulator-container');
  assert(!indexHtml.includes('src="js/simulator.js"'), 'index.html does NOT include js/simulator.js script tag');
  assert(!indexHtml.includes("id='exam-simulator-container'"), 'index.html does NOT contain single-quoted exam-simulator-container');

  // 2. exam.html MUST contain simulator container and exam.js
  const hasExamContainer = examHtml.includes('id="exam-simulator-container"') || examHtml.includes('class="sim-container"');
  assert(hasExamContainer, 'exam.html DOES contain interactive oral exam simulator container');
  assert(examHtml.includes('src="js/exam.js"'), 'exam.html includes js/exam.js script tag');

  // 3. Check all 28 lectures do NOT contain #exam-simulator-container
  const lectureFiles = fs.readdirSync(LECTURES_DIR).filter(f => f.endsWith('.html'));
  assert(lectureFiles.length === 28, `Found exactly 28 lecture files`);

  let anyLectureHasSimulator = false;
  lectureFiles.forEach(f => {
    const content = fs.readFileSync(path.join(LECTURES_DIR, f), 'utf-8');
    if (content.includes('id="exam-simulator-container"') || content.includes('src="js/simulator.js"')) {
      anyLectureHasSimulator = true;
    }
  });
  assert(!anyLectureHasSimulator, 'None of the 28 lecture files contain #exam-simulator-container or simulator.js');
}

// -----------------------------------------------------------------------------
// Suite 4: Relative Navigation Links Resolution across All 28 Lectures
// -----------------------------------------------------------------------------
function testLectureRelativeNavigationLinks() {
  console.log('\n--- Suite 4: Relative Navigation Links Graph Resolution ---');

  const lectureFiles = fs.readdirSync(LECTURES_DIR).filter(f => f.endsWith('.html')).sort();

  lectureFiles.forEach(f => {
    const filePath = path.join(LECTURES_DIR, f);
    const content = fs.readFileSync(filePath, 'utf-8');

    // Bottom Navigation Bar
    assert(content.includes('class="bottom-nav-bar"'), `${f} contains .bottom-nav-bar`);
    assert(content.includes('href="../index.html?focus=search"'), `${f} search nav links to ../index.html?focus=search`);
    assert(content.includes('href="../exam.html"'), `${f} exam nav links to ../exam.html`);
    assert(content.includes('id="nav-progress-btn"'), `${f} contains #nav-progress-btn`);

    // Modal
    assert(content.includes('id="course-progress-modal"'), `${f} contains #course-progress-modal`);

    // Backlink & Stylesheet
    assert(content.includes('href="../index.html"'), `${f} backlink points to ../index.html`);
    assert(content.includes('href="../style.css"'), `${f} stylesheet link points to ../style.css`);
    assert(content.includes('src="../js/tracker.js"'), `${f} tracker script points to ../js/tracker.js`);
    assert(content.includes('src="../js/lecture.js"'), `${f} lecture script points to ../js/lecture.js`);
  });

  assert(true, 'All 28 lectures have 100% valid relative links to ../index.html, ../exam.html, and core assets');
}

// -----------------------------------------------------------------------------
// Suite 5: CSS Responsive & Safe Area Inset Rules
// -----------------------------------------------------------------------------
function testCssResponsiveAndSafeAreaRules() {
  console.log('\n--- Suite 5: CSS Responsive & Safe Area Inset Rules ---');

  const css = fs.readFileSync(STYLE_CSS_PATH, 'utf-8');

  // Check safe area inset rules
  assert(css.includes('env(safe-area-inset-bottom'), 'style.css includes env(safe-area-inset-bottom) rules');
  assert(css.includes('padding-bottom: max(8px, env(safe-area-inset-bottom, 0px))'), '.bottom-nav-bar uses max(8px, env(safe-area-inset-bottom, 0px))');
  assert(css.includes('padding-bottom: calc(72px + env(safe-area-inset-bottom, 0px))'), 'mobile body padding accounts for safe area');
  assert(css.includes('calc(80px + env(safe-area-inset-bottom, 0px))'), '.back-to-top elevated above bottom navigation bar');

  // Check modal styles
  assert(css.includes('.progress-modal-overlay'), '.progress-modal-overlay styling present');
  assert(css.includes('.progress-modal-content'), '.progress-modal-content styling present');
  assert(css.includes('.progress-modal-overlay[hidden]'), 'Hidden attribute rule for modal overlay present with display: none !important');

  // Check desktop hiding and mobile display
  assert(css.includes('.btn-header-exam'), '.btn-header-exam desktop button style present');
  assert(css.includes('display: none !important'), 'display: none !important rules present for responsive elements');
}

// -----------------------------------------------------------------------------
// Execution Runner
// -----------------------------------------------------------------------------
try {
  console.log('=== Challenger 2 Empirical Verification & Adversarial Stress Suite ===');
  testProgressModalLifecycle();
  testRapidThemeToggleSync();
  testExamSimulatorIsolation();
  testLectureRelativeNavigationLinks();
  testCssResponsiveAndSafeAreaRules();

  console.log('\n======================================================');
  console.log(`Challenger 2 Results: ${passedTests} passed, ${failedTests} failed`);
  console.log('======================================================');

  if (failedTests > 0) {
    process.exit(1);
  }
} catch (err) {
  console.error('\n[FATAL ERROR during test execution]:', err);
  process.exit(1);
}
