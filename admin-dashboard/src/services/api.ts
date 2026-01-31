import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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

export default api;

