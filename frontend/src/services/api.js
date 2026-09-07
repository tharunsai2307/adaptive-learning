import axios from 'axios';

const API_BASE = '';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Attach token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Intercept 401s to clean up expired sessions
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
    return detail.map((d) => (typeof d === 'string' ? d : d?.msg || JSON.stringify(d))).join(', ');
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
};

// ── Profile ────────────────────────────────────────────────────────
export const profileAPI = {
  get: () => api.get('/api/profile/me'),
  save: (data) => api.post('/api/profile/save', data),
  selectSubject: (subjectId) => api.post(`/api/profile/select-subject?subject_id=${subjectId}`),
};

// ── Subjects ───────────────────────────────────────────────────────
export const subjectsAPI = {
  list: (education, year, department) =>
    api.get(`/api/subjects/?education=${education}&year=${year}&department=${department}`),
  departments: (education) =>
    api.get(`/api/subjects/departments${education ? `?education=${education}` : ''}`),
};

// ── Topics ─────────────────────────────────────────────────────────
export const topicsAPI = {
  list: (subjectId) => api.get(`/api/topics/?subject_id=${subjectId}`),
  get: (topicId) => api.get(`/api/topics/${topicId}`),
  learningPath: (subjectId) => api.get(`/api/topics/learning-path/${subjectId}`),
};

// ── Quiz ───────────────────────────────────────────────────────────
export const quizAPI = {
  questions: (topicId) => api.get(`/api/quiz/questions/${topicId}`),
  submit: (data) => api.post('/api/quiz/submit', data),
};

// ── Tutor ──────────────────────────────────────────────────────────
export const tutorAPI = {
  ask: (topicId, question) => api.post('/api/tutor/ask', { topic_id: topicId, question }),
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
