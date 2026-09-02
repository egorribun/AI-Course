/**
 * Lightweight Zero-Dependency Browser & DOM Mock Harness for Node.js Native Test Runner.
 */

class MockDOMTokenList {
  constructor(element) {
    this._element = element;
    this._tokens = new Set();
  }
  add(...tokens) {
    tokens.forEach(t => this._tokens.add(t));
    this._sync();
  }
  remove(...tokens) {
    tokens.forEach(t => this._tokens.delete(t));
    this._sync();
  }
  toggle(token, force) {
    let result;
    if (force !== undefined) {
      if (force) {
        this._tokens.add(token);
        result = true;
      } else {
        this._tokens.delete(token);
        result = false;
      }
    } else {
      if (this._tokens.has(token)) {
        this._tokens.delete(token);
        result = false;
      } else {
        this._tokens.add(token);
        result = true;
      }
    }
    this._sync();
    return result;
  }
  contains(token) {
    return this._tokens.has(token);
  }
  _sync() {
    if (this._element) {
      this._element.className = Array.from(this._tokens).join(' ');
    }
  }
  _parse(className) {
    this._tokens.clear();
    if (className) {
      className.split(/\s+/).filter(Boolean).forEach(t => this._tokens.add(t));
    }
  }
}

let currentActiveElementState = { current: null };

class MockElement {
  constructor(tagName = 'div', activeElementState = null) {
    this.tagName = tagName.toUpperCase();
    this.attributes = {};
    this.dataset = {};
    this.children = [];
    this.parentNode = null;
    this._activeElementState = activeElementState || currentActiveElementState;
    this.listeners = {};
    this.style = {};
    this.classList = new MockDOMTokenList(this);
    this._innerHTML = '';
    this._textContent = '';
    this.checked = false;
    this.value = '';
    this.open = false;
    this.isContentEditable = false;
    this.scrollTop = 0;
    this.scrollHeight = 1000;
    this.clientHeight = 500;
  }

  get id() {
    return this.attributes.id || '';
  }
  set id(val) {
    this.setAttribute('id', val);
  }

  get className() {
    return this.attributes.class || '';
  }
  set className(val) {
    this.setAttribute('class', val);
    this.classList._parse(val);
  }

  get textContent() {
    return this._textContent || this.innerText || '';
  }
  set textContent(val) {
    this._textContent = String(val);
    this._innerHTML = String(val);
  }

  get innerText() {
    return this._textContent || '';
  }
  set innerText(val) {
    this._textContent = String(val);
  }

  get innerHTML() {
    return this._innerHTML;
  }
  set innerHTML(val) {
    this._innerHTML = String(val);
    // Simple child simulation from basic HTML tags if needed
    this._parseHTMLToMock(val);
  }

  _parseHTMLToMock(html) {
    // Retain existing listeners or create basic structure
    this.children = [];
    if (!html) return;
    // Extract tags roughly for selector queries
    const tagMatches = html.match(/<([a-zA-Z0-9-]+)([^>]*)>/g) || [];
    tagMatches.forEach(tagStr => {
      const tagMatch = tagStr.match(/<([a-zA-Z0-9-]+)/);
      if (tagMatch) {
        const tag = tagMatch[1].toLowerCase();
        if (tag === 'br' || tag === 'hr' || tag === 'span' || tag === 'div' || tag === 'button' || tag === 'input' || tag === 'details' || tag === 'summary' || tag === 'p' || tag === 'option' || tag === 'select' || tag === 'label' || tag === 'h3' || tag === 'h4' || tag === 'ol' || tag === 'li' || tag === 'a' || tag === 'pre' || tag === 'code') {
          const child = new MockElement(tag, this._activeElementState);
          child.parentNode = this;
          // Extract class
          const classMatch = tagStr.match(/class=["']([^"']+)["']/);
          if (classMatch) child.className = classMatch[1];
          // Extract id
          const idMatch = tagStr.match(/id=["']([^"']+)["']/);
          if (idMatch) child.id = idMatch[1];
          // Extract data- attributes
          const dataMatches = tagStr.match(/data-([a-zA-Z0-9-]+)=["']([^"']+)["']/g) || [];
          dataMatches.forEach(dm => {
            const m = dm.match(/data-([a-zA-Z0-9-]+)=["']([^"']+)["']/);
            if (m) {
              child.dataset[m[1]] = m[2];
              child.setAttribute(`data-${m[1]}`, m[2]);
            }
          });
          // Extract type
          const typeMatch = tagStr.match(/type=["']([^"']+)["']/);
          if (typeMatch) child.type = typeMatch[1];
          // Extract value
          const valMatch = tagStr.match(/value=["']([^"']+)["']/);
          if (valMatch) child.value = valMatch[1];
          // Extract checked
          if (tagStr.includes('checked')) child.checked = true;

          this.children.push(child);
        }
      }
    });
  }

  setAttribute(k, v) {
    this.attributes[k] = String(v);
    if (k.startsWith('data-')) {
      const prop = k.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      this.dataset[prop] = String(v);
    }
    if (k === 'class') {
      this.classList._parse(String(v));
    }
  }

  getAttribute(k) {
    return Object.prototype.hasOwnProperty.call(this.attributes, k) ? this.attributes[k] : null;
  }

  removeAttribute(k) {
    delete this.attributes[k];
    if (k.startsWith('data-')) {
      const prop = k.slice(5).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      delete this.dataset[prop];
    }
    if (k === 'class') {
      this.classList._tokens.clear();
    }
  }

  hasAttribute(k) {
    return Object.prototype.hasOwnProperty.call(this.attributes, k);
  }

  appendChild(child) {
    if (child) {
      child.parentNode = this;
      this.children.push(child);
    }
    return child;
  }

  prepend(child) {
    if (child) {
      child.parentNode = this;
      this.children.unshift(child);
    }
    return child;
  }

  removeChild(child) {
    const idx = this.children.indexOf(child);
    if (idx !== -1) {
      this.children.splice(idx, 1);
      child.parentNode = null;
    }
    return child;
  }

  insertBefore(newNode, referenceNode) {
    const idx = this.children.indexOf(referenceNode);
    newNode.parentNode = this;
    if (idx !== -1) {
      this.children.splice(idx, 0, newNode);
    } else {
      this.children.push(newNode);
    }
    return newNode;
  }

  addEventListener(evt, cb) {
    this.listeners[evt] = this.listeners[evt] || [];
    this.listeners[evt].push(cb);
  }

  removeEventListener(evt, cb) {
    if (this.listeners[evt]) {
      this.listeners[evt] = this.listeners[evt].filter(fn => fn !== cb);
    }
  }

  dispatchEvent(evt) {
    evt.target = evt.target || this;
    evt.currentTarget = this;
    const handlers = this.listeners[evt.type] || [];
    handlers.forEach(cb => cb.call(this, evt));
    return !evt.defaultPrevented;
  }

  focus() {
    this._activeElementState.current = this;
  }

  blur() {
    if (this._activeElementState.current === this) {
      this._activeElementState.current = null;
    }
  }

  select() {
    this.focus();
  }

  scrollIntoView() {}

  querySelector(selector) {
    const all = this.querySelectorAll(selector);
    return all.length > 0 ? all[0] : null;
  }

  querySelectorAll(selector) {
    const results = [];
    const matchElement = (el) => {
      if (_matchesSelector(el, selector)) {
        results.push(el);
      }
      (el.children || []).forEach(matchElement);
    };
    (this.children || []).forEach(matchElement);
    return results;
  }
}

function _matchesSingle(el, sel) {
  if (!el || !sel) return false;
  sel = sel.trim();
  if (!sel) return false;

  // Extract ID if present: #id
  const idMatch = sel.match(/#([a-zA-Z0-9-_]+)/);
  if (idMatch && el.id !== idMatch[1]) return false;

  // Extract attributes if present: [attr] or [attr="val"]
  const attrRegex = /\[([a-zA-Z0-9-_]+)(?:=["']?([^"'\]]*)["']?)?\]/g;
  let attrMatch;
  while ((attrMatch = attrRegex.exec(sel)) !== null) {
    const attrName = attrMatch[1];
    const attrVal = attrMatch[2];
    if (attrVal !== undefined) {
      if (el.getAttribute(attrName) !== attrVal) return false;
    } else {
      if (!el.hasAttribute(attrName)) return false;
    }
  }

  // Strip ID and attributes to parse tag and classes
  const cleanSel = sel.replace(/#[a-zA-Z0-9-_]+/g, '').replace(/\[[^\]]+\]/g, '').trim();
  if (cleanSel) {
    const parts = cleanSel.split('.');
    const tag = parts[0];
    const classes = parts.slice(1);
    if (tag && el.tagName.toLowerCase() !== tag.toLowerCase()) return false;
    if (classes.length > 0 && !classes.every(c => el.classList.contains(c))) return false;
  }

  return true;
}

function _matchesCompound(el, compoundSel) {
  const parts = compoundSel.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return false;
  if (parts.length === 1) return _matchesSingle(el, parts[0]);

  // Last part must match el
  if (!_matchesSingle(el, parts[parts.length - 1])) return false;

  // Preceding parts must match ancestors in sequence
  let currParent = el.parentNode;
  for (let i = parts.length - 2; i >= 0; i--) {
    const part = parts[i];
    let found = false;
    while (currParent) {
      if (_matchesSingle(currParent, part)) {
        found = true;
        currParent = currParent.parentNode;
        break;
      }
      currParent = currParent.parentNode;
    }
    if (!found) return false;
  }
  return true;
}

function _matchesSelector(el, selector) {
  if (!el || !selector) return false;
  const groups = selector.split(',').map(s => s.trim()).filter(Boolean);
  return groups.some(group => _matchesCompound(el, group));
}

/**
 * Setup a fresh Mock Browser environment.
 */
function setupMockBrowser(options = {}) {
  const store = {};
  const activeElementState = { current: null };
  currentActiveElementState = activeElementState;
  const docListeners = {};
  const winListeners = {};

  const localStorage = {
    getItem: (k) => (Object.prototype.hasOwnProperty.call(store, k) ? store[k] : null),
    setItem: (k, v) => { store[k] = String(v); },
    removeItem: (k) => { delete store[k]; },
    clear: () => { Object.keys(store).forEach(k => delete store[k]); },
    _store: store
  };

  const documentElement = new MockElement('html', activeElementState);
  documentElement.scrollTop = 0;
  documentElement.scrollHeight = 1000;
  documentElement.clientHeight = 500;

  const body = new MockElement('body', activeElementState);
  documentElement.appendChild(body);

  const elementsById = new Map();

  const document = {
    documentElement,
    body,
    readyState: 'complete',
    get activeElement() {
      return activeElementState.current;
    },
    createElement: (tag) => new MockElement(tag, activeElementState),
    getElementById: (id) => {
      if (elementsById.has(id)) return elementsById.get(id);
      return documentElement.querySelector(`#${id}`);
    },
    querySelector: (sel) => documentElement.querySelector(sel),
    querySelectorAll: (sel) => documentElement.querySelectorAll(sel),
    addEventListener: (evt, cb) => {
      docListeners[evt] = docListeners[evt] || [];
      docListeners[evt].push(cb);
    },
    removeEventListener: (evt, cb) => {
      if (docListeners[evt]) {
        docListeners[evt] = docListeners[evt].filter(fn => fn !== cb);
      }
    },
    dispatchEvent: (evt) => {
      evt.target = evt.target || document;
      const handlers = docListeners[evt.type] || [];
      handlers.forEach(cb => cb.call(document, evt));
      return !evt.defaultPrevented;
    },
    execCommand: () => true
  };

  class MockCustomEvent {
    constructor(type, options = {}) {
      this.type = type;
      this.detail = options.detail || null;
      this.bubbles = !!options.bubbles;
      this.cancelable = !!options.cancelable;
      this.defaultPrevented = false;
    }
    preventDefault() {
      this.defaultPrevented = true;
    }
    stopPropagation() {}
  }

  class MockAudioContext {
    constructor() {
      this.currentTime = 0;
      this.destination = {};
    }
    createOscillator() {
      return {
        type: 'sine',
        frequency: { value: 440 },
        connect: () => {},
        start: () => {},
        stop: () => {}
      };
    }
    createGain() {
      return {
        gain: {
          setValueAtTime: () => {},
          exponentialRampToValueAtTime: () => {}
        },
        connect: () => {}
      };
    }
  }

  const window = {
    document,
    localStorage,
    location: {
      href: options.pathname ? `http://localhost${options.pathname}` : 'http://localhost/index.html',
      pathname: options.pathname || '/index.html',
      search: options.search || '',
      reload: () => { window.location._reloaded = true; },
      _reloaded: false
    },
    scrollY: 0,
    scrollTo: (opts) => {
      if (typeof opts === 'object' && opts.top !== undefined) {
        window.scrollY = opts.top;
      }
    },
    AudioContext: MockAudioContext,
    webkitAudioContext: MockAudioContext,
    CustomEvent: MockCustomEvent,
    navigator: {
      clipboard: {
        writeText: (text) => {
          window.navigator.clipboard._lastCopied = text;
          return Promise.resolve();
        },
        _lastCopied: null
      },
      serviceWorker: {
        addEventListener: (evt, cb) => {
          window.navigator.serviceWorker._listeners[evt] = window.navigator.serviceWorker._listeners[evt] || [];
          window.navigator.serviceWorker._listeners[evt].push(cb);
        },
        register: (swPath) => {
          window.navigator.serviceWorker._lastRegisteredPath = swPath;
          return Promise.resolve({
            update: () => Promise.resolve()
          });
        },
        _listeners: {},
        _lastRegisteredPath: null
      }
    },
    addEventListener: (evt, cb) => {
      winListeners[evt] = winListeners[evt] || [];
      winListeners[evt].push(cb);
    },
    removeEventListener: (evt, cb) => {
      if (winListeners[evt]) {
        winListeners[evt] = winListeners[evt].filter(fn => fn !== cb);
      }
    },
    dispatchEvent: (evt) => {
      evt.target = evt.target || window;
      const handlers = winListeners[evt.type] || [];
      handlers.forEach(cb => cb.call(window, evt));
      return !evt.defaultPrevented;
    },
    MathJax: {
      typesetPromise: () => Promise.resolve()
    }
  };

  // Assign to global using Object.defineProperty to override Node 24 built-ins
  const globals = {
    window,
    document,
    localStorage,
    navigator: window.navigator,
    CustomEvent: MockCustomEvent,
    AudioContext: MockAudioContext,
    confirm: () => true
  };

  for (const [key, val] of Object.entries(globals)) {
    try {
      Object.defineProperty(global, key, {
        value: val,
        configurable: true,
        writable: true
      });
    } catch (e) {
      global[key] = val;
    }
  }

  return {
    window,
    document,
    localStorage,
    docListeners,
    winListeners,
    activeElementState,
    elementsById
  };
}

module.exports = {
  MockElement,
  MockDOMTokenList,
  setupMockBrowser
};
