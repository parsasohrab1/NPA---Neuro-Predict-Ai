import axios from '../config/api'

const API_BASE = '/api/v1/data-monitoring'

export const dataMonitoringService = {
  async getOverview(disease?: string) {
    const params = new URLSearchParams()
    if (disease && disease !== 'all') {
      params.append('disease', disease)
    }
    const url = params.toString() ? `${API_BASE}/overview?${params}` : `${API_BASE}/overview`
    const response = await axios.get(url)
    return response.data
  },

  async getCategoryData(category: string, timeRange: string, disease?: string) {
    const params = new URLSearchParams({ time_range: timeRange })
    if (disease && disease !== 'all') {
      params.append('disease', disease)
    }
    const response = await axios.get(`${API_BASE}/category/${category}?${params}`)
    return response.data
  },

  async getRecentData(disease?: string, limit: number = 20) {
    const params = new URLSearchParams({ limit: limit.toString() })
    if (disease && disease !== 'all') {
      params.append('disease', disease)
    }
    const response = await axios.get(`${API_BASE}/recent?${params}`)
    return response.data
  },

  async getTrends(timeRange: string, disease?: string) {
    const params = new URLSearchParams({ time_range: timeRange })
    if (disease && disease !== 'all') {
      params.append('disease', disease)
    }
    const response = await axios.get(`${API_BASE}/trends?${params}`)
    return response.data
  },

  async loadSampleData() {
    const response = await axios.post(`${API_BASE}/load-sample-data`)
    return response.data
  },
}

