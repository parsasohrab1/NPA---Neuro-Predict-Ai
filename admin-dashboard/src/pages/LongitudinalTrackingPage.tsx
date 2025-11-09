import { useMemo, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import {
  Line,
  LineChart,
  Tooltip,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
} from 'recharts'
import { ArrowPathIcon, PlusIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx'

import {
  longitudinalService,
  type EpisodeDetail,
  type EpisodeSummary,
  type Metric,
  type MetricCategory,
  type TrendPoint,
  type ImagingComparison,
  type LongitudinalAlert,
  type ProgressionSummary,
  type LongitudinalReport,
} from '../services/longitudinal'

type MetricOption = {
  key: string
  category: MetricCategory
}

export default function LongitudinalTrackingPage() {
  const [patientIdInput, setPatientIdInput] = useState('')
  const [activePatientId, setActivePatientId] = useState<number | null>(null)
  const [selectedEpisodeId, setSelectedEpisodeId] = useState<number | null>(null)
  const [trendMetricKey, setTrendMetricKey] = useState<string | null>(null)
  const [trendMetricCategory, setTrendMetricCategory] = useState<MetricCategory | undefined>(undefined)
  const [comparisonSelection, setComparisonSelection] = useState<number[]>([])
  const [comparisonResult, setComparisonResult] = useState<ImagingComparison | null>(null)
  const [comparisonError, setComparisonError] = useState<string | null>(null)
  const [reportForm, setReportForm] = useState<{ start: string; end: string; format: 'xlsx' | 'pdf' }>({
    start: '',
    end: '',
    format: 'xlsx',
  })
  const [reportError, setReportError] = useState<string | null>(null)

  const loadEpisodes = () => {
    const parsed = parseInt(patientIdInput, 10)
    if (Number.isNaN(parsed)) {
      alert('Patient ID should be a number')
      return
    }
    setActivePatientId(parsed)
    setSelectedEpisodeId(null)
    setTrendMetricKey(null)
    setComparisonSelection([])
    setComparisonResult(null)
    setComparisonError(null)
    setReportForm({ start: '', end: '', format: 'xlsx' })
    setReportError(null)
  }

  const episodesQuery = useQuery({
    queryKey: ['longitudinal', 'episodes', activePatientId],
    queryFn: () => longitudinalService.fetchEpisodes(activePatientId!),
    enabled: activePatientId !== null,
  })

  const selectedEpisode = episodesQuery.data?.find((episode) => episode.id === selectedEpisodeId) ?? null

  const episodeDetailQuery = useQuery({
    queryKey: ['longitudinal', 'episode', selectedEpisodeId],
    queryFn: () => longitudinalService.fetchEpisode(selectedEpisodeId!, activePatientId ?? undefined),
    enabled: selectedEpisodeId !== null,
  })

  const timelineQuery = useQuery({
    queryKey: ['longitudinal', 'timeline', selectedEpisodeId],
    queryFn: () => longitudinalService.fetchTimeline(selectedEpisodeId!),
    enabled: selectedEpisodeId !== null,
  })

  const trendQuery = useQuery({
    queryKey: ['longitudinal', 'trend', selectedEpisodeId, trendMetricKey, trendMetricCategory],
    queryFn: () =>
      longitudinalService.fetchTrend(
        selectedEpisodeId!,
        trendMetricKey || '',
        trendMetricCategory,
      ),
    enabled: selectedEpisodeId !== null && Boolean(trendMetricKey),
  })

  const alertsQuery = useQuery({
    queryKey: ['longitudinal', 'alerts', selectedEpisodeId],
    queryFn: () => longitudinalService.fetchAlerts(selectedEpisodeId!),
    enabled: selectedEpisodeId !== null,
    refetchInterval: 60_000,
  })

  const progressionQuery = useQuery({
    queryKey: ['longitudinal', 'progression', selectedEpisodeId],
    queryFn: () => longitudinalService.fetchProgression(selectedEpisodeId!),
    enabled: selectedEpisodeId !== null,
  })

  const reportsQuery = useQuery({
    queryKey: ['longitudinal', 'reports', selectedEpisodeId],
    queryFn: () => longitudinalService.fetchReports(selectedEpisodeId!),
    enabled: selectedEpisodeId !== null,
  })

  const createEpisode = useMutation({
    mutationFn: (payload: { patientId: number; title?: string }) =>
      longitudinalService.createEpisode(payload.patientId, {
        title: payload.title,
        start_date: new Date().toISOString(),
      }),
    onSuccess: (episode) => {
      episodesQuery.refetch()
      setSelectedEpisodeId(episode.id)
      setComparisonSelection([])
      setComparisonResult(null)
      setComparisonError(null)
      setReportForm({ start: '', end: '', format: 'xlsx' })
      setReportError(null)
    },
  })

  const metricOptions = useMemo<MetricOption[]>(() => {
    const detail = episodeDetailQuery.data
    if (!detail) return []
    const map = new Map<string, MetricCategory>()
    detail.visits.forEach((visit) => {
      visit.metrics.forEach((metric) => {
        if (!map.has(metric.metric_key)) {
          map.set(metric.metric_key, metric.metric_type)
        }
      })
    })
    return Array.from(map.entries()).map(([key, category]) => ({ key, category }))
  }, [episodeDetailQuery.data])

  const timelineEvents = timelineQuery.data ?? []

  const trendData: TrendPoint[] = trendQuery.data ?? []

  const selectedMetricLabel = trendMetricKey && trendMetricCategory ? `${trendMetricKey} (${trendMetricCategory})` : 'Select metric'

  const compareVisitsMutation = useMutation({
    mutationFn: (payload: { episodeId: number; visitA: number; visitB: number }) =>
      longitudinalService.compareVisits(payload.episodeId, payload.visitA, payload.visitB),
    onSuccess: (data) => {
      setComparisonResult(data)
      setComparisonError(null)
    },
    onError: (error: any) => {
      setComparisonResult(null)
      setComparisonError(error?.response?.data?.detail || 'Unable to compare the selected visits.')
    },
  })

  const toggleVisitForComparison = (visitId: number, imagingAvailable: boolean) => {
    if (!imagingAvailable) {
      setComparisonError('Selected visit has no imaging data available for comparison.')
      return
    }
    setComparisonError(null)
    setComparisonResult(null)
    setComparisonSelection((prev) => {
      if (prev.includes(visitId)) {
        return prev.filter((id) => id !== visitId)
      }
      if (prev.length >= 2) {
        return [prev[1], visitId]
      }
      return [...prev, visitId]
    })
  }

  const comparisonReady = comparisonSelection.length === 2 && selectedEpisodeId !== null
  const comparisonButtonDisabled = compareVisitsMutation.isPending || !comparisonReady

  const acknowledgeAlertMutation = useMutation({
    mutationFn: (alertId: number) => longitudinalService.acknowledgeAlert(alertId),
    onSuccess: () => {
      alertsQuery.refetch()
    },
  })

  const generateReportMutation = useMutation({
    mutationFn: async () => {
      if (!selectedEpisodeId) return null
      const payload = {
        start_date: reportForm.start || undefined,
        end_date: reportForm.end || undefined,
        format: reportForm.format,
      }
      return longitudinalService.generateReport(selectedEpisodeId, payload)
    },
    onSuccess: () => {
      reportsQuery.refetch()
      setReportForm({ start: '', end: '', format: 'xlsx' })
      setReportError(null)
    },
    onError: (error: any) => {
      setReportError(error?.response?.data?.detail || 'Unable to generate report.')
    },
  })

  const handleDownload = async (report: LongitudinalReport, variant: 'excel' | 'pdf') => {
    try {
      const response = await longitudinalService.downloadReport(report.id, variant)
      const contentType = response.headers['content-type'] ?? 'application/octet-stream'
      const blob = new Blob([response.data], { type: contentType })
      const url = window.URL.createObjectURL(blob)
      const extractName = (path: string | null | undefined) => {
        if (!path) return null
        const segments = path.split(/[/\\]/)
        return segments[segments.length - 1] || null
      }
      const baseExcel = extractName(report.file_path) || 'longitudinal-report.xlsx'
      const pdfName =
        extractName(report.pdf_path) || (baseExcel.endsWith('.xlsx') ? `${baseExcel.replace(/\.xlsx$/, '')}.pdf` : 'longitudinal-report.pdf')
      const filename = variant === 'pdf' ? pdfName : baseExcel

      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      setReportError(null)
    } catch (error: any) {
      setReportError(error?.response?.data?.detail || 'Download failed.')
    }
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2">
        <h1 className="text-2xl font-semibold text-white">Longitudinal Tracking</h1>
        <p className="text-sm text-slate-400">
          Explore patient episodes, visit timelines, and progression trends across cognitive, biomarker, and imaging metrics.
        </p>
      </header>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div className="flex flex-col gap-2 md:flex-row md:items-end md:gap-4">
            <label className="flex flex-col gap-1 text-sm">
              <span className="text-xs uppercase text-slate-400">Patient ID</span>
              <input
                className="w-48 rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                placeholder="e.g. 101"
                value={patientIdInput}
                onChange={(event) => setPatientIdInput(event.target.value)}
              />
            </label>
            <button
              className="inline-flex items-center gap-2 rounded-lg bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400"
              onClick={loadEpisodes}
            >
              <ArrowPathIcon className="h-4 w-4" />
              Load episodes
            </button>
          </div>

          <button
            className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-slate-200 transition hover:border-sky-400 hover:text-sky-300 disabled:opacity-40"
            onClick={() => {
              if (!activePatientId) {
                alert('Load patient episodes first')
                return
              }
              const title = prompt('Episode title', 'Longitudinal Study')
              createEpisode.mutate({ patientId: activePatientId, title: title || undefined })
            }}
            disabled={!activePatientId || createEpisode.isPending}
          >
            <PlusIcon className="h-4 w-4" />
            New episode
          </button>
        </div>

        {activePatientId && (
          <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
            {episodesQuery.isLoading && <p className="text-sm text-slate-400">Loading episodes…</p>}
            {episodesQuery.isError && (
              <p className="text-sm text-rose-400">Failed to load episodes. Check permissions or patient id.</p>
            )}
            {episodesQuery.data && episodesQuery.data.length === 0 && (
              <p className="text-sm text-slate-400">No episodes yet. Create the first episode to get started.</p>
            )}
            {episodesQuery.data && episodesQuery.data.length > 0 && (
              <div className="flex flex-col gap-4">
                <div className="flex flex-wrap items-center gap-2">
                  {episodesQuery.data.map((episode) => (
                    <button
                      key={episode.id}
                      onClick={() => {
                        setSelectedEpisodeId(episode.id)
                        setTrendMetricKey(null)
                        setTrendMetricCategory(undefined)
                        setReportForm({ start: '', end: '', format: 'xlsx' })
                        setReportError(null)
                      }}
                      className={clsx(
                        'rounded-xl border px-4 py-2 text-sm transition',
                        selectedEpisodeId === episode.id
                          ? 'border-sky-500 bg-sky-500/10 text-sky-200'
                          : 'border-slate-700 bg-slate-900 text-slate-300 hover:border-sky-400 hover:text-sky-200'
                      )}
                    >
                      <div className="font-semibold">{episode.title || `Episode ${episode.id}`}</div>
                      <div className="text-xs text-slate-400">
                        {episode.visit_count} visits • {episode.status}
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </section>

      {selectedEpisodeId && (
        <section className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[2fr,1fr]">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-white">Visit timeline</h2>
                  <p className="text-xs text-slate-400">
                    Chronological breakdown of visits and recorded metrics for the selected episode.
                  </p>
                </div>
                <span className="text-xs uppercase text-slate-400">
                  {timelineQuery.isLoading ? 'Loading…' : `${timelineEvents.length} entries`}
                </span>
              </div>

              <div className="mt-4 space-y-4">
                {timelineEvents.map((event) => (
                  <div
                    key={event.visit_id}
                    className="rounded-2xl border border-slate-800/80 bg-slate-900/80 p-4"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="text-sm font-semibold text-white">
                        {event.label} • {format(new Date(event.visit_date), 'PP')}
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          type="button"
                          disabled={!event.imaging_available}
                          onClick={() => toggleVisitForComparison(event.visit_id, event.imaging_available)}
                          className={clsx(
                            'rounded-full border px-3 py-1 text-xs transition',
                            event.imaging_available
                              ? comparisonSelection.includes(event.visit_id)
                                ? 'border-sky-500 bg-sky-500/20 text-sky-200'
                                : 'border-slate-700 bg-slate-900 text-slate-300 hover:border-sky-400 hover:text-sky-200'
                              : 'cursor-not-allowed border-slate-800 bg-slate-900 text-slate-600'
                          )}
                        >
                          {comparisonSelection.includes(event.visit_id) ? 'Selected' : 'Compare'}
                        </button>
                        {event.progression_score !== undefined && event.progression_score !== null && (
                          <span className="text-xs text-sky-300">
                            Progression score {Math.round(event.progression_score * 100)}%
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-2">
                      {event.metrics.map((metric: Metric) => (
                        <div key={metric.id} className="rounded-xl border border-slate-800/70 bg-slate-950/80 p-3">
                          <div className="text-xs uppercase text-slate-400">{metric.metric_type}</div>
                          <div className="text-sm font-medium text-white">
                            {metric.metric_key}: {metric.metric_value ?? '—'} {metric.unit ?? ''}
                          </div>
                          {metric.z_score !== null && metric.z_score !== undefined && (
                            <div className="text-xs text-slate-500">z-score {metric.z_score.toFixed(2)}</div>
                          )}
                        </div>
                      ))}
                      {event.metrics.length === 0 && (
                        <p className="text-sm text-slate-500">No metrics recorded.</p>
                      )}
                    </div>
                  </div>
                ))}
                {timelineEvents.length === 0 && !timelineQuery.isLoading && (
                  <p className="text-sm text-slate-400">No visits recorded yet.</p>
                )}
              </div>
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h3 className="text-lg font-semibold text-white">Metric trend</h3>
              <p className="text-xs text-slate-400">
                Select a metric to visualise its progression across visits.
              </p>

              <label className="mt-4 block text-xs uppercase text-slate-400">
                Metric
                <select
                  className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                  value={trendMetricKey ?? ''}
                  onChange={(event) => {
                    const value = event.target.value
                    if (!value) {
                      setTrendMetricKey(null)
                      setTrendMetricCategory(undefined)
                      return
                    }
                    const option = metricOptions.find((item) => item.key === value)
                    setTrendMetricKey(value)
                    setTrendMetricCategory(option?.category)
                  }}
                >
                  <option value="">Select metric…</option>
                  {metricOptions.map((option) => (
                    <option key={option.key} value={option.key}>
                      {option.key} ({option.category})
                    </option>
                  ))}
                </select>
              </label>

              <div className="mt-6 h-64 rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                {trendMetricKey ? (
                  trendQuery.isLoading ? (
                    <p className="text-sm text-slate-400">Loading trend…</p>
                  ) : trendData.length === 0 ? (
                    <p className="text-sm text-slate-400">No data for {selectedMetricLabel}.</p>
                  ) : (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={trendData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                        <XAxis
                          dataKey="visit_date"
                          stroke="#94a3b8"
                          tickFormatter={(value: string) => format(new Date(value), 'MM/dd')}
                        />
                        <YAxis stroke="#94a3b8" />
                        <Tooltip
                          contentStyle={{
                            background: '#0f172a',
                            borderRadius: '12px',
                            borderColor: '#1e293b',
                          }}
                          labelFormatter={(value: string) => format(new Date(value), 'PPpp')}
                        />
                        <Line
                          type="monotone"
                          dataKey="metric_value"
                          stroke="#38bdf8"
                          strokeWidth={2}
                          dot={{ r: 3 }}
                          name={trendMetricKey}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  )
                ) : (
                  <p className="text-sm text-slate-400">Select a metric to display its trend.</p>
                )}
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h3 className="text-lg font-semibold text-white">Episode snapshot</h3>
            <div className="flex flex-wrap items-center gap-2">
              <button
                type="button"
                disabled={comparisonButtonDisabled}
                onClick={() => {
                  if (!comparisonReady || !selectedEpisodeId) return
                  compareVisitsMutation.mutate({
                    episodeId: selectedEpisodeId,
                    visitA: comparisonSelection[0],
                    visitB: comparisonSelection[1],
                  })
                }}
                className={clsx(
                  'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs transition',
                  comparisonButtonDisabled
                    ? 'cursor-not-allowed border-slate-800 bg-slate-900 text-slate-600'
                    : 'border-sky-500 bg-sky-500/10 text-sky-200 hover:border-sky-400 hover:text-sky-100'
                )}
              >
                {compareVisitsMutation.isPending ? 'Comparing…' : 'Compare selected visits'}
              </button>
              {comparisonSelection.length > 0 && (
                <span className="text-xs text-slate-400">
                  Selected visits: {comparisonSelection.map((id) => `#${id}`).join(', ')}
                </span>
              )}
            </div>
            {comparisonError && (
              <p className="mt-3 rounded-xl border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-xs text-rose-200">
                {comparisonError}
              </p>
            )}
            {episodeDetailQuery.isLoading && <p className="text-sm text-slate-400">Loading episode…</p>}
            {episodeDetailQuery.data && (
              <EpisodeSummaryPanel
                summary={episodeDetailQuery.data}
                episodes={episodesQuery.data ?? []}
                progression={progressionQuery.data ?? null}
              />
            )}
            <AlertsPanel
              alerts={alertsQuery.data ?? []}
              isLoading={alertsQuery.isLoading}
              onAcknowledge={(alertId) => acknowledgeAlertMutation.mutate(alertId)}
            />
            {comparisonResult && (
              <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
                <h4 className="text-sm font-semibold text-white">Imaging comparison</h4>
                <p className="text-xs text-slate-400">
                  Visits {comparisonResult.visit_a_id} vs {comparisonResult.visit_b_id} • mean diff{' '}
                  {comparisonResult.mean_absolute_difference.toFixed(3)}
                </p>
                <div className="mt-3 overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/70">
                  <img
                    src={comparisonResult.heatmap}
                    alt="MRI difference heatmap"
                    className="h-full w-full object-contain"
                  />
                </div>
              </div>
            )}
            <ReportsPanel
              reports={reportsQuery.data ?? []}
              isLoading={reportsQuery.isLoading || generateReportMutation.isPending}
              reportForm={reportForm}
              onChangeForm={(form) => setReportForm(form)}
              onGenerate={() => generateReportMutation.mutate()}
              onDownload={handleDownload}
              error={reportError}
            />
          </div>
        </section>
      )}
    </div>
  )
}

type EpisodeSummaryPanelProps = {
  summary: EpisodeDetail
  episodes: EpisodeSummary[]
  progression: ProgressionSummary | null
}

function EpisodeSummaryPanel({ summary, episodes, progression }: EpisodeSummaryPanelProps) {
  const visitCount = summary.visits.length
  const firstVisit = summary.visits[0]?.visit_date
  const latestVisit = summary.visits[visitCount - 1]?.visit_date
  const totalMetrics = summary.visits.reduce((acc, visit) => acc + visit.metrics.length, 0)

  const mmseSlope = progression?.metrics['mmse']?.slope ?? null
  const amyloidSlope = progression?.metrics['amyloid_beta']?.slope ?? null
  const riskSlope = progression?.metrics['parkinson_risk_score']?.slope ?? null

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
      <SummaryCard label="Episode title" value={summary.title || `Episode ${summary.id}`} />
      <SummaryCard
        label="Visits recorded"
        value={`${visitCount}`}
        helper={firstVisit && latestVisit ? `${format(new Date(firstVisit), 'PP')} → ${format(new Date(latestVisit), 'PP')}` : undefined}
      />
      <SummaryCard label="Total metrics logged" value={`${totalMetrics}`} />
      <SummaryCard label="Patient episodes" value={`${episodes.length}`} helper="Across active projects" />
      <SummaryCard
        label="MMSE slope (per day)"
        value={formatSlope(mmseSlope)}
        trend={mmseSlope}
      />
      <SummaryCard
        label="Amyloid β slope"
        value={formatSlope(amyloidSlope)}
        trend={amyloidSlope}
      />
      <SummaryCard
        label="Risk slope"
        value={formatSlope(riskSlope)}
        trend={riskSlope}
      />
    </div>
  )
}

type SummaryCardProps = {
  label: string
  value: string
  helper?: string
  trend?: number | null
}

function SummaryCard({ label, value, helper, trend }: SummaryCardProps) {
  const trendColor =
    trend === undefined || trend === null
      ? 'text-slate-300'
      : trend > 0
      ? 'text-emerald-400'
      : trend < 0
      ? 'text-rose-400'
      : 'text-slate-300'

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">
      <div className="text-xs uppercase text-slate-400">{label}</div>
      <div className={clsx('mt-2 text-xl font-semibold', trendColor)}>{value}</div>
      {helper && <div className="text-xs text-slate-500">{helper}</div>}
    </div>
  )
}

type AlertsPanelProps = {
  alerts: LongitudinalAlert[]
  isLoading: boolean
  onAcknowledge: (alertId: number) => void
}

function AlertsPanel({ alerts, isLoading, onAcknowledge }: AlertsPanelProps) {
  if (isLoading) {
    return <p className="mt-4 text-sm text-slate-400">Loading alerts…</p>
  }
  if (alerts.length === 0) {
    return <p className="mt-4 text-sm text-slate-500">No active alerts.</p>
  }
  return (
    <div className="mt-4 space-y-3">
      {alerts.map((alert) => (
        <div
          key={alert.id}
          className="flex flex-col gap-2 rounded-2xl border border-slate-800/80 bg-slate-900/70 p-4 md:flex-row md:items-center md:justify-between"
        >
          <div>
            <div className="flex items-center gap-2 text-sm text-white">
              <SeverityBadge severity={alert.severity} />
              <span>{alert.message}</span>
            </div>
            <div className="text-xs text-slate-400">
              {format(new Date(alert.created_at), 'PPpp')}{' '}
              {alert.metric_key ? `• ${alert.metric_key}` : ''}
            </div>
          </div>
          <div className="flex items-center gap-2">
            {alert.acknowledged_at ? (
              <span className="text-xs text-slate-500">
                Acknowledged {format(new Date(alert.acknowledged_at), 'PPpp')}
              </span>
            ) : (
              <button
                type="button"
                onClick={() => onAcknowledge(alert.id)}
                className="rounded-full border border-emerald-500/40 px-3 py-1 text-xs text-emerald-300 hover:border-emerald-400 hover:text-emerald-200"
              >
                Acknowledge
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

function SeverityBadge({ severity }: { severity: LongitudinalAlert['severity'] }) {
  const styles: Record<LongitudinalAlert['severity'], string> = {
    low: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30',
    medium: 'bg-amber-500/10 text-amber-300 border-amber-500/30',
    high: 'bg-rose-500/10 text-rose-300 border-rose-500/30',
  }
  return (
    <span className={clsx('rounded-full border px-2 py-0.5 text-xs uppercase tracking-wide', styles[severity])}>
      {severity}
    </span>
  )
}

function formatSlope(slope: number | null | undefined): string {
  if (slope === null || slope === undefined) {
    return '—'
  }
  const formatted = slope.toFixed(3)
  return `${formatted} /day`
}

type ReportsPanelProps = {
  reports: LongitudinalReport[]
  isLoading: boolean
  reportForm: { start: string; end: string; format: 'xlsx' | 'pdf' }
  onChangeForm: (form: { start: string; end: string; format: 'xlsx' | 'pdf' }) => void
  onGenerate: () => void
  onDownload: (report: LongitudinalReport, variant: 'excel' | 'pdf') => void
  error?: string | null
}

function ReportsPanel({ reports, isLoading, reportForm, onChangeForm, onGenerate, onDownload, error }: ReportsPanelProps) {
  return (
    <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h4 className="text-sm font-semibold text-white">Longitudinal reports</h4>
          <p className="text-xs text-slate-400">Generate periodic summaries of MMSE, biomarkers, and risk trends.</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <label className="text-xs text-slate-400">
            From
            <input
              type="date"
              value={reportForm.start}
              onChange={(event) => onChangeForm({ ...reportForm, start: event.target.value })}
              className="ml-1 rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            />
          </label>
          <label className="text-xs text-slate-400">
            To
            <input
              type="date"
              value={reportForm.end}
              onChange={(event) => onChangeForm({ ...reportForm, end: event.target.value })}
              className="ml-1 rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            />
          </label>
          <select
            value={reportForm.format}
            onChange={(event) => onChangeForm({ ...reportForm, format: event.target.value as 'xlsx' | 'pdf' })}
            className="rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
          >
            <option value="xlsx">Excel</option>
            <option value="pdf">PDF</option>
          </select>
          <button
            type="button"
            onClick={onGenerate}
            disabled={isLoading}
            className="rounded border border-sky-500/40 bg-sky-500/10 px-3 py-1 text-xs text-sky-200 hover:border-sky-400 hover:text-sky-100 disabled:opacity-40"
          >
            {isLoading ? 'Generating…' : 'Generate'}
          </button>
        </div>
      </div>
      {error && (
        <p className="mt-3 rounded-xl border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-xs text-rose-200">{error}</p>
      )}
      {isLoading && reports.length === 0 ? (
        <p className="mt-3 text-xs text-slate-400">Processing…</p>
      ) : (
        <div className="mt-3 space-y-2">
          {reports.map((report) => {
            const metrics = (report.summary?.metrics ?? {}) as Record<string, any>
            return (
              <div
                key={report.id}
                className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-slate-800/70 bg-slate-950/70 px-3 py-2 text-xs text-slate-200"
              >
                <div>
                  <div className="font-medium text-white">
                    {report.report_type} • {format(new Date(report.created_at), 'PPpp')}
                  </div>
                  <div className="text-[11px] text-slate-400">
                    Range {report.start_date ? format(new Date(report.start_date), 'PP') : 'start'} →{' '}
                    {report.end_date ? format(new Date(report.end_date), 'PP') : 'latest'} • Format {report.format.toUpperCase()}
                  </div>
                  {Object.entries(metrics)
                    .slice(0, 2)
                    .map(([metricKey, stats]) => (
                      <div key={metricKey} className="text-[11px] text-slate-500">
                        {metricKey}: avg {stats?.average ?? '—'} • slope {stats?.slope ?? '—'}
                      </div>
                    ))}
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <span
                    className={clsx(
                      'rounded-full border px-2 py-0.5 uppercase tracking-wide',
                      report.status === 'completed'
                        ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300'
                        : 'border-amber-500/40 bg-amber-500/10 text-amber-300'
                    )}
                  >
                    {report.status}
                  </span>
                  {report.format === 'xlsx' && (
                    <button
                      type="button"
                      onClick={() => onDownload(report, 'excel')}
                      className="rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-200 hover:border-sky-400 hover:text-sky-200"
                    >
                      Excel
                    </button>
                  )}
                  {report.pdf_path && (
                    <button
                      type="button"
                      onClick={() => onDownload(report, 'pdf')}
                      className="rounded border border-slate-700 px-2 py-0.5 text-xs text-amber-200 hover:border-amber-400 hover:text-amber-100"
                    >
                      PDF
                    </button>
                  )}
                </div>
              </div>
            )
          })}
          {reports.length === 0 && <p className="text-xs text-slate-500">No reports generated yet.</p>}
        </div>
      )}
    </div>
  )
}


