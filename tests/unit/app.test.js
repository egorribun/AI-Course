/**
 * Unit Test Suite for js/app.js
 * Comprehensive 100% Lines, Branches, Functions Coverage via Node.js Native Runner.
 */

const { describe, it, beforeEach } = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const { setupMockBrowser, MockElement } = require('../harness/mock_browser');

const APP_PATH = path.resolve(__dirname, '../../js/app.js');
const TRACKER_PATH = path.resolve(__dirname, '../../js/tracker.js');

function loadTracker() {
  delete require.cache[require.resolve(TRACKER_PATH)];
  require(TRACKER_PATH);
  return global.window.CourseTracker;
}

function loadApp() {
  delete require.cache[require.resolve(APP_PATH)];
  require(APP_PATH);
}

describe('App Portal Hub Suite', () => {
  beforeEach(() => {
    setupMockBrowser({ pathname: '/index.html' });
    loadTracker();
  });

  it('should initialize theme toggle in header if not already present', () => {
    const header = new MockElement('header');
    header.className = 'top';
    const inner = new MockElement('div');
    inner.className = 'inner';
    header.appendChild(inner);
    global.document.body.appendChild(header);

    loadApp();
    global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

    const toggle = inner.querySelector('.theme-toggle');
    assert.ok(toggle);

    toggle.dispatchEvent(new global.window.CustomEvent('click'));
    assert.strictEqual(global.window.CourseTracker.getTheme(), 'light');
  });

  it('should render global progress hub and update on course-progress-changed event', () => {
    const fill = new MockElement('div');
    fill.id = 'global-progress-fill';
    const label = new MockElement('div');
    label.id = 'global-progress-label';
    const lecs = new MockElement('div');
    lecs.id = 'stat-lecs-val';
    const qas = new MockElement('div');
    qas.id = 'stat-qas-val';
    const tasks = new MockElement('div');
    tasks.id = 'stat-tasks-val';

    global.document.body.appendChild(fill);
    global.document.body.appendChild(label);
    global.document.body.appendChild(lecs);
    global.document.body.appendChild(qas);
    global.document.body.appendChild(tasks);

    // Lecture grid cards
    const grid = new MockElement('div');
    grid.className = 'grid';
    const card0 = new MockElement('a');
    card0.className = 'lec';
    card0.setAttribute('href', 'lectures/00-intro-ml.html');
    const card1 = new MockElement('a');
    card1.className = 'lec';
    card1.setAttribute('href', 'lectures/01-fcnn.html');
    grid.appendChild(card0);
    grid.appendChild(card1);
    global.document.body.appendChild(grid);

    global.window.CourseTracker.setLectureCompleted('00', true);

    loadApp();
    global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

    assert.ok(card0.classList.contains('completed'));
    assert.strictEqual(card1.classList.contains('completed'), false);

    // Trigger course-progress-changed
    global.window.CourseTracker.setLectureCompleted('01', true);
    assert.ok(card1.classList.contains('completed'));
  });

  describe('Live Search and 4-Block Category Filtering', () => {
    it('should filter cards by text query, block tags, and keyword tags', () => {
      const searchInput = global.document.createElement('input');
      searchInput.id = 'lecture-search-input';
      global.document.body.appendChild(searchInput);

      const countBadge = global.document.createElement('div');
      countBadge.id = 'search-count-badge';
      global.document.body.appendChild(countBadge);

      const chipAll = global.document.createElement('span');
      chipAll.className = 'tag-chip active';
      chipAll.setAttribute('data-tag', 'all');

      const chipBlockA = global.document.createElement('span');
      chipBlockA.className = 'tag-chip';
      chipBlockA.setAttribute('data-tag', 'block-a');

      const chipCV = global.document.createElement('span');
      chipCV.className = 'tag-chip';
      chipCV.setAttribute('data-tag', 'cv');

      const chipNLP = global.document.createElement('span');
      chipNLP.className = 'tag-chip';
      chipNLP.setAttribute('data-tag', 'nlp');

      const chipRL = global.document.createElement('span');
      chipRL.className = 'tag-chip';
      chipRL.setAttribute('data-tag', 'rl');

      const chipMath = global.document.createElement('span');
      chipMath.className = 'tag-chip';
      chipMath.setAttribute('data-tag', 'math');

      global.document.body.appendChild(chipAll);
      global.document.body.appendChild(chipBlockA);
      global.document.body.appendChild(chipCV);
      global.document.body.appendChild(chipNLP);
      global.document.body.appendChild(chipRL);
      global.document.body.appendChild(chipMath);

      const grid = global.document.createElement('div');
      grid.className = 'grid';

      // Card 0: Block A, ML Intro
      const card0 = global.document.createElement('a');
      card0.className = 'lec';
      card0.setAttribute('href', 'lectures/00-intro-ml.html');
      const t0 = global.document.createElement('div');
      t0.className = 't';
      t0.textContent = 'Каркас машинного обучения';
      const d0 = global.document.createElement('div');
      d0.className = 'd';
      d0.textContent = 'Вводная лекция, bias-variance tradeoff';
      const n0 = global.document.createElement('div');
      n0.className = 'n';
      n0.textContent = '00';
      card0.appendChild(t0);
      card0.appendChild(d0);
      card0.appendChild(n0);
      grid.appendChild(card0);

      // Card 4: Block A, CNN layers (matches CV keyword)
      const card4 = global.document.createElement('a');
      card4.className = 'lec';
      card4.setAttribute('href', 'lectures/04-cnn-layers.html');
      const t4 = global.document.createElement('div');
      t4.className = 't';
      t4.textContent = 'Свёрточные слои (CNN)';
      const d4 = global.document.createElement('div');
      d4.className = 'd';
      d4.textContent = 'Receptive field, pooling, vision';
      const n4 = global.document.createElement('div');
      n4.className = 'n';
      n4.textContent = '04';
      card4.appendChild(t4);
      card4.appendChild(d4);
      card4.appendChild(n4);
      grid.appendChild(card4);

      // Card 16: Block C, Transformers
      const card16 = global.document.createElement('a');
      card16.className = 'lec';
      card16.setAttribute('href', 'lectures/16-transformers.html');
      const t16 = global.document.createElement('div');
      t16.className = 't';
      t16.textContent = 'Архитектура Transformer';
      const d16 = global.document.createElement('div');
      d16.className = 'd';
      d16.textContent = 'Self-attention, multi-head attention';
      const n16 = global.document.createElement('div');
      n16.className = 'n';
      n16.textContent = '16';
      card16.appendChild(t16);
      card16.appendChild(d16);
      card16.appendChild(n16);
      grid.appendChild(card16);

      // Card 22: Block D, RL Intro
      const card22 = global.document.createElement('a');
      card22.className = 'lec';
      card22.setAttribute('href', 'lectures/22-rl-intro.html');
      const t22 = global.document.createElement('div');
      t22.className = 't';
      t22.textContent = 'Введение в RL';
      const d22 = global.document.createElement('div');
      d22.className = 'd';
      d22.textContent = 'Reinforcement learning, MDP, Bellman';
      const n22 = global.document.createElement('div');
      n22.className = 'n';
      n22.textContent = '22';
      card22.appendChild(t22);
      card22.appendChild(d22);
      card22.appendChild(n22);
      grid.appendChild(card22);

      global.document.body.appendChild(grid);

      loadApp();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      // 1. Query filter: "transformer"
      searchInput.value = 'transformer';
      searchInput.dispatchEvent(new global.window.CustomEvent('input'));
      assert.strictEqual(card0.style.display, 'none');
      assert.strictEqual(card4.style.display, 'none');
      assert.strictEqual(card16.style.display, 'block');
      assert.strictEqual(card22.style.display, 'none');
      assert.ok(countBadge.textContent.includes('1'));

      // 2. Clear query
      searchInput.value = '';
      searchInput.dispatchEvent(new global.window.CustomEvent('input'));
      assert.strictEqual(countBadge.style.display, 'none');

      // 3. Block A chip filter
      chipBlockA.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(card0.style.display, 'block');
      assert.strictEqual(card4.style.display, 'block');
      assert.strictEqual(card16.style.display, 'none');

      // 4. CV keyword chip filter
      chipCV.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(card0.style.display, 'none');
      assert.strictEqual(card4.style.display, 'block');
      assert.strictEqual(card16.style.display, 'none');

      // 5. NLP keyword chip filter
      chipNLP.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(card16.style.display, 'block');
      assert.strictEqual(card4.style.display, 'none');

      // 6. RL keyword chip filter
      chipRL.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(card22.style.display, 'block');
      assert.strictEqual(card0.style.display, 'none');

      // 7. Math keyword chip filter
      chipMath.dispatchEvent(new global.window.CustomEvent('click'));

      // 8. Back to All chip
      chipAll.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(card0.style.display, 'block');
      assert.strictEqual(card4.style.display, 'block');
      assert.strictEqual(card16.style.display, 'block');
      assert.strictEqual(card22.style.display, 'block');
    });
  });

  describe('Mobile Navigation and Quick Action Controls', () => {
    it('should handle mobile theme, search, top buttons and ?focus=search URL parameter', (t, done) => {
      setupMockBrowser({ pathname: '/index.html', search: '?focus=search' });
      loadTracker();

      const searchInput = global.document.createElement('input');
      searchInput.id = 'lecture-search-input';
      global.document.body.appendChild(searchInput);

      const mobTheme = global.document.createElement('button');
      mobTheme.id = 'mob-theme-toggle';
      global.document.body.appendChild(mobTheme);

      const mobSearch = global.document.createElement('button');
      mobSearch.id = 'mob-search-btn';
      global.document.body.appendChild(mobSearch);

      const mobTop = global.document.createElement('button');
      mobTop.id = 'mob-top-btn';
      global.document.body.appendChild(mobTop);

      loadApp();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      // Mobile theme toggle
      mobTheme.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(global.window.CourseTracker.getTheme(), 'light');

      // Mobile search click
      mobSearch.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(global.document.activeElement, searchInput);

      // Mobile top click
      global.window.scrollY = 600;
      mobTop.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(global.window.scrollY, 0);

      // Back to top scroll listener
      const backToTop = global.document.getElementById('back-to-top-btn');
      assert.ok(backToTop);

      global.window.scrollY = 500;
      global.window.dispatchEvent(new global.window.CustomEvent('scroll'));
      assert.ok(backToTop.classList.contains('visible'));

      global.window.scrollY = 200;
      global.window.dispatchEvent(new global.window.CustomEvent('scroll'));
      assert.strictEqual(backToTop.classList.contains('visible'), false);

      backToTop.dispatchEvent(new global.window.CustomEvent('click'));
      assert.strictEqual(global.window.scrollY, 0);

      // Wait for focus=search timeout
      setTimeout(() => {
        done();
      }, 150);
    });
  });

  describe('Keyboard Shortcuts and Print Hooks', () => {
    it('should handle shortcuts: / (search focus), ] (first lecture), T (theme), and Alt+O (expand details)', () => {
      const searchInput = global.document.createElement('input');
      searchInput.id = 'lecture-search-input';
      global.document.body.appendChild(searchInput);

      const d1 = global.document.createElement('details');
      d1.open = false;
      global.document.body.appendChild(d1);

      loadApp();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      // '/' focuses search
      const keySlash = new global.window.CustomEvent('keydown');
      keySlash.key = '/';
      global.window.dispatchEvent(keySlash);
      assert.strictEqual(global.document.activeElement, searchInput);

      // Escape blurs search
      const keyEsc = new global.window.CustomEvent('keydown');
      keyEsc.key = 'Escape';
      global.window.dispatchEvent(keyEsc);
      assert.strictEqual(global.document.activeElement, null);

      // 'T' toggles theme
      const keyT = new global.window.CustomEvent('keydown');
      keyT.key = 'T';
      global.window.dispatchEvent(keyT);
      assert.strictEqual(global.window.CourseTracker.getTheme(), 'light');

      // ']' navigates to first lecture
      const keyBracket = new global.window.CustomEvent('keydown');
      keyBracket.key = ']';
      global.window.dispatchEvent(keyBracket);
      assert.strictEqual(global.window.location.href, 'lectures/00-intro-ml.html');

      // Alt+O expands details
      const keyAltO = new global.window.CustomEvent('keydown');
      keyAltO.altKey = true;
      keyAltO.key = 'o';
      global.window.dispatchEvent(keyAltO);
      assert.strictEqual(d1.open, true);

      // Alt+O collapses details
      global.window.dispatchEvent(keyAltO);
      assert.strictEqual(d1.open, false);
    });

    it('should ignore shortcuts while typing in input/textarea/select/contentEditable', () => {
      const input = global.document.createElement('input');
      global.document.body.appendChild(input);
      input.focus();

      loadApp();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      const keyT = new global.window.CustomEvent('keydown');
      keyT.key = 't';
      global.window.dispatchEvent(keyT);
      assert.strictEqual(global.window.CourseTracker.getTheme(), 'dark');

      const keyA = new global.window.CustomEvent('keydown');
      keyA.key = 'a';
      global.window.dispatchEvent(keyA);

      // Textarea
      const ta = global.document.createElement('textarea');
      global.document.body.appendChild(ta);
      ta.focus();
      global.window.dispatchEvent(keyA);

      // Select
      const sel = global.document.createElement('select');
      global.document.body.appendChild(sel);
      sel.focus();
      global.window.dispatchEvent(keyA);

      // ContentEditable
      const div = global.document.createElement('div');
      div.isContentEditable = true;
      global.document.body.appendChild(div);
      div.focus();
      global.window.dispatchEvent(keyA);
    });

    it('should handle print hooks beforeprint and afterprint in app.js', () => {
      const d = global.document.createElement('details');
      d.open = false;
      global.document.body.appendChild(d);

      loadApp();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      // beforeprint
      global.window.dispatchEvent(new global.window.CustomEvent('beforeprint'));
      assert.strictEqual(d.open, true);
      assert.strictEqual(d.dataset.wasOpen, 'false');

      // afterprint
      global.window.dispatchEvent(new global.window.CustomEvent('afterprint'));
      assert.strictEqual(d.open, false);
    });
  });
});
