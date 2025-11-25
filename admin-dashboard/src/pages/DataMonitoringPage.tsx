import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { format } from 'date-fns'
import { toast } from 'react-hot-toast'
import {
  BeakerIcon,
  BoltIcon,
  CpuChipIcon,
  HeartIcon,
  ClockIcon,
  ChartBarIcon,
  FunnelIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts'

import { dataMonitoringService } from '../services/dataMonitoring'

type DataCategory = 'cognitive' | 'biomarker' | 'imaging' | 'motor' | 'genetic' | 'all'
type DiseaseFilter = 'all' | 'alzheimer' | 'parkinson'

export default function DataMonitoringPage() {
  const queryClient = useQueryClient()
  const [selectedCategory, setSelectedCategory] = useState<DataCategory>('all')
  const [diseaseFilter, setDiseaseFilter] = useState<DiseaseFilter>('all')
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | '90d'>('7d')
  const [showLoadDataModal, setShowLoadDataModal] = useState(false)

  const overviewQuery = useQuery({
    queryKey: ['data-monitoring', 'overview', diseaseFilter],
    queryFn: () => dataMonitoringService.getOverview(diseaseFilter),
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  const categoryDataQuery = useQuery({
    queryKey: ['data-monitoring', 'category', selectedCategory, timeRange, diseaseFilter],
    queryFn: () => dataMonitoringService.getCategoryData(selectedCategory, timeRange, diseaseFilter),
    enabled: selectedCategory !== 'all',
    refetchInterval: 30000,
  })

  const recentDataQuery = useQuery({
    queryKey: ['data-monitoring', 'recent', diseaseFilter],
    queryFn: () => dataMonitoringService.getRecentData(diseaseFilter),
    refetchInterval: 10000, // Refresh every 10 seconds for real-time feel
  })

  const trendsQuery = useQuery({
    queryKey: ['data-monitoring', 'trends', timeRange, diseaseFilter],
    queryFn: () => dataMonitoringService.getTrends(timeRange, diseaseFilter),
    refetchInterval: 30000,
  })

  const loadSampleDataMutation = useMutation({
    mutationFn: () => dataMonitoringService.loadSampleData(),
    onSuccess: (data) => {
      toast.success(
        `Sample data loaded! ${data.records_created} records created for ${data.patients_processed} patients.`
      )
      queryClient.invalidateQueries({ queryKey: ['data-monitoring'] })
      setShowLoadDataModal(false)
    },
    onError: (error: any) => {
      toast.error(`Failed to load data: ${error.response?.data?.detail || error.message}`)
    },
  })

  const categories = [
    {
      id: 'cognitive' as DataCategory,
      name: 'Cognitive',
      nameEn: 'Cognitive',
      icon: CpuChipIcon,
      color: 'sky',
      description: 'MMSE, MoCA, Memory, Attention',
      items: ['MMSE Score', 'MoCA Score', 'Memory Score', 'Attention Score', 'Executive Function'],
    },
    {
      id: 'biomarker' as DataCategory,
      name: 'Biomarker',
      nameEn: 'Biomarker',
      icon: BeakerIcon,
      color: 'emerald',
      description: 'Amyloid, Tau, Dopamine',
      items: ['Amyloid Beta', 'Tau Protein', 'P-Tau', 'Dopamine Level', 'Alpha-Synuclein'],
    },
    {
      id: 'imaging' as DataCategory,
      name: 'Imaging',
      nameEn: 'Imaging',
      icon: HeartIcon,
      color: 'purple',
      description: 'MRI, Hippocampal Volume, Cortical Thickness',
      items: ['Hippocampal Volume', 'Cortical Thickness', 'Ventricular Volume', 'White Matter', 'Brain Volume'],
    },
    {
      id: 'motor' as DataCategory,
      name: 'Motor',
      nameEn: 'Motor',
      icon: BoltIcon,
      color: 'amber',
      description: 'Tremor, Rigidity, Movement',
      items: ['Tremor Severity', 'Rigidity', 'Bradykinesia', 'Postural Stability', 'Gait'],
    },
    {
      id: 'genetic' as DataCategory,
      name: 'Genetic',
      nameEn: 'Genetic',
      icon: ChartBarIcon,
      color: 'rose',
      description: 'APOE-e4, Family History',
      items: ['APOE-e4 Status', 'Family History', 'Genetic Risk Score', 'Mutation Analysis'],
    },
  ]

  const overview = overviewQuery.data || {
    total_records: 0,
    total_patients: 0,
    categories: {},
    recent_activity: [],
    data_quality_score: 0,
  }

  const categoryColors: Record<string, string> = {
    sky: 'bg-sky-500',
    emerald: 'bg-emerald-500',
    purple: 'bg-purple-500',
    amber: 'bg-amber-500',
    rose: 'bg-rose-500',
  }

  const categoryBorderColors: Record<string, string> = {
    sky: 'border-sky-500',
    emerald: 'border-emerald-500',
    purple: 'border-purple-500',
    amber: 'border-amber-500',
    rose: 'border-rose-500',
  }

  const categoryTextColors: Record<string, string> = {
    sky: 'text-sky-400',
    emerald: 'text-emerald-400',
    purple: 'text-purple-400',
    amber: 'text-amber-400',
    rose: 'text-rose-400',
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-semibold text-white">Clinical Data Monitoring</h1>
            <p className="text-sm text-slate-400">
              Real-time monitoring of diagnostic data types for Alzheimer's and Parkinson's disease
            </p>
          </div>
          <button
            onClick={() => setShowLoadDataModal(true)}
            className="flex items-center gap-2 rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500"
          >
            <ChartBarIcon className="h-5 w-5" />
            Load Sample Data
          </button>
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2">
            <FunnelIcon className="h-5 w-5 text-slate-400" />
            <span className="text-sm text-slate-400">Filters:</span>
          </div>

          {/* Disease Filter */}
          <select
            value={diseaseFilter}
            onChange={(e) => setDiseaseFilter(e.target.value as DiseaseFilter)}
            className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-1.5 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
          >
            <option value="all">All Diseases</option>
            <option value="alzheimer">Alzheimer's</option>
            <option value="parkinson">Parkinson's</option>
          </select>

          {/* Time Range */}
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-1.5 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
          >
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>

          <div className="ml-auto flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/60 px-3 py-1.5">
            <ClockIcon className="h-4 w-4 text-emerald-400" />
            <span className="text-xs text-slate-300">Auto-refresh: 30s</span>
          </div>
        </div>
      </header>

      {/* Overview Stats */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-xs uppercase text-slate-400">Total Records</div>
          <div className="mt-2 text-3xl font-semibold text-white">
            {overviewQuery.isLoading ? '...' : overview.total_records.toLocaleString()}
          </div>
          <div className="mt-1 text-xs text-slate-500">
            in {timeRange === '24h' ? '24 hours' : timeRange === '7d' ? '7 days' : timeRange === '30d' ? '30 days' : '90 days'}
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-xs uppercase text-slate-400">Active Patients</div>
          <div className="mt-2 text-3xl font-semibold text-white">
            {overviewQuery.isLoading ? '...' : overview.total_patients.toLocaleString()}
          </div>
          <div className="mt-1 text-xs text-emerald-400">● Online</div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-xs uppercase text-slate-400">Data Categories</div>
          <div className="mt-2 text-3xl font-semibold text-white">{categories.length}</div>
          <div className="mt-1 text-xs text-slate-500">Cognitive, Biomarker, Imaging...</div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-xs uppercase text-slate-400">Data Quality</div>
          <div className="mt-2 text-3xl font-semibold text-white">
            {overviewQuery.isLoading ? '...' : Math.round(overview.data_quality_score || 0)}%
          </div>
          <div className={clsx(
            'mt-1 text-xs',
            (overview.data_quality_score || 0) >= 80 ? 'text-emerald-400' : 'text-amber-400'
          )}>
            {(overview.data_quality_score || 0) >= 80 ? 'Excellent' : 'Acceptable'}
          </div>
        </div>
      </div>

      {/* Category Cards */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
        {categories.map((category) => {
          const categoryStats = overview.categories?.[category.id] || { count: 0, avg_value: 0, trend: 0 }
          const Icon = category.icon

          return (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={clsx(
                'rounded-2xl border p-6 text-right transition',
                selectedCategory === category.id
                  ? `${categoryBorderColors[category.color]} bg-slate-900/80`
                  : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
              )}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-semibold text-white">{category.name}</h3>
                    {categoryStats.trend !== 0 && (
                      categoryStats.trend > 0 ? (
                        <ArrowTrendingUpIcon className="h-4 w-4 text-emerald-400" />
                      ) : (
                        <ArrowTrendingDownIcon className="h-4 w-4 text-rose-400" />
                      )
                    )}
                  </div>
                  <p className="mt-1 text-xs text-slate-400">{category.description}</p>
                  
                  <div className="mt-4 space-y-1">
                    <div className="text-2xl font-semibold text-white">
                      {overviewQuery.isLoading ? '...' : categoryStats.count.toLocaleString()}
                    </div>
                    <div className="text-xs text-slate-500">Records</div>
                  </div>

                  <div className="mt-4 flex flex-wrap gap-1">
                    {category.items.slice(0, 3).map((item, idx) => (
                      <span
                        key={idx}
                        className="rounded-full bg-slate-800/60 px-2 py-0.5 text-xs text-slate-300"
                      >
                        {item}
                      </span>
                    ))}
                    {category.items.length > 3 && (
                      <span className="rounded-full bg-slate-800/60 px-2 py-0.5 text-xs text-slate-400">
                        +{category.items.length - 3}
                      </span>
                    )}
                  </div>
                </div>

                <div className={clsx(
                  'rounded-xl p-3',
                  `${categoryColors[category.color]}/10`
                )}>
                  <Icon className={clsx('h-8 w-8', categoryTextColors[category.color])} />
                </div>
              </div>
            </button>
          )
        })}
      </div>

      {/* Category Detail View */}
      {selectedCategory !== 'all' && categoryDataQuery.data && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">
              {categories.find((c) => c.id === selectedCategory)?.name} Data Details
            </h2>
            <button
              onClick={() => setSelectedCategory('all')}
              className="rounded-full border border-slate-700 px-4 py-2 text-sm text-slate-300 transition hover:border-slate-600 hover:text-white"
            >
              Back
            </button>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            {/* Time Series Chart */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h3 className="text-sm font-semibold text-white">Time Series</h3>
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={categoryDataQuery.data.time_series || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis
                      dataKey="date"
                      stroke="#94a3b8"
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        background: '#0f172a',
                        border: '1px solid #1e293b',
                        borderRadius: '8px',
                      }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="avg_value"
                      stroke="#38bdf8"
                      strokeWidth={2}
                      name="Average"
                    />
                    <Line
                      type="monotone"
                      dataKey="count"
                      stroke="#10b981"
                      strokeWidth={2}
                      name="Count"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Distribution Chart */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h3 className="text-sm font-semibold text-white">Value Distribution</h3>
              <div className="mt-4 h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categoryDataQuery.data.distribution || []}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                    <XAxis
                      dataKey="range"
                      stroke="#94a3b8"
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{
                        background: '#0f172a',
                        border: '1px solid #1e293b',
                        borderRadius: '8px',
                      }}
                    />
                    <Bar dataKey="count" fill="#a78bfa" name="Count" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Metrics Table */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-800">
                <thead className="bg-slate-900/80">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-400">
                      Data Type
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-400">
                      Average
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-400">
                      Minimum
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-400">
                      Maximum
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-400">
                      Count
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-slate-400">
                      Last Updated
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/70">
                  {(categoryDataQuery.data.metrics || []).map((metric: any, idx: number) => (
                    <tr key={idx} className="hover:bg-slate-900/50">
                      <td className="px-4 py-3 text-sm font-medium text-white">
                        {metric.metric_name}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-300">
                        {metric.avg_value?.toFixed(2) || '—'}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-300">
                        {metric.min_value?.toFixed(2) || '—'}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-300">
                        {metric.max_value?.toFixed(2) || '—'}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-300">
                        {metric.count || 0}
                      </td>
                      <td className="px-4 py-3 text-sm text-slate-400">
                        {metric.last_updated ? format(new Date(metric.last_updated), 'PPp') : '—'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Recent Activity */}
      {selectedCategory === 'all' && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">Recent Activity</h2>
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 animate-pulse rounded-full bg-emerald-400"></div>
              <span className="text-xs text-slate-400">Live</span>
            </div>
          </div>

          <div className="mt-4 space-y-3">
            {recentDataQuery.isLoading && (
              <p className="text-sm text-slate-400">Loading...</p>
            )}

            {recentDataQuery.data && recentDataQuery.data.length === 0 && (
              <p className="text-sm text-slate-400">No recent activity</p>
            )}

            {recentDataQuery.data?.map((activity: any, idx: number) => {
              const category = categories.find((c) => c.id === activity.category)
              const Icon = category?.icon || ClockIcon

              return (
                <div
                  key={idx}
                  className="flex items-center gap-4 rounded-xl border border-slate-800/70 bg-slate-950/60 p-4"
                >
                  <div className={clsx(
                    'rounded-lg p-2',
                    category ? `${categoryColors[category.color]}/10` : 'bg-slate-800'
                  )}>
                    <Icon className={clsx(
                      'h-5 w-5',
                      category ? categoryTextColors[category.color] : 'text-slate-400'
                    )} />
                  </div>

                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{activity.description}</div>
                    <div className="mt-1 flex items-center gap-3 text-xs text-slate-400">
                      <span>Patient: {activity.patient_name || activity.patient_id}</span>
                      <span>•</span>
                      <span>{activity.metric_type}</span>
                      {activity.value && (
                        <>
                          <span>•</span>
                          <span>Value: {activity.value}</span>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="text-left text-xs text-slate-500">
                    {format(new Date(activity.timestamp), 'HH:mm:ss')}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Trends Summary */}
      {selectedCategory === 'all' && trendsQuery.data && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-xl font-semibold text-white">Overall Trends</h2>

          <div className="mt-6 h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={trendsQuery.data.radar_data || []}>
                <PolarGrid stroke="#1f2937" />
                <PolarAngleAxis dataKey="category" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                <PolarRadiusAxis stroke="#94a3b8" />
                <Radar
                  name="Alzheimer"
                  dataKey="alzheimer"
                  stroke="#f59e0b"
                  fill="#f59e0b"
                  fillOpacity={0.3}
                />
                <Radar
                  name="Parkinson"
                  dataKey="parkinson"
                  stroke="#8b5cf6"
                  fill="#8b5cf6"
                  fillOpacity={0.3}
                />
                <Legend />
                <Tooltip
                  contentStyle={{
                    background: '#0f172a',
                    border: '1px solid #1e293b',
                    borderRadius: '8px',
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Load Sample Data Modal */}
      {showLoadDataModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
          <div className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
            <h3 className="text-xl font-semibold text-white">Load Sample Data</h3>
            <p className="mt-2 text-sm text-slate-400">
              This will create comprehensive medical records with complete data for all categories (Cognitive, Biomarker, Imaging, Genetic).
            </p>

            <div className="mt-4 rounded-lg border border-slate-800 bg-slate-950/60 p-3">
              <p className="text-xs text-slate-400 mb-2">Data to be created:</p>
              <ul className="space-y-1 text-sm text-slate-300">
                <li>• 3-5 records per patient</li>
                <li>• Cognitive data: MMSE, MoCA, Memory, Attention</li>
                <li>• Biomarkers: Amyloid, Tau, Dopamine</li>
                <li>• Imaging data: MRI, Brain volume</li>
                <li>• Genetic info: APOE-e4</li>
              </ul>
            </div>

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

