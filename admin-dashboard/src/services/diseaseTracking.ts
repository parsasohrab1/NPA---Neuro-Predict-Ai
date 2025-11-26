import axios from '../config/api'

export interface FeatureDataPoint {
  date: string
  [key: string]: string | number | null | undefined
}

export interface PatientFeatures {
  patient_id: number
  patient_name: string
  age: number
  gender: string
  cognitive_features: FeatureDataPoint[]
  biomarker_features: FeatureDataPoint[]
  mri_features: FeatureDataPoint[]
  genetic_features: FeatureDataPoint[]
  latest_values: {
    mmse_score?: number | null
    moca_score?: number | null
    amyloid_beta?: number | null
    tau_protein?: number | null
    dopamine_level?: number | null
    hippocampal_volume?: number | null
    cortical_thickness?: number | null
    apoe_e4_status?: boolean | null
  }
  trends: {
    mmse_trend?: number
    amyloid_trend?: number
    hippocampal_trend?: number
    [key: string]: number | undefined
  }
  alerts: Array<{
    feature: string
    severity: 'critical' | 'warning'
    value: number
    normal_range: [number, number]
    message: string
  }>
  latest_prediction?: {
    alzheimer_risk: number | null
    parkinson_risk: number | null
    alzheimer_level: string | null
    parkinson_level: string | null
    date: string | null
  } | null
}

export interface FutureRiskPrediction {
  patient_id: number
  months_ahead: number
  projected_values: {
    mmse_score?: number | null
    amyloid_beta?: number | null
    hippocampal_volume?: number | null
  }
  predicted_risks: {
    alzheimer: {
      risk_score: number
      risk_level: 'low' | 'medium' | 'high'
    }
    parkinson: {
      risk_score: number
      risk_level: 'low' | 'medium' | 'high'
    }
  }
  trends: {
    mmse_trend?: number
    amyloid_trend?: number
    hippocampal_trend?: number
  }
}

export interface Recommendation {
  priority: 'critical' | 'high' | 'medium' | 'low'
  category: string
  title: string
  description: string
  actions: string[]
}

export interface PatientRecommendations {
  patient_id: number
  recommendations: {
    alzheimer: Recommendation[]
    parkinson: Recommendation[]
    general: Recommendation[]
  }
  generated_at: string
}

const diseaseTrackingApi = {
  async getPatientFeatures(patientId: number, days: number = 365): Promise<PatientFeatures> {
    const response = await axios.get(`/api/v1/disease-tracking/patient/${patientId}/features`, {
      params: { days },
    })
    return response.data
  },

  async predictFutureRisk(
    patientId: number,
    monthsAhead: number = 12
  ): Promise<FutureRiskPrediction> {
    const response = await axios.get(
      `/api/v1/disease-tracking/patient/${patientId}/future-risk`,
      {
        params: { months_ahead: monthsAhead },
      }
    )
    return response.data
  },

  async getRecommendations(patientId: number): Promise<PatientRecommendations> {
    const response = await axios.get(
      `/api/v1/disease-tracking/patient/${patientId}/recommendations`
    )
    return response.data
  },

  async getAllPatientsSummary(): Promise<{
    total_patients: number
    high_risk_alzheimer: number
    high_risk_parkinson: number
    medium_risk_alzheimer: number
    medium_risk_parkinson: number
    low_risk: number
    patients: Array<{
      patient_id: number
      name: string
      alzheimer_risk: number
      parkinson_risk: number
      last_prediction_date: string
    }>
  }> {
    const response = await axios.get('/api/v1/disease-tracking/all-patients/summary')
    return response.data
  },

  async createPatient(patientData: {
    patient_id: string
    first_name: string
    last_name: string
    date_of_birth: string
    gender: 'male' | 'female' | 'other'
    email?: string
    phone?: string
    address?: string
    education_years?: number
    medical_history?: string
    family_history?: string
    current_medications?: string
  }): Promise<any> {
    const response = await axios.post('/api/v1/patients/', patientData)
    return response.data
  },

  async createMedicalRecord(patientId: number, recordData: {
    visit_date: string
    visit_type?: string
    mmse_score?: number
    moca_score?: number
    memory_score?: number
    attention_score?: number
    executive_function_score?: number
    amyloid_beta?: number
    tau_protein?: number
    dopamine_level?: number
    apoe_e4_status?: boolean
    hippocampal_volume?: number
    cortical_thickness?: number
    ventricular_volume?: number
    white_matter_hyperintensities?: number
    brain_volume_total?: number
    symptoms?: string
    clinical_notes?: string
  }): Promise<any> {
    const response = await axios.post(`/api/v1/patients/${patientId}/medical-records`, recordData)
    return response.data
  },

  async addDefaultDataForAllPatients(): Promise<{
    message: string
    added_records: number
    added_predictions: number
    skipped: number
    total_patients: number
  }> {
    const response = await axios.post('/api/v1/disease-tracking/add-default-data')
    return response.data
  },

  async loadAllDatasets(): Promise<{
    message: string
    total_patients: number
    total_records: number
    total_predictions: number
    skipped: number
    errors?: string[]
    error_count?: number
  }> {
    const response = await axios.post('/api/v1/disease-tracking/load-all-datasets', {}, {
      timeout: 600000, // 10 minutes timeout for 100k records
    })
    return response.data
  },

  async loadSampleDatasets(): Promise<{
    message: string
    total_patients: number
    total_records: number
    total_predictions: number
    skipped: number
    sample_size: number
    categories_included: string
    source_distribution: string
    errors?: string[]
    error_count?: number
  }> {
    const response = await axios.post('/api/v1/disease-tracking/load-sample-datasets', {}, {
      timeout: 300000, // 5 minutes timeout for sample data
    })
    return response.data
  },

  async clearAllData(): Promise<{
    message: string
    patients_deleted: number
    records_deleted: number
    predictions_deleted: number
  }> {
    const response = await axios.post('/api/v1/disease-tracking/clear-all-data')
    return response.data
  },
}

export default diseaseTrackingApi

