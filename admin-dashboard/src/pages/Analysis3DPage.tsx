import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import Plot from 'react-plotly.js'
import { 
  CubeIcon, 
  ChartBarIcon, 
  BeakerIcon,
  CpuChipIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'
import { analysis3DService } from '../services/analysis3D'

type AnalysisType = 'scatter' | 'surface' | 'correlation' | 'feature-space'
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
      return (
        <div className="flex h-[600px] items-center justify-center">
          <p className="text-rose-400">Failed to load 3D data</p>
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

