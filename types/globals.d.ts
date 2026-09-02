/**
 * Global TypeScript ambient type definitions for DL Exam Course.
 */

interface SM2CardState {
  cardId: string;
  box: number;
  repetitions: number;
  interval: number;
  easeFactor: number;
  lastReviewed: number | null;
  nextReview: number | null;
}

interface SM2Stats {
  totalReviewed: number;
  dueCount: number;
  boxCounts: Record<number, number>;
  matureCount: number;
}

interface OverallProgressStats {
  totalLectures: number;
  completedLectures: number;
  lecturePercent: number;
  totalQAs: number;
  checkedQAs: number;
  qaPercent: number;
  totalTasks: number;
  checkedTasks: number;
  taskPercent: number;
  overallPercent: number;
}

interface CourseTrackerInstance {
  getTheme(): string;
  setTheme(theme: string): void;
  toggleTheme(): string;
  updateThemeButtons(): void;
  getCompletedLectures(): string[];
  isLectureCompleted(id: string | number): boolean;
  setLectureCompleted(id: string | number, completed: boolean): boolean;
  toggleLecture(id: string | number): boolean;
  getCheckedQAs(): string[];
  isQAChecked(qaId: string): boolean;
  setQAChecked(qaId: string, checked: boolean): boolean;
  toggleQA(qaId: string): boolean;
  getCheckedTasks(): string[];
  isTaskChecked(taskId: string): boolean;
  setTaskChecked(taskId: string, checked: boolean): boolean;
  toggleTask(taskId: string): boolean;
  calcSM2(grade: number, reps: number, ef: number, interval: number): SM2CardState;
  sm2: {
    getCards(): Record<string, SM2CardState>;
    getCard(cardId: string): SM2CardState;
    calculateNextState(prevState: SM2CardState | null, grade: number): SM2CardState;
    recordReview(cardId: string, grade: number): SM2CardState;
    isCardDue(cardId: string): boolean;
    getStats(): SM2Stats;
    resetSM2(): void;
  };
  getOverallStats(): OverallProgressStats;
  exportProgressJSON(): string;
  importProgressJSON(jsonStr: string): boolean;
  resetProgress(): void;
}

interface ExamQA {
  question: string;
  answer: string;
}

interface ExamTask {
  title: string;
  problem: string;
  solution: string;
}

interface ExamLectureData {
  id: string;
  filename: string;
  title: string;
  ticket: string;
  module: string;
  qas: ExamQA[];
  tasks: ExamTask[];
  cheat_items: string[];
}

interface ExamSimulatorInstance {
  init(): void;
  renderRandomTicket(ticketData: ExamLectureData): void;
  toggleTimer(): void;
  resetTimer(): void;
  getLectureBlock(lecId: string | number): string;
  getLectureTopic(lecId: string | number): string;
}

interface Window {
  CourseTracker?: CourseTrackerInstance;
  ExamSimulator?: ExamSimulatorInstance;
  EXAM_DATA?: ExamLectureData[];
  MathJax?: {
    typesetPromise?: (elements?: any[]) => Promise<void>;
  };
  webkitAudioContext?: typeof AudioContext;
  skipWaiting?: () => Promise<void>;
  clients?: Clients;
}

declare var CourseTracker: CourseTrackerInstance | undefined;
declare var ExamSimulator: ExamSimulatorInstance | undefined;
declare var EXAM_DATA: ExamLectureData[] | undefined;
