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
}

export default diseaseTrackingApi

