import axios from 'axios';

// Use proxy in dev (Vite proxies /api -> localhost:8001) to avoid CORS and wrong port
const API_URL = import.meta.env.VITE_API_URL || '/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests (use same key as LoginPage / devAuth: auth_token)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// On 401, clear auth and redirect to login
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('auth_token');
      sessionStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export const monitoringApi = {
  // AI/ML Health
  getMLHealth: (hours: number = 24) =>
    api.get(`/monitoring/ai/ml-health?hours=${hours}`),
  
  getFeatureImportance: (limit: number = 20, hours: number = 24) =>
    api.get(`/monitoring/ai/feature-importance?limit=${limit}&hours=${hours}`),
  
  getModelPerformance: (modelVersion?: string, hours: number = 24) => {
    const params = new URLSearchParams({ hours: hours.toString() });
    if (modelVersion) params.append('model_version', modelVersion);
    return api.get(`/monitoring/ai/model-performance?${params}`);
  },

  getMultimodalSummary: (hours: number = 24) =>
    api.get(`/monitoring/ai/multimodal-summary?hours=${hours}`),

  // Clinical Monitoring
  getLongitudinalTracking: (patientId: number) =>
    api.get(`/monitoring/clinical/longitudinal/${patientId}`),
  
  getSmartAlerts: () =>
    api.get('/monitoring/clinical/smart-alerts'),
  
  getPredictionQueue: () =>
    api.get('/monitoring/clinical/prediction-queue'),

  // System Health
  getSystemHealth: () =>
    api.get('/monitoring/system/health'),
  
  getSystemPerformance: (hours: number = 24) =>
    api.get(`/monitoring/system/performance?hours=${hours}`),
  
  getServicesStatus: () =>
    api.get('/monitoring/system/services'),

  // Security & Compliance
  getAuditLogs: (limit: number = 100, actionType?: string, hours: number = 24) => {
    const params = new URLSearchParams({
      limit: limit.toString(),
      hours: hours.toString(),
    });
    if (actionType) params.append('action_type', actionType);
    return api.get(`/monitoring/security/audit-logs?${params}`);
  },
  
  getAuthenticationMonitoring: (hours: number = 24) =>
    api.get(`/monitoring/security/authentication-monitoring?hours=${hours}`),
  
  getAdminActivity: (hours: number = 24) =>
    api.get(`/monitoring/security/admin-activity?hours=${hours}`),
};

// Disease tracking: Parkinson's & Alzheimer's ranges and patient classification
export const usersApi = {
  getAll: (skip = 0, limit = 100) =>
    api.get('/users/', { params: { skip, limit } }),
  create: (data: Record<string, unknown>) =>
    api.post('/users/', data),
  update: (id: number, data: Record<string, unknown>) =>
    api.put(`/users/${id}`, data),
  delete: (id: number) =>
    api.delete(`/users/${id}`),
};

export const adminSettingsApi = {
  getPasswordPolicy: () =>
    api.get('/admin/settings/security/password-policy'),
  updatePasswordPolicy: (data: Record<string, unknown>) =>
    api.put('/admin/settings/security/password-policy', data),
};

export const diseaseApi = {
  getFeatureRanges: () => api.get('/disease-tracking/feature-ranges'),
  getPatientsSummary: () => api.get('/disease-tracking/all-patients/summary'),
};

// Data monitoring: MRI, Biomarkers, Cognitive (synthetic/dataset from data generator)
export const dataApi = {
  getOverview: (disease?: string) => {
    const params = disease && disease !== 'all' ? `?disease=${disease}` : '';
    return api.get(`/data-monitoring/overview${params}`);
  },
  getCategoryData: (category: 'cognitive' | 'biomarker' | 'imaging', timeRange: string = '30d', disease?: string) => {
    const params = new URLSearchParams({ time_range: timeRange });
    if (disease && disease !== 'all') params.append('disease', disease);
    return api.get(`/data-monitoring/category/${category}?${params}`);
  },
  loadSampleData: () => api.post('/data-monitoring/load-sample-data'),
};

export default api;

