import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

// Auth token injection
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response error handling
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// Auth
export const authAPI = {
  login: (email, password) => {
    const form = new FormData();
    form.append('username', email);
    form.append('password', password);
    return api.post('/auth/login', form, { headers: { 'Content-Type': 'multipart/form-data' } });
  },
  register: (name, email, password) => api.post('/auth/register', { name, email, password }),
};

// Metrics
export const metricsAPI = {
  getLive: () => api.get('/metrics/live'),
  collect: (projectName, region = 'us-east') =>
    api.post(`/metrics/collect?project_name=${encodeURIComponent(projectName)}&region=${region}`),
  getRegions: () => api.get('/metrics/regions'),
};

// Carbon
export const carbonAPI = {
  estimate: (params) => api.get('/carbon/estimate', { params }),
};

// Green Score
export const greenScoreAPI = {
  calculate: (params) => api.get('/greenscore/calculate', { params }),
};

// Suggestions
export const suggestionsAPI = {
  generate: (params) => api.get('/suggestions/generate', { params }),
  scan: (directory) => api.get('/suggestions/scan', { params: { directory } }),
  refactor: (payload) => api.post('/suggestions/refactor', payload),
};

// Certificates
export const certificateAPI = {
  generate: (projectId, projectName) =>
    api.post('/certificate/generate', { project_id: projectId, project_name: projectName }),
  list: () => api.get('/certificate/list'),
  getHtml: (certId) => api.get(`/certificate/${certId}/html`, { responseType: 'text' }),
};

// History
export const historyAPI = {
  getProjects: (params) => api.get('/history/projects', { params }),
  getProjectNames: () => api.get('/history/projects/names'),
  getTrends: (projectName) => api.get('/history/trends', { params: { project_name: projectName } }),
  getSummary: () => api.get('/history/summary'),
};

export default api;
