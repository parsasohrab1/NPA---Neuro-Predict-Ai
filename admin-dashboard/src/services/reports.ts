import axios from 'axios'

const API_BASE = '/api/v1/reports'

export type ClinicalReportFilters = {
  patientId: number
  start?: string
  end?: string
}

export type ResearchReportFilters = {
  start?: string
  end?: string
  diseaseType?: string
  riskLevel?: string
}

export type ManagementReportFilters = {
  modelVersion?: string
  start?: string
  end?: string
}

export type ClinicalReport = {
  patient: {
    id: number
    patient_identifier: string
    full_name: string
    age: number
    gender: string
  }
  predictions: Array<{
    id: number
    created_at: string
    disease_type: string
    alzheimer_risk_score?: number
    alzheimer_risk_level?: string
    parkinson_risk_score?: number
    parkinson_risk_level?: string
    recommendations?: string
  }>
  last_medical_record_at?: string | null
  pending_follow_up: boolean
}

export type ResearchReport = {
  total_predictions: number
  unique_patients: number
  aggregation: Array<{
    disease_type: string
    risk_level?: string | null
    count: number
  }>
  timeframe_start?: string | null
  timeframe_end?: string | null
}

export type ManagementReport = {
  kpi: {
    total_predictions: number
    reviewed_predictions: number
    active_patients: number
    avg_response_time_ms?: number | null
  }
  model_version_distribution: Record<string, number>
  alerts: Array<{
    title: string
    severity: string
    description: string
    created_at: string
  }>
}

export type ReportExportResponse = {
  message: string
  report_type: string
  format: string
  generated_at: string
}

const buildParams = (filters: Record<string, unknown>) => {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, String(value))
    }
  })
  return params
}

export const reportsService = {
  async fetchClinical(filters: ClinicalReportFilters) {
    const params = buildParams({
      patient_id: filters.patientId,
      start: filters.start,
      end: filters.end,
    })
    const response = await axios.get(`${API_BASE}/clinical?${params.toString()}`)
    return response.data as ClinicalReport
  },

  async fetchResearch(filters: ResearchReportFilters) {
    const params = buildParams({
      start: filters.start,
      end: filters.end,
      disease_type: filters.diseaseType,
      risk_level: filters.riskLevel,
    })
    const response = await axios.get(`${API_BASE}/research?${params.toString()}`)
    return response.data as ResearchReport
  },

  async fetchManagement(filters: ManagementReportFilters) {
    const params = buildParams({
      model_version: filters.modelVersion,
      start: filters.start,
      end: filters.end,
    })
    const response = await axios.get(`${API_BASE}/management?${params.toString()}`)
    return response.data as ManagementReport
  },

  async exportReport(payload: { reportType: string; format: 'pdf' | 'excel' | 'csv'; filters: Record<string, unknown> }) {
    const response = await axios.post(`${API_BASE}/export`, {
      report_type: payload.reportType,
      format: payload.format,
      filters: payload.filters,
    })
    return response.data as ReportExportResponse
  },
}


