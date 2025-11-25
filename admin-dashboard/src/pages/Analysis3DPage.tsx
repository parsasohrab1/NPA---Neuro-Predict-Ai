import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Plot from 'react-plotly.js'
import { 
  CubeIcon, 
  ChartBarIcon, 
  BeakerIcon,
  CpuChipIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'
import { analysis3DService } from '../services/analysis3D'

interface QualityControlData {
  pipelines: Array<{
    name: string
    description: string
    acceptable: {
      patient_id: string
      patient_name: string
      scan_date: string
      image_url: string
      metrics: Record<string, number>
      notes: string
    }
    discarded: {
      patient_id: string
      patient_name: string
      scan_date: string
      image_url: string
      metrics: Record<string, number>
      issues: string[]
      notes: string
    }
  }>
}

function QualityControlView({ data }: { data?: any }) {
  const [selectedPipeline, setSelectedPipeline] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'grid' | 'detail'>('grid')

  if (!data?.qc_data) {
    return (
      <div className="flex h-[600px] items-center justify-center">
        <p className="text-slate-400">No quality control data available</p>
      </div>
    )
  }

  const qcData: QualityControlData = data.qc_data

  return (
    <div className="space-y-6">
      {/* View Mode Toggle */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => setViewMode('grid')}
          className={clsx(
            'rounded-lg px-4 py-2 text-sm font-medium transition',
            viewMode === 'grid'
              ? 'bg-sky-500 text-white'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          )}
        >
          Grid View
        </button>
        <button
          onClick={() => setViewMode('detail')}
          className={clsx(
            'rounded-lg px-4 py-2 text-sm font-medium transition',
            viewMode === 'detail'
              ? 'bg-sky-500 text-white'
              : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          )}
        >
          Detailed View
        </button>
      </div>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <div className="space-y-4">
          {/* Header Row */}
          <div className="grid grid-cols-4 gap-4">
            <div className="rounded-lg border border-slate-700 bg-slate-800/50 p-3 text-center">
              <div className="text-sm font-semibold text-slate-300">Pipeline</div>
            </div>
            {qcData.pipelines.map((pipeline) => (
              <div
                key={pipeline.name}
                className="rounded-lg border border-slate-700 bg-slate-800/50 p-3 text-center"
              >
                <div className="text-sm font-semibold text-white">{pipeline.name}</div>
                <div className="mt-1 text-xs text-slate-400">{pipeline.description}</div>
              </div>
            ))}
          </div>

          {/* Acceptable Row */}
          <div className="grid grid-cols-4 gap-4">
            <div className="flex items-center justify-center rounded-lg border border-emerald-900/50 bg-emerald-950/30 p-3">
              <div className="flex items-center gap-2">
                <CheckCircleIcon className="h-5 w-5 text-emerald-400" />
                <span className="font-semibold text-emerald-400">Acceptable</span>
              </div>
            </div>
            {qcData.pipelines.map((pipeline) => (
              <div
                key={`acceptable-${pipeline.name}`}
                className="group cursor-pointer rounded-lg border border-slate-700 bg-slate-900/60 p-3 transition hover:border-emerald-500 hover:shadow-lg hover:shadow-emerald-500/20"
                onClick={() => {
                  setSelectedPipeline(pipeline.name)
                  setViewMode('detail')
                }}
              >
                <div className="relative aspect-[4/3] overflow-hidden rounded-lg bg-slate-800">
                  {pipeline.acceptable.image_url ? (
                    <img
                      src={pipeline.acceptable.image_url}
                      alt={`${pipeline.name} acceptable`}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center text-slate-600">
                      <BeakerIcon className="h-12 w-12" />
                    </div>
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-0 transition group-hover:opacity-100" />
                </div>
                <div className="mt-2 space-y-1">
                  <div className="text-xs text-slate-400">
                    Patient: {pipeline.acceptable.patient_name}
                  </div>
                  <div className="text-xs text-slate-500">
                    {pipeline.acceptable.scan_date}
                  </div>
                  {Object.entries(pipeline.acceptable.metrics).slice(0, 2).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-xs">
                      <span className="text-slate-500">{key}:</span>
                      <span className="font-mono text-emerald-400">{value.toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Discarded Row */}
          <div className="grid grid-cols-4 gap-4">
            <div className="flex items-center justify-center rounded-lg border border-rose-900/50 bg-rose-950/30 p-3">
              <div className="flex items-center gap-2">
                <XCircleIcon className="h-5 w-5 text-rose-400" />
                <span className="font-semibold text-rose-400">Discarded</span>
              </div>
            </div>
            {qcData.pipelines.map((pipeline) => (
              <div
                key={`discarded-${pipeline.name}`}
                className="group cursor-pointer rounded-lg border border-slate-700 bg-slate-900/60 p-3 transition hover:border-rose-500 hover:shadow-lg hover:shadow-rose-500/20"
                onClick={() => {
                  setSelectedPipeline(pipeline.name)
                  setViewMode('detail')
                }}
              >
                <div className="relative aspect-[4/3] overflow-hidden rounded-lg bg-slate-800">
                  {pipeline.discarded.image_url ? (
                    <img
                      src={pipeline.discarded.image_url}
                      alt={`${pipeline.name} discarded`}
                      className="h-full w-full object-cover"
                    />
                  ) : (
                    <div className="flex h-full items-center justify-center text-slate-600">
                      <BeakerIcon className="h-12 w-12" />
                    </div>
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-0 transition group-hover:opacity-100" />
                </div>
                <div className="mt-2 space-y-1">
                  <div className="text-xs text-slate-400">
                    Patient: {pipeline.discarded.patient_name}
                  </div>
                  <div className="text-xs text-slate-500">
                    {pipeline.discarded.scan_date}
                  </div>
                  {pipeline.discarded.issues.slice(0, 2).map((issue, idx) => (
                    <div key={idx} className="flex items-start gap-1 text-xs text-rose-400">
                      <ExclamationTriangleIcon className="mt-0.5 h-3 w-3 flex-shrink-0" />
                      <span className="line-clamp-1">{issue}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed View */}
      {viewMode === 'detail' && (
        <div className="space-y-6">
          {qcData.pipelines.map((pipeline) => (
            <div
              key={pipeline.name}
              className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6"
            >
              <h3 className="mb-4 text-xl font-semibold text-white">
                {pipeline.name} - {pipeline.description}
              </h3>
              
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                {/* Acceptable */}
                <div className="space-y-4 rounded-lg border border-emerald-900/50 bg-emerald-950/20 p-4">
                  <div className="flex items-center gap-2">
                    <CheckCircleIcon className="h-6 w-6 text-emerald-400" />
                    <h4 className="text-lg font-semibold text-emerald-400">Acceptable Result</h4>
                  </div>
                  
                  <div className="aspect-video overflow-hidden rounded-lg bg-slate-800">
                    {pipeline.acceptable.image_url ? (
                      <img
                        src={pipeline.acceptable.image_url}
                        alt={`${pipeline.name} acceptable`}
                        className="h-full w-full object-contain"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center text-slate-600">
                        <BeakerIcon className="h-16 w-16" />
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="text-slate-400">Patient:</span>
                      <span className="ml-2 font-medium text-white">
                        {pipeline.acceptable.patient_name}
                      </span>
                    </div>
                    <div className="text-sm">
                      <span className="text-slate-400">ID:</span>
                      <span className="ml-2 font-mono text-white">
                        {pipeline.acceptable.patient_id}
                      </span>
                    </div>
                    <div className="text-sm">
                      <span className="text-slate-400">Scan Date:</span>
                      <span className="ml-2 text-white">{pipeline.acceptable.scan_date}</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm font-semibold text-slate-300">Quality Metrics:</div>
                    <div className="space-y-1">
                      {Object.entries(pipeline.acceptable.metrics).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                          <span className="text-slate-400">{key}:</span>
                          <span className="font-mono text-emerald-400">{value.toFixed(3)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {pipeline.acceptable.notes && (
                    <div className="rounded-lg bg-slate-800/50 p-3 text-sm text-slate-300">
                      <div className="mb-1 font-semibold text-slate-200">Notes:</div>
                      {pipeline.acceptable.notes}
                    </div>
                  )}
                </div>

                {/* Discarded */}
                <div className="space-y-4 rounded-lg border border-rose-900/50 bg-rose-950/20 p-4">
                  <div className="flex items-center gap-2">
                    <XCircleIcon className="h-6 w-6 text-rose-400" />
                    <h4 className="text-lg font-semibold text-rose-400">Discarded Result</h4>
                  </div>
                  
                  <div className="aspect-video overflow-hidden rounded-lg bg-slate-800">
                    {pipeline.discarded.image_url ? (
                      <img
                        src={pipeline.discarded.image_url}
                        alt={`${pipeline.name} discarded`}
                        className="h-full w-full object-contain"
                      />
                    ) : (
                      <div className="flex h-full items-center justify-center text-slate-600">
                        <BeakerIcon className="h-16 w-16" />
                      </div>
                    )}
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="text-slate-400">Patient:</span>
                      <span className="ml-2 font-medium text-white">
                        {pipeline.discarded.patient_name}
                      </span>
                    </div>
                    <div className="text-sm">
                      <span className="text-slate-400">ID:</span>
                      <span className="ml-2 font-mono text-white">
                        {pipeline.discarded.patient_id}
                      </span>
                    </div>
                    <div className="text-sm">
                      <span className="text-slate-400">Scan Date:</span>
                      <span className="ml-2 text-white">{pipeline.discarded.scan_date}</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm font-semibold text-slate-300">Quality Metrics:</div>
                    <div className="space-y-1">
                      {Object.entries(pipeline.discarded.metrics).map(([key, value]) => (
                        <div key={key} className="flex justify-between text-sm">
                          <span className="text-slate-400">{key}:</span>
                          <span className="font-mono text-rose-400">{value.toFixed(3)}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="text-sm font-semibold text-rose-300">Issues Detected:</div>
                    <ul className="space-y-1">
                      {pipeline.discarded.issues.map((issue, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-rose-300">
                          <ExclamationTriangleIcon className="mt-0.5 h-4 w-4 flex-shrink-0" />
                          {issue}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {pipeline.discarded.notes && (
                    <div className="rounded-lg bg-slate-800/50 p-3 text-sm text-slate-300">
                      <div className="mb-1 font-semibold text-slate-200">Notes:</div>
                      {pipeline.discarded.notes}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

type AnalysisType = 'scatter' | 'surface' | 'correlation' | 'feature-space' | 'quality-control'
type DiseaseFilter = 'all' | 'alzheimer' | 'parkinson' | 'normal'

export default function Analysis3DPage() {
  const [analysisType, setAnalysisType] = useState<AnalysisType>('scatter')
  const [diseaseFilter, setDiseaseFilter] = useState<DiseaseFilter>('all')
  const [selectedFeatures, setSelectedFeatures] = useState({
    x: 'mmse_score',
    y: 'amyloid_beta',
    z: 'hippocampal_volume',
  })

  const analysis3DQuery = useQuery({
    queryKey: ['analysis-3d', analysisType, diseaseFilter, selectedFeatures],
    queryFn: () => analysis3DService.getAnalysisData(analysisType, diseaseFilter, selectedFeatures),
    refetchInterval: 60000, // Refresh every minute
  })

  const availableFeatures = [
    { value: 'mmse_score', label: 'MMSE Score', category: 'cognitive' },
    { value: 'moca_score', label: 'MoCA Score', category: 'cognitive' },
    { value: 'memory_score', label: 'Memory Score', category: 'cognitive' },
    { value: 'attention_score', label: 'Attention Score', category: 'cognitive' },
    { value: 'amyloid_beta', label: 'Amyloid Beta', category: 'biomarker' },
    { value: 'tau_protein', label: 'Tau Protein', category: 'biomarker' },
    { value: 'dopamine_level', label: 'Dopamine Level', category: 'biomarker' },
    { value: 'hippocampal_volume', label: 'Hippocampal Volume', category: 'imaging' },
    { value: 'cortical_thickness', label: 'Cortical Thickness', category: 'imaging' },
    { value: 'brain_volume_total', label: 'Brain Volume', category: 'imaging' },
    { value: 'age', label: 'Age', category: 'demographic' },
  ]

  const renderPlot = () => {
    if (analysis3DQuery.isLoading) {
      return (
        <div className="flex h-[600px] items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <ArrowPathIcon className="h-12 w-12 animate-spin text-sky-500" />
            <p className="text-slate-400">Loading 3D visualization...</p>
          </div>
        </div>
      )
    }

    if (analysis3DQuery.isError) {
      const queryError = analysis3DQuery.error as any
      return (
        <div className="flex h-[600px] items-center justify-center">
          <div className="text-center max-w-2xl mx-auto px-8">
            <ExclamationTriangleIcon className="mx-auto h-16 w-16 text-amber-400 mb-4" />
            <p className="text-rose-400 text-xl font-semibold mb-3">No Patient Data Available</p>
            <p className="text-slate-300 text-sm mb-6">
              The 3D visualization requires patient data with medical records. Import patient data with biomarker measurements to use this feature.
            </p>
            {queryError?.response?.status === 401 && (
              <button
                onClick={() => window.location.href = '/login'}
                className="mt-4 px-4 py-2 bg-sky-600 hover:bg-sky-700 text-white rounded-lg transition-colors"
              >
                Go to Login
              </button>
            )}
          </div>
        </div>
      )
    }

    const data = analysis3DQuery.data

    if (analysisType === 'scatter') {
      return (
        <Plot
          data={data?.traces || []}
          layout={{
            title: '3D Scatter Plot - Patient Feature Space',
            scene: {
              xaxis: { title: selectedFeatures.x.replace('_', ' ').toUpperCase() },
              yaxis: { title: selectedFeatures.y.replace('_', ' ').toUpperCase() },
              zaxis: { title: selectedFeatures.z.replace('_', ' ').toUpperCase() },
              camera: {
                eye: { x: 1.5, y: 1.5, z: 1.3 }
              },
            },
            paper_bgcolor: '#0f172a',
            plot_bgcolor: '#0f172a',
            font: { color: '#e2e8f0' },
            height: 600,
            margin: { l: 0, r: 0, t: 40, b: 0 },
            showlegend: true,
            legend: {
              bgcolor: '#1e293b',
              bordercolor: '#334155',
              borderwidth: 1,
            },
          }}
          config={{
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['sendDataToCloud'],
          }}
          style={{ width: '100%', height: '600px' }}
        />
      )
    }

    if (analysisType === 'surface') {
      return (
        <Plot
          data={data?.traces || []}
          layout={{
            title: '3D Surface Plot - Brain Region Analysis',
            scene: {
              xaxis: { title: 'Region X' },
              yaxis: { title: 'Region Y' },
              zaxis: { title: 'Volume/Thickness' },
              camera: {
                eye: { x: 1.87, y: 0.88, z: -0.64 }
              },
            },
            paper_bgcolor: '#0f172a',
            plot_bgcolor: '#0f172a',
            font: { color: '#e2e8f0' },
            height: 600,
            margin: { l: 0, r: 0, t: 40, b: 0 },
          }}
          config={{
            displayModeBar: true,
            displaylogo: false,
          }}
          style={{ width: '100%', height: '600px' }}
        />
      )
    }

    if (analysisType === 'correlation') {
      return (
        <Plot
          data={data?.traces || []}
          layout={{
            title: '3D Correlation Matrix',
            scene: {
              xaxis: { title: 'Feature 1' },
              yaxis: { title: 'Feature 2' },
              zaxis: { title: 'Correlation' },
            },
            paper_bgcolor: '#0f172a',
            plot_bgcolor: '#0f172a',
            font: { color: '#e2e8f0' },
            height: 600,
            margin: { l: 0, r: 0, t: 40, b: 0 },
          }}
          config={{
            displayModeBar: true,
            displaylogo: false,
          }}
          style={{ width: '100%', height: '600px' }}
        />
      )
    }

    if (analysisType === 'feature-space') {
      return (
        <Plot
          data={data?.traces || []}
          layout={{
            title: '3D Feature Space - Disease Clustering',
            scene: {
              xaxis: { title: 'PC1' },
              yaxis: { title: 'PC2' },
              zaxis: { title: 'PC3' },
              camera: {
                eye: { x: 2, y: 2, z: 1.5 }
              },
            },
            paper_bgcolor: '#0f172a',
            plot_bgcolor: '#0f172a',
            font: { color: '#e2e8f0' },
            height: 600,
            margin: { l: 0, r: 0, t: 40, b: 0 },
            showlegend: true,
            legend: {
              bgcolor: '#1e293b',
              bordercolor: '#334155',
              borderwidth: 1,
            },
          }}
          config={{
            displayModeBar: true,
            displaylogo: false,
          }}
          style={{ width: '100%', height: '600px' }}
        />
      )
    }

    if (analysisType === 'quality-control') {
      return <QualityControlView data={data} />
    }

    return null
  }

  const analysisTypes = [
    {
      id: 'scatter' as AnalysisType,
      name: '3D Scatter',
      icon: CubeIcon,
      description: 'Explore patient data in 3D space',
    },
    {
      id: 'surface' as AnalysisType,
      name: 'Brain Surface',
      icon: BeakerIcon,
      description: 'Visualize brain regions',
    },
    {
      id: 'correlation' as AnalysisType,
      name: 'Correlation',
      icon: ChartBarIcon,
      description: 'Feature correlations in 3D',
    },
    {
      id: 'feature-space' as AnalysisType,
      name: 'Feature Space',
      icon: CpuChipIcon,
      description: 'PCA-based clustering',
    },
    {
      id: 'quality-control' as AnalysisType,
      name: 'Quality Control',
      icon: ChartBarIcon,
      description: 'Imaging pipeline QC comparison',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <header className="flex flex-col gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">3D Analysis</h1>
          <p className="text-sm text-slate-400">
            Interactive 3D visualization and analysis of patient data
          </p>
        </div>

        {/* Analysis Type Selector */}
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {analysisTypes.map((type) => {
            const Icon = type.icon
            return (
              <button
                key={type.id}
                onClick={() => setAnalysisType(type.id)}
                className={clsx(
                  'flex items-start gap-3 rounded-2xl border p-4 text-left transition',
                  analysisType === type.id
                    ? 'border-sky-500 bg-sky-500/10'
                    : 'border-slate-800 bg-slate-900/60 hover:border-slate-700'
                )}
              >
                <div className={clsx(
                  'rounded-xl p-2',
                  analysisType === type.id ? 'bg-sky-500/20' : 'bg-slate-800'
                )}>
                  <Icon className={clsx(
                    'h-6 w-6',
                    analysisType === type.id ? 'text-sky-400' : 'text-slate-400'
                  )} />
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-white">{type.name}</div>
                  <div className="text-xs text-slate-400">{type.description}</div>
                </div>
              </button>
            )
          })}
        </div>
      </header>

      {/* Controls */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-4">
          {/* Disease Filter */}
          <div>
            <label className="mb-2 block text-xs font-semibold uppercase text-slate-400">
              Disease Filter
            </label>
            <select
              value={diseaseFilter}
              onChange={(e) => setDiseaseFilter(e.target.value as DiseaseFilter)}
              className="w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
            >
              <option value="all">All Patients</option>
              <option value="alzheimer">Alzheimer's Only</option>
              <option value="parkinson">Parkinson's Only</option>
              <option value="normal">Normal Only</option>
            </select>
          </div>

          {/* X Axis Feature */}
          {analysisType === 'scatter' && (
            <>
              <div>
                <label className="mb-2 block text-xs font-semibold uppercase text-slate-400">
                  X-Axis Feature
                </label>
                <select
                  value={selectedFeatures.x}
                  onChange={(e) => setSelectedFeatures({ ...selectedFeatures, x: e.target.value })}
                  className="w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                >
                  {availableFeatures.map((feature) => (
                    <option key={feature.value} value={feature.value}>
                      {feature.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Y Axis Feature */}
              <div>
                <label className="mb-2 block text-xs font-semibold uppercase text-slate-400">
                  Y-Axis Feature
                </label>
                <select
                  value={selectedFeatures.y}
                  onChange={(e) => setSelectedFeatures({ ...selectedFeatures, y: e.target.value })}
                  className="w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                >
                  {availableFeatures.map((feature) => (
                    <option key={feature.value} value={feature.value}>
                      {feature.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Z Axis Feature */}
              <div>
                <label className="mb-2 block text-xs font-semibold uppercase text-slate-400">
                  Z-Axis Feature
                </label>
                <select
                  value={selectedFeatures.z}
                  onChange={(e) => setSelectedFeatures({ ...selectedFeatures, z: e.target.value })}
                  className="w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                >
                  {availableFeatures.map((feature) => (
                    <option key={feature.value} value={feature.value}>
                      {feature.label}
                    </option>
                  ))}
                </select>
              </div>
            </>
          )}
        </div>
      </div>

      {/* 3D Visualization */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        {renderPlot()}
      </div>

      {/* Stats */}
      {analysis3DQuery.data?.stats && (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Total Points</div>
            <div className="mt-2 text-3xl font-semibold text-white">
              {analysis3DQuery.data.stats.total_points}
            </div>
          </div>
          
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Alzheimer Cases</div>
            <div className="mt-2 text-3xl font-semibold text-amber-400">
              {analysis3DQuery.data.stats.alzheimer_count}
            </div>
          </div>
          
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Parkinson Cases</div>
            <div className="mt-2 text-3xl font-semibold text-purple-400">
              {analysis3DQuery.data.stats.parkinson_count}
            </div>
          </div>
          
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase text-slate-400">Normal Cases</div>
            <div className="mt-2 text-3xl font-semibold text-emerald-400">
              {analysis3DQuery.data.stats.normal_count}
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="font-semibold text-white">Interaction Guide</h3>
        <ul className="mt-3 space-y-2 text-sm text-slate-400">
          <li>• <strong className="text-slate-300">Rotate:</strong> Click and drag to rotate the 3D view</li>
          <li>• <strong className="text-slate-300">Zoom:</strong> Scroll or pinch to zoom in/out</li>
          <li>• <strong className="text-slate-300">Pan:</strong> Right-click and drag to pan</li>
          <li>• <strong className="text-slate-300">Reset:</strong> Double-click to reset the view</li>
          <li>• <strong className="text-slate-300">Hover:</strong> Hover over points to see detailed information</li>
        </ul>
      </div>
    </div>
  )
}

