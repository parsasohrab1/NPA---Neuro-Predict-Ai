import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
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
import { predictionsApi, patientsApi, imagingApi } from '../services/api'
import { PrinterIcon, DocumentArrowDownIcon, PhotoIcon } from '@heroicons/react/24/outline'
import MRIViewer from '../components/MRIViewer'

export default function PredictionResultPage() {
  const { id } = useParams<{ id: string }>()
  const [selectedStudyId, setSelectedStudyId] = useState<number | null>(null)
  const [currentSlice, setCurrentSlice] = useState(0)

  const { data: prediction, isLoading } = useQuery({
    queryKey: ['prediction', id],
    queryFn: () => predictionsApi.getById(Number(id)),
    enabled: !!id,
  })

  const { data: patient } = useQuery({
    queryKey: ['patient', prediction?.patient_id],
    queryFn: () => patientsApi.getById(prediction!.patient_id),
    enabled: !!prediction?.patient_id,
  })

  const { data: imagingStudies = [] } = useQuery({
    queryKey: ['prediction-imaging', id],
    queryFn: () => predictionsApi.getImagingStudies(Number(id!)),
    enabled: !!id && !!prediction,
  })

  const { data: sliceInfo } = useQuery({
    queryKey: ['study-slices', selectedStudyId],
    queryFn: () => imagingApi.getStudySlices(selectedStudyId!),
    enabled: !!selectedStudyId,
  })

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary-600 border-t-transparent"></div>
        <p className="mt-2 text-gray-600">Loading prediction results...</p>
      </div>
    )
  }

  if (!prediction) {
    return <div className="text-center py-12">Prediction not found</div>
  }

  const getRiskColor = (level: string) => {
    switch (level) {
      case 'high':
        return 'danger'
      case 'medium':
        return 'yellow'
      case 'low':
        return 'success'
      default:
        return 'gray'
    }
  }

  // Prepare data for interactive charts
  const featureImportanceData =
    prediction.feature_importance
      ? Object.entries(prediction.feature_importance)
          .slice(0, 10)
          .map(([name, value]) => ({
            name: name.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
            value: (value as number) * 100,
          }))
      : []

  const riskComparisonData = [
    {
      name: 'Alzheimer',
      risk: prediction.alzheimer_prediction ? prediction.alzheimer_prediction.risk_score * 100 : 0,
      confidence: prediction.alzheimer_prediction ? prediction.alzheimer_prediction.confidence * 100 : 0,
    },
    {
      name: 'Parkinson',
      risk: prediction.parkinson_prediction ? prediction.parkinson_prediction.risk_score * 100 : 0,
      confidence: prediction.parkinson_prediction ? prediction.parkinson_prediction.confidence * 100 : 0,
    },
  ]

  const multiDimensionalData = prediction.input_features
    ? [
        {
          subject: 'Cognitive',
          score: ((prediction.input_features.mmse_score || 0) / 30) * 100,
          fullMark: 100,
        },
        {
          subject: 'Biomarkers',
          score: prediction.input_features.amyloid_beta
            ? Math.min((prediction.input_features.amyloid_beta / 1000) * 100, 100)
            : 50,
          fullMark: 100,
        },
        {
          subject: 'Imaging',
          score: prediction.input_features.hippocampal_volume
            ? Math.min((prediction.input_features.hippocampal_volume / 5000) * 100, 100)
            : 50,
          fullMark: 100,
        },
        {
          subject: 'Genetic',
          score: prediction.input_features.apoe_e4_status ? 80 : 20,
          fullMark: 100,
        },
      ]
    : []

  const handlePrintReport = () => {
    window.print()
  }

  const handleExportPDF = async () => {
    // TODO: Implement PDF export
    alert('PDF export will be implemented')
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <Link
          to={patient ? `/patients/${patient.id}` : '/patients'}
          className="text-primary-600 hover:text-primary-700 text-sm font-medium mb-4 inline-block"
        >
          ← Back to Patient
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Prediction Results</h1>
            <p className="text-gray-600">
              {patient && `${patient.first_name} ${patient.last_name} • `}
              {new Date(prediction.created_at).toLocaleString()}
            </p>
          </div>
          <div className="flex gap-2">
            <button onClick={handlePrintReport} className="btn btn-secondary">
              <PrinterIcon className="h-5 w-5 mr-2" />
              Print
            </button>
            <button onClick={handleExportPDF} className="btn btn-secondary">
              <DocumentArrowDownIcon className="h-5 w-5 mr-2" />
              Export PDF
            </button>
          </div>
        </div>
      </div>

      {/* MRI Viewer Section */}
      {imagingStudies.length > 0 && (
        <div className="card mb-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <PhotoIcon className="h-6 w-6" />
            MRI Viewer
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2">
              {selectedStudyId ? (
                <div className="h-[600px]">
                  <MRIViewer
                    studyId={selectedStudyId}
                    initialSlice={currentSlice}
                    onSliceChange={setCurrentSlice}
                    enableMeasurement={true}
                    enableOverlay={imagingStudies.length > 1}
                    comparisonStudyId={
                      imagingStudies.length > 1 && selectedStudyId !== imagingStudies[0].id
                        ? imagingStudies.find((s) => s.id !== selectedStudyId)?.id
                        : undefined
                    }
                  />
                </div>
              ) : (
                <div className="flex items-center justify-center h-[600px] bg-gray-100 rounded-lg border-2 border-dashed border-gray-300">
                  <p className="text-gray-500">Select a study to view</p>
                </div>
              )}
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold text-gray-700">Available Studies</h3>
              {imagingStudies.map((study) => (
                <button
                  key={study.id}
                  onClick={() => {
                    setSelectedStudyId(study.id)
                    setCurrentSlice(0)
                  }}
                  className={`w-full text-left p-3 rounded-lg border transition ${
                    selectedStudyId === study.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-primary-300'
                  }`}
                >
                  <div className="font-medium text-sm">{study.modality}</div>
                  <div className="text-xs text-gray-600 mt-1">
                    {study.study_date ? new Date(study.study_date).toLocaleDateString() : 'N/A'}
                  </div>
                  {study.quality_score && (
                    <div className="text-xs text-gray-500 mt-1">
                      Quality: {(study.quality_score * 100).toFixed(0)}%
                    </div>
                  )}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Risk Assessment Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {prediction.alzheimer_prediction && (
          <div className={`card border-2 border-${getRiskColor(prediction.alzheimer_prediction.risk_level)}-300`}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">🧠 Alzheimer's Risk</h2>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium bg-${getRiskColor(prediction.alzheimer_prediction.risk_level)}-100 text-${getRiskColor(prediction.alzheimer_prediction.risk_level)}-700 capitalize`}
              >
                {prediction.alzheimer_prediction.risk_level} Risk
              </span>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-end mb-2">
                <span className="text-sm text-gray-600">Risk Score</span>
                <span
                  className={`text-3xl font-bold text-${getRiskColor(prediction.alzheimer_prediction.risk_level)}-600`}
                >
                  {(prediction.alzheimer_prediction.risk_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`bg-${getRiskColor(prediction.alzheimer_prediction.risk_level)}-500 h-3 rounded-full transition-all`}
                  style={{ width: `${prediction.alzheimer_prediction.risk_score * 100}%` }}
                ></div>
              </div>
            </div>

            <div>
              <span className="text-sm text-gray-600">Confidence</span>
              <div className="flex items-center mt-1">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full"
                    style={{ width: `${prediction.alzheimer_prediction.confidence * 100}%` }}
                  ></div>
                </div>
                <span className="ml-3 text-sm font-medium">
                  {(prediction.alzheimer_prediction.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {prediction.parkinson_prediction && (
          <div className={`card border-2 border-${getRiskColor(prediction.parkinson_prediction.risk_level)}-300`}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold">🤝 Parkinson's Risk</h2>
              <span
                className={`px-3 py-1 rounded-full text-sm font-medium bg-${getRiskColor(prediction.parkinson_prediction.risk_level)}-100 text-${getRiskColor(prediction.parkinson_prediction.risk_level)}-700 capitalize`}
              >
                {prediction.parkinson_prediction.risk_level} Risk
              </span>
            </div>

            <div className="mb-4">
              <div className="flex justify-between items-end mb-2">
                <span className="text-sm text-gray-600">Risk Score</span>
                <span
                  className={`text-3xl font-bold text-${getRiskColor(prediction.parkinson_prediction.risk_level)}-600`}
                >
                  {(prediction.parkinson_prediction.risk_score * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`bg-${getRiskColor(prediction.parkinson_prediction.risk_level)}-500 h-3 rounded-full transition-all`}
                  style={{ width: `${prediction.parkinson_prediction.risk_score * 100}%` }}
                ></div>
              </div>
            </div>

            <div>
              <span className="text-sm text-gray-600">Confidence</span>
              <div className="flex items-center mt-1">
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-500 h-2 rounded-full"
                    style={{ width: `${prediction.parkinson_prediction.confidence * 100}%` }}
                  ></div>
                </div>
                <span className="ml-3 text-sm font-medium">
                  {(prediction.parkinson_prediction.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Interactive Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Feature Importance Chart */}
        {featureImportanceData.length > 0 && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4">🔍 Top Contributing Factors</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={featureImportanceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Risk Comparison Chart */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">📊 Risk Comparison</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={riskComparisonData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="risk" fill="#ef4444" name="Risk Score (%)" />
              <Bar dataKey="confidence" fill="#3b82f6" name="Confidence (%)" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Multi-dimensional Analysis */}
        {multiDimensionalData.length > 0 && (
          <div className="card lg:col-span-2">
            <h2 className="text-xl font-bold mb-4">📈 Multi-dimensional Analysis</h2>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={multiDimensionalData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="subject" />
                <PolarRadiusAxis angle={90} domain={[0, 100]} />
                <Radar name="Score" dataKey="score" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
                <Tooltip />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recommendations */}
        <div className="lg:col-span-2 card">
          <h2 className="text-xl font-bold mb-4">📋 Clinical Recommendations</h2>
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700 leading-relaxed">
              {prediction.recommendations || 'No recommendations available'}
            </pre>
          </div>
        </div>

        {/* Model Information */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">🤖 Model Information</h2>
          <div className="space-y-3 text-sm">
            {prediction.model_name && (
              <div>
                <span className="text-gray-600">Model:</span>
                <div className="font-medium">{prediction.model_name}</div>
              </div>
            )}
            {prediction.model_version && (
              <div>
                <span className="text-gray-600">Version:</span>
                <div className="font-medium">{prediction.model_version}</div>
              </div>
            )}
            <div>
              <span className="text-gray-600">Disease Type:</span>
              <div className="font-medium capitalize">{prediction.disease_type}</div>
            </div>
            <div>
              <span className="text-gray-600">Created:</span>
              <div className="font-medium">{new Date(prediction.created_at).toLocaleString()}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
