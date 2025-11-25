import axios from '../config/api'

const API_BASE = '/api/v1/analysis-3d'

export interface Analysis3DData {
  traces: any[]
  stats: {
    total_points: number
    alzheimer_count: number
    parkinson_count: number
    normal_count: number
  }
}

export const analysis3DService = {
  async getAnalysisData(
    analysisType: string,
    diseaseFilter: string,
    selectedFeatures: { x: string; y: string; z: string }
  ): Promise<Analysis3DData> {
    const params = new URLSearchParams()
    params.append('analysis_type', analysisType)
    params.append('disease_filter', diseaseFilter)
    params.append('x_feature', selectedFeatures.x)
    params.append('y_feature', selectedFeatures.y)
    params.append('z_feature', selectedFeatures.z)

    const response = await axios.get(`${API_BASE}/data?${params.toString()}`)
    return response.data
  },

  async loadSampleData() {
    const response = await axios.post(`${API_BASE}/load-sample-data`)
    return response.data
  },
}

