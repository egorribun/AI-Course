/**
 * CourseTracker - LocalStorage-based state & progress management for DL Exam Course.
 */
(function() {
  'use strict';

  const STORAGE_KEYS = {
    THEME: 'ai_course_theme',
    COMPLETED_LECTURES: 'ai_course_completed_lectures',
    CHECKED_QAS: 'ai_course_checked_qas',
    CHECKED_TASKS: 'ai_course_checked_tasks',
    SM2_CARDS: 'ai_course_sm2_cards',
  };

  const TOTAL_LECTURES = 28;
  const TOTAL_QAS = 296;
  const TOTAL_TASKS = 170;

  function safeGetJSON(key, defaultVal) {
    try {
      const data = localStorage.getItem(key);
      if (data === null || data === undefined) {
        return defaultVal;
      }
      const parsed = JSON.parse(data);
      if (Array.isArray(defaultVal)) {
        return Array.isArray(parsed) ? parsed : defaultVal;
      }
      if (typeof defaultVal === 'object' && defaultVal !== null) {
        return (typeof parsed === 'object' && parsed !== null && !Array.isArray(parsed)) ? parsed : defaultVal;
      }
      if (typeof defaultVal === 'string') {
        return typeof parsed === 'string' ? parsed : defaultVal;
      }
      if (typeof defaultVal === 'number') {
        return typeof parsed === 'number' && !isNaN(parsed) ? parsed : defaultVal;
      }
      if (typeof defaultVal === 'boolean') {
        return typeof parsed === 'boolean' ? parsed : defaultVal;
      }
      return parsed !== null && parsed !== undefined ? parsed : defaultVal;
    } catch (e) {
      console.warn('LocalStorage error:', e);
      return defaultVal;
    }
  }

  function safeSetJSON(key, val) {
    try {
      localStorage.setItem(key, JSON.stringify(val));
    } catch (e) {
      console.warn('LocalStorage save error:', e);
    }
  }

  function notifyChange() {
    try {
      window.dispatchEvent(new CustomEvent('course-progress-changed', {
        detail: CourseTracker.getOverallStats()
      }));
    } catch (e) {}
  }

  const CourseTracker = {
    // ---------- Theme ----------
    getTheme() {
      try {
        return localStorage.getItem(STORAGE_KEYS.THEME) || 'dark';
      } catch (e) {
        return 'dark';
      }
    },

    setTheme(theme) {
      const validTheme = theme === 'light' ? 'light' : 'dark';
      try {
        localStorage.setItem(STORAGE_KEYS.THEME, validTheme);
      } catch (e) {}
      document.documentElement.setAttribute('data-theme', validTheme);
      this.updateThemeButtons();
    },

    toggleTheme() {
      const current = this.getTheme();
      const next = current === 'dark' ? 'light' : 'dark';
      this.setTheme(next);
      return next;
    },

    updateThemeButtons() {
      const theme = this.getTheme();
      const isLight = theme === 'light';
      document.querySelectorAll('.theme-toggle').forEach(btn => {
        const isBottomNav = btn.classList.contains('bottom-nav-item');
        const icon = btn.querySelector('.theme-icon');
        const text = btn.querySelector('.theme-text, .theme-label');
        if (icon) {
          icon.textContent = isLight ? '🌙' : '☀️';
        }
        if (text) {
          text.textContent = isBottomNav ? 'Тема' : (isLight ? 'Тёмная тема' : 'Светлая тема');
        }
        if (!icon && !text) {
          if (isBottomNav) {
            btn.innerHTML = `<span class="bottom-nav-icon theme-icon" aria-hidden="true">${isLight ? '🌙' : '☀️'}</span><span class="bottom-nav-label theme-label">Тема</span>`;
          } else {
            btn.innerHTML = `<span class="theme-icon" aria-hidden="true">${isLight ? '🌙' : '☀️'}</span><span class="theme-text">${isLight ? 'Тёмная тема' : 'Светлая тема'}</span>`;
          }
        }
        btn.setAttribute('aria-label', isLight ? 'Включить тёмную тему' : 'Включить светлую тему');
        btn.setAttribute('title', isLight ? 'Включить тёмную тему' : 'Включить светлую тему');
      });
    },

    // ---------- Lectures Progress ----------
    getCompletedLectures() {
      const val = safeGetJSON(STORAGE_KEYS.COMPLETED_LECTURES, []);
      return Array.isArray(val) ? val : [];
    },

    isLectureCompleted(id) {
      const list = this.getCompletedLectures();
      return Array.isArray(list) && list.includes(String(id));
    },

    setLectureCompleted(id, completed) {
      const strId = String(id);
      let list = this.getCompletedLectures();
      if (!Array.isArray(list)) list = [];
      if (completed) {
        if (!list.includes(strId)) list.push(strId);
      } else {
        list = list.filter(item => item !== strId);
      }
      safeSetJSON(STORAGE_KEYS.COMPLETED_LECTURES, list);
      notifyChange();
      return completed;
    },

    toggleLecture(id) {
      const current = this.isLectureCompleted(id);
      return this.setLectureCompleted(id, !current);
    },

    // ---------- QA Items ----------
    getCheckedQAs() {
      const val = safeGetJSON(STORAGE_KEYS.CHECKED_QAS, []);
      return Array.isArray(val) ? val : [];
    },

    isQAChecked(qaId) {
      const list = this.getCheckedQAs();
      return Array.isArray(list) && list.includes(String(qaId));
    },

    setQAChecked(qaId, checked) {
      const strId = String(qaId);
      let list = this.getCheckedQAs();
      if (!Array.isArray(list)) list = [];
      if (checked) {
        if (!list.includes(strId)) list.push(strId);
      } else {
        list = list.filter(item => item !== strId);
      }
      safeSetJSON(STORAGE_KEYS.CHECKED_QAS, list);
      notifyChange();
      return checked;
    },

    toggleQA(qaId) {
      const current = this.isQAChecked(qaId);
      return this.setQAChecked(qaId, !current);
    },

    // ---------- Task Items ----------
    getCheckedTasks() {
      const val = safeGetJSON(STORAGE_KEYS.CHECKED_TASKS, []);
      return Array.isArray(val) ? val : [];
    },

    isTaskChecked(taskId) {
      const list = this.getCheckedTasks();
      return Array.isArray(list) && list.includes(String(taskId));
    },

    setTaskChecked(taskId, checked) {
      const strId = String(taskId);
      let list = this.getCheckedTasks();
      if (!Array.isArray(list)) list = [];
      if (checked) {
        if (!list.includes(strId)) list.push(strId);
      } else {
        list = list.filter(item => item !== strId);
      }
      safeSetJSON(STORAGE_KEYS.CHECKED_TASKS, list);
      notifyChange();
      return checked;
    },

    toggleTask(taskId) {
      const current = this.isTaskChecked(taskId);
      return this.setTaskChecked(taskId, !current);
    },

    // ---------- Direct SM-2 Calculation Helper ----------
    calcSM2(grade, reps, ef, interval) {
      return this.sm2.calculateNextState({
        cardId: '',
        box: 1,
        repetitions: reps,
        easeFactor: ef,
        interval: interval
      }, grade);
    },

    // ---------- Leitner / SM-2 Spaced Repetition Engine ----------
    sm2: {
      getCards() {
        const val = safeGetJSON(STORAGE_KEYS.SM2_CARDS, {});
        return (typeof val === 'object' && val !== null && !Array.isArray(val)) ? val : {};
      },

      getCard(cardId) {
        const cards = this.getCards();
        const strId = String(cardId);
        if (cards[strId]) {
          return cards[strId];
        }
        return {
          cardId: strId,
          box: 1,
          repetitions: 0,
          interval: 1,
          easeFactor: 2.5,
          lastReviewed: null,
          nextReview: null
        };
      },

      calculateNextState(prevState, grade) {
        const q = Math.max(0, Math.min(5, Number(grade) || 0));
        const prev = prevState || {
          cardId: '',
          box: 1,
          repetitions: 0,
          interval: 1,
          easeFactor: 2.5
        };

        let ef = Math.max(1.3, Number(prev.easeFactor) || 2.5);
        let reps = Math.max(0, Number(prev.repetitions) || 0);
        let interval = Math.max(1, Number(prev.interval) || 1);
        let box = Math.max(1, Math.min(5, Number(prev.box) || 1));

        // SM-2 Ease Factor formula: EF' = EF + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        const efDelta = 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02);
        ef = Math.max(1.3, Math.round((ef + efDelta) * 100) / 100);

        if (q >= 3) {
          if (reps === 0) {
            interval = 1;
          } else if (reps === 1) {
            interval = 6;
          } else {
            interval = Math.max(1, Math.round(interval * ef));
          }
          reps += 1;
          box = Math.min(5, box + 1);
        } else {
          reps = 0;
          interval = 1;
          box = 1;
        }

        const now = Date.now();
        const nextReview = now + interval * 24 * 60 * 60 * 1000;

        return {
          cardId: prev.cardId || '',
          box: box,
          repetitions: reps,
          interval: interval,
          easeFactor: ef,
          lastReviewed: now,
          nextReview: nextReview
        };
      },

      recordReview(cardId, grade) {
        const strId = String(cardId);
        const current = this.getCard(strId);
        const nextState = this.calculateNextState(current, grade);
        nextState.cardId = strId;

        const allCards = this.getCards();
        allCards[strId] = nextState;
        safeSetJSON(STORAGE_KEYS.SM2_CARDS, allCards);

        try {
          window.dispatchEvent(new CustomEvent('sm2-card-reviewed', {
            detail: nextState
          }));
        } catch (e) {}

        return nextState;
      },

      isCardDue(cardId) {
        const card = this.getCard(cardId);
        if (!card.nextReview) return true; // never reviewed
        return card.nextReview <= Date.now();
      },

      getStats() {
        const cards = this.getCards();
        const entries = Object.values(cards);
        const boxCounts = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
        let dueCount = 0;
        const now = Date.now();

        entries.forEach(card => {
          const b = Math.max(1, Math.min(5, card.box || 1));
          boxCounts[b] = (boxCounts[b] || 0) + 1;
          if (!card.nextReview || card.nextReview <= now) {
            dueCount++;
          }
        });

        return {
          totalReviewed: entries.length,
          dueCount: dueCount,
          boxCounts: boxCounts,
          matureCount: (boxCounts[4] || 0) + (boxCounts[5] || 0)
        };
      },

      resetSM2() {
        try {
          localStorage.removeItem(STORAGE_KEYS.SM2_CARDS);
        } catch (e) {}
      }
    },

    // ---------- Global Statistics ----------
    getOverallStats() {
      const completedList = this.getCompletedLectures();
      const checkedQAList = this.getCheckedQAs();
      const checkedTaskList = this.getCheckedTasks();

      const completedLecs = Array.isArray(completedList) ? completedList.length : 0;
      const checkedQAs = Array.isArray(checkedQAList) ? checkedQAList.length : 0;
      const checkedTasks = Array.isArray(checkedTaskList) ? checkedTaskList.length : 0;

      const safeLecs = (typeof completedLecs === 'number' && !isNaN(completedLecs) && isFinite(completedLecs)) ? Math.max(0, completedLecs) : 0;
      const safeQAs = (typeof checkedQAs === 'number' && !isNaN(checkedQAs) && isFinite(checkedQAs)) ? Math.max(0, checkedQAs) : 0;
      const safeTasks = (typeof checkedTasks === 'number' && !isNaN(checkedTasks) && isFinite(checkedTasks)) ? Math.max(0, checkedTasks) : 0;

      const lecPct = TOTAL_LECTURES > 0 ? Math.min(100, Math.max(0, Math.round((safeLecs / TOTAL_LECTURES) * 100))) : 0;
      const qaPct = TOTAL_QAS > 0 ? Math.min(100, Math.max(0, Math.round((safeQAs / TOTAL_QAS) * 100))) : 0;
      const taskPct = TOTAL_TASKS > 0 ? Math.min(100, Math.max(0, Math.round((safeTasks / TOTAL_TASKS) * 100))) : 0;
      const totalPct = Math.min(100, Math.max(0, Math.round((lecPct * 0.4) + (qaPct * 0.35) + (taskPct * 0.25))));

      return {
        totalLectures: TOTAL_LECTURES,
        completedLectures: safeLecs,
        lecturePercent: isNaN(lecPct) ? 0 : lecPct,

        totalQAs: TOTAL_QAS,
        checkedQAs: safeQAs,
        qaPercent: isNaN(qaPct) ? 0 : qaPct,

        totalTasks: TOTAL_TASKS,
        checkedTasks: safeTasks,
        taskPercent: isNaN(taskPct) ? 0 : taskPct,

        overallPercent: isNaN(totalPct) ? 0 : totalPct
      };
    },

    exportProgressJSON() {
      return JSON.stringify({
        theme: this.getTheme(),
        completedLectures: this.getCompletedLectures(),
        checkedQAs: this.getCheckedQAs(),
        checkedTasks: this.getCheckedTasks(),
        sm2Cards: this.sm2.getCards(),
        exportedAt: new Date().toISOString()
      }, null, 2);
    },

    importProgressJSON(jsonStr) {
      try {
        const obj = JSON.parse(jsonStr);
        if (obj === null || obj === undefined) {
          return false;
        }
        if (typeof obj === 'object') {
          if (typeof obj.theme === 'string') this.setTheme(obj.theme);
          if (Array.isArray(obj.completedLectures)) safeSetJSON(STORAGE_KEYS.COMPLETED_LECTURES, obj.completedLectures);
          if (Array.isArray(obj.checkedQAs)) safeSetJSON(STORAGE_KEYS.CHECKED_QAS, obj.checkedQAs);
          if (Array.isArray(obj.checkedTasks)) safeSetJSON(STORAGE_KEYS.CHECKED_TASKS, obj.checkedTasks);
          if (obj.sm2Cards && typeof obj.sm2Cards === 'object' && !Array.isArray(obj.sm2Cards)) safeSetJSON(STORAGE_KEYS.SM2_CARDS, obj.sm2Cards);
        }
        notifyChange();
        return true;
      } catch (e) {
        console.error('Import failed:', e);
        return false;
      }
    },

    resetProgress() {
      try {
        localStorage.removeItem(STORAGE_KEYS.COMPLETED_LECTURES);
        localStorage.removeItem(STORAGE_KEYS.CHECKED_QAS);
        localStorage.removeItem(STORAGE_KEYS.CHECKED_TASKS);
        localStorage.removeItem(STORAGE_KEYS.SM2_CARDS);
      } catch (e) {}
      notifyChange();
    }
  };

  // Universal Progress Modal Controller
  function initProgressModal() {
    const modal = document.getElementById('course-progress-modal');
    const openBtn = document.getElementById('nav-progress-btn');
    const closeBtn = document.getElementById('modal-progress-close');
    const closeActionBtn = document.getElementById('modal-close-action-btn');
    const resetBtn = document.getElementById('modal-reset-progress-btn');

    function updateModalStats() {
      if (!modal) return;
      const stats = CourseTracker.getOverallStats();
      const fill = document.getElementById('modal-progress-fill');
      const percent = document.getElementById('modal-progress-percent');
      const lecs = document.getElementById('modal-stat-lecs');
      const qas = document.getElementById('modal-stat-qas');
      const tasks = document.getElementById('modal-stat-tasks');

      if (fill) fill.style.width = `${stats.overallPercent}%`;
      if (percent) percent.textContent = `Общий прогресс: ${stats.overallPercent}%`;
      if (lecs) lecs.textContent = `${stats.completedLectures} / ${stats.totalLectures} (${stats.lecturePercent}%)`;
      if (qas) qas.textContent = `${stats.checkedQAs} / ${stats.totalQAs} (${stats.qaPercent}%)`;
      if (tasks) tasks.textContent = `${stats.checkedTasks} / ${stats.totalTasks} (${stats.taskPercent}%)`;
    }

    function openModal() {
      if (!modal) return;
      updateModalStats();
      modal.removeAttribute('hidden');
      if (closeBtn) closeBtn.focus();
    }

    function closeModal() {
      if (!modal) return;
      modal.setAttribute('hidden', '');
      if (openBtn) openBtn.focus();
    }

    if (openBtn) {
      openBtn.addEventListener('click', openModal);
    }
    if (closeBtn) {
      closeBtn.addEventListener('click', closeModal);
    }
    if (closeActionBtn) {
      closeActionBtn.addEventListener('click', closeModal);
    }
    if (modal) {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
      });
    }
    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        if (confirm('Сбросить весь сохраненный прогресс курса?')) {
          CourseTracker.resetProgress();
          updateModalStats();
        }
      });
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && modal && !modal.hasAttribute('hidden')) {
        e.preventDefault();
        closeModal();
      }
    });

    window.addEventListener('course-progress-changed', () => {
      updateModalStats();
    });
  }

  // Auto-init theme & modal
  document.addEventListener('DOMContentLoaded', () => {
    const currentTheme = CourseTracker.getTheme();
    document.documentElement.setAttribute('data-theme', currentTheme);
    CourseTracker.updateThemeButtons();
    initProgressModal();

    document.querySelectorAll('.theme-toggle').forEach(btn => {
      btn.addEventListener('click', () => {
        CourseTracker.toggleTheme();
      });
    });
  });

  // Auto Service Worker registration for Zero-build PWA
  if (typeof window !== 'undefined' && typeof navigator !== 'undefined' && 'serviceWorker' in navigator) {
    let refreshing = false;
    if (typeof navigator.serviceWorker.addEventListener === 'function') {
      navigator.serviceWorker.addEventListener('controllerchange', () => {
        if (!refreshing) {
          refreshing = true;
          window.location.reload();
        }
      });
    }

    window.addEventListener('load', () => {
      const swPath = window.location.pathname.includes('/lectures/') ? '../sw.js' : './sw.js';
      navigator.serviceWorker.register(swPath).then((reg) => {
        if (reg && typeof reg.update === 'function') {
          reg.update().catch(() => {});
        }
      }).catch((err) => {
        console.debug('ServiceWorker registration note:', err);
      });
    });
  }

  window.CourseTracker = CourseTracker;
})();
