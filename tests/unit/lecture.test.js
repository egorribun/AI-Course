/**
 * Unit Test Suite for js/lecture.js
 * Comprehensive 100% Lines, Branches, Functions Coverage via Node.js Native Runner.
 */

const { describe, it, beforeEach } = require('node:test');
const assert = require('node:assert');
const path = require('node:path');
const { setupMockBrowser, MockElement } = require('../harness/mock_browser');

const LECTURE_PATH = path.resolve(__dirname, '../../js/lecture.js');
const TRACKER_PATH = path.resolve(__dirname, '../../js/tracker.js');

function loadTracker() {
  delete require.cache[require.resolve(TRACKER_PATH)];
  require(TRACKER_PATH);
  return global.window.CourseTracker;
}

function loadLecture() {
  delete require.cache[require.resolve(LECTURE_PATH)];
  require(LECTURE_PATH);
}

describe('Lecture Suite', () => {
  beforeEach(() => {
    setupMockBrowser({ pathname: '/lectures/01-fcnn.html' });
    loadTracker();
  });

  it('should initialize reading progress bar and handle scroll', () => {
    loadLecture();
    global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

    const bar = global.document.getElementById('reading-progress');
    assert.ok(bar);
    assert.strictEqual(bar.className, 'reading-progress');

    // Scroll with height > 0
    global.document.documentElement.scrollTop = 250;
    global.document.documentElement.scrollHeight = 1000;
    global.document.documentElement.clientHeight = 500;
    global.window.dispatchEvent(new global.window.CustomEvent('scroll'));
    assert.strictEqual(bar.style.width, '50%');

    // Scroll with height = 0
    global.document.documentElement.scrollTop = 0;
    global.document.documentElement.scrollHeight = 500;
    global.document.documentElement.clientHeight = 500;
    global.window.dispatchEvent(new global.window.CustomEvent('scroll'));
    assert.strictEqual(bar.style.width, '0%');
  });

  it('should add theme toggle to header and toggle theme on click (light and dark branches)', () => {
    const header = new MockElement('header');
    header.className = 'top';
    const inner = new MockElement('div');
    inner.className = 'inner';
    header.appendChild(inner);
    global.document.body.appendChild(header);

    // Initial dark theme
    loadLecture();
    global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

    const toggle = inner.querySelector('.theme-toggle');
    assert.ok(toggle);
    assert.strictEqual(toggle.getAttribute('aria-label'), 'Включить светлую тему');

    toggle.dispatchEvent(new global.window.CustomEvent('click'));
    assert.strictEqual(global.window.CourseTracker.getTheme(), 'light');

    // Re-run with light theme initial
    setupMockBrowser({ pathname: '/lectures/01-fcnn.html' });
    loadTracker();
    global.window.CourseTracker.setTheme('light');
    const header2 = new MockElement('header');
    header2.className = 'top';
    const inner2 = new MockElement('div');
    inner2.className = 'inner';
    header2.appendChild(inner2);
    global.document.body.appendChild(header2);

    loadLecture();
    global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));
    const toggle2 = inner2.querySelector('.theme-toggle');
    assert.ok(toggle2);
    assert.strictEqual(toggle2.getAttribute('aria-label'), 'Включить тёмную тему');
  });

  it('should add code copy buttons to <pre> with clipboard and fallback paths', async () => {
    const pre1 = new MockElement('pre');
    const code1 = new MockElement('code');
    code1.innerText = 'import torch\nx = torch.randn(2, 3)';
    pre1.appendChild(code1);
    global.document.body.appendChild(pre1);

    const pre2 = new MockElement('pre');
    pre2.innerText = 'plain text inside pre';
    global.document.body.appendChild(pre2);

    // pre with existing copy-btn should be skipped
    const pre3 = new MockElement('pre');
    const existingBtn = new MockElement('button');
    existingBtn.className = 'copy-btn';
    pre3.appendChild(existingBtn);
    global.document.body.appendChild(pre3);

    loadLecture();
    global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

    const copyBtn1 = pre1.querySelector('.copy-btn');
    assert.ok(copyBtn1);

    // Click on copyBtn1 with navigator.clipboard
    await copyBtn1.dispatchEvent(new global.window.CustomEvent('click'));
    assert.strictEqual(global.navigator.clipboard._lastCopied, 'import torch\nx = torch.randn(2, 3)');
    assert.strictEqual(copyBtn1.textContent, '✓ Скопировано!');
    assert.ok(copyBtn1.classList.contains('copied'));

    // Fallback: without navigator.clipboard
    const origClipboard = global.navigator.clipboard;
    global.navigator.clipboard = null;
    const copyBtn2 = pre2.querySelector('.copy-btn');
    await copyBtn2.dispatchEvent(new global.window.CustomEvent('click'));
    assert.strictEqual(copyBtn2.textContent, '✓ Скопировано!');

    // Error path
    global.navigator.clipboard = {
      writeText: () => Promise.reject(new Error('Copy denied'))
    };
    await copyBtn1.dispatchEvent(new global.window.CustomEvent('click'));

    global.navigator.clipboard = origClipboard;
  });

  it('should extract lecture ID fallback when URL does not have number pattern', () => {
    setupMockBrowser({ pathname: '/other/page.html' });
    loadTracker();

    const qa = new MockElement('details');
    qa.className = 'qa';
    const summary = new MockElement('summary');
    summary.innerText = 'Вопрос без номера?';
    qa.appendChild(summary);
    global.document.body.appendChild(qa);

    loadLecture();
    global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

    const checkWrap = summary.querySelector('.item-check');
    assert.ok(checkWrap);
    const checkbox = checkWrap.querySelector('input');
    assert.ok(checkbox);
    assert.strictEqual(checkbox.id, 'l00_qa0');
  });

  it('should bind interactive QA checkboxes with stopPropagation and state sync', () => {
    const qa = new MockElement('details');
    qa.className = 'qa';
    const summary = new MockElement('summary');
    summary.innerText = 'Что такое SGD?';
    qa.appendChild(summary);
    global.document.body.appendChild(qa);

    // Pre-checked QA
    global.window.CourseTracker.setQAChecked('l01_qa0', true);

    loadLecture();
    global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

    const checkWrap = summary.querySelector('.item-check');
    assert.ok(checkWrap);
    assert.ok(checkWrap.classList.contains('checked'));
    const checkbox = checkWrap.querySelector('input');
    assert.ok(checkbox);

    // Stop propagation on click
    let stopped = false;
    const clickEvt = new global.window.CustomEvent('click');
    clickEvt.stopPropagation = () => { stopped = true; };
    checkWrap.dispatchEvent(clickEvt);
    assert.strictEqual(stopped, true);

    // Toggle check
    checkbox.checked = false;
    const changeEvt = new global.window.CustomEvent('change');
    changeEvt.target = checkbox;
    checkbox.dispatchEvent(changeEvt);

    assert.strictEqual(global.window.CourseTracker.isQAChecked('l01_qa0'), false);
    assert.strictEqual(checkWrap.classList.contains('checked'), false);

    // Check again
    checkbox.checked = true;
    checkbox.dispatchEvent(changeEvt);
    assert.strictEqual(global.window.CourseTracker.isQAChecked('l01_qa0'), true);
    assert.ok(checkWrap.classList.contains('checked'));
  });

  it('should bind interactive Task checkboxes with .tt and without .tt', () => {
    // Task 1 with .tt (pre-checked)
    global.window.CourseTracker.setTaskChecked('l01_t0', true);

    const task1 = new MockElement('div');
    task1.className = 'task';
    const tt1 = new MockElement('div');
    tt1.className = 'tt';
    tt1.innerText = 'Задача 1: Расчёт прямого прохода';
    task1.appendChild(tt1);
    global.document.body.appendChild(task1);

    // Task 2 without .tt
    const task2 = new MockElement('div');
    task2.className = 'task';
    global.document.body.appendChild(task2);

    loadLecture();
    global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

    const checkWrap1 = task1.querySelector('.item-check');
    assert.ok(checkWrap1);
    assert.ok(checkWrap1.classList.contains('checked'));
    const checkbox1 = checkWrap1.querySelector('input');

    checkbox1.checked = false;
    const changeEvt = new global.window.CustomEvent('change');
    changeEvt.target = checkbox1;
    checkbox1.dispatchEvent(changeEvt);

    assert.strictEqual(global.window.CourseTracker.isTaskChecked('l01_t0'), false);
    assert.strictEqual(checkWrap1.classList.contains('checked'), false);

    const checkWrap2 = task2.querySelector('.item-check');
    assert.ok(checkWrap2);
  });

  it('should handle floating back to top button visibility and smooth scroll', () => {
    loadLecture();
    global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

    const backToTop = global.document.getElementById('back-to-top');
    assert.ok(backToTop);

    global.window.scrollY = 500;
    global.window.dispatchEvent(new global.window.CustomEvent('scroll'));
    assert.ok(backToTop.classList.contains('visible'));

    global.window.scrollY = 200;
    global.window.dispatchEvent(new global.window.CustomEvent('scroll'));
    assert.strictEqual(backToTop.classList.contains('visible'), false);

    backToTop.dispatchEvent(new global.window.CustomEvent('click'));
    assert.strictEqual(global.window.scrollY, 0);
  });

  describe('Keyboard Shortcuts and Navigation', () => {
    it('should handle lecture navigation [, ], and theme toggle T', () => {
      const navrow = new MockElement('div');
      navrow.className = 'navrow';

      const prevLink = new MockElement('a');
      prevLink.className = 'backlink';
      prevLink.textContent = '← Назад к лекции 00';
      prevLink.setAttribute('href', '00-intro-ml.html');

      const nextLink = new MockElement('a');
      nextLink.className = 'backlink';
      nextLink.textContent = 'Вперёд к лекции 02 →';
      nextLink.setAttribute('href', '02-autodiff-pinn.html');

      navrow.appendChild(prevLink);
      navrow.appendChild(nextLink);
      global.document.body.appendChild(navrow);

      loadLecture();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      // Key 'T'
      const keyT = new global.window.CustomEvent('keydown');
      keyT.key = 'T';
      global.window.dispatchEvent(keyT);
      assert.strictEqual(global.window.CourseTracker.getTheme(), 'light');

      // Key '['
      const keyPrev = new global.window.CustomEvent('keydown');
      keyPrev.key = '[';
      global.window.dispatchEvent(keyPrev);
      assert.strictEqual(global.window.location.href, '00-intro-ml.html');

      // Key ']'
      const keyNext = new global.window.CustomEvent('keydown');
      keyNext.key = ']';
      global.window.dispatchEvent(keyNext);
      assert.strictEqual(global.window.location.href, '02-autodiff-pinn.html');
    });

    it('should handle navigation shortcuts when nav links do not exist', () => {
      loadLecture();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      const keyPrev = new global.window.CustomEvent('keydown');
      keyPrev.key = '[';
      global.window.dispatchEvent(keyPrev);

      const keyNext = new global.window.CustomEvent('keydown');
      keyNext.key = ']';
      global.window.dispatchEvent(keyNext);
    });

    it('should blur on Escape and ignore shortcuts while typing in inputs, textarea, select, contentEditable', () => {
      // 1. Input
      const input = global.document.createElement('input');
      global.document.body.appendChild(input);
      input.focus();

      loadLecture();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      // Escape key blurs input
      const escEvt = new global.window.CustomEvent('keydown');
      escEvt.key = 'Escape';
      global.window.dispatchEvent(escEvt);
      assert.strictEqual(global.document.activeElement, null);

      // Focus again and type regular key 'a' (isInput early return)
      input.focus();
      const keyA = new global.window.CustomEvent('keydown');
      keyA.key = 'a';
      global.window.dispatchEvent(keyA);

      // Focus again and trigger T shortcut (should be ignored)
      const keyT = new global.window.CustomEvent('keydown');
      keyT.key = 't';
      global.window.dispatchEvent(keyT);
      assert.strictEqual(global.window.CourseTracker.getTheme(), 'dark');

      // 2. Textarea
      const textarea = global.document.createElement('textarea');
      global.document.body.appendChild(textarea);
      textarea.focus();
      global.window.dispatchEvent(keyA);

      // 3. Select
      const select = global.document.createElement('select');
      global.document.body.appendChild(select);
      select.focus();
      global.window.dispatchEvent(keyA);

      // 4. ContentEditable
      const divEdit = global.document.createElement('div');
      divEdit.isContentEditable = true;
      global.document.body.appendChild(divEdit);
      divEdit.focus();
      global.window.dispatchEvent(keyA);
    });

    it('should expand/collapse all details on Alt+O and handle empty details', () => {
      // Empty details case
      loadLecture();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      const altO = new global.window.CustomEvent('keydown');
      altO.altKey = true;
      altO.key = 'o';
      global.window.dispatchEvent(altO);

      // With details
      const d1 = new MockElement('details');
      d1.open = false;
      const d2 = new MockElement('details');
      d2.open = true;
      global.document.body.appendChild(d1);
      global.document.body.appendChild(d2);

      // Alt+O expands all
      global.window.dispatchEvent(altO);
      assert.strictEqual(d1.open, true);
      assert.strictEqual(d2.open, true);

      // Alt+O collapses all
      global.window.dispatchEvent(altO);
      assert.strictEqual(d1.open, false);
      assert.strictEqual(d2.open, false);
    });

    it('should handle print hooks beforeprint and afterprint', () => {
      const d = new MockElement('details');
      d.open = false;
      global.document.body.appendChild(d);

      loadLecture();
      global.document.dispatchEvent(new global.window.CustomEvent('DOMContentLoaded'));

      // beforeprint opens details
      global.window.dispatchEvent(new global.window.CustomEvent('beforeprint'));
      assert.strictEqual(d.open, true);
      assert.strictEqual(d.dataset.wasOpen, 'false');

      // afterprint restores details
      global.window.dispatchEvent(new global.window.CustomEvent('afterprint'));
      assert.strictEqual(d.open, false);
    });
  });
});
