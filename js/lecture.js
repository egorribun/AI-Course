/**
 * Lecture interactivity: Code copying, reading progress bar, Back to Top, QA/Task checkmark bindings.
 */
document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // 1. Reading Progress Bar
  const progressBar = document.createElement('div');
  progressBar.className = 'reading-progress';
  progressBar.id = 'reading-progress';
  document.body.prepend(progressBar);

  window.addEventListener('scroll', () => {
    const winScroll = document.documentElement.scrollTop || document.body.scrollTop;
    const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    const scrolled = height > 0 ? (winScroll / height) * 100 : 0;
    progressBar.style.width = scrolled + '%';
  }, { passive: true });

  // 2. Theme Toggle in Header
  const headerInner = document.querySelector('header.top .inner');
  if (headerInner && !document.querySelector('.theme-toggle')) {
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'theme-toggle';
    toggleBtn.type = 'button';
    const isLight = window.CourseTracker && window.CourseTracker.getTheme() === 'light';
    toggleBtn.innerHTML = `<span class="theme-icon" aria-hidden="true">${isLight ? '🌙' : '☀️'}</span><span class="theme-text">${isLight ? 'Тёмная тема' : 'Светлая тема'}</span>`;
    toggleBtn.setAttribute('aria-label', isLight ? 'Включить тёмную тему' : 'Включить светлую тему');
    toggleBtn.setAttribute('title', isLight ? 'Включить тёмную тему' : 'Включить светлую тему');
    toggleBtn.addEventListener('click', () => {
      if (window.CourseTracker) window.CourseTracker.toggleTheme();
    });
    headerInner.appendChild(toggleBtn);
  }

  // 3. Code Copy Buttons on <pre>
  document.querySelectorAll('pre').forEach((pre) => {
    if (pre.querySelector('.copy-btn')) return;
    const btn = document.createElement('button');
    btn.className = 'copy-btn';
    btn.type = 'button';
    btn.textContent = '📋 Копировать';
    btn.setAttribute('aria-label', 'Скопировать код');

    btn.addEventListener('click', async () => {
      const code = pre.querySelector('code');
      const textToCopy = code ? code.innerText : pre.innerText;
      try {
        if (typeof navigator !== 'undefined' && navigator.clipboard && navigator.clipboard.writeText) {
          await navigator.clipboard.writeText(textToCopy);
        } else {
          const ta = document.createElement('textarea');
          ta.value = textToCopy;
          ta.style.position = 'fixed';
          ta.style.left = '-9999px';
          document.body.appendChild(ta);
          ta.select();
          document.execCommand('copy');
          document.body.removeChild(ta);
        }
        btn.textContent = '✓ Скопировано!';
        btn.classList.add('copied');
        setTimeout(() => {
          btn.textContent = '📋 Копировать';
          btn.classList.remove('copied');
        }, 2000);
      } catch (err) {
        console.warn('Clipboard write failed:', err);
      }
    });

    pre.appendChild(btn);
  });

  // 4. Extract Lecture Number from URL (e.g. 00, 01, 16)
  const path = window.location.pathname;
  const match = path.match(/(\d{2})-/);
  const lectureId = match ? match[1] : '00';

  // 5. Interactive QA Checkmarks
  document.querySelectorAll('.qa').forEach((qa, idx) => {
    const summary = qa.querySelector('summary');
    if (!summary || summary.querySelector('.item-check')) return;

    const qaId = `l${lectureId}_qa${idx}`;
    const checkWrap = document.createElement('span');
    checkWrap.className = 'item-check';
    
    const isChecked = window.CourseTracker ? window.CourseTracker.isQAChecked(qaId) : false;
    if (isChecked) checkWrap.classList.add('checked');

    checkWrap.innerHTML = `<input type="checkbox" id="${qaId}" ${isChecked ? 'checked' : ''}> <label for="${qaId}">Выучено</label>`;

    checkWrap.addEventListener('click', (e) => {
      e.stopPropagation(); // prevent expanding/collapsing <details>
    });

    const checkbox = checkWrap.querySelector('input');
    checkbox.addEventListener('change', (e) => {
      const checked = e.target.checked;
      if (window.CourseTracker) window.CourseTracker.setQAChecked(qaId, checked);
      checkWrap.classList.toggle('checked', checked);
    });

    summary.appendChild(checkWrap);
  });

  // 6. Interactive Task Checkmarks
  document.querySelectorAll('.task').forEach((task, idx) => {
    if (task.querySelector('.item-check')) return;
    const taskId = `l${lectureId}_t${idx}`;
    const tt = task.querySelector('.tt');

    const checkWrap = document.createElement('span');
    checkWrap.className = 'item-check';
    const isChecked = window.CourseTracker ? window.CourseTracker.isTaskChecked(taskId) : false;
    if (isChecked) checkWrap.classList.add('checked');

    checkWrap.innerHTML = `<input type="checkbox" id="${taskId}" ${isChecked ? 'checked' : ''}> <label for="${taskId}">Решено</label>`;

    const checkbox = checkWrap.querySelector('input');
    checkbox.addEventListener('change', (e) => {
      const checked = e.target.checked;
      if (window.CourseTracker) window.CourseTracker.setTaskChecked(taskId, checked);
      checkWrap.classList.toggle('checked', checked);
    });

    if (tt) {
      const headerDiv = document.createElement('div');
      headerDiv.className = 'task-header';
      tt.parentNode.insertBefore(headerDiv, tt);
      headerDiv.appendChild(tt);
      headerDiv.appendChild(checkWrap);
    } else {
      task.prepend(checkWrap);
    }
  });

  // 7. Floating Back to Top Button
  const backToTop = document.createElement('button');
  backToTop.className = 'back-to-top';
  backToTop.id = 'back-to-top';
  backToTop.innerHTML = '↑';
  backToTop.setAttribute('aria-label', 'Наверх страницы');
  document.body.appendChild(backToTop);

  window.addEventListener('scroll', () => {
    if (window.scrollY > 400) {
      backToTop.classList.add('visible');
    } else {
      backToTop.classList.remove('visible');
    }
  }, { passive: true });

  backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  // 8. Global Keyboard Shortcuts
  function getLectureNavHrefs() {
    const navLinks = Array.from(document.querySelectorAll('.navrow a.backlink, header.top a.backlink'));
    let prevHref = null;
    let nextHref = null;
    navLinks.forEach(a => {
      const text = a.textContent || '';
      const href = a.getAttribute('href');
      if (text.includes('←') || text.includes('Назад') || text.includes('В оглавление')) {
        if (!prevHref) prevHref = href;
      } else if (text.includes('→') || text.includes('Вперёд')) {
        if (!nextHref) nextHref = href;
      }
    });
    return { prevHref, nextHref };
  }

  window.addEventListener('keydown', (e) => {
    const active = document.activeElement;
    const isInput = active && (
      active.tagName === 'INPUT' ||
      active.tagName === 'TEXTAREA' ||
      active.tagName === 'SELECT' ||
      active.isContentEditable
    );

    if (e.key === 'Escape' && isInput) {
      active.blur();
      return;
    }

    if (isInput) return;

    // T / t : Toggle Theme
    if (e.key === 't' || e.key === 'T') {
      e.preventDefault();
      if (window.CourseTracker) window.CourseTracker.toggleTheme();
      return;
    }

    // [ : Navigate to previous lecture
    if (e.key === '[') {
      const { prevHref } = getLectureNavHrefs();
      if (prevHref) {
        window.location.href = prevHref;
      }
      return;
    }

    // ] : Navigate to next lecture
    if (e.key === ']') {
      const { nextHref } = getLectureNavHrefs();
      if (nextHref) {
        window.location.href = nextHref;
      }
      return;
    }

    // Alt+O : Expand / Collapse all spoilers on page
    if (e.altKey && (e.key === 'o' || e.key === 'O' || e.code === 'KeyO')) {
      e.preventDefault();
      const allDetails = Array.from(document.querySelectorAll('details'));
      if (allDetails.length === 0) return;
      const anyClosed = allDetails.some(d => !d.open);
      allDetails.forEach(d => { d.open = anyClosed; });
    }
  });

  // 9. Print Support - open all details before print and restore after
  window.addEventListener('beforeprint', () => {
    document.querySelectorAll('details').forEach(d => {
      d.dataset.wasOpen = d.open ? 'true' : 'false';
      d.open = true;
    });
  });

  window.addEventListener('afterprint', () => {
    document.querySelectorAll('details').forEach(d => {
      if (d.dataset.wasOpen === 'false') {
        d.open = false;
      }
    });
  });
});
