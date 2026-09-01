/**
 * App - Main portal hub: Live Search, 4-Block Topic Filter Chips, Quick Action Bar, and Global Progress Hub.
 */
document.addEventListener('DOMContentLoaded', () => {
  'use strict';

  // 1. Theme Toggle in Top Header
  const headerInner = document.querySelector('header.top .inner');
  if (headerInner && !document.querySelector('.theme-toggle')) {
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'theme-toggle';
    toggleBtn.type = 'button';
    toggleBtn.innerHTML = (window.CourseTracker && window.CourseTracker.getTheme() === 'light')
      ? '🌙 Тёмная тема'
      : '☀️ Светлая тема';
    toggleBtn.addEventListener('click', () => {
      if (window.CourseTracker) window.CourseTracker.toggleTheme();
    });
    headerInner.appendChild(toggleBtn);
  }

  // 2. Global Progress Hub Rendering
  function updateProgressUI(stats) {
    if (!stats && window.CourseTracker) {
      stats = window.CourseTracker.getOverallStats();
    }
    if (!stats) return;

    const fill = document.getElementById('global-progress-fill');
    const label = document.getElementById('global-progress-label');
    const lecCount = document.getElementById('stat-lecs-val');
    const qaCount = document.getElementById('stat-qas-val');
    const taskCount = document.getElementById('stat-tasks-val');

    if (fill) fill.style.width = `${stats.overallPercent}%`;
    if (label) label.textContent = `Общий прогресс: ${stats.overallPercent}%`;
    if (lecCount) lecCount.textContent = `${stats.completedLectures} / ${stats.totalLectures} (${stats.lecturePercent}%)`;
    if (qaCount) qaCount.textContent = `${stats.checkedQAs} / ${stats.totalQAs} (${stats.qaPercent}%)`;
    if (taskCount) taskCount.textContent = `${stats.checkedTasks} / ${stats.totalTasks} (${stats.taskPercent}%)`;

    // Mark completed lecture cards in the grid
    if (window.CourseTracker) {
      document.querySelectorAll('.grid .lec').forEach(card => {
        const href = card.getAttribute('href') || '';
        const match = href.match(/(\d{2})-/);
        if (match) {
          const lecId = match[1];
          const isDone = window.CourseTracker.isLectureCompleted(lecId);
          card.classList.toggle('completed', isDone);
        }
      });
    }
  }

  window.addEventListener('course-progress-changed', (e) => {
    updateProgressUI(e.detail);
  });

  updateProgressUI();

  // 3. Live Search & 4-Block Category Filtering
  const searchInput = document.getElementById('lecture-search-input');
  const tagChips = document.querySelectorAll('.tag-chip');
  const lecCards = document.querySelectorAll('.grid .lec');
  const searchCountEl = document.getElementById('search-count-badge');

  let activeTag = 'all';

  const BLOCK_MAP = {
    'block-a': ['00', '01', '02', '03', '04', '05', '06', '07'],
    'a': ['00', '01', '02', '03', '04', '05', '06', '07'],
    'block-b': ['08', '09', '10', '11', '12', '13'],
    'b': ['08', '09', '10', '11', '12', '13'],
    'block-c': ['14', '15', '16', '17', '18', '19', '20', '21'],
    'c': ['14', '15', '16', '17', '18', '19', '20', '21'],
    'block-d': ['22', '23', '24', '25', '26', '27'],
    'd': ['22', '23', '24', '25', '26', '27']
  };

  const TAG_KEYWORDS = {
    cv: ['свёрт', 'cnn', 'vision', 'детекц', 'сегмент', 'lenet', 'resnet', 'yolo', 'u-net', 'зрение'],
    nlp: ['трансформ', 'transformer', 'attention', 'вниман', 'текст', 'word2vec', 'bleu', 'bert', 'gpt', 'токен', 'языков'],
    rl: ['rl', 'reinforcement', 'беллман', 'подкреплен', 'агент', 'sarsa', 'q-learning', 'policy', 'actor-critic', 'cem', 'mdp'],
    math: ['backprop', 'производн', 'mle', 'loss', 'матрич', 'autograd', 'pinn', 'оптимиз', 'adam', 'sgd', 'elbo', 'vae', 'gan']
  };

  function filterCards() {
    const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
    let visibleCount = 0;

    lecCards.forEach(card => {
      const title = (card.querySelector('.t')?.textContent || '').toLowerCase();
      const desc = (card.querySelector('.d')?.textContent || '').toLowerCase();
      const num = (card.querySelector('.n')?.textContent || '').toLowerCase();
      const href = card.getAttribute('href') || '';
      const match = href.match(/(\d{2})-/);
      const lecId = match ? match[1] : '';
      const combined = `${title} ${desc} ${num}`;

      // Tag match
      let matchesTag = true;
      if (activeTag !== 'all') {
        if (BLOCK_MAP[activeTag]) {
          matchesTag = BLOCK_MAP[activeTag].includes(lecId);
        } else if (TAG_KEYWORDS[activeTag]) {
          const kws = TAG_KEYWORDS[activeTag] || [];
          matchesTag = kws.some(kw => combined.includes(kw));
        }
      }

      // Query match
      let matchesQuery = true;
      if (query.length > 0) {
        matchesQuery = combined.includes(query);
      }

      if (matchesTag && matchesQuery) {
        card.style.display = 'block';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    if (searchCountEl) {
      if (query.length > 0 || activeTag !== 'all') {
        searchCountEl.textContent = `Найдено лекций: ${visibleCount} из ${lecCards.length}`;
        searchCountEl.style.display = 'inline-block';
      } else {
        searchCountEl.style.display = 'none';
      }
    }
  }

  if (searchInput) {
    searchInput.addEventListener('input', filterCards);
  }

  tagChips.forEach(chip => {
    chip.addEventListener('click', () => {
      tagChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      activeTag = chip.getAttribute('data-tag') || 'all';
      filterCards();
    });
  });

  // 4. Back to Top Button
  let backToTop = document.getElementById('back-to-top-btn') || document.getElementById('back-to-top');
  if (!backToTop) {
    backToTop = document.createElement('button');
    backToTop.className = 'back-to-top';
    backToTop.id = 'back-to-top-btn';
    backToTop.innerHTML = '↑';
    backToTop.setAttribute('aria-label', 'Наверх страницы');
    document.body.appendChild(backToTop);
  }

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

  // 5. Mobile Quick Action Bar Buttons
  const mobThemeBtn = document.getElementById('mob-theme-toggle');
  const mobSearchBtn = document.getElementById('mob-search-btn');
  const mobTopBtn = document.getElementById('mob-top-btn');

  if (mobThemeBtn) {
    mobThemeBtn.addEventListener('click', () => {
      if (window.CourseTracker) window.CourseTracker.toggleTheme();
    });
  }

  if (mobSearchBtn) {
    mobSearchBtn.addEventListener('click', () => {
      if (searchInput) {
        searchInput.focus();
        searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    });
  }

  if (mobTopBtn) {
    mobTopBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // 6. Global Keyboard Shortcuts
  window.addEventListener('keydown', (e) => {
    const active = document.activeElement;
    const isInput = active && (
      active.tagName === 'INPUT' ||
      active.tagName === 'TEXTAREA' ||
      active.tagName === 'SELECT' ||
      active.isContentEditable
    );

    // Escape key blurs active input
    if (e.key === 'Escape' && isInput) {
      active.blur();
      return;
    }

    // Bypass shortcuts when typing inside form inputs
    if (isInput) return;

    // T / t : Toggle Theme
    if (e.key === 't' || e.key === 'T') {
      e.preventDefault();
      if (window.CourseTracker) window.CourseTracker.toggleTheme();
      return;
    }

    // / : Focus Search Input
    if (e.key === '/') {
      const searchBox = document.getElementById('lecture-search-input');
      if (searchBox) {
        e.preventDefault();
        searchBox.focus();
        searchBox.select();
      }
      return;
    }

    // ] : Navigate to first lecture from portal
    if (e.key === ']') {
      window.location.href = 'lectures/00-intro-ml.html';
      return;
    }

    // Alt+O : Expand / Collapse all spoilers
    if (e.altKey && (e.key === 'o' || e.key === 'O' || e.code === 'KeyO')) {
      e.preventDefault();
      const allDetails = Array.from(document.querySelectorAll('details'));
      if (allDetails.length === 0) return;
      const anyClosed = allDetails.some(d => !d.open);
      allDetails.forEach(d => { d.open = anyClosed; });
    }
  });

  // 7. Print CSS Support - open details before print and restore after
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
