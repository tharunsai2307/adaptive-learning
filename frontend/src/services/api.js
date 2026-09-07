import axios from 'axios';

// Empty baseURL => requests go to this origin (e.g. /api/...). The Vite dev
// server proxies them to the FastAPI backend, so this works both locally and
// behind the sandbox preview host without any hardcoded localhost URLs.
const api = axios.create({
  baseURL: '',
  headers: { 'Content-Type': 'application/json' },
});

// Attach the JWT to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Clean up expired sessions on 401
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
    return Promise.reject(error);
  }
);

export const getErrorMessage = (err, fallback = 'Something went wrong') => {
  const detail = err?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => (typeof d === 'string' ? d : d?.msg || JSON.stringify(d)))
      .join(', ');
  }
  if (detail && typeof detail === 'object') {
    return detail.msg || detail.message || JSON.stringify(detail);
  }
  return err?.message || fallback;
};

// ── Auth ───────────────────────────────────────────────────────────
export const authAPI = {
  signup: (data) => api.post('/api/auth/signup', data),
  login: (data) => api.post('/api/auth/login', data),
  me: () => api.get('/api/auth/me'),
};

// ── Profile ────────────────────────────────────────────────────────
export const profileAPI = {
  get: () => api.get('/api/profile/me'),
  save: (data) => api.post('/api/profile/save', data),
  selectSubject: (subjectId) =>
    api.post('/api/profile/select-subject', null, { params: { subject_id: subjectId } }),
};

// ── Subjects ───────────────────────────────────────────────────────
export const subjectsAPI = {
  list: (education, year, department) =>
    api.get('/api/subjects/', { params: { education, year, department } }),
  departments: (education) =>
    api.get('/api/subjects/departments', { params: education ? { education } : {} }),
  options: () => api.get('/api/subjects/options'),
};

// ── Topics ─────────────────────────────────────────────────────────
export const topicsAPI = {
  list: (subjectId) => api.get('/api/topics/', { params: { subject_id: subjectId } }),
  get: (topicId) => api.get(`/api/topics/${topicId}`),
  learningPath: (subjectId) => api.get(`/api/topics/learning-path/${subjectId}`),
};

// ── Quiz ───────────────────────────────────────────────────────────
export const quizAPI = {
  questions: (topicId) => api.get(`/api/quiz/questions/${topicId}`),
  submit: (data) => api.post('/api/quiz/submit', data),
  result: (topicId) => api.get(`/api/quiz/result/${topicId}`),
};

// ── Tutor ──────────────────────────────────────────────────────────
export const tutorAPI = {
  ask: (topicId, question) => api.post('/api/tutor/ask', { topic_id: topicId, question }),
  status: () => api.get('/api/tutor/status'),
};

// ── Dashboard ──────────────────────────────────────────────────────
export const dashboardAPI = {
  get: () => api.get('/api/dashboard/'),
  performanceHistory: () => api.get('/api/dashboard/performance-history'),
};

// ── Q-Learning ─────────────────────────────────────────────────────
export const qlearningAPI = {
  qTable: () => api.get('/api/qlearning/q-table'),
  lastDecision: () => api.get('/api/qlearning/last-decision'),
};

export default api;
