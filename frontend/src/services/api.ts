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

export interface DicomUploadResponse {
  imaging_study_id: number
  study_id: string
  medical_record_id: number
  dicom_path: string
  metadata: Record<string, unknown>
  created_at: string
}

export const imagingApi = {
  uploadDicom: async (payload: { patientId: number; file: File; medicalRecordId?: number }) => {
    const formData = new FormData()
    formData.append('patient_id', payload.patientId.toString())
    if (payload.medicalRecordId) {
      formData.append('medical_record_id', payload.medicalRecordId.toString())
    }
    formData.append('file', payload.file)

    const response = await axios.post(`${API_URL}/imaging/dicom`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data as DicomUploadResponse
  },
}

