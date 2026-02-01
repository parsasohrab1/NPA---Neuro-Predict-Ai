import axios from 'axios'
import { mockDataService } from './mockData'

const API_URL = '/api/v1'
const USE_MOCK_DATA =
  import.meta.env.VITE_USE_MOCK_DATA === undefined
    ? true
    :       import.meta.env.VITE_USE_MOCK_DATA === 'true' ||
      import.meta.env.VITE_USE_MOCK_DATA === true

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
    if (USE_MOCK_DATA) {
      // Use local mock data
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
    
    // Use backend API (server-side pagination)
    try {
      const response = await axios.get(`${API_URL}/patients`, {
        params: { skip, limit, search: search || undefined },
      })
      return response.data as Patient[]
    } catch (error) {
      console.error('Error fetching patients:', error)
      // Fallback to local mock data
      const data = await mockDataService.getPatients()
      return data.slice(skip, skip + limit) as Patient[]
    }
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
    if (USE_MOCK_DATA) {
      const data = await mockDataService.getPredictions(patientId)
      return data.slice(skip, skip + limit) as Prediction[]
    }

    try {
      const response = await axios.get(`${API_URL}/predictions`, {
        params: { skip, limit, patient_id: patientId ?? undefined },
      })
      return response.data as Prediction[]
    } catch (error) {
      console.error('Error fetching predictions:', error)
      const data = await mockDataService.getPredictions(patientId)
      return data.slice(skip, skip + limit) as Prediction[]
    }
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
    if (USE_MOCK_DATA) {
      return await mockDataService.getReportSummary()
    }

    try {
      const response = await axios.get(`${API_URL}/reports/summary`, {
        params: { report_type: reportType, start_date: startDate, end_date: endDate },
      })
      return response.data
    } catch (error) {
      console.error('Error fetching report summary:', error)
      return await mockDataService.getReportSummary()
    }
  },

  getPredictionsTrend: async (days: number = 7) => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getPredictionsTrend(days)
    }

    try {
      const response = await axios.get(`${API_URL}/reports/predictions-trend`, {
        params: { days },
      })
      return response.data
    } catch (error) {
      console.error('Error fetching predictions trend:', error)
      return await mockDataService.getPredictionsTrend(days)
    }
  },

  getRiskDistribution: async () => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getRiskDistribution()
    }

    try {
      const response = await axios.get(`${API_URL}/reports/risk-distribution`)
      return response.data
    } catch (error) {
      console.error('Error fetching risk distribution:', error)
      return await mockDataService.getRiskDistribution()
    }
  },
}

export const modelsApi = {
  getAll: async () => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getModels()
    }
    
    try {
      const response = await axios.get(`${API_URL}/mock/models/`)
      return response.data
    } catch (error) {
      console.error('Error fetching models:', error)
      return await mockDataService.getModels()
    }
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
    
    try {
      const response = await axios.get(`${API_URL}/mock/analytics/population/age-distribution`)
      return response.data
    } catch (error) {
      console.error('Error fetching age distribution:', error)
      return await mockDataService.getAgeDistribution()
    }
  },

  getGenderDistribution: async () => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getGenderDistribution()
    }
    
    try {
      const response = await axios.get(`${API_URL}/mock/analytics/population/gender-distribution`)
      return response.data
    } catch (error) {
      console.error('Error fetching gender distribution:', error)
      return await mockDataService.getGenderDistribution()
    }
  },

  getPopulationStatistics: async () => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getPopulationStatistics()
    }
    
    try {
      const response = await axios.get(`${API_URL}/mock/analytics/population/statistics`)
      return response.data
    } catch (error) {
      console.error('Error fetching population statistics:', error)
      return await mockDataService.getPopulationStatistics()
    }
  },

  getLongitudinalData: async (patientId: number) => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getLongitudinalData(patientId)
    }
    
    try {
      const response = await axios.get(`${API_URL}/mock/analytics/longitudinal/${patientId}`)
      return response.data
    } catch (error) {
      console.error('Error fetching longitudinal data:', error)
      return await mockDataService.getLongitudinalData(patientId)
    }
  },
}

export const usersApi = {
  getAll: async (skip = 0, limit = 100) => {
    if (USE_MOCK_DATA) {
      return await mockDataService.getUsers()
    }
    
    try {
      const response = await axios.get(`${API_URL}/mock/users/`)
      return response.data
    } catch (error) {
      console.error('Error fetching users:', error)
      return await mockDataService.getUsers()
    }
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

