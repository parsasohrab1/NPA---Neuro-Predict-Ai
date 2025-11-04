import axios from 'axios'

const API_URL = '/api/v1'

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
  created_at: string
  is_reviewed: boolean
}

export const patientsApi = {
  getAll: async (skip = 0, limit = 100, search?: string) => {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (search) params.append('search', search)
    const response = await axios.get(`${API_URL}/patients?${params}`)
    return response.data as Patient[]
  },

  getById: async (id: number) => {
    const response = await axios.get(`${API_URL}/patients/${id}`)
    return response.data as Patient
  },

  create: async (data: Partial<Patient>) => {
    const response = await axios.post(`${API_URL}/patients`, data)
    return response.data as Patient
  },

  update: async (id: number, data: Partial<Patient>) => {
    const response = await axios.put(`${API_URL}/patients/${id}`, data)
    return response.data as Patient
  },

  delete: async (id: number) => {
    await axios.delete(`${API_URL}/patients/${id}`)
  },
}

export const predictionsApi = {
  getAll: async (patientId?: number, skip = 0, limit = 100) => {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (patientId) params.append('patient_id', patientId.toString())
    const response = await axios.get(`${API_URL}/predictions?${params}`)
    return response.data as Prediction[]
  },

  getById: async (id: number) => {
    const response = await axios.get(`${API_URL}/predictions/${id}`)
    return response.data as Prediction
  },

  create: async (data: { patient_id: number; disease_type: string }) => {
    const response = await axios.post(`${API_URL}/predictions`, data)
    return response.data as Prediction
  },

  review: async (id: number, notes: string, approved: boolean) => {
    const response = await axios.post(`${API_URL}/predictions/${id}/review`, {
      review_notes: notes,
      approved,
    })
    return response.data as Prediction
  },
}

export const reportsApi = {
  getSummary: async (reportType: string = 'clinical', startDate?: string, endDate?: string) => {
    const params = new URLSearchParams({ report_type: reportType })
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    const response = await axios.get(`${API_URL}/reports/summary?${params}`)
    return response.data
  },

  getPredictionsTrend: async (days: number = 7) => {
    const response = await axios.get(`${API_URL}/reports/predictions-trend?days=${days}`)
    return response.data
  },

  getRiskDistribution: async () => {
    const response = await axios.get(`${API_URL}/reports/risk-distribution`)
    return response.data
  },
}

export const modelsApi = {
  getAll: async () => {
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
    const response = await axios.get(`${API_URL}/analytics/population/age-distribution`)
    return response.data
  },

  getGenderDistribution: async () => {
    const response = await axios.get(`${API_URL}/analytics/population/gender-distribution`)
    return response.data
  },

  getPopulationStatistics: async () => {
    const response = await axios.get(`${API_URL}/analytics/population/statistics`)
    return response.data
  },

  getLongitudinalData: async (patientId: number) => {
    const response = await axios.get(`${API_URL}/analytics/longitudinal/${patientId}`)
    return response.data
  },
}

export const usersApi = {
  getAll: async (skip = 0, limit = 100) => {
    const response = await axios.get(`${API_URL}/users?skip=${skip}&limit=${limit}`)
    return response.data
  },

  create: async (data: any) => {
    const response = await axios.post(`${API_URL}/users`, data)
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

