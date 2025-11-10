import axios from '../config/api'

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

export type ReportChartPoint = {
  series: 'cohort' | 'target'
  visit_date: string
  value: number | null
}

export type ReportMetricStats = {
  average?: number | null
  minimum?: number | null
  maximum?: number | null
  latest?: number | null
  slope?: number | null
}

export type ReportComparisonRow = {
  metric: string
  cohort_average?: number | null
  patient_average?: number | null
  delta?: number | null
  cohort_a_average?: number | null
  cohort_b_average?: number | null
}

export type LongitudinalReportSummary = {
  report_type: string
  episode_id: number
  range?: { from?: string | null; to?: string | null }
  generated_at?: string
  visit_count?: number
  cohort_size?: number
  metrics?: Record<string, ReportMetricStats>
  comparison?: { table: ReportComparisonRow[] }
}

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
  heatmap_path?: string | null
  charts_payload?: Record<string, ReportChartPoint[]>
  summary?: LongitudinalReportSummary | null
  cohort_definition?: Record<string, unknown> | null
  comparison_definition?: Record<string, unknown> | null
  created_at: string
}

export type ReportCreatePayload = {
  start_date?: string
  end_date?: string
  format?: LongitudinalReportFormat
  report_type?: 'summary' | 'cohort_patient_vs_average' | 'cohort_vs_cohort'
  cohort_filters?: Record<string, unknown>
  comparison_filters?: Record<string, unknown>
}

export type ReportScheduleStatus = 'active' | 'paused' | 'archived'
export type ReportRunStatus = 'queued' | 'running' | 'success' | 'failed'

export type ReportSchedule = {
  id: number
  name: string
  episode_id: number
  report_type: string
  schedule_cron: string
  status: ReportScheduleStatus
  next_run_at?: string | null
  last_run_at?: string | null
  cohort_definition?: Record<string, unknown> | null
  comparison_definition?: Record<string, unknown> | null
  created_at: string
}

export type ReportRun = {
  id: number
  schedule_id: number
  report_id?: number | null
  status: ReportRunStatus
  started_at?: string | null
  finished_at?: string | null
  error_message?: string | null
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

  async downloadReportHeatmap(reportId: number) {
    const response = await axios.get(`${API_BASE}/reports/${reportId}/heatmap`, {
      responseType: 'blob',
    })
    return response
  },

  async createReportSchedule(payload: {
    name: string
    episode_id: number
    report_type: string
    schedule_cron: string
    cohort_filters?: Record<string, unknown>
    comparison_filters?: Record<string, unknown>
  }) {
    const response = await axios.post(`${API_BASE}/reports/schedules`, payload)
    return response.data as ReportSchedule
  },

  async fetchReportSchedules() {
    const response = await axios.get(`${API_BASE}/reports/schedules`)
    return response.data as ReportSchedule[]
  },

  async updateReportScheduleStatus(scheduleId: number, status: ReportScheduleStatus) {
    const response = await axios.patch(`${API_BASE}/reports/schedules/${scheduleId}`, { status })
    return response.data as ReportSchedule
  },

  async deleteReportSchedule(scheduleId: number) {
    await axios.delete(`${API_BASE}/reports/schedules/${scheduleId}`)
  },

  async enqueueScheduleRun(scheduleId: number) {
    const response = await axios.post(`${API_BASE}/reports/schedules/${scheduleId}/runs`)
    return response.data as ReportRun
  },

  async fetchScheduleRuns(scheduleId: number) {
    const response = await axios.get(`${API_BASE}/reports/schedules/${scheduleId}/runs`)
    return response.data as ReportRun[]
  },

  async executeScheduleRun(runId: number) {
    const response = await axios.post(`${API_BASE}/reports/runs/${runId}/execute`)
    return response.data as ReportRun
  },

  async fetchBaseline(episodeId: number, metricKey: string, baselineWindowDays = 90) {
    const params = new URLSearchParams({
      metric_key: metricKey,
      baseline_window_days: baselineWindowDays.toString(),
    })
    const response = await axios.get(`${API_BASE}/episodes/${episodeId}/baseline?${params}`)
    return response.data
  },

  async fetchPrediction(episodeId: number, metricKey: string, daysAhead = 30) {
    const params = new URLSearchParams({
      metric_key: metricKey,
      days_ahead: daysAhead.toString(),
    })
    const response = await axios.get(`${API_BASE}/episodes/${episodeId}/prediction?${params}`)
    return response.data
  },

  async fetchCombinedAlerts(episodeId: number, metricKeys?: string[]) {
    const params = new URLSearchParams()
    if (metricKeys && metricKeys.length > 0) {
      params.append('metric_keys', metricKeys.join(','))
    }
    const query = params.toString()
    const url = query ? `${API_BASE}/episodes/${episodeId}/combined-alerts?${query}` : `${API_BASE}/episodes/${episodeId}/combined-alerts`
    const response = await axios.get(url)
    return response.data as { alerts: Array<Record<string, unknown>> }
  },

  async fetchScheduleMonitoring(scheduleId: number) {
    const response = await axios.get(`${API_BASE}/reports/schedules/${scheduleId}/monitoring`)
    return response.data
  },
}

