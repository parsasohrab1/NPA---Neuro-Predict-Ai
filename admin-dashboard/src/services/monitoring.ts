import axios from '../config/api'

export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy'
  services: {
    database?: { status: string; latency?: number }
    redis?: { status: string; latency?: number }
    [key: string]: any
  }
  timestamp: string
}

export interface SystemMetrics {
  metrics: {
    users_total?: number
    patients_total?: number
    predictions_total?: number
    requests_total?: number
    predictions_today?: number
    patients_today?: number
    [key: string]: any
  }
  timestamp: string
}

export interface BusinessKPIs {
  total_patients: number
  total_predictions: number
  predictions_today: number
  patients_today: number
  high_risk_cases: number
  average_prediction_time: number
  success_rate: number
  [key: string]: any
}

export interface SLOStatus {
  p95_latency: number
  p99_latency: number
  error_rate: number
  uptime_percentage: number
  status: 'compliant' | 'at_risk' | 'violated'
}

export interface ActivityItem {
  id: string
  type: 'info' | 'warning' | 'error' | 'success'
  message: string
  timestamp: string
  details?: any
}

export interface ModelMetrics {
  status: string
  has_metrics?: boolean
  overall_accuracy?: number
  alzheimer_accuracy?: number
  parkinson_accuracy?: number
  alzheimer_f1?: number
  parkinson_f1?: number
  validation_date?: string
  test_samples?: number
  alzheimer?: {
    accuracy: number
    precision: number
    recall: number
    f1: number
  }
  parkinson?: {
    accuracy: number
    precision: number
    recall: number
    f1: number
  }
}

const monitoringApi = {
  // Health checks
  async getHealth(): Promise<HealthStatus> {
    const response = await axios.get('/api/v1/monitoring/health')
    return response.data
  },

  async getLiveness(): Promise<{ status: string }> {
    const response = await axios.get('/api/v1/monitoring/health/live')
    return response.data
  },

  async getReadiness(): Promise<{ status: string }> {
    const response = await axios.get('/api/v1/monitoring/health/ready')
    return response.data
  },

  // Metrics
  async getMetrics(): Promise<SystemMetrics> {
    const response = await axios.get('/api/v1/monitoring/metrics')
    return response.data
  },

  async getPrometheusMetrics(): Promise<string> {
    const response = await axios.get('/api/v1/monitoring/metrics/prometheus', {
      responseType: 'text',
    })
    return response.data
  },

  // Business KPIs
  async getKPIs(): Promise<BusinessKPIs> {
    const response = await axios.get('/api/v1/monitoring/kpis')
    return response.data
  },

  // SLO Status
  async getSLOStatus(): Promise<SLOStatus> {
    const response = await axios.get('/api/v1/monitoring/slo')
    return response.data
  },

  // Admin overview (combined data)
  async getOverview(): Promise<{
    health: HealthStatus
    metrics: SystemMetrics
    kpis: BusinessKPIs
    counts?: { users: number; patients: number; predictions: number }
    recent_alerts?: Array<{
      id: string | number
      event_type: string
      severity: string
      timestamp: string
      description: string
      ip_address?: string
      success?: boolean
    }>
  }> {
    const response = await axios.get('/api/v1/admin/system/overview')
    return response.data
  },

  // Activity Feed
  async getActivityFeed(limit: number = 20): Promise<Array<{
    id: string
    type: 'info' | 'warning' | 'error' | 'success'
    message: string
    timestamp: string
    details?: any
  }>> {
    const response = await axios.get('/api/v1/admin/system/activity-feed', {
      params: { limit },
    })
    return response.data
  },

  // Model Metrics
  async getModelMetrics(): Promise<ModelMetrics> {
    const response = await axios.get('/api/v1/model-metrics/current')
    return response.data
  },

  async getModelSummary(): Promise<ModelMetrics> {
    const response = await axios.get('/api/v1/model-metrics/summary')
    return response.data
  },
}

export default monitoringApi

