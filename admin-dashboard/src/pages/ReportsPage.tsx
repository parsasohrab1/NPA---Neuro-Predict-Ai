import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { ArrowDownTrayIcon, FunnelIcon, PlusCircleIcon } from '@heroicons/react/24/outline'
import clsx from 'clsx'
import { toast } from 'react-hot-toast'

import {
  reportsService,
  type ClinicalReport,
  type ClinicalReportFilters,
  type ResearchReport,
  type ResearchReportFilters,
  type ManagementReport,
  type ManagementReportFilters,
} from '../services/reports'

type ActiveTab = 'clinical' | 'research' | 'management'

const exportFormats: Array<{ value: 'pdf' | 'excel' | 'csv'; label: string }> = [
  { value: 'pdf', label: 'PDF' },
  { value: 'excel', label: 'Excel' },
  { value: 'csv', label: 'CSV' },
]

export default function ReportsPage() {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<ActiveTab>('clinical')
  const [showLoadDataModal, setShowLoadDataModal] = useState(false)

  const [clinicalFilters, setClinicalFilters] = useState({
    patientId: '',
    start: '',
    end: '',
  })
  const [appliedClinicalFilters, setAppliedClinicalFilters] = useState<ClinicalReportFilters | null>(null)

  const [researchFilters, setResearchFilters] = useState({
    start: '',
    end: '',
    diseaseType: '',
    riskLevel: '',
  })
  const [appliedResearchFilters, setAppliedResearchFilters] = useState<ResearchReportFilters | null>(null)

  const [managementFilters, setManagementFilters] = useState({
    modelVersion: '',
    start: '',
    end: '',
  })
  const [appliedManagementFilters, setAppliedManagementFilters] = useState<ManagementReportFilters | null>(null)

  const clinicalQuery = useQuery({
    queryKey: ['reports', 'clinical', appliedClinicalFilters],
    queryFn: () => reportsService.fetchClinical(appliedClinicalFilters!),
    enabled: Boolean(appliedClinicalFilters?.patientId),
  })

  const researchQuery = useQuery({
    queryKey: ['reports', 'research', appliedResearchFilters],
    queryFn: () => reportsService.fetchResearch(appliedResearchFilters!),
    enabled: Boolean(appliedResearchFilters),
  })

  const managementQuery = useQuery({
    queryKey: ['reports', 'management', appliedManagementFilters],
    queryFn: () => reportsService.fetchManagement(appliedManagementFilters!),
    enabled: Boolean(appliedManagementFilters),
  })

  const statsQuery = useQuery({
    queryKey: ['reports', 'stats'],
    queryFn: () => reportsService.getStats(),
    staleTime: 30000, // 30 seconds
  })

  const loadSampleDataMutation = useMutation({
    mutationFn: () => reportsService.loadSampleData(),
    onSuccess: (data) => {
      toast.success(
        `Sample data loaded! ${data.total_patients} patients, ${data.total_predictions} predictions created.`
      )
      queryClient.invalidateQueries({ queryKey: ['reports'] })
      setShowLoadDataModal(false)
    },
    onError: (error: any) => {
      toast.error(`Failed to load sample data: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleGenerate = () => {
    if (activeTab === 'clinical') {
      if (!clinicalFilters.patientId) {
        alert('Patient ID is required for clinical reports.')
        return
      }
      setAppliedClinicalFilters({
        patientId: Number(clinicalFilters.patientId),
        start: clinicalFilters.start || undefined,
        end: clinicalFilters.end || undefined,
      })
    }

    if (activeTab === 'research') {
      setAppliedResearchFilters({
        start: researchFilters.start || undefined,
        end: researchFilters.end || undefined,
        diseaseType: researchFilters.diseaseType || undefined,
        riskLevel: researchFilters.riskLevel || undefined,
      })
    }

    if (activeTab === 'management') {
      setAppliedManagementFilters({
        modelVersion: managementFilters.modelVersion || undefined,
        start: managementFilters.start || undefined,
        end: managementFilters.end || undefined,
      })
    }
  }

  const handleExport = async (formatType: 'pdf' | 'excel' | 'csv') => {
    const filters =
      activeTab === 'clinical'
        ? clinicalFilters
        : activeTab === 'research'
        ? researchFilters
        : managementFilters

    const response = await reportsService.exportReport({
      reportType: activeTab,
      format: formatType,
      filters,
    })

    alert(`${response.message} • Generated at ${format(new Date(response.generated_at), 'PPpp')}`)
  }

  const activeQuery = activeTab === 'clinical' ? clinicalQuery : activeTab === 'research' ? researchQuery : managementQuery

  const renderFilters = () => {
    if (activeTab === 'clinical') {
      return (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-xs uppercase text-slate-400">Patient ID</span>
            <input
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
              placeholder="e.g. 101"
              value={clinicalFilters.patientId}
              onChange={(event) => setClinicalFilters((prev) => ({ ...prev, patientId: event.target.value }))}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-xs uppercase text-slate-400">From</span>
            <input
              type="datetime-local"
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
              value={clinicalFilters.start}
              onChange={(event) => setClinicalFilters((prev) => ({ ...prev, start: event.target.value }))}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-xs uppercase text-slate-400">To</span>
            <input
              type="datetime-local"
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
              value={clinicalFilters.end}
              onChange={(event) => setClinicalFilters((prev) => ({ ...prev, end: event.target.value }))}
            />
          </label>
        </div>
      )
    }

    if (activeTab === 'research') {
      return (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-xs uppercase text-slate-400">From</span>
            <input
              type="date"
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
              value={researchFilters.start}
              onChange={(event) => setResearchFilters((prev) => ({ ...prev, start: event.target.value }))}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-xs uppercase text-slate-400">To</span>
            <input
              type="date"
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
              value={researchFilters.end}
              onChange={(event) => setResearchFilters((prev) => ({ ...prev, end: event.target.value }))}
            />
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-xs uppercase text-slate-400">Disease type</span>
            <select
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
              value={researchFilters.diseaseType}
              onChange={(event) => setResearchFilters((prev) => ({ ...prev, diseaseType: event.target.value }))}
            >
              <option value="">All</option>
              <option value="alzheimer">Alzheimer</option>
              <option value="parkinson">Parkinson</option>
              <option value="both">Both</option>
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="text-xs uppercase text-slate-400">Risk level</span>
            <select
              className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
              value={researchFilters.riskLevel}
              onChange={(event) => setResearchFilters((prev) => ({ ...prev, riskLevel: event.target.value }))}
            >
              <option value="">All</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>
        </div>
      )
    }

    return (
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-xs uppercase text-slate-400">Model version</span>
          <input
            className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
            placeholder="e.g. alzheimers-v2"
            value={managementFilters.modelVersion}
            onChange={(event) => setManagementFilters((prev) => ({ ...prev, modelVersion: event.target.value }))}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-xs uppercase text-slate-400">From</span>
          <input
            type="date"
            className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
            value={managementFilters.start}
            onChange={(event) => setManagementFilters((prev) => ({ ...prev, start: event.target.value }))}
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-xs uppercase text-slate-400">To</span>
          <input
            type="date"
            className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
            value={managementFilters.end}
            onChange={(event) => setManagementFilters((prev) => ({ ...prev, end: event.target.value }))}
          />
        </label>
      </div>
    )
  }

  const renderClinicalReport = (report: ClinicalReport | undefined) => {
    if (!appliedClinicalFilters) {
      return <p className="text-sm text-slate-400">Select a patient and generate the report.</p>
    }
    if (clinicalQuery.isLoading) {
      return <p className="text-sm text-slate-400">Loading clinical insights…</p>
    }
    if (clinicalQuery.isError) {
      return <p className="text-sm text-rose-400">Failed to load clinical report.</p>
    }
    if (!report) {
      return <p className="text-sm text-slate-400">No predictions available for this patient in the selected range.</p>
    }

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Patient</div>
            <div className="mt-2 text-lg font-semibold text-white">{report.patient.full_name}</div>
            <div className="text-xs text-slate-500">ID: {report.patient.patient_identifier}</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Age</div>
            <div className="mt-2 text-2xl font-semibold text-white">{Math.round(report.patient.age)}</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Last medical record</div>
            <div className="mt-2 text-sm text-white">
              {report.last_medical_record_at ? format(new Date(report.last_medical_record_at), 'PPpp') : 'N/A'}
            </div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Follow-up</div>
            <div className={clsx('mt-2 text-sm font-semibold', report.pending_follow_up ? 'text-amber-400' : 'text-slate-300')}>
              {report.pending_follow_up ? 'Pending action' : 'Up to date'}
            </div>
          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/60">
          <table className="min-w-full divide-y divide-slate-800 text-sm text-slate-200">
            <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
              <tr>
                <th className="px-4 py-3 text-left">Date</th>
                <th className="px-4 py-3 text-left">Disease</th>
                <th className="px-4 py-3 text-left">Alzheimer Risk</th>
                <th className="px-4 py-3 text-left">Parkinson Risk</th>
                <th className="px-4 py-3 text-left">Recommendation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/70">
              {report.predictions.map((entry) => (
                <tr key={entry.id} className="hover:bg-slate-900/50">
                  <td className="px-4 py-3 text-slate-300">{format(new Date(entry.created_at), 'PPpp')}</td>
                  <td className="px-4 py-3 capitalize">{entry.disease_type}</td>
                  <td className="px-4 py-3">
                    {entry.alzheimer_risk_level ? (
                      <span className="rounded-full bg-slate-800/60 px-2 py-1 text-xs uppercase tracking-wide text-sky-300">
                        {entry.alzheimer_risk_level} ({Math.round((entry.alzheimer_risk_score ?? 0) * 100)}%)
                      </span>
                    ) : (
                      <span className="text-slate-500">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    {entry.parkinson_risk_level ? (
                      <span className="rounded-full bg-slate-800/60 px-2 py-1 text-xs uppercase tracking-wide text-emerald-300">
                        {entry.parkinson_risk_level} ({Math.round((entry.parkinson_risk_score ?? 0) * 100)}%)
                      </span>
                    ) : (
                      <span className="text-slate-500">—</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-slate-300">{entry.recommendations || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }

  const renderResearchReport = (report: ResearchReport | undefined) => {
    if (!appliedResearchFilters) {
      return <p className="text-sm text-slate-400">Set date range or filters to generate aggregate insights.</p>
    }
    if (researchQuery.isLoading) {
      return <p className="text-sm text-slate-400">Crunching population statistics…</p>
    }
    if (researchQuery.isError) {
      return <p className="text-sm text-rose-400">Failed to load research report.</p>
    }
    if (!report) {
      return <p className="text-sm text-slate-400">No data for selected filters.</p>
    }

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Total predictions</div>
            <div className="mt-2 text-3xl font-semibold text-white">{report.total_predictions}</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Unique patients</div>
            <div className="mt-2 text-3xl font-semibold text-white">{report.unique_patients}</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Timeframe</div>
            <div className="mt-2 text-sm text-white">
              {report.timeframe_start ? format(new Date(report.timeframe_start), 'PP') : '—'} →{' '}
              {report.timeframe_end ? format(new Date(report.timeframe_end), 'PP') : '—'}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white">Risk distribution</h3>
          <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
            {report.aggregation.map((row) => (
              <div key={`${row.disease_type}-${row.risk_level ?? 'all'}`} className="rounded-xl border border-slate-800/70 bg-slate-900/80 p-4">
                <div className="text-xs uppercase text-slate-400">
                  {row.disease_type} • {row.risk_level ?? 'all'}
                </div>
                <div className="mt-2 text-2xl font-semibold text-white">{row.count}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const renderManagementReport = (report: ManagementReport | undefined) => {
    if (!appliedManagementFilters) {
      return <p className="text-sm text-slate-400">Select timeframe or model version to view KPIs.</p>
    }
    if (managementQuery.isLoading) {
      return <p className="text-sm text-slate-400">Loading operational KPIs…</p>
    }
    if (managementQuery.isError) {
      return <p className="text-sm text-rose-400">Failed to load management report.</p>
    }
    if (!report) {
      return <p className="text-sm text-slate-400">No operational data for selected filters.</p>
    }

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Total predictions</div>
            <div className="mt-2 text-3xl font-semibold text-white">{report.kpi.total_predictions}</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Reviewed</div>
            <div className="mt-2 text-3xl font-semibold text-white">{report.kpi.reviewed_predictions}</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Active patients</div>
            <div className="mt-2 text-3xl font-semibold text-white">{report.kpi.active_patients}</div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Avg inference latency</div>
            <div className="mt-2 text-xl font-semibold text-white">
              {report.kpi.avg_response_time_ms ? `${Math.round(report.kpi.avg_response_time_ms)} ms` : '—'}
            </div>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white">Model version distribution</h3>
          <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
            {Object.entries(report.model_version_distribution).map(([version, count]) => (
              <div key={version} className="rounded-xl border border-slate-800/70 bg-slate-900/80 p-4">
                <div className="text-xs uppercase text-slate-400">{version}</div>
                <div className="mt-2 text-2xl font-semibold text-white">{count}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h3 className="text-lg font-semibold text-white">Active alerts</h3>
          <div className="mt-4 space-y-3">
            {report.alerts.length === 0 && <p className="text-sm text-slate-500">No active alerts.</p>}
            {report.alerts.map((alert) => (
              <div key={`${alert.title}-${alert.created_at}`} className="rounded-xl border border-slate-800/70 bg-slate-900/80 p-4">
                <div className="flex items-center justify-between text-xs uppercase text-slate-400">
                  <span className={clsx(alert.severity === 'critical' ? 'text-rose-400' : 'text-amber-400')}>{alert.severity}</span>
                  <span className="text-slate-500">{format(new Date(alert.created_at), 'PPpp')}</span>
                </div>
                <div className="mt-2 text-sm font-semibold text-white">{alert.title}</div>
                <p className="mt-1 text-xs text-slate-400">{alert.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  const renderReportContent = () => {
    if (activeTab === 'clinical') {
      return renderClinicalReport(clinicalQuery.data)
    }
    if (activeTab === 'research') {
      return renderResearchReport(researchQuery.data)
    }
    return renderManagementReport(managementQuery.data)
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-white">Reports Center</h1>
            <p className="text-sm text-slate-400">
              Generate clinical, research, and operational reports powered by live NeuroPredict data.
            </p>
          </div>
          <button
            onClick={() => setShowLoadDataModal(true)}
            className="flex items-center gap-2 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500"
          >
            <PlusCircleIcon className="h-5 w-5" />
            Load Sample Data
          </button>
        </div>

        {statsQuery.data && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="text-xs uppercase text-slate-400">Total Patients</div>
              <div className="mt-2 text-3xl font-semibold text-white">{statsQuery.data.total_patients}</div>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="text-xs uppercase text-slate-400">Total Predictions</div>
              <div className="mt-2 text-3xl font-semibold text-white">{statsQuery.data.total_predictions}</div>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="text-xs uppercase text-slate-400">Medical Records</div>
              <div className="mt-2 text-3xl font-semibold text-white">{statsQuery.data.total_medical_records}</div>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="text-xs uppercase text-slate-400">Status</div>
              <div className={clsx(
                "mt-2 text-sm font-semibold uppercase",
                statsQuery.data.status === 'ready' ? 'text-emerald-400' : 'text-amber-400'
              )}>
                {statsQuery.data.status === 'ready' ? 'Ready' : 'No Data'}
              </div>
            </div>
          </div>
        )}
      </header>

      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap items-center gap-2">
            {(['clinical', 'research', 'management'] as ActiveTab[]).map((tab) => (
              <button
                key={tab}
                className={clsx(
                  'rounded-full px-4 py-2 text-sm font-medium transition',
                  activeTab === tab ? 'bg-sky-500 text-slate-950' : 'bg-slate-800 text-slate-200 hover:bg-slate-700'
                )}
                onClick={() => setActiveTab(tab)}
              >
                {tab === 'clinical' ? 'Clinical' : tab === 'research' ? 'Research' : 'Management'}
              </button>
            ))}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {exportFormats.map((item) => (
              <button
                key={item.value}
                className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 transition hover:border-sky-400 hover:text-sky-300"
                onClick={() => handleExport(item.value)}
                disabled={activeQuery.status === 'loading'}
              >
                <ArrowDownTrayIcon className="h-4 w-4" />
                {item.label}
              </button>
            ))}
            <button
              className="flex items-center gap-2 rounded-full bg-sky-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-sky-400"
              onClick={handleGenerate}
            >
              <FunnelIcon className="h-4 w-4" />
              Generate report
            </button>
          </div>
        </div>

        <div className="mt-6 space-y-6">
          <div className="rounded-2xl border border-slate-800 bg-slate-950/60 p-4">{renderFilters()}</div>
          <div className="rounded-2xl border border-slate-800 bg-slate-950/50 p-6">{renderReportContent()}</div>
        </div>
      </div>

      {/* Load Sample Data Modal */}
      {showLoadDataModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
            <h3 className="text-xl font-semibold text-white">Load Sample Data</h3>
            <p className="mt-2 text-sm text-slate-400">
              This will create 10 sample patients with medical records and predictions for testing the Reports feature.
              Existing data will not be affected.
            </p>

            {statsQuery.data && (
              <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950/60 p-3">
                <p className="text-xs text-slate-400">Current database status:</p>
                <ul className="mt-2 space-y-1 text-sm text-slate-300">
                  <li>• {statsQuery.data.total_patients} patients</li>
                  <li>• {statsQuery.data.total_predictions} predictions</li>
                  <li>• {statsQuery.data.total_medical_records} medical records</li>
                </ul>
              </div>
            )}

            <div className="mt-6 flex gap-3">
              <button
                onClick={() => setShowLoadDataModal(false)}
                className="flex-1 rounded-full border border-slate-700 bg-slate-800 px-4 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-700"
                disabled={loadSampleDataMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={() => loadSampleDataMutation.mutate()}
                className="flex-1 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500 disabled:bg-slate-700 disabled:text-slate-400"
                disabled={loadSampleDataMutation.isPending}
              >
                {loadSampleDataMutation.isPending ? 'Loading...' : 'Load Data'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


