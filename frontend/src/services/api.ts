import axios from 'axios'
import { mockDataService } from './mockData'

const API_URL = '/api/v1'

/** Mock data is OFF by default — only enabled when explicitly set to 'true'. */
export const USE_MOCK_DATA = import.meta.env.VITE_USE_MOCK_DATA === 'true'

/** Backend health check (proxied to backend /health) */
export const backendHealthApi = {
  check: async (): Promise<{ status: string; service?: string; database?: string; redis?: string }> => {
    const response = await axios.get('/health', { timeout: 5000 })
    return response.data
  },
}

export interface Patient {
  id: number
  patient_id: string
  first_name: string
  last_name: string
  date_of_birth: string
  gender: 'male' | 'female' | 'other'
  email?: string
  phone?: string
  education_years?: number
  created_at: string
}

/** Clinical explainability: one feature with labels and interpretation */
export interface ClinicalFeatureImportanceItem {
  feature_key: string
  clinical_label_fa: string
  clinical_label_en: string
  importance: number
  interpretation_fa?: string
  interpretation_en?: string
}

/** Cohort distribution summary for one disease */
export interface CohortDiseaseSummary {
  patient_percentile?: number
  cohort_min?: number
  cohort_p25?: number
  cohort_median?: number
  cohort_p75?: number
  cohort_max?: number
  cohort_size?: number
  summary_fa?: string
  summary_en?: string
}

/** Comparison to similar cohort */
export interface CohortComparison {
  cohort_size: number
  cohort_description_fa?: string
  cohort_description_en?: string
  alzheimer?: CohortDiseaseSummary
  parkinson?: CohortDiseaseSummary
}

/** Progression visualization data */
export interface ProgressionVisualization {
  has_longitudinal_data: boolean
  trend_data?: { visit_dates?: string[]; progression_scores?: (number | null)[] }
  recommended_follow_up_months: number
  trajectory_summary_fa?: string
  trajectory_summary_en?: string
  risk_context?: Record<string, string>
}

/** Full clinical explainability for physicians */
export interface ClinicalExplanation {
  clinical_feature_importance: ClinicalFeatureImportanceItem[]
  cohort_comparison?: CohortComparison
  progression_visualization?: ProgressionVisualization
}

export interface Prediction {
  id: number
  patient_id: number
  disease_type: string
  alzheimer_prediction?: {
    risk_score: number
    risk_level: string
    confidence: number
  }
  parkinson_prediction?: {
    risk_score: number
    risk_level: string
    confidence: number
  }
  recommendations?: string
  feature_importance?: Record<string, number>
  attention_scores?: Record<string, number>
  clinical_explanation?: ClinicalExplanation
  model_version?: string
  model_name?: string
  created_at: string
  is_reviewed: boolean
  reviewed_by?: number
  reviewed_at?: string
  review_notes?: string
}

export interface PredictionReviewPayload {
  review_notes: string
  approved: boolean
  /** Optional clinician risk adjustment note (folded into review_notes for the API). */
  risk_adjustment?: string
}

export const patientsApi = {
  getAll: async (skip = 0, limit = 100, search?: string) => {
    if (USE_MOCK_DATA) {
      const data = await mockDataService.getPatients()
      let filtered = data
      if (search) {
        const searchLower = search.toLowerCase()
        filtered = data.filter(p =>
          p.first_name?.toLowerCase().includes(searchLower) ||
          p.last_name?.toLowerCase().includes(searchLower) ||
          p.patient_id?.toLowerCase().includes(searchLower)
        )
      }
      return filtered.slice(skip, skip + limit) as Patient[]
    }

    const response = await axios.get(`${API_URL}/patients`, {
      params: { skip, limit, search: search || undefined },
    })
    return response.data as Patient[]
  },

  getById: async (id: number) => {
    if (USE_MOCK_DATA) {
      const data = await mockDataService.getPatients()
      const patient = data.find((p: Patient) => p.id === id)
      if (!patient) throw new Error(`Patient ${id} not found`)
      return patient as Patient
    }
    const response = await axios.get(`${API_URL}/patients/${id}`)
    return response.data as Patient
  },

  create: async (data: Partial<Patient>) => {
    if (USE_MOCK_DATA) {
      throw new Error('Patient create is not available in mock mode')
    }
    const response = await axios.post(`${API_URL}/patients`, data)
    return response.data as Patient
  },

  update: async (id: number, data: Partial<Patient>) => {
    if (USE_MOCK_DATA) {
      throw new Error('Patient update is not available in mock mode')
    }
    const response = await axios.put(`${API_URL}/patients/${id}`, data)
    return response.data as Patient
  },

  delete: async (id: number) => {
    if (USE_MOCK_DATA) {
      throw new Error('Patient delete is not available in mock mode')
    }
    await axios.delete(`${API_URL}/patients/${id}`)
  },
}

export const predictionsApi = {
  getAll: async (patientId?: number, skip = 0, limit = 100) => {
    if (USE_MOCK_DATA) {
      const data = await mockDataService.getPredictions(patientId)
      return data.slice(skip, skip + limit) as unknown as Prediction[]
    }

    const response = await axios.get(`${API_URL}/predictions`, {
      params: { skip, limit, patient_id: patientId ?? undefined },
    })
    return response.data as Prediction[]
  },

  getById: async (id: number) => {
    if (USE_MOCK_DATA) {
      const data = await mockDataService.getPredictions()
      const prediction = data.find((p) => p.id === id)
      if (!prediction) throw new Error(`Prediction ${id} not found`)
      return prediction as unknown as Prediction
    }
    const response = await axios.get(`${API_URL}/predictions/${id}`)
    return response.data as Prediction
  },

  create: async (data: { patient_id: number; disease_type: string }) => {
    if (USE_MOCK_DATA) {
      throw new Error('Prediction create is not available in mock mode')
    }
    const response = await axios.post(`${API_URL}/predictions`, data)
    return response.data as Prediction
  },

  review: async (id: number, payload: PredictionReviewPayload | string, approvedArg?: boolean) => {
    // Support legacy (id, notes, approved) and new payload form
    const body: PredictionReviewPayload =
      typeof payload === 'string'
        ? { review_notes: payload, approved: approvedArg ?? true }
        : payload

    let review_notes = body.review_notes
    if (body.risk_adjustment?.trim()) {
      review_notes = `${review_notes}\n\nRisk adjustment: ${body.risk_adjustment.trim()}`
    }

    if (USE_MOCK_DATA) {
      throw new Error('Prediction review is not available in mock mode')
    }

    const response = await axios.post(`${API_URL}/predictions/${id}/review`, {
      review_notes,
      approved: body.approved,
    })
    return response.data as Prediction
  },
}

export const reportsApi = {
  getSummary: async (reportType: string = 'clinical', startDate?: string, endDate?: string) => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getReportSummary()
    }

    const response = await axios.get(`${API_URL}/reports/summary`, {
      params: { report_type: reportType, start_date: startDate, end_date: endDate },
    })
    return response.data
  },

  getPredictionsTrend: async (days: number = 7) => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getPredictionsTrend(days)
    }

    const response = await axios.get(`${API_URL}/reports/predictions-trend`, {
      params: { days },
    })
    return response.data
  },

  getRiskDistribution: async () => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getRiskDistribution()
    }

    const response = await axios.get(`${API_URL}/reports/risk-distribution`)
    return response.data
  },
}

export const modelsApi = {
  getAll: async () => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getModels()
    }

    const response = await axios.get(`${API_URL}/models`)
    return response.data
  },

  getById: async (modelId: string) => {
    const response = await axios.get(`${API_URL}/models/${modelId}`)
    return response.data
  },

  getPerformance: async (modelId: string) => {
    const response = await axios.get(`${API_URL}/models/${modelId}/performance`)
    return response.data
  },

  activate: async (modelId: string) => {
    const response = await axios.post(`${API_URL}/models/${modelId}/activate`)
    return response.data
  },

  deactivate: async (modelId: string) => {
    const response = await axios.post(`${API_URL}/models/${modelId}/deactivate`)
    return response.data
  },

  upload: async (file: File, modelName?: string, version?: string, diseaseType?: string) => {
    const formData = new FormData()
    formData.append('file', file)
    if (modelName) formData.append('model_name', modelName)
    if (version) formData.append('version', version)
    if (diseaseType) formData.append('disease_type', diseaseType)
    const response = await axios.post(`${API_URL}/models/upload`, formData)
    return response.data
  },
}

export const analyticsApi = {
  getAgeDistribution: async () => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getAgeDistribution()
    }

    const response = await axios.get(`${API_URL}/analytics/population/age-distribution`)
    return response.data
  },

  getGenderDistribution: async () => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getGenderDistribution()
    }

    const response = await axios.get(`${API_URL}/analytics/population/gender-distribution`)
    return response.data
  },

  getPopulationStatistics: async () => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getPopulationStatistics()
    }

    const response = await axios.get(`${API_URL}/analytics/population/statistics`)
    return response.data
  },

  getLongitudinalData: async (patientId: number) => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getLongitudinalData(patientId)
    }

    const response = await axios.get(`${API_URL}/analytics/longitudinal/${patientId}`)
    return response.data
  },
}

export const usersApi = {
  getAll: async (skip = 0, limit = 100) => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getUsers()
    }

    const response = await axios.get(`${API_URL}/users/`, {
      params: { skip, limit },
    })
    return response.data
  },

  create: async (data: any) => {
    const response = await axios.post(`${API_URL}/users/`, data)
    return response.data
  },

  update: async (id: number, data: any) => {
    const response = await axios.put(`${API_URL}/users/${id}`, data)
    return response.data
  },

  delete: async (id: number) => {
    await axios.delete(`${API_URL}/users/${id}`)
  },
}
