import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  SparklesIcon,
  DocumentTextIcon,
  ArrowDownTrayIcon,
  XMarkIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline'
import axios from 'axios'

const API_BASE = 'http://localhost:8001'

interface FusionReport {
  id: number
  patient_id: number
  generated_at: string
  fusion_scores: {
    cognitive: number
    biomarker: number
    imaging: number
    integrated: number
    confidence: string
  }
  cross_modal: {
    consistency_score: number
    correlations: {
      cognitive_biomarker: number
      cognitive_imaging: number
      biomarker_imaging: number
    }
    has_conflicts: boolean
  }
  disease_analysis: {
    alzheimer: {
      score: number
      confidence: number
    }
    parkinson: {
      score: number
      confidence: number
    }
  }
  interpretation: {
    overall: string
    primary_concern: string
    confidence: number
  }
  report: {
    executive_summary: string
    detailed_findings: string
    risk_assessment: string
    recommendations: string
    follow_up_plan: string
  }
  quality: {
    data_completeness: number
    has_outliers: boolean
  }
}

export default function DataFusionReportsPage() {
  const [patientId, setPatientId] = useState('')
  const [selectedReport, setSelectedReport] = useState<FusionReport | null>(null)
  const queryClient = useQueryClient()

  // Fetch patient reports
  const { data: reports, isLoading } = useQuery<FusionReport[]>({
    queryKey: ['fusion-reports', patientId],
    queryFn: async () => {
      if (!patientId) return []
      const response = await axios.get(`${API_BASE}/api/v1/data-fusion/patient/${patientId}`)
      return response.data
    },
    enabled: !!patientId,
  })

  // Generate new report mutation
  const generateReport = useMutation({
    mutationFn: async (patId: number) => {
      const response = await axios.post(`${API_BASE}/api/v1/data-fusion/generate`, {
        patient_id: patId,
      })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['fusion-reports', patientId] })
    },
  })

  const getInterpretationColor = (interpretation: string) => {
    switch (interpretation) {
      case 'normal':
        return 'bg-green-100 text-green-800 border-green-300'
      case 'mild_concern':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300'
      case 'moderate_concern':
        return 'bg-orange-100 text-orange-800 border-orange-300'
      case 'high_concern':
        return 'bg-red-100 text-red-800 border-red-300'
      case 'critical':
        return 'bg-red-200 text-red-900 border-red-400'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300'
    }
  }

  const getConfidenceColor = (confidence: string) => {
    switch (confidence) {
      case 'very_high':
        return 'text-green-400'
      case 'high':
        return 'text-blue-400'
      case 'moderate':
        return 'text-yellow-400'
      case 'low':
        return 'text-orange-400'
      case 'very_low':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  const downloadReport = (report: FusionReport) => {
    const content = `
MULTI-MODAL DATA FUSION REPORT
NeuroPredict-AI System

Report ID: ${report.id}
Generated: ${new Date(report.generated_at).toLocaleString()}
Patient ID: ${report.patient_id}

${report.report.executive_summary}

DETAILED FINDINGS:
${report.report.detailed_findings}

RISK ASSESSMENT:
${report.report.risk_assessment}

RECOMMENDATIONS:
${report.report.recommendations}

FOLLOW-UP PLAN:
${report.report.follow_up_plan}

---
This report was generated using our proprietary multi-modal data fusion algorithm.
© 2024 NeuroPredict-AI
    `.trim()

    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `DataFusionReport_Patient${report.patient_id}_${report.id}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2 text-slate-100">
            <SparklesIcon className="h-8 w-8 text-purple-400" />
            Data Fusion Reports
          </h1>
          <p className="text-slate-400 mt-1">
            Multi-Modal Medical Data Integration & Interpretation
          </p>
        </div>
      </div>

      {/* System Information */}
      <div className="border-2 border-purple-500/30 bg-gradient-to-r from-purple-900/30 to-blue-900/30 rounded-lg p-6">
        <div className="flex items-start gap-3">
          <SparklesIcon className="h-6 w-6 text-purple-400 mt-1 flex-shrink-0" />
          <div>
            <h3 className="font-semibold text-purple-200">Advanced Data Fusion</h3>
            <p className="text-sm text-purple-300 mt-1">
              This system implements a <strong>Multi-Modal Data Fusion Algorithm</strong> that
              integrates cognitive assessments, biomarker profiles, and neuroimaging findings through
              confidence-weighted correlation analysis with automated conflict resolution and natural
              language report generation.
            </p>
          </div>
        </div>
      </div>

      {/* Search & Generate */}
      <div className="bg-slate-800/50 rounded-lg border border-slate-700 p-6">
        <h2 className="text-xl font-semibold mb-4 text-slate-100">Generate or View Fusion Reports</h2>
        <div className="space-y-4">
          <div className="flex gap-2">
            <input
              type="number"
              placeholder="Enter Patient ID"
              value={patientId}
              onChange={(e) => setPatientId(e.target.value)}
              className="flex-1 px-4 py-2 border border-slate-600 rounded-lg bg-slate-900 text-slate-100 placeholder:text-slate-500 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            />
            <button
              onClick={() => {
                if (patientId) {
                  generateReport.mutate(parseInt(patientId))
                }
              }}
              disabled={!patientId || generateReport.isPending}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
            >
              <SparklesIcon className="h-5 w-5" />
              Generate Fusion Report
            </button>
          </div>

          {generateReport.isPending && (
            <div className="text-sm text-slate-400 flex items-center gap-2">
              <ArrowPathIcon className="h-4 w-4 animate-spin" />
              Generating multi-modal fusion report...
            </div>
          )}

          {generateReport.isSuccess && (
            <div className="text-sm text-green-400 flex items-center gap-2">
              <CheckCircleIcon className="h-4 w-4" />
              Fusion report generated successfully!
            </div>
          )}

          {generateReport.isError && (
            <div className="text-sm text-red-400 flex items-center gap-2">
              <ExclamationTriangleIcon className="h-4 w-4" />
              Error generating report. Please try again.
            </div>
          )}
        </div>
      </div>

      {/* Reports List */}
      {isLoading && (
        <div className="text-center py-8">
          <ArrowPathIcon className="h-8 w-8 animate-spin mx-auto text-purple-400" />
          <p className="text-slate-400 mt-2">Loading reports...</p>
        </div>
      )}

      {reports && reports.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {reports.map((report) => (
            <div
              key={report.id}
              className="bg-slate-800/50 rounded-lg border border-slate-700 hover:border-purple-500/50 transition-all cursor-pointer border-l-4 border-l-purple-500 p-6"
              onClick={() => setSelectedReport(report)}
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-slate-100">Report #{report.id}</h3>
                  <p className="text-sm text-slate-400">
                    {new Date(report.generated_at).toLocaleDateString()}
                  </p>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getInterpretationColor(report.interpretation.overall)}`}>
                  {report.interpretation.overall.replace('_', ' ').toUpperCase()}
                </span>
              </div>

              {/* Fusion Score */}
              <div className="mb-4">
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-semibold text-slate-300">Integrated Fusion Score</span>
                  <span className={`font-bold ${getConfidenceColor(report.fusion_scores.confidence)}`}>
                    {report.fusion_scores.integrated.toFixed(1)}/100
                  </span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-blue-500 h-2 rounded-full"
                    style={{ width: `${report.fusion_scores.integrated}%` }}
                  />
                </div>
              </div>

              {/* Primary Concern */}
              <div className="mb-4">
                <p className="text-sm font-semibold text-slate-300">Primary Concern:</p>
                <p className="text-sm text-slate-100">{report.interpretation.primary_concern}</p>
              </div>

              {/* Modality Scores */}
              <div className="grid grid-cols-3 gap-2 text-xs mb-4">
                <div className="bg-blue-900/30 p-2 rounded border border-blue-700/30">
                  <p className="text-slate-400">Cognitive</p>
                  <p className="font-semibold text-slate-100">{report.fusion_scores.cognitive.toFixed(0)}</p>
                </div>
                <div className="bg-green-900/30 p-2 rounded border border-green-700/30">
                  <p className="text-slate-400">Biomarker</p>
                  <p className="font-semibold text-slate-100">{report.fusion_scores.biomarker.toFixed(0)}</p>
                </div>
                <div className="bg-purple-900/30 p-2 rounded border border-purple-700/30">
                  <p className="text-slate-400">Imaging</p>
                  <p className="font-semibold text-slate-100">{report.fusion_scores.imaging.toFixed(0)}</p>
                </div>
              </div>

              {/* Conflicts Warning */}
              {report.cross_modal.has_conflicts && (
                <div className="flex items-center gap-2 text-xs text-orange-400 bg-orange-900/20 border border-orange-700/30 p-2 rounded mb-4">
                  <ExclamationTriangleIcon className="h-4 w-4" />
                  Cross-modal conflicts detected
                </div>
              )}

              {/* Disease Analysis */}
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-blue-900/30 p-2 rounded border border-blue-700/30">
                  <p className="text-slate-400">AD Risk</p>
                  <p className="font-semibold text-blue-300">
                    {report.disease_analysis.alzheimer.score.toFixed(0)}%
                  </p>
                </div>
                <div className="bg-green-900/30 p-2 rounded border border-green-700/30">
                  <p className="text-slate-400">PD Risk</p>
                  <p className="font-semibold text-green-300">
                    {report.disease_analysis.parkinson.score.toFixed(0)}%
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {reports && reports.length === 0 && patientId && !isLoading && (
        <div className="text-center py-12 bg-slate-800/30 rounded-lg border border-slate-700">
          <DocumentTextIcon className="h-12 w-12 text-slate-600 mx-auto mb-4" />
          <p className="text-slate-400">No fusion reports found for this patient.</p>
          <p className="text-sm text-slate-500 mt-2">Generate one using the button above.</p>
        </div>
      )}

      {/* Detailed Report Modal */}
      {selectedReport && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-slate-900 rounded-lg border border-slate-700 max-w-4xl max-h-[90vh] overflow-y-auto shadow-2xl">
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 sticky top-0 z-10">
              <div className="flex justify-between items-start">
                <div>
                  <h2 className="text-2xl font-bold flex items-center gap-2">
                    <DocumentTextIcon className="h-6 w-6" />
                    Data Fusion Report #{selectedReport.id}
                  </h2>
                  <p className="text-purple-100 mt-1">
                    Patient ID: {selectedReport.patient_id} | 
                    Generated: {new Date(selectedReport.generated_at).toLocaleString()}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedReport(null)}
                  className="text-white hover:bg-purple-700 rounded p-2 transition-colors"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Executive Summary */}
              <div>
                <h3 className="font-bold text-lg mb-2 flex items-center gap-2 text-slate-100">
                  <DocumentTextIcon className="h-5 w-5 text-purple-400" />
                  Executive Summary
                </h3>
                <pre className="whitespace-pre-wrap text-sm bg-slate-800 p-4 rounded border border-slate-700 text-slate-200">
                  {selectedReport.report.executive_summary}
                </pre>
              </div>

              {/* Detailed Findings */}
              <div>
                <h3 className="font-bold text-lg mb-2 text-slate-100">Detailed Findings</h3>
                <pre className="whitespace-pre-wrap text-sm bg-slate-800 p-4 rounded border border-slate-700 text-slate-200">
                  {selectedReport.report.detailed_findings}
                </pre>
              </div>

              {/* Risk Assessment */}
              <div>
                <h3 className="font-bold text-lg mb-2 flex items-center gap-2 text-slate-100">
                  <ExclamationTriangleIcon className="h-5 w-5 text-orange-400" />
                  Risk Assessment
                </h3>
                <pre className="whitespace-pre-wrap text-sm bg-orange-900/20 p-4 rounded border border-orange-700/30 text-slate-200">
                  {selectedReport.report.risk_assessment}
                </pre>
              </div>

              {/* Recommendations */}
              <div>
                <h3 className="font-bold text-lg mb-2 flex items-center gap-2 text-slate-100">
                  <CheckCircleIcon className="h-5 w-5 text-green-400" />
                  Recommendations
                </h3>
                <pre className="whitespace-pre-wrap text-sm bg-green-900/20 p-4 rounded border border-green-700/30 text-slate-200">
                  {selectedReport.report.recommendations}
                </pre>
              </div>

              {/* Follow-up Plan */}
              {selectedReport.report.follow_up_plan && (
                <div>
                  <h3 className="font-bold text-lg mb-2 text-slate-100">Follow-up Plan</h3>
                  <pre className="whitespace-pre-wrap text-sm bg-blue-900/20 p-4 rounded border border-blue-700/30 text-slate-200">
                    {selectedReport.report.follow_up_plan}
                  </pre>
                </div>
              )}

              {/* Quality Metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2 text-slate-100">Data Completeness</h4>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-700 rounded-full h-2">
                      <div
                        className="bg-green-500 h-2 rounded-full"
                        style={{ width: `${selectedReport.quality.data_completeness}%` }}
                      />
                    </div>
                    <span className="text-sm text-slate-200">{selectedReport.quality.data_completeness.toFixed(0)}%</span>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2 text-slate-100">Confidence</h4>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getConfidenceColor(selectedReport.fusion_scores.confidence)}`}>
                    {selectedReport.fusion_scores.confidence.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
              </div>

              {/* Actions */}
              <div className="flex gap-2 pt-4 border-t border-slate-700">
                <button
                  onClick={() => downloadReport(selectedReport)}
                  className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium flex items-center justify-center gap-2 transition-colors"
                >
                  <ArrowDownTrayIcon className="h-5 w-5" />
                  Download Report
                </button>
                <button
                  onClick={() => setSelectedReport(null)}
                  className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-100 rounded-lg font-medium transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

