import axios from 'axios'

const API_BASE = '/api/v1/longitudinal'

export type EpisodeStatus = 'active' | 'completed' | 'archived'
export type VisitType = 'baseline' | 'followup' | 'therapy' | 'imaging' | 'lab'
export type MetricCategory = 'cognitive' | 'biomarker' | 'imaging' | 'functional'

export type EpisodeSummary = {
  id: number
  patient_id: number
  title?: string | null
  start_date?: string | null
  end_date?: string | null
  status: EpisodeStatus
  visit_count: number
}

export type Metric = {
  id: number
  metric_type: MetricCategory
  metric_key: string
  metric_value?: number | null
  metric_payload?: Record<string, unknown> | null
  unit?: string | null
  z_score?: number | null
  created_at: string
}

export type Visit = {
  id: number
  episode_id: number
  visit_date: string
  visit_type: VisitType
  notes?: string | null
  progression_score?: number | null
  medical_record_id?: number | null
  imaging_study_id?: number | null
  prediction_id?: number | null
  metrics: Metric[]
}

export type EpisodeDetail = {
  id: number
  patient_id: number
  title?: string | null
  start_date?: string | null
  end_date?: string | null
  status: EpisodeStatus
  visits: Visit[]
}

export type TimelineEvent = {
  visit_id: number
  visit_date: string
  visit_type: VisitType
  label: string
  metrics: Metric[]
  progression_score?: number | null
}

export type TrendPoint = {
  visit_id: number
  visit_date: string
  metric_value?: number | null
  z_score?: number | null
}

export type ImagingComparison = {
  episode_id: number
  visit_a_id: number
  visit_b_id: number
  visit_a_date: string
  visit_b_date: string
  mean_absolute_difference: number
  max_absolute_difference: number
  heatmap: string
  metadata: Record<string, unknown>
}

export type AlertSeverity = 'low' | 'medium' | 'high'
export type AlertType = 'progression_speed' | 'sudden_change'

export type LongitudinalAlert = {
  id: number
  episode_id: number
  visit_id?: number | null
  metric_key?: string | null
  alert_type: AlertType
  severity: AlertSeverity
  message: string
  created_at: string
  acknowledged_at?: string | null
}

export type ProgressionMetricSummary = {
  slope?: number | null
  latest_value?: number | null
  latest_recorded_at?: string | null
}

export type ProgressionSummary = {
  metrics: Record<string, ProgressionMetricSummary>
}

export type EpisodeCreatePayload = {
  title?: string
  start_date?: string
  end_date?: string
}

export type LongitudinalReportFormat = 'pdf' | 'xlsx'
export type LongitudinalReportStatus = 'completed' | 'failed'

export type LongitudinalReport = {
  id: number
  episode_id: number
  report_type: string
  format: LongitudinalReportFormat
  status: LongitudinalReportStatus
  start_date?: string | null
  end_date?: string | null
  file_path: string
  pdf_path?: string | null
  summary?: Record<string, unknown> | null
  created_at: string
}

export type ReportCreatePayload = {
  start_date?: string
  end_date?: string
  format?: LongitudinalReportFormat
}

export const longitudinalService = {
  async fetchEpisodes(patientId: number) {
    const response = await axios.get(`${API_BASE}/${patientId}/episodes`)
    return response.data as EpisodeSummary[]
  },

  async createEpisode(patientId: number, payload: EpisodeCreatePayload) {
    const response = await axios.post(`${API_BASE}/${patientId}/episodes`, payload)
    return response.data as EpisodeDetail
  },

  async fetchEpisode(episodeId: number, patientId?: number) {
    const params = new URLSearchParams()
    if (patientId) params.append('patient_id', patientId.toString())
    const query = params.toString()
    const url = query ? `${API_BASE}/episodes/${episodeId}?${query}` : `${API_BASE}/episodes/${episodeId}`
    const response = await axios.get(url)
    return response.data as EpisodeDetail
  },

  async fetchTimeline(episodeId: number) {
    const response = await axios.get(`${API_BASE}/episodes/${episodeId}/timeline`)
    return response.data as TimelineEvent[]
  },

  async fetchTrend(episodeId: number, metricKey: string, metricType?: MetricCategory) {
    const params = new URLSearchParams({ metric_key: metricKey })
    if (metricType) params.append('metric_type', metricType)
    const response = await axios.get(`${API_BASE}/episodes/${episodeId}/trend?${params}`)
    return response.data as TrendPoint[]
  },

  async compareVisits(episodeId: number, visitA: number, visitB: number) {
    const params = new URLSearchParams({
      visit_a: visitA.toString(),
      visit_b: visitB.toString(),
    })
    const response = await axios.get(`${API_BASE}/episodes/${episodeId}/comparison?${params}`)
    return response.data as ImagingComparison
  },

  async fetchAlerts(episodeId: number) {
    const response = await axios.get(`${API_BASE}/episodes/${episodeId}/alerts`)
    return response.data as LongitudinalAlert[]
  },

  async acknowledgeAlert(alertId: number) {
    const response = await axios.post(`${API_BASE}/alerts/${alertId}/acknowledge`)
    return response.data as LongitudinalAlert
  },

  async fetchProgression(episodeId: number) {
    const response = await axios.get(`${API_BASE}/episodes/${episodeId}/progression`)
    return response.data as ProgressionSummary
  },

  async generateReport(episodeId: number, payload: ReportCreatePayload) {
    const response = await axios.post(`${API_BASE}/episodes/${episodeId}/reports`, payload)
    return response.data as LongitudinalReport
  },

  async fetchReports(episodeId: number) {
    const response = await axios.get(`${API_BASE}/episodes/${episodeId}/reports`)
    return response.data as LongitudinalReport[]
  },

  async downloadReport(reportId: number, variant: 'excel' | 'pdf' = 'excel') {
    const params = new URLSearchParams()
    if (variant === 'pdf') {
      params.append('variant', 'pdf')
    }
    const response = await axios.get(`${API_BASE}/reports/${reportId}/download${params.toString() ? `?${params}` : ''}`, {
      responseType: 'blob',
    })
    return response
  },
}

