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
      return data ? JSON.parse(data) : defaultVal;
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
        btn.innerHTML = isLight ? '🌙 Тёмная тема' : '☀️ Светлая тема';
        btn.setAttribute('aria-label', isLight ? 'Включить тёмную тему' : 'Включить светлую тему');
      });
    },

    // ---------- Lectures Progress ----------
    getCompletedLectures() {
      return safeGetJSON(STORAGE_KEYS.COMPLETED_LECTURES, []);
    },

    isLectureCompleted(id) {
      const list = this.getCompletedLectures();
      return list.includes(String(id));
    },

    setLectureCompleted(id, completed) {
      const strId = String(id);
      let list = this.getCompletedLectures();
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
      return safeGetJSON(STORAGE_KEYS.CHECKED_QAS, []);
    },

    isQAChecked(qaId) {
      const list = this.getCheckedQAs();
      return list.includes(String(qaId));
    },

    setQAChecked(qaId, checked) {
      const strId = String(qaId);
      let list = this.getCheckedQAs();
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
      return safeGetJSON(STORAGE_KEYS.CHECKED_TASKS, []);
    },

    isTaskChecked(taskId) {
      const list = this.getCheckedTasks();
      return list.includes(String(taskId));
    },

    setTaskChecked(taskId, checked) {
      const strId = String(taskId);
      let list = this.getCheckedTasks();
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

    // ---------- Leitner / SM-2 Spaced Repetition Engine ----------
    sm2: {
      getCards() {
        return safeGetJSON(STORAGE_KEYS.SM2_CARDS, {});
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
        const q = Math.max(0, Math.min(5, Number(grade)));
        const prev = prevState || {
          cardId: '',
          box: 1,
          repetitions: 0,
          interval: 1,
          easeFactor: 2.5
        };

        let ef = Number(prev.easeFactor) || 2.5;
        let reps = Number(prev.repetitions) || 0;
        let interval = Number(prev.interval) || 1;
        let box = Number(prev.box) || 1;

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
          cardId: prev.cardId,
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
      const completedLecs = this.getCompletedLectures().length;
      const checkedQAs = this.getCheckedQAs().length;
      const checkedTasks = this.getCheckedTasks().length;

      const lecPct = Math.round((completedLecs / TOTAL_LECTURES) * 100);
      const qaPct = Math.round((checkedQAs / TOTAL_QAS) * 100);
      const taskPct = Math.round((checkedTasks / TOTAL_TASKS) * 100);
      const totalPct = Math.round((lecPct * 0.4) + (qaPct * 0.35) + (taskPct * 0.25));

      return {
        totalLectures: TOTAL_LECTURES,
        completedLectures: completedLecs,
        lecturePercent: lecPct,

        totalQAs: TOTAL_QAS,
        checkedQAs: checkedQAs,
        qaPercent: qaPct,

        totalTasks: TOTAL_TASKS,
        checkedTasks: checkedTasks,
        taskPercent: taskPct,

        overallPercent: Math.min(100, Math.max(0, totalPct))
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
        if (obj.theme) this.setTheme(obj.theme);
        if (Array.isArray(obj.completedLectures)) safeSetJSON(STORAGE_KEYS.COMPLETED_LECTURES, obj.completedLectures);
        if (Array.isArray(obj.checkedQAs)) safeSetJSON(STORAGE_KEYS.CHECKED_QAS, obj.checkedQAs);
        if (Array.isArray(obj.checkedTasks)) safeSetJSON(STORAGE_KEYS.CHECKED_TASKS, obj.checkedTasks);
        if (obj.sm2Cards && typeof obj.sm2Cards === 'object') safeSetJSON(STORAGE_KEYS.SM2_CARDS, obj.sm2Cards);
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

  // Auto-init theme
  document.addEventListener('DOMContentLoaded', () => {
    const currentTheme = CourseTracker.getTheme();
    document.documentElement.setAttribute('data-theme', currentTheme);
    CourseTracker.updateThemeButtons();
  });

  // Auto Service Worker registration for Zero-build PWA
  if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      const swPath = window.location.pathname.includes('/lectures/') ? '../sw.js' : './sw.js';
      navigator.serviceWorker.register(swPath).catch((err) => {
        console.debug('ServiceWorker registration note:', err);
      });
    });
  }

  window.CourseTracker = CourseTracker;
})();
