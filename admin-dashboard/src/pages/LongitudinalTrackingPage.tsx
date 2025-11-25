import React, { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { toast } from 'react-hot-toast'
import {
  Line,
  LineChart,
  Tooltip,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  BarChart,
  Bar,
} from 'recharts'
import { ArrowPathIcon, PlusIcon, LinkIcon, ChartBarIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

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
  type ReportCreatePayload,
  type ReportSchedule,
  type ReportRun,
  type ReportScheduleStatus,
  type ReportRunStatus,
} from '../services/longitudinal'

type MetricOption = {
  key: string
  category: MetricCategory
}

type ReportFormState = {
  start: string
  end: string
  format: 'xlsx' | 'pdf'
  reportType: 'summary' | 'cohort_patient_vs_average' | 'cohort_vs_cohort'
  cohortGender: string
  cohortAgeMin: string
  cohortAgeMax: string
  cohortPatientIds: string
  comparisonGender: string
  comparisonPatientIds: string
}

type ScheduleFormState = {
  name: string
  scheduleCron: string
  reportType: 'summary' | 'cohort_patient_vs_average' | 'cohort_vs_cohort'
  cohortGender: string
  cohortAgeMin: string
  cohortAgeMax: string
  cohortPatientIds: string
  comparisonGender: string
  comparisonPatientIds: string
}

type HeatmapPreviewState = {
  url: string
  name: string
}

export default function LongitudinalTrackingPage() {
  const queryClient = useQueryClient()
  const [patientIdInput, setPatientIdInput] = useState('')
  const [activePatientId, setActivePatientId] = useState<number | null>(null)
  const [selectedEpisodeId, setSelectedEpisodeId] = useState<number | null>(null)
  const [showLoadDataModal, setShowLoadDataModal] = useState(false)
  const [trendMetricKey, setTrendMetricKey] = useState<string | null>(null)
  const [trendMetricCategory, setTrendMetricCategory] = useState<MetricCategory | undefined>(undefined)
  const [comparisonSelection, setComparisonSelection] = useState<number[]>([])
  const [comparisonResult, setComparisonResult] = useState<ImagingComparison | null>(null)
  const [comparisonError, setComparisonError] = useState<string | null>(null)
  const [reportForm, setReportForm] = useState<ReportFormState>({
    start: '',
    end: '',
    format: 'xlsx',
    reportType: 'summary',
    cohortGender: '',
    cohortAgeMin: '',
    cohortAgeMax: '',
    cohortPatientIds: '',
    comparisonGender: '',
    comparisonPatientIds: '',
  })
  const [reportError, setReportError] = useState<string | null>(null)
  const [heatmapPreview, setHeatmapPreview] = useState<HeatmapPreviewState | null>(null)
  const [scheduleForm, setScheduleForm] = useState<ScheduleFormState>({
    name: '',
    scheduleCron: '0 6 * * 1',
    reportType: 'summary',
    cohortGender: '',
    cohortAgeMin: '',
    cohortAgeMax: '',
    cohortPatientIds: '',
    comparisonGender: '',
    comparisonPatientIds: '',
  })
  const [scheduleError, setScheduleError] = useState<string | null>(null)
  const [expandedScheduleId, setExpandedScheduleId] = useState<number | null>(null)
  const [sortedTimelineEvents, setSortedTimelineEvents] = useState<TimelineEvent[]>([])
  const [showCohortAnalysis, setShowCohortAnalysis] = useState(false)
  const [selectedReportId, setSelectedReportId] = useState<number | null>(null)

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  useEffect(() => {
    return () => {
      if (heatmapPreview) {
        URL.revokeObjectURL(heatmapPreview.url)
      }
    }
  }, [heatmapPreview])

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
    setReportForm({
      start: '',
      end: '',
      format: 'xlsx',
      reportType: 'summary',
      cohortGender: '',
      cohortAgeMin: '',
      cohortAgeMax: '',
      cohortPatientIds: '',
      comparisonGender: '',
      comparisonPatientIds: '',
    })
    setReportError(null)
    setScheduleForm({
      name: '',
      scheduleCron: '0 6 * * 1',
      reportType: 'summary',
      cohortGender: '',
      cohortAgeMin: '',
      cohortAgeMax: '',
      cohortPatientIds: '',
      comparisonGender: '',
      comparisonPatientIds: '',
    })
    setScheduleError(null)
    setExpandedScheduleId(null)
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

  const schedulesQuery = useQuery({
    queryKey: ['longitudinal', 'reportSchedules'],
    queryFn: () => longitudinalService.fetchReportSchedules(),
  })

  const applicableSchedules = useMemo<ReportSchedule[]>(() => {
    if (!selectedEpisodeId) return []
    return (schedulesQuery.data ?? []).filter((schedule) => schedule.episode_id === selectedEpisodeId)
  }, [schedulesQuery.data, selectedEpisodeId])

  const scheduleRunsQuery = useQuery({
    queryKey: ['longitudinal', 'scheduleRuns', expandedScheduleId],
    queryFn: () => longitudinalService.fetchScheduleRuns(expandedScheduleId!),
    enabled: expandedScheduleId !== null,
  })
  const scheduleRuns = expandedScheduleId ? scheduleRunsQuery.data ?? [] : []

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
      setReportForm({
        start: '',
        end: '',
        format: 'xlsx',
        reportType: 'summary',
        cohortGender: '',
        cohortAgeMin: '',
        cohortAgeMax: '',
        cohortPatientIds: '',
        comparisonGender: '',
        comparisonPatientIds: '',
      })
      setReportError(null)
      setScheduleForm((prev) => ({
        ...prev,
        name: '',
        scheduleCron: '0 6 * * 1',
        reportType: 'summary',
        cohortGender: '',
        cohortAgeMin: '',
        cohortAgeMax: '',
        cohortPatientIds: '',
        comparisonGender: '',
        comparisonPatientIds: '',
      }))
      setScheduleError(null)
      setExpandedScheduleId(null)
    },
  })

  const loadSampleDataMutation = useMutation({
    mutationFn: () => longitudinalService.loadSampleData(),
    onSuccess: (data) => {
      toast.success(
        `Sample data loaded! ${data.total_episodes} episodes, ${data.total_visits} visits, ${data.total_metrics} metrics created.`
      )
      queryClient.invalidateQueries({ queryKey: ['longitudinal'] })
      setShowLoadDataModal(false)
    },
    onError: (error: any) => {
      toast.error(`Failed to load sample data: ${error.response?.data?.detail || error.message}`)
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

  // Initialize sorted timeline events
  useEffect(() => {
    if (timelineQuery.data) {
      setSortedTimelineEvents([...timelineQuery.data])
    }
  }, [timelineQuery.data])

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event
    if (over && active.id !== over.id) {
      setSortedTimelineEvents((items) => {
        const oldIndex = items.findIndex((item) => item.visit_id === Number(active.id))
        const newIndex = items.findIndex((item) => item.visit_id === Number(over.id))
        return arrayMove(items, oldIndex, newIndex)
      })
    }
  }

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

  const buildReportPayload = (): ReportCreatePayload => {
    const payload: ReportCreatePayload = {
      format: reportForm.format,
      report_type: reportForm.reportType,
    }

    if (reportForm.start) {
      payload.start_date = new Date(reportForm.start).toISOString()
    }
    if (reportForm.end) {
      payload.end_date = new Date(reportForm.end).toISOString()
    }

    if (reportForm.reportType !== 'summary') {
      const cohortFilters: Record<string, unknown> = {}
      if (reportForm.cohortGender) cohortFilters.gender = reportForm.cohortGender
      if (reportForm.cohortAgeMin) {
        const value = Number(reportForm.cohortAgeMin)
        if (!Number.isNaN(value)) cohortFilters.age_min = value
      }
      if (reportForm.cohortAgeMax) {
        const value = Number(reportForm.cohortAgeMax)
        if (!Number.isNaN(value)) cohortFilters.age_max = value
      }
      if (reportForm.cohortPatientIds.trim()) {
        cohortFilters.patient_ids = reportForm.cohortPatientIds
          .split(',')
          .map((id) => id.trim())
          .filter(Boolean)
      }
      if (Object.keys(cohortFilters).length > 0) {
        payload.cohort_filters = cohortFilters
      }
    }

    if (reportForm.reportType === 'cohort_vs_cohort') {
      const comparisonFilters: Record<string, unknown> = {}
      if (reportForm.comparisonGender) comparisonFilters.gender = reportForm.comparisonGender
      if (reportForm.comparisonPatientIds.trim()) {
        comparisonFilters.patient_ids = reportForm.comparisonPatientIds
          .split(',')
          .map((id) => id.trim())
          .filter(Boolean)
      }
      if (Object.keys(comparisonFilters).length > 0) {
        payload.comparison_filters = comparisonFilters
      }
    }

    return payload
  }

  const generateReportMutation = useMutation({
    mutationFn: async () => {
      if (!selectedEpisodeId) {
        throw new Error('Episode must be selected before generating a report.')
      }
      const payload = buildReportPayload()
      return longitudinalService.generateReport(selectedEpisodeId, payload)
    },
    onSuccess: () => {
      reportsQuery.refetch()
      setReportForm({
        start: '',
        end: '',
        format: 'xlsx',
        reportType: 'summary',
        cohortGender: '',
        cohortAgeMin: '',
        cohortAgeMax: '',
        cohortPatientIds: '',
        comparisonGender: '',
        comparisonPatientIds: '',
      })
      setReportError(null)
    },
    onError: (error: any) => {
      setReportError(error?.response?.data?.detail || 'Unable to generate report.')
    },
  })

  const buildSchedulePayload = () => {
    if (!selectedEpisodeId) {
      throw new Error('Episode must be selected before creating a schedule.')
    }
    const payload: {
      name: string
      episode_id: number
      report_type: string
      schedule_cron: string
      cohort_filters?: Record<string, unknown>
      comparison_filters?: Record<string, unknown>
    } = {
      name: scheduleForm.name.trim() || `Scheduled ${new Date().toLocaleDateString()}`,
      episode_id: selectedEpisodeId,
      report_type: scheduleForm.reportType,
      schedule_cron: scheduleForm.scheduleCron || '0 6 * * 1',
    }

    if (scheduleForm.reportType !== 'summary') {
      const cohortFilters: Record<string, unknown> = {}
      if (scheduleForm.cohortGender) cohortFilters.gender = scheduleForm.cohortGender
      if (scheduleForm.cohortAgeMin) {
        const value = Number(scheduleForm.cohortAgeMin)
        if (!Number.isNaN(value)) cohortFilters.age_min = value
      }
      if (scheduleForm.cohortAgeMax) {
        const value = Number(scheduleForm.cohortAgeMax)
        if (!Number.isNaN(value)) cohortFilters.age_max = value
      }
      if (scheduleForm.cohortPatientIds.trim()) {
        cohortFilters.patient_ids = scheduleForm.cohortPatientIds
          .split(',')
          .map((id) => id.trim())
          .filter(Boolean)
      }
      if (Object.keys(cohortFilters).length > 0) {
        payload.cohort_filters = cohortFilters
      }
    }

    if (scheduleForm.reportType === 'cohort_vs_cohort') {
      const comparisonFilters: Record<string, unknown> = {}
      if (scheduleForm.comparisonGender) comparisonFilters.gender = scheduleForm.comparisonGender
      if (scheduleForm.comparisonPatientIds.trim()) {
        comparisonFilters.patient_ids = scheduleForm.comparisonPatientIds
          .split(',')
          .map((id) => id.trim())
          .filter(Boolean)
      }
      if (Object.keys(comparisonFilters).length > 0) {
        payload.comparison_filters = comparisonFilters
      }
    }

    return payload
  }

  const createScheduleMutation = useMutation({
    mutationFn: async () => {
      const payload = buildSchedulePayload()
      return longitudinalService.createReportSchedule(payload)
    },
    onSuccess: () => {
      schedulesQuery.refetch()
      setScheduleForm({
        name: '',
        scheduleCron: '0 6 * * 1',
        reportType: 'summary',
        cohortGender: '',
        cohortAgeMin: '',
        cohortAgeMax: '',
        cohortPatientIds: '',
        comparisonGender: '',
        comparisonPatientIds: '',
      })
      setScheduleError(null)
    },
    onError: (error: any) => {
      setScheduleError(error?.response?.data?.detail || 'Unable to create schedule.')
    },
  })

  const updateScheduleStatusMutation = useMutation({
    mutationFn: ({ scheduleId, status }: { scheduleId: number; status: ReportScheduleStatus }) =>
      longitudinalService.updateReportScheduleStatus(scheduleId, status),
    onSuccess: () => {
      schedulesQuery.refetch()
      setScheduleError(null)
    },
    onError: (error: any) => {
      setScheduleError(error?.response?.data?.detail || 'Unable to update schedule status.')
    },
  })

  const deleteScheduleMutation = useMutation({
    mutationFn: (scheduleId: number) => longitudinalService.deleteReportSchedule(scheduleId),
    onSuccess: (_, scheduleId) => {
      schedulesQuery.refetch()
      if (expandedScheduleId === scheduleId) {
        setExpandedScheduleId(null)
      }
      setScheduleError(null)
    },
    onError: (error: any) => {
      setScheduleError(error?.response?.data?.detail || 'Unable to delete schedule.')
    },
  })

  const enqueueRunMutation = useMutation({
    mutationFn: (scheduleId: number) => longitudinalService.enqueueScheduleRun(scheduleId),
    onSuccess: (_, scheduleId) => {
      schedulesQuery.refetch()
      if (expandedScheduleId === scheduleId) {
        scheduleRunsQuery.refetch()
      } else {
        setExpandedScheduleId(scheduleId)
      }
      setScheduleError(null)
    },
    onError: (error: any) => {
      setScheduleError(error?.response?.data?.detail || 'Unable to queue run.')
    },
  })

  const executeRunMutation = useMutation({
    mutationFn: (runId: number) => longitudinalService.executeScheduleRun(runId),
    onSuccess: () => {
      schedulesQuery.refetch()
      scheduleRunsQuery.refetch()
      setScheduleError(null)
    },
    onError: (error: any) => {
      setScheduleError(error?.response?.data?.detail || 'Unable to execute run.')
    },
  })

  const handleDownload = async (report: LongitudinalReport, variant: 'excel' | 'pdf') => {
    try {
      setReportError(null)
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

  const handleViewHeatmap = async (report: LongitudinalReport) => {
    if (!report.heatmap_path) {
      setReportError('No heatmap available for this report.')
      return
    }
    try {
      setReportError(null)
      if (heatmapPreview) {
        URL.revokeObjectURL(heatmapPreview.url)
      }
      const response = await longitudinalService.downloadReportHeatmap(report.id)
      const blob = new Blob([response.data], { type: 'image/png' })
      const url = URL.createObjectURL(blob)
      const disposition = response.headers['content-disposition'] as string | undefined
      let filename = `heatmap-${report.id}.png`
      if (disposition) {
        const match = disposition.match(/filename="?([^";]+)"?/i)
        if (match && match[1]) {
          filename = match[1]
        }
      }
      setHeatmapPreview({ url, name: filename })
    } catch (error: any) {
      setReportError(error?.response?.data?.detail || 'Failed to load heatmap.')
    }
  }

  const handleCreateSchedule = () => {
    if (createScheduleMutation.isPending) return
    try {
      createScheduleMutation.mutate()
    } catch (error: any) {
      setScheduleError(error?.message || 'Unable to create schedule.')
    }
  }

  const handleToggleScheduleStatus = (schedule: ReportSchedule) => {
    const nextStatus: ReportScheduleStatus =
      schedule.status === 'active' ? 'paused' : 'active'
    updateScheduleStatusMutation.mutate({ scheduleId: schedule.id, status: nextStatus })
  }

  const handleDeleteSchedule = (schedule: ReportSchedule) => {
    deleteScheduleMutation.mutate(schedule.id)
  }

  const handleQueueRun = (schedule: ReportSchedule) => {
    enqueueRunMutation.mutate(schedule.id)
  }

  const handleExecuteRun = (run: ReportRun) => {
    executeRunMutation.mutate(run.id)
  }

  const handleExpandSchedule = (scheduleId: number) => {
    setExpandedScheduleId((prev) => (prev === scheduleId ? null : scheduleId))
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-semibold text-white">Longitudinal Tracking</h1>
          <p className="text-sm text-slate-400">
            Explore patient episodes, visit timelines, and progression trends across cognitive, biomarker, and imaging metrics.
          </p>
        </div>
        <button
          onClick={() => setShowLoadDataModal(true)}
          className="flex items-center gap-2 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500"
        >
          <PlusIcon className="h-5 w-5" />
          Load Sample Data
        </button>
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
                        setReportForm({
                          start: '',
                          end: '',
                          format: 'xlsx',
                          reportType: 'summary',
                          cohortGender: '',
                          cohortAgeMin: '',
                          cohortAgeMax: '',
                          cohortPatientIds: '',
                          comparisonGender: '',
                          comparisonPatientIds: '',
                        })
                        setReportError(null)
                        setScheduleForm({
                          name: '',
                          scheduleCron: '0 6 * * 1',
                          reportType: 'summary',
                          cohortGender: '',
                          cohortAgeMin: '',
                          cohortAgeMax: '',
                          cohortPatientIds: '',
                          comparisonGender: '',
                          comparisonPatientIds: '',
                        })
                        setScheduleError(null)
                        setExpandedScheduleId(null)
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

              <div className="mt-4">
                <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
                  <SortableContext items={sortedTimelineEvents.map((e) => e.visit_id)} strategy={verticalListSortingStrategy}>
                    <div className="space-y-4">
                      {sortedTimelineEvents.map((event) => (
                        <SortableTimelineEvent
                          key={event.visit_id}
                          event={event}
                          reports={reportsQuery.data ?? []}
                          onCompare={() => toggleVisitForComparison(event.visit_id, event.imaging_available)}
                          isSelected={comparisonSelection.includes(event.visit_id)}
                          onViewReport={(reportId) => setSelectedReportId(reportId)}
                        />
                      ))}
                      {sortedTimelineEvents.length === 0 && !timelineQuery.isLoading && (
                        <p className="text-sm text-slate-400">No visits recorded yet.</p>
                      )}
                    </div>
                  </SortableContext>
                </DndContext>
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
            <div className="mt-6 flex items-center gap-2">
              <button
                type="button"
                onClick={() => setShowCohortAnalysis(!showCohortAnalysis)}
                className={clsx(
                  'inline-flex items-center gap-2 rounded-lg border px-3 py-1.5 text-xs transition',
                  showCohortAnalysis
                    ? 'border-sky-500 bg-sky-500/10 text-sky-200'
                    : 'border-slate-700 bg-slate-900 text-slate-300 hover:border-sky-400 hover:text-sky-200'
                )}
              >
                <ChartBarIcon className="h-4 w-4" />
                {showCohortAnalysis ? 'Hide' : 'Show'} Cohort Analysis
              </button>
            </div>
            {showCohortAnalysis && selectedEpisodeId && (
              <CohortAnalysisPanel episodeId={selectedEpisodeId} reports={reportsQuery.data ?? []} />
            )}
            <ReportsPanel
              reports={reportsQuery.data ?? []}
              isLoading={reportsQuery.isLoading || generateReportMutation.isPending}
              reportForm={reportForm}
              onChangeForm={(form) => setReportForm(form)}
              onGenerate={() => generateReportMutation.mutate()}
              onDownload={handleDownload}
              onViewHeatmap={handleViewHeatmap}
              error={reportError}
              selectedReportId={selectedReportId}
              onSelectReport={setSelectedReportId}
            />
            <SchedulesPanel
              schedules={applicableSchedules}
              runs={scheduleRuns}
              isLoadingSchedules={schedulesQuery.isLoading}
              isLoadingRuns={scheduleRunsQuery.isLoading}
              form={scheduleForm}
              onChangeForm={(form) => setScheduleForm(form)}
              onCreate={handleCreateSchedule}
              onToggleStatus={handleToggleScheduleStatus}
              onDelete={handleDeleteSchedule}
              onQueueRun={handleQueueRun}
              onExecuteRun={handleExecuteRun}
              expandedScheduleId={expandedScheduleId}
              onExpand={handleExpandSchedule}
              error={scheduleError}
              isCreating={createScheduleMutation.isPending}
              isUpdatingStatus={updateScheduleStatusMutation.isPending}
              isDeleting={deleteScheduleMutation.isPending}
              isQueuingRun={enqueueRunMutation.isPending}
              isExecutingRun={executeRunMutation.isPending}
            />
          </div>
        </section>
      )}

      {/* Load Sample Data Modal */}
      <LoadSampleDataModal
        isOpen={showLoadDataModal}
        onClose={() => setShowLoadDataModal(false)}
        onConfirm={() => loadSampleDataMutation.mutate()}
        isPending={loadSampleDataMutation.isPending}
      />

      {heatmapPreview && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-slate-950/80 px-4">
          <div className="w-full max-w-4xl rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-lg">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div className="text-sm font-semibold text-white">{heatmapPreview.name}</div>
              <button
                type="button"
                onClick={() => setHeatmapPreview(null)}
                className="rounded border border-slate-700 px-3 py-1 text-xs text-slate-200 hover:border-rose-400 hover:text-rose-200"
              >
                Close
              </button>
            </div>
            <div className="max-h-[70vh] overflow-auto rounded-xl border border-slate-800 bg-slate-950/70 p-2">
              <img
                src={heatmapPreview.url}
                alt="Report heatmap"
                className="mx-auto max-h-[65vh] w-full object-contain"
              />
            </div>
          </div>
        </div>
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
  reportForm: ReportFormState
  onChangeForm: (form: ReportFormState) => void
  onGenerate: () => void
  onDownload: (report: LongitudinalReport, variant: 'excel' | 'pdf') => void
  onViewHeatmap: (report: LongitudinalReport) => void
  error?: string | null
  selectedReportId?: number | null
  onSelectReport?: (reportId: number | null) => void
}

function ReportsPanel({
  reports,
  isLoading,
  reportForm,
  onChangeForm,
  onGenerate,
  onDownload,
  onViewHeatmap,
  error,
  selectedReportId,
  onSelectReport,
}: ReportsPanelProps) {
  const showCohortFields = reportForm.reportType !== 'summary'
  const showComparisonFields = reportForm.reportType === 'cohort_vs_cohort'
  const formatNumber = (value?: number | null, fractionDigits = 2) => {
    if (value === null || value === undefined) return '—'
    return Number.isInteger(value) ? `${value}` : value.toFixed(fractionDigits)
  }

  return (
    <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h4 className="text-sm font-semibold text-white">Longitudinal reports</h4>
          <p className="text-xs text-slate-400">
            Generate periodic summaries, cohort comparisons, and high-fidelity exports.
          </p>
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
          <select
            value={reportForm.reportType}
            onChange={(event) =>
              onChangeForm({
                ...reportForm,
                reportType: event.target.value as ReportFormState['reportType'],
              })
            }
            className="rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
          >
            <option value="summary">Summary</option>
            <option value="cohort_patient_vs_average">Patient vs Cohort</option>
            <option value="cohort_vs_cohort">Cohort vs Cohort</option>
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
      {showCohortFields && (
        <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-4">
          <label className="text-xs text-slate-400">
            Cohort gender
            <select
              value={reportForm.cohortGender}
              onChange={(event) => onChangeForm({ ...reportForm, cohortGender: event.target.value })}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            >
              <option value="">Any</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label className="text-xs text-slate-400">
            Age min
            <input
              type="number"
              min={0}
              value={reportForm.cohortAgeMin}
              onChange={(event) => onChangeForm({ ...reportForm, cohortAgeMin: event.target.value })}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            />
          </label>
          <label className="text-xs text-slate-400">
            Age max
            <input
              type="number"
              min={0}
              value={reportForm.cohortAgeMax}
              onChange={(event) => onChangeForm({ ...reportForm, cohortAgeMax: event.target.value })}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            />
          </label>
          <label className="text-xs text-slate-400 md:col-span-1">
            Cohort patient IDs
            <input
              type="text"
              value={reportForm.cohortPatientIds}
              onChange={(event) => onChangeForm({ ...reportForm, cohortPatientIds: event.target.value })}
              placeholder="e.g. PT-101, PT-202"
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            />
          </label>
        </div>
      )}
      {showComparisonFields && (
        <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-3">
          <label className="text-xs text-slate-400">
            Comparison gender
            <select
              value={reportForm.comparisonGender}
              onChange={(event) => onChangeForm({ ...reportForm, comparisonGender: event.target.value })}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            >
              <option value="">Any</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label className="text-xs text-slate-400 md:col-span-2">
            Comparison patient IDs
            <input
              type="text"
              value={reportForm.comparisonPatientIds}
              onChange={(event) => onChangeForm({ ...reportForm, comparisonPatientIds: event.target.value })}
              placeholder="e.g. PT-301, PT-402"
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            />
          </label>
        </div>
      )}
      {error && (
        <p className="mt-3 rounded-xl border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-xs text-rose-200">{error}</p>
      )}
      {isLoading && reports.length === 0 ? (
        <p className="mt-3 text-xs text-slate-400">Processing…</p>
      ) : (
        <div className="mt-3 space-y-3">
          {reports.map((report) => {
            const metrics = report.summary?.metrics ?? {}
            const comparisonRows = report.summary?.comparison?.table ?? []
            return (
              <div
                key={report.id}
                className={clsx(
                  'space-y-3 rounded-xl border p-4 text-xs text-slate-200 transition',
                  selectedReportId === report.id
                    ? 'border-sky-500 bg-sky-500/10'
                    : 'border-slate-800/70 bg-slate-950/70 hover:border-slate-700'
                )}
                onClick={() => onSelectReport?.(report.id)}
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div>
                    <div className="font-medium text-white">
                      {report.report_type} • {format(new Date(report.created_at), 'PPpp')}
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Range {report.start_date ? format(new Date(report.start_date), 'PP') : 'start'} →{' '}
                      {report.end_date ? format(new Date(report.end_date), 'PP') : 'latest'} • Format{' '}
                      {report.format.toUpperCase()}
                    </div>
                    {report.summary?.cohort_size && (
                      <div className="text-[11px] text-slate-500">
                        Cohort size {report.summary.cohort_size}
                      </div>
                    )}
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
                    {report.heatmap_path && (
                      <button
                        type="button"
                        onClick={() => onViewHeatmap(report)}
                        className="rounded border border-rose-500/40 px-2 py-0.5 text-xs text-rose-200 hover:border-rose-400 hover:text-rose-100"
                      >
                        Heatmap
                      </button>
                    )}
                  </div>
                </div>
                {Object.keys(metrics).length > 0 && (
                  <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                    {Object.entries(metrics).map(([metricKey, stats]) => (
                      <div key={metricKey} className="rounded-lg border border-slate-800/60 bg-slate-950/60 px-3 py-2">
                        <div className="text-[11px] uppercase text-slate-500">{metricKey}</div>
                        <div className="text-xs text-slate-300">
                          Avg {formatNumber(stats.average)} • Latest {formatNumber(stats.latest)}
                        </div>
                        <div className="text-[11px] text-slate-500">
                          Min {formatNumber(stats.minimum)} / Max {formatNumber(stats.maximum)} • Slope{' '}
                          {formatNumber(stats.slope)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                {comparisonRows.length > 0 && (
                  <div className="rounded-lg border border-slate-800/60 bg-slate-950/40 p-3 text-[11px] text-slate-400">
                    <div className="mb-1 font-semibold text-slate-300">Comparison snapshot</div>
                    <ul className="space-y-1">
                      {comparisonRows.slice(0, 4).map((row) => (
                        <li key={row.metric}>
                          <span className="text-slate-300">{row.metric}</span>: Δ {formatNumber(row.delta, 3)}
                        </li>
                      ))}
                      {comparisonRows.length > 4 && <li>+{comparisonRows.length - 4} more metrics…</li>}
                    </ul>
                  </div>
                )}
              </div>
            )
          })}
          {reports.length === 0 && <p className="text-xs text-slate-500">No reports generated yet.</p>}
        </div>
      )}
    </div>
  )
}

type SchedulesPanelProps = {
  schedules: ReportSchedule[]
  runs: ReportRun[]
  isLoadingSchedules: boolean
  isLoadingRuns: boolean
  form: ScheduleFormState
  onChangeForm: (form: ScheduleFormState) => void
  onCreate: () => void
  onToggleStatus: (schedule: ReportSchedule) => void
  onDelete: (schedule: ReportSchedule) => void
  onQueueRun: (schedule: ReportSchedule) => void
  onExecuteRun: (run: ReportRun) => void
  expandedScheduleId: number | null
  onExpand: (scheduleId: number) => void
  error?: string | null
  isCreating: boolean
  isUpdatingStatus: boolean
  isDeleting: boolean
  isQueuingRun: boolean
  isExecutingRun: boolean
}

function SchedulesPanel({
  schedules,
  runs,
  isLoadingSchedules,
  isLoadingRuns,
  form,
  onChangeForm,
  onCreate,
  onToggleStatus,
  onDelete,
  onQueueRun,
  onExecuteRun,
  expandedScheduleId,
  onExpand,
  error,
  isCreating,
  isUpdatingStatus,
  isDeleting,
  isQueuingRun,
  isExecutingRun,
}: SchedulesPanelProps) {
  const showCohortFields = form.reportType !== 'summary'
  const showComparisonFields = form.reportType === 'cohort_vs_cohort'
  const renderScheduleStatus = (status: ReportScheduleStatus) => {
    const labels: Record<ReportScheduleStatus, string> = {
      active: 'Active',
      paused: 'Paused',
      archived: 'Archived',
    }
    const styles: Record<ReportScheduleStatus, string> = {
      active: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
      paused: 'border-amber-500/40 bg-amber-500/10 text-amber-300',
      archived: 'border-slate-700 bg-slate-900 text-slate-400',
    }
    return (
      <span className={clsx('rounded-full border px-2 py-0.5 text-xs uppercase tracking-wide', styles[status])}>
        {labels[status]}
      </span>
    )
  }

  const renderRunStatus = (status: ReportRunStatus) => {
    const labels: Record<ReportRunStatus, string> = {
      queued: 'Queued',
      running: 'Running',
      success: 'Success',
      failed: 'Failed',
    }
    const styles: Record<ReportRunStatus, string> = {
      queued: 'border-slate-600 bg-slate-900 text-slate-300',
      running: 'border-sky-500/40 bg-sky-500/10 text-sky-200',
      success: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300',
      failed: 'border-rose-500/40 bg-rose-500/10 text-rose-300',
    }
    return (
      <span className={clsx('rounded-full border px-2 py-0.5 text-[10px] uppercase tracking-wide', styles[status])}>
        {labels[status]}
      </span>
    )
  }

  return (
    <div className="mt-6 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h4 className="text-sm font-semibold text-white">Scheduled reports</h4>
          <p className="text-xs text-slate-400">
            Automate cohort comparisons and exports. Cron syntax uses server timezone.
          </p>
        </div>
      </div>
      <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-3">
        <label className="text-xs text-slate-400">
          Name
          <input
            type="text"
            value={form.name}
            onChange={(event) => onChangeForm({ ...form, name: event.target.value })}
            placeholder="e.g. Weekly summary"
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
          />
        </label>
        <label className="text-xs text-slate-400">
          Cron expression
          <input
            type="text"
            value={form.scheduleCron}
            onChange={(event) => onChangeForm({ ...form, scheduleCron: event.target.value })}
            placeholder="0 6 * * 1"
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
          />
        </label>
        <label className="text-xs text-slate-400">
          Report type
          <select
            value={form.reportType}
            onChange={(event) =>
              onChangeForm({
                ...form,
                reportType: event.target.value as ScheduleFormState['reportType'],
              })
            }
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
          >
            <option value="summary">Summary</option>
            <option value="cohort_patient_vs_average">Patient vs Cohort</option>
            <option value="cohort_vs_cohort">Cohort vs Cohort</option>
          </select>
        </label>
      </div>
      {showCohortFields && (
        <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-4">
          <label className="text-xs text-slate-400">
            Cohort gender
            <select
              value={form.cohortGender}
              onChange={(event) => onChangeForm({ ...form, cohortGender: event.target.value })}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            >
              <option value="">Any</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label className="text-xs text-slate-400">
            Age min
            <input
              type="number"
              min={0}
              value={form.cohortAgeMin}
              onChange={(event) => onChangeForm({ ...form, cohortAgeMin: event.target.value })}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            />
          </label>
          <label className="text-xs text-slate-400">
            Age max
            <input
              type="number"
              min={0}
              value={form.cohortAgeMax}
              onChange={(event) => onChangeForm({ ...form, cohortAgeMax: event.target.value })}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            />
          </label>
          <label className="text-xs text-slate-400 md:col-span-1">
            Cohort patient IDs
            <input
              type="text"
              value={form.cohortPatientIds}
              onChange={(event) => onChangeForm({ ...form, cohortPatientIds: event.target.value })}
              placeholder="PT-101, PT-202"
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            />
          </label>
        </div>
      )}
      {showComparisonFields && (
        <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-3">
          <label className="text-xs text-slate-400">
            Comparison gender
            <select
              value={form.comparisonGender}
              onChange={(event) => onChangeForm({ ...form, comparisonGender: event.target.value })}
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            >
              <option value="">Any</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
              <option value="other">Other</option>
            </select>
          </label>
          <label className="text-xs text-slate-400 md:col-span-2">
            Comparison patient IDs
            <input
              type="text"
              value={form.comparisonPatientIds}
              onChange={(event) => onChangeForm({ ...form, comparisonPatientIds: event.target.value })}
              placeholder="PT-301, PT-402"
              className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1 text-xs text-white focus:border-sky-500 focus:outline-none"
            />
          </label>
        </div>
      )}
      <div className="mt-3 flex items-center justify-between">
        <button
          type="button"
          onClick={onCreate}
          disabled={isCreating}
          className="rounded border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-200 hover:border-emerald-400 hover:text-emerald-100 disabled:opacity-40"
        >
          {isCreating ? 'Creating…' : 'Create schedule'}
        </button>
        {error && <p className="text-xs text-rose-300">{error}</p>}
      </div>
      {isLoadingSchedules ? (
        <p className="mt-3 text-xs text-slate-400">Loading schedules…</p>
      ) : schedules.length === 0 ? (
        <p className="mt-3 text-xs text-slate-500">No schedules yet. Create your first automated report.</p>
      ) : (
        <div className="mt-4 space-y-3">
          {schedules.map((schedule) => (
            <div key={schedule.id} className="space-y-2 rounded-xl border border-slate-800/70 bg-slate-950/70 px-4 py-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <div className="text-sm font-semibold text-white">{schedule.name}</div>
                  <div className="text-[11px] text-slate-400">
                    Cron: <code className="font-mono text-slate-300">{schedule.schedule_cron}</code>
                  </div>
                  {schedule.last_run_at && (
                    <div className="text-[11px] text-slate-500">
                      Last run {format(new Date(schedule.last_run_at), 'PPpp')}
                    </div>
                  )}
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  {renderScheduleStatus(schedule.status)}
                  <button
                    type="button"
                    onClick={() => onToggleStatus(schedule)}
                    disabled={isUpdatingStatus || schedule.status === 'archived'}
                    className="rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-200 hover:border-sky-400 hover:text-sky-200 disabled:opacity-40"
                  >
                    {schedule.status === 'active' ? 'Pause' : 'Resume'}
                  </button>
                  <button
                    type="button"
                    onClick={() => onQueueRun(schedule)}
                    disabled={isQueuingRun || schedule.status === 'archived'}
                    className="rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-200 hover:border-emerald-400 hover:text-emerald-200 disabled:opacity-40"
                  >
                    Run now
                  </button>
                  <button
                    type="button"
                    onClick={() => onExpand(schedule.id)}
                    className="rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-200 hover:border-sky-400 hover:text-sky-200"
                  >
                    {expandedScheduleId === schedule.id ? 'Hide runs' : 'View runs'}
                  </button>
                  <button
                    type="button"
                    onClick={() => onDelete(schedule)}
                    disabled={isDeleting}
                    className="rounded border border-rose-500/40 px-2 py-0.5 text-xs text-rose-200 hover:border-rose-400 hover:text-rose-100 disabled:opacity-40"
                  >
                    Delete
                  </button>
                </div>
              </div>
              {expandedScheduleId === schedule.id && (
                <div className="rounded-lg border border-slate-800/60 bg-slate-950/50 p-3">
                  {isLoadingRuns ? (
                    <p className="text-[11px] text-slate-400">Loading runs…</p>
                  ) : runs.length === 0 ? (
                    <p className="text-[11px] text-slate-500">No runs yet.</p>
                  ) : (
                    <div className="space-y-2">
                      {runs.map((run) => (
                        <div
                          key={run.id}
                          className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-800/70 bg-slate-950/70 px-3 py-2"
                        >
                          <div className="flex flex-col gap-1 text-[11px] text-slate-400">
                            <div className="flex items-center gap-2 text-xs text-slate-200">
                              Run #{run.id} {renderRunStatus(run.status)}
                            </div>
                            {run.started_at && <div>Started {format(new Date(run.started_at), 'PPpp')}</div>}
                            {run.finished_at && <div>Finished {format(new Date(run.finished_at), 'PPpp')}</div>}
                            {run.error_message && (
                              <div className="text-rose-300">Error: {run.error_message.slice(0, 120)}</div>
                            )}
                          </div>
                          <div className="flex flex-wrap items-center gap-2">
                            {run.status === 'queued' && (
                              <button
                                type="button"
                                onClick={() => onExecuteRun(run)}
                                disabled={isExecutingRun}
                                className="rounded border border-slate-700 px-2 py-0.5 text-xs text-slate-200 hover:border-emerald-400 hover:text-emerald-200 disabled:opacity-40"
                              >
                                Execute
                              </button>
                            )}
                            {run.report_id && (
                              <span className="text-[11px] text-slate-500">
                                Report #{run.report_id} available in history
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

type SortableTimelineEventProps = {
  event: TimelineEvent
  reports: LongitudinalReport[]
  onCompare: () => void
  isSelected: boolean
  onViewReport: (reportId: number) => void
}

function SortableTimelineEvent({ event, reports, onCompare, isSelected, onViewReport }: SortableTimelineEventProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: event.visit_id,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  }

  // Find reports that include this visit date
  const relatedReports = reports.filter((report) => {
    if (!report.start_date || !report.end_date) return false
    const visitDate = new Date(event.visit_date)
    const startDate = new Date(report.start_date)
    const endDate = new Date(report.end_date)
    return visitDate >= startDate && visitDate <= endDate
  })

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={clsx(
        'rounded-2xl border border-slate-800/80 bg-slate-900/80 p-4',
        isDragging && 'shadow-lg ring-2 ring-sky-500/50'
      )}
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <button
            {...attributes}
            {...listeners}
            className="cursor-grab active:cursor-grabbing rounded border border-slate-700 p-1 text-slate-400 hover:border-sky-400 hover:text-sky-300"
            title="Drag to reorder"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8h16M4 16h16" />
            </svg>
          </button>
          <div className="text-sm font-semibold text-white">
            {event.label} • {format(new Date(event.visit_date), 'PP')}
          </div>
        </div>
        <div className="flex items-center gap-2">
          {relatedReports.length > 0 && (
            <div className="flex items-center gap-1">
              <LinkIcon className="h-3 w-3 text-sky-400" />
              <select
                className="rounded border border-slate-700 bg-slate-950 px-2 py-0.5 text-xs text-sky-300 focus:border-sky-500 focus:outline-none"
                onChange={(e) => {
                  const reportId = Number(e.target.value)
                  if (reportId) onViewReport(reportId)
                }}
                onClick={(e) => e.stopPropagation()}
              >
                <option value="">Reports ({relatedReports.length})</option>
                {relatedReports.map((report) => (
                  <option key={report.id} value={report.id}>
                    {report.report_type} - {format(new Date(report.created_at), 'MM/dd/yyyy')}
                  </option>
                ))}
              </select>
            </div>
          )}
          <button
            type="button"
            disabled={!event.imaging_available}
            onClick={onCompare}
            className={clsx(
              'rounded-full border px-3 py-1 text-xs transition',
              event.imaging_available
                ? isSelected
                  ? 'border-sky-500 bg-sky-500/20 text-sky-200'
                  : 'border-slate-700 bg-slate-900 text-slate-300 hover:border-sky-400 hover:text-sky-200'
                : 'cursor-not-allowed border-slate-800 bg-slate-900 text-slate-600'
            )}
          >
            {isSelected ? 'Selected' : 'Compare'}
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
        {event.metrics.length === 0 && <p className="text-sm text-slate-500">No metrics recorded.</p>}
      </div>
    </div>
  )
}

type CohortAnalysisPanelProps = {
  episodeId: number
  reports: LongitudinalReport[]
}

function CohortAnalysisPanel({ episodeId, reports }: CohortAnalysisPanelProps) {
  const cohortReports = reports.filter((r) => r.report_type !== 'summary')
  const { data: combinedAlerts } = useQuery({
    queryKey: ['combined-alerts', episodeId],
    queryFn: () => longitudinalService.fetchCombinedAlerts(episodeId),
    enabled: episodeId !== null,
  })

  if (cohortReports.length === 0) {
    return (
      <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h4 className="text-sm font-semibold text-white">Cohort Analysis</h4>
        <p className="mt-2 text-xs text-slate-400">Generate cohort comparison reports to see analysis here.</p>
      </div>
    )
  }

  const comparisonData = cohortReports
    .filter((r) => r.summary?.comparison?.table)
    .flatMap((r) => r.summary?.comparison?.table ?? [])
    .reduce((acc, row) => {
      if (!acc[row.metric]) {
        acc[row.metric] = []
      }
      if (row.delta !== null && row.delta !== undefined) {
        acc[row.metric].push(row.delta)
      }
      return acc
    }, {} as Record<string, number[]>)

  const chartData = Object.entries(comparisonData).map(([metric, deltas]) => ({
    metric,
    avgDelta: deltas.length > 0 ? deltas.reduce((a, b) => a + b, 0) / deltas.length : 0,
    count: deltas.length,
  }))

  return (
    <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
      <h4 className="text-sm font-semibold text-white">Cohort Analysis</h4>
      <p className="mt-1 text-xs text-slate-400">
        Comparison metrics across {cohortReports.length} cohort report{cohortReports.length > 1 ? 's' : ''}
      </p>

      {chartData.length > 0 && (
        <div className="mt-4 h-64 rounded-xl border border-slate-800 bg-slate-950/60 p-4">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="metric" stroke="#94a3b8" angle={-45} textAnchor="end" height={80} />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  background: '#0f172a',
                  borderRadius: '12px',
                  borderColor: '#1e293b',
                }}
              />
              <Bar dataKey="avgDelta" fill="#38bdf8" name="Average Delta" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {combinedAlerts?.alerts && combinedAlerts.alerts.length > 0 && (
        <div className="mt-4 space-y-2">
          <h5 className="text-xs font-semibold text-white">Combined Alerts</h5>
          {combinedAlerts.alerts.map((alert: any, idx: number) => (
            <div
              key={idx}
              className={clsx(
                'rounded-lg border p-2 text-xs',
                alert.severity === 'high'
                  ? 'border-rose-500/40 bg-rose-500/10 text-rose-200'
                  : 'border-amber-500/40 bg-amber-500/10 text-amber-200'
              )}
            >
            {alert.message}
          </div>
        ))}
      </div>
    )}
  </div>
  )
}

// Load Sample Data Modal Component
function LoadSampleDataModal({ isOpen, onClose, onConfirm, isPending }: {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  isPending: boolean
}) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
        <h3 className="text-xl font-semibold text-white">Load Sample Data</h3>
        <p className="mt-2 text-sm text-slate-400">
          This will create sample episodes, visits, and metrics for existing patients in the database.
          This is useful for testing the Longitudinal Tracking features.
        </p>

        <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950/60 p-3">
          <p className="text-xs text-slate-400 mb-2">What will be created:</p>
          <ul className="space-y-1 text-sm text-slate-300">
            <li>• 1-2 episodes per patient</li>
            <li>• 4-8 visits per episode</li>
            <li>• Multiple metrics per visit (cognitive, biomarker, imaging, functional)</li>
            <li>• Progression scores for each visit</li>
          </ul>
        </div>

        <div className="mt-6 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 rounded-full border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-700"
            disabled={isPending}
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-400"
            disabled={isPending}
          >
            {isPending ? 'Loading...' : 'Load Data'}
          </button>
        </div>
      </div>
    </div>
  )
}


