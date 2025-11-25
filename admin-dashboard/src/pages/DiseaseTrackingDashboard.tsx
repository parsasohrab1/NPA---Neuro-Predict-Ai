import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import {
  ExclamationTriangleIcon,
  CheckCircleIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline'
import diseaseTrackingApi, {
  PatientFeatures,
  FutureRiskPrediction,
  PatientRecommendations,
} from '../services/diseaseTracking'

const COLORS = {
  alzheimer: '#ef4444',
  parkinson: '#f59e0b',
  normal: '#10b981',
  warning: '#f59e0b',
  critical: '#ef4444',
}

const FEATURE_LABELS: Record<string, string> = {
  mmse_score: 'MMSE Score',
  moca_score: 'MoCA Score',
  memory_score: 'Memory Score',
  attention_score: 'Attention Score',
  executive_function_score: 'Executive Function Score',
  amyloid_beta: 'Amyloid-Beta (pg/mL)',
  tau_protein: 'Tau Protein (pg/mL)',
  dopamine_level: 'Dopamine Level (ng/mL)',
  hippocampal_volume: 'Hippocampal Volume (mm³)',
  cortical_thickness: 'Cortical Thickness (mm)',
  ventricular_volume: 'Ventricular Volume (mm³)',
  white_matter_hyperintensities: 'White Matter Hyperintensities',
  brain_volume_total: 'Total Brain Volume (mm³)',
}

export default function DiseaseTrackingDashboard() {
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null)
  const [monthsAhead, setMonthsAhead] = useState(12)
  const [refreshInterval, setRefreshInterval] = useState(10000) // 10 seconds

  // Get all patients summary
  const { data: patientsSummary } = useQuery({
    queryKey: ['patients-summary'],
    queryFn: () => diseaseTrackingApi.getAllPatientsSummary(),
    refetchInterval: refreshInterval,
  })

  // Get selected patient features
  const { data: patientFeatures } = useQuery({
    queryKey: ['patient-features', selectedPatientId],
    queryFn: () => diseaseTrackingApi.getPatientFeatures(selectedPatientId!, 365),
    enabled: selectedPatientId !== null,
    refetchInterval: refreshInterval,
  })

  // Get future risk prediction
  const { data: futureRisk } = useQuery({
    queryKey: ['future-risk', selectedPatientId, monthsAhead],
    queryFn: () => diseaseTrackingApi.predictFutureRisk(selectedPatientId!, monthsAhead),
    enabled: selectedPatientId !== null,
    refetchInterval: refreshInterval,
  })

  // Get recommendations
  const { data: recommendations } = useQuery({
    queryKey: ['recommendations', selectedPatientId],
    queryFn: () => diseaseTrackingApi.getRecommendations(selectedPatientId!),
    enabled: selectedPatientId !== null,
    refetchInterval: refreshInterval,
  })

  // Select first patient by default
  useEffect(() => {
    if (!selectedPatientId && patientsSummary?.patients.length > 0) {
      setSelectedPatientId(patientsSummary.patients[0].patient_id)
    }
  }, [patientsSummary, selectedPatientId])

  const renderFeatureChart = (
    data: PatientFeatures['cognitive_features'] | PatientFeatures['biomarker_features'] | PatientFeatures['mri_features'],
    featureKey: string,
    title: string,
    yAxisLabel: string
  ) => {
    if (!data || data.length === 0) {
      return (
        <div className="flex items-center justify-center h-64 text-slate-400">
          No data available for {title}
        </div>
      )
    }

    return (
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id={`color${featureKey}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={COLORS.alzheimer} stopOpacity={0.8} />
              <stop offset="95%" stopColor={COLORS.alzheimer} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis dataKey="date" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" label={{ value: yAxisLabel, angle: -90, position: 'insideLeft' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f172a',
              borderColor: '#1e293b',
              borderRadius: '12px',
              color: '#fff',
            }}
          />
          <Area
            type="monotone"
            dataKey={featureKey}
            stroke={COLORS.alzheimer}
            fillOpacity={1}
            fill={`url(#color${featureKey})`}
            name={FEATURE_LABELS[featureKey] || featureKey}
          />
        </AreaChart>
      </ResponsiveContainer>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Disease Tracking Dashboard</h1>
          <p className="text-slate-400 mt-1">
            Real-time monitoring of Alzheimer's and Parkinson's disease indicators
          </p>
        </div>
        <select
          value={refreshInterval}
          onChange={(e) => setRefreshInterval(Number(e.target.value))}
          className="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-1"
        >
          <option value={5000}>Update every 5s</option>
          <option value={10000}>Update every 10s</option>
          <option value={30000}>Update every 30s</option>
          <option value={60000}>Update every 1m</option>
        </select>
      </div>

      {/* Summary Cards */}
      {patientsSummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-400">Total Patients</div>
            <div className="mt-2 text-3xl font-semibold text-white">
              {patientsSummary.total_patients}
            </div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-400">High Risk Alzheimer</div>
            <div className="mt-2 text-3xl font-semibold text-rose-400">
              {patientsSummary.high_risk_alzheimer}
            </div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-400">High Risk Parkinson</div>
            <div className="mt-2 text-3xl font-semibold text-amber-400">
              {patientsSummary.high_risk_parkinson}
            </div>
          </div>
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-xs uppercase tracking-wide text-slate-400">Low Risk</div>
            <div className="mt-2 text-3xl font-semibold text-emerald-400">
              {patientsSummary.low_risk}
            </div>
          </div>
        </div>
      )}

      {/* Patient Selection */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Select Patient</h2>
        <select
          value={selectedPatientId || ''}
          onChange={(e) => setSelectedPatientId(Number(e.target.value))}
          className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2"
        >
          <option value="">Select a patient...</option>
          {patientsSummary?.patients.map((patient) => (
            <option key={patient.patient_id} value={patient.patient_id}>
              {patient.name} - Alzheimer: {(patient.alzheimer_risk * 100).toFixed(1)}%, Parkinson:{' '}
              {(patient.parkinson_risk * 100).toFixed(1)}%
            </option>
          ))}
        </select>
      </div>

      {/* Patient Details */}
      {patientFeatures && selectedPatientId && (
        <>
          {/* Patient Info and Current Risk */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h2 className="text-xl font-semibold text-white mb-4">
                Patient: {patientFeatures.patient_name}
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400">Age</div>
                  <div className="text-2xl font-semibold text-white">{patientFeatures.age}</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wide text-slate-400">Gender</div>
                  <div className="text-2xl font-semibold text-white capitalize">
                    {patientFeatures.gender}
                  </div>
                </div>
              </div>

              {patientFeatures.latest_prediction && (
                <div className="mt-6 grid grid-cols-2 gap-4">
                  <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">
                      Alzheimer's Risk
                    </div>
                    <div className="text-3xl font-semibold text-rose-400 mb-1">
                      {((patientFeatures.latest_prediction.alzheimer_risk || 0) * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-slate-400 capitalize">
                      {patientFeatures.latest_prediction.alzheimer_level || 'N/A'}
                    </div>
                  </div>
                  <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-400 mb-2">
                      Parkinson's Risk
                    </div>
                    <div className="text-3xl font-semibold text-amber-400 mb-1">
                      {((patientFeatures.latest_prediction.parkinson_risk || 0) * 100).toFixed(1)}%
                    </div>
                    <div className="text-sm text-slate-400 capitalize">
                      {patientFeatures.latest_prediction.parkinson_level || 'N/A'}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Alerts */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Active Alerts</h3>
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {patientFeatures.alerts.length > 0 ? (
                  patientFeatures.alerts.map((alert, idx) => (
                    <div
                      key={idx}
                      className={`rounded-xl border p-3 ${
                        alert.severity === 'critical'
                          ? 'border-rose-500 bg-rose-900/20'
                          : 'border-amber-500 bg-amber-900/20'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-1">
                        <ExclamationTriangleIcon
                          className={`h-5 w-5 ${
                            alert.severity === 'critical' ? 'text-rose-400' : 'text-amber-400'
                          }`}
                        />
                        <span
                          className={`text-xs font-semibold uppercase ${
                            alert.severity === 'critical' ? 'text-rose-400' : 'text-amber-400'
                          }`}
                        >
                          {alert.severity}
                        </span>
                      </div>
                      <div className="text-sm text-white font-medium">
                        {FEATURE_LABELS[alert.feature] || alert.feature}
                      </div>
                      <div className="text-xs text-slate-400 mt-1">{alert.message}</div>
                      <div className="text-xs text-slate-500 mt-1">
                        Normal: {alert.normal_range[0]} - {alert.normal_range[1]}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="flex items-center gap-2 text-slate-400">
                    <CheckCircleIcon className="h-5 w-5 text-emerald-400" />
                    <span>No active alerts</span>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Cognitive Features Chart */}
          {patientFeatures.cognitive_features.length > 0 && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Cognitive Assessment Trends</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {patientFeatures.cognitive_features[0].mmse_score !== undefined && (
                  <div>
                    <h3 className="text-sm text-slate-400 mb-2">MMSE Score</h3>
                    {renderFeatureChart(
                      patientFeatures.cognitive_features,
                      'mmse_score',
                      'MMSE Score',
                      'Score (0-30)'
                    )}
                  </div>
                )}
                {patientFeatures.cognitive_features[0].moca_score !== undefined && (
                  <div>
                    <h3 className="text-sm text-slate-400 mb-2">MoCA Score</h3>
                    {renderFeatureChart(
                      patientFeatures.cognitive_features,
                      'moca_score',
                      'MoCA Score',
                      'Score (0-30)'
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Biomarker Features Chart */}
          {patientFeatures.biomarker_features.length > 0 && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h2 className="text-xl font-semibold text-white mb-4">Biomarker Trends</h2>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {patientFeatures.biomarker_features[0].amyloid_beta !== undefined && (
                  <div>
                    <h3 className="text-sm text-slate-400 mb-2">Amyloid-Beta</h3>
                    {renderFeatureChart(
                      patientFeatures.biomarker_features,
                      'amyloid_beta',
                      'Amyloid-Beta',
                      'pg/mL'
                    )}
                  </div>
                )}
                {patientFeatures.biomarker_features[0].tau_protein !== undefined && (
                  <div>
                    <h3 className="text-sm text-slate-400 mb-2">Tau Protein</h3>
                    {renderFeatureChart(
                      patientFeatures.biomarker_features,
                      'tau_protein',
                      'Tau Protein',
                      'pg/mL'
                    )}
                  </div>
                )}
                {patientFeatures.biomarker_features[0].dopamine_level !== undefined && (
                  <div>
                    <h3 className="text-sm text-slate-400 mb-2">Dopamine Level</h3>
                    {renderFeatureChart(
                      patientFeatures.biomarker_features,
                      'dopamine_level',
                      'Dopamine Level',
                      'ng/mL'
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* MRI Features Chart */}
          {patientFeatures.mri_features.length > 0 && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h2 className="text-xl font-semibold text-white mb-4">MRI Features Trends</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {patientFeatures.mri_features[0].hippocampal_volume !== undefined && (
                  <div>
                    <h3 className="text-sm text-slate-400 mb-2">Hippocampal Volume</h3>
                    {renderFeatureChart(
                      patientFeatures.mri_features,
                      'hippocampal_volume',
                      'Hippocampal Volume',
                      'mm³'
                    )}
                  </div>
                )}
                {patientFeatures.mri_features[0].cortical_thickness !== undefined && (
                  <div>
                    <h3 className="text-sm text-slate-400 mb-2">Cortical Thickness</h3>
                    {renderFeatureChart(
                      patientFeatures.mri_features,
                      'cortical_thickness',
                      'Cortical Thickness',
                      'mm'
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Future Risk Prediction */}
          {futureRisk && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white">Future Risk Prediction</h2>
                <select
                  value={monthsAhead}
                  onChange={(e) => setMonthsAhead(Number(e.target.value))}
                  className="bg-slate-800 border border-slate-700 text-white text-sm rounded-lg px-3 py-1"
                >
                  <option value={6}>6 months</option>
                  <option value={12}>12 months</option>
                  <option value={24}>24 months</option>
                  <option value={36}>36 months</option>
                </select>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-6">
                  <h3 className="text-lg font-semibold text-rose-400 mb-4">Alzheimer's Disease</h3>
                  <div className="text-4xl font-bold text-white mb-2">
                    {(futureRisk.predicted_risks.alzheimer.risk_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-slate-400 capitalize mb-4">
                    Risk Level: {futureRisk.predicted_risks.alzheimer.risk_level}
                  </div>
                  {futureRisk.projected_values.mmse_score && (
                    <div className="text-sm text-slate-300">
                      Projected MMSE: {futureRisk.projected_values.mmse_score.toFixed(1)}
                    </div>
                  )}
                  {futureRisk.projected_values.amyloid_beta && (
                    <div className="text-sm text-slate-300">
                      Projected Amyloid-Beta: {futureRisk.projected_values.amyloid_beta.toFixed(1)} pg/mL
                    </div>
                  )}
                </div>
                <div className="rounded-xl border border-slate-800 bg-slate-900/90 p-6">
                  <h3 className="text-lg font-semibold text-amber-400 mb-4">Parkinson's Disease</h3>
                  <div className="text-4xl font-bold text-white mb-2">
                    {(futureRisk.predicted_risks.parkinson.risk_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-slate-400 capitalize mb-4">
                    Risk Level: {futureRisk.predicted_risks.parkinson.risk_level}
                  </div>
                  {futureRisk.projected_values.hippocampal_volume && (
                    <div className="text-sm text-slate-300">
                      Projected Hippocampal Volume:{' '}
                      {futureRisk.projected_values.hippocampal_volume.toFixed(0)} mm³
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Recommendations */}
          {recommendations && (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
              <h2 className="text-xl font-semibold text-white mb-4">
                Prevention & Control Recommendations
              </h2>
              <div className="space-y-6">
                {/* Alzheimer's Recommendations */}
                {recommendations.recommendations.alzheimer.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-rose-400 mb-3">
                      Alzheimer's Disease Recommendations
                    </h3>
                    <div className="space-y-3">
                      {recommendations.recommendations.alzheimer.map((rec, idx) => (
                        <div
                          key={idx}
                          className={`rounded-xl border p-4 ${
                            rec.priority === 'critical'
                              ? 'border-rose-500 bg-rose-900/20'
                              : rec.priority === 'high'
                              ? 'border-amber-500 bg-amber-900/20'
                              : 'border-slate-700 bg-slate-800/50'
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <span
                              className={`text-xs font-semibold uppercase px-2 py-1 rounded ${
                                rec.priority === 'critical'
                                  ? 'bg-rose-500 text-white'
                                  : rec.priority === 'high'
                                  ? 'bg-amber-500 text-white'
                                  : 'bg-slate-700 text-slate-300'
                              }`}
                            >
                              {rec.priority}
                            </span>
                            <span className="text-xs text-slate-400">{rec.category}</span>
                          </div>
                          <h4 className="text-white font-semibold mb-1">{rec.title}</h4>
                          <p className="text-sm text-slate-300 mb-3">{rec.description}</p>
                          <ul className="list-disc list-inside space-y-1">
                            {rec.actions.map((action, actionIdx) => (
                              <li key={actionIdx} className="text-sm text-slate-400">
                                {action}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Parkinson's Recommendations */}
                {recommendations.recommendations.parkinson.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-amber-400 mb-3">
                      Parkinson's Disease Recommendations
                    </h3>
                    <div className="space-y-3">
                      {recommendations.recommendations.parkinson.map((rec, idx) => (
                        <div
                          key={idx}
                          className={`rounded-xl border p-4 ${
                            rec.priority === 'critical'
                              ? 'border-rose-500 bg-rose-900/20'
                              : rec.priority === 'high'
                              ? 'border-amber-500 bg-amber-900/20'
                              : 'border-slate-700 bg-slate-800/50'
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <span
                              className={`text-xs font-semibold uppercase px-2 py-1 rounded ${
                                rec.priority === 'critical'
                                  ? 'bg-rose-500 text-white'
                                  : rec.priority === 'high'
                                  ? 'bg-amber-500 text-white'
                                  : 'bg-slate-700 text-slate-300'
                              }`}
                            >
                              {rec.priority}
                            </span>
                            <span className="text-xs text-slate-400">{rec.category}</span>
                          </div>
                          <h4 className="text-white font-semibold mb-1">{rec.title}</h4>
                          <p className="text-sm text-slate-300 mb-3">{rec.description}</p>
                          <ul className="list-disc list-inside space-y-1">
                            {rec.actions.map((action, actionIdx) => (
                              <li key={actionIdx} className="text-sm text-slate-400">
                                {action}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* General Recommendations */}
                {recommendations.recommendations.general.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-blue-400 mb-3">
                      General Recommendations
                    </h3>
                    <div className="space-y-3">
                      {recommendations.recommendations.general.map((rec, idx) => (
                        <div
                          key={idx}
                          className="rounded-xl border border-slate-700 bg-slate-800/50 p-4"
                        >
                          <div className="flex items-center gap-2 mb-2">
                            <span className="text-xs font-semibold uppercase px-2 py-1 rounded bg-slate-700 text-slate-300">
                              {rec.priority}
                            </span>
                            <span className="text-xs text-slate-400">{rec.category}</span>
                          </div>
                          <h4 className="text-white font-semibold mb-1">{rec.title}</h4>
                          <p className="text-sm text-slate-300 mb-3">{rec.description}</p>
                          <ul className="list-disc list-inside space-y-1">
                            {rec.actions.map((action, actionIdx) => (
                              <li key={actionIdx} className="text-sm text-slate-400">
                                {action}
                              </li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}

