import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
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
  PlusIcon,
  XMarkIcon,
  UserPlusIcon,
  DocumentPlusIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'
import diseaseTrackingApi, {
  PatientFeatures,
  FutureRiskPrediction,
  PatientRecommendations,
} from '../services/diseaseTracking'
import BrainVisualization3D from '../components/BrainVisualization3D'

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
  blood_pressure_systolic: 'فشار خون سیستولیک (mmHg)',
  blood_pressure_diastolic: 'فشار خون دیاستولیک (mmHg)',
  temperature: 'درجه حرارت (°C)',
  heart_rate: 'ضربان قلب (bpm)',
  respiratory_rate: 'نرخ تنفس (breaths/min)',
  oxygen_saturation: 'اشباع اکسیژن SpO2 (%)',
  weight: 'وزن (kg)',
  height: 'قد (cm)',
  bmi: 'شاخص توده بدنی (kg/m²)',
  blood_glucose: 'قند خون ناشتا (mg/dL)',
  cholesterol_total: 'کلسترول کل (mg/dL)',
}

export default function DiseaseTrackingDashboard() {
  const [selectedPatientId, setSelectedPatientId] = useState<number | null>(null)
  const [monthsAhead, setMonthsAhead] = useState(12)
  const [refreshInterval, setRefreshInterval] = useState(10000) // 10 seconds
  const [showAddPatientModal, setShowAddPatientModal] = useState(false)
  const [showAddDataModal, setShowAddDataModal] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [showLoadDataConfirm, setShowLoadDataConfirm] = useState(false)
  const [showLoadSampleDataConfirm, setShowLoadSampleDataConfirm] = useState(false)
  const [showClearDataConfirm, setShowClearDataConfirm] = useState(false)
  const queryClient = useQueryClient()

  // Get all patients summary
  const { data: patientsSummary, error: patientsError } = useQuery({
    queryKey: ['patients-summary'],
    queryFn: () => diseaseTrackingApi.getAllPatientsSummary(),
    refetchInterval: refreshInterval,
    retry: 2,
  })

  // Get patient classification (تقسیم‌بندی بیماران - نرمال/آلزایمر/پارکینسون)
  const { data: patientClassification } = useQuery({
    queryKey: ['patient-classification'],
    queryFn: () => diseaseTrackingApi.getPatientClassification(),
    refetchInterval: refreshInterval,
    retry: 2,
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

  const [notification, setNotification] = useState<{ type: 'success' | 'error'; message: string } | null>(null)

  // Create patient mutation
  const createPatientMutation = useMutation({
    mutationFn: (patientData: any) => diseaseTrackingApi.createPatient(patientData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patients-summary'] })
      queryClient.invalidateQueries({ queryKey: ['patient-classification'] })
      setShowAddPatientModal(false)
      setNotification({ type: 'success', message: 'Patient created successfully!' })
      setTimeout(() => setNotification(null), 3000)
    },
    onError: (error: any) => {
      setNotification({
        type: 'error',
        message: error.response?.data?.detail || 'Failed to create patient',
      })
      setTimeout(() => setNotification(null), 5000)
    },
  })

  // Create medical record mutation
  const createMedicalRecordMutation = useMutation({
    mutationFn: ({ patientId, recordData }: { patientId: number; recordData: any }) =>
      diseaseTrackingApi.createMedicalRecord(patientId, recordData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['patient-features', selectedPatientId] })
      queryClient.invalidateQueries({ queryKey: ['patients-summary'] })
      queryClient.invalidateQueries({ queryKey: ['patient-classification'] })
      queryClient.invalidateQueries({ queryKey: ['future-risk', selectedPatientId] })
      queryClient.invalidateQueries({ queryKey: ['recommendations', selectedPatientId] })
      setShowAddDataModal(false)
      setNotification({ type: 'success', message: 'Medical data added successfully!' })
      setTimeout(() => setNotification(null), 3000)
    },
    onError: (error: any) => {
      setNotification({
        type: 'error',
        message: error.response?.data?.detail || 'Failed to add medical data',
      })
      setTimeout(() => setNotification(null), 5000)
    },
  })

  // Load all datasets mutation
  const loadAllDatasetsMutation = useMutation({
    mutationFn: () => diseaseTrackingApi.loadAllDatasets(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['patients-summary'] })
      queryClient.invalidateQueries({ queryKey: ['patient-classification'] })
      setShowLoadDataConfirm(false)
      
      let message = `All datasets loaded! ${data.total_patients} patients, ${data.total_records} records, ${data.total_predictions} predictions created.`
      
      if (data.skipped > 0) {
        message += ` (${data.skipped} skipped - already exist)`
      }
      
      if (data.error_count && data.error_count > 0) {
        message += ` WARNING: ${data.error_count} errors occurred during import.`
        console.error('Import errors:', data.errors)
      }
      
      setNotification({
        type: data.error_count && data.error_count > 0 ? 'error' : 'success',
        message,
      })
      setTimeout(() => setNotification(null), 8000)
    },
    onError: (error: any) => {
      console.error('Load datasets error:', error)
      const detail = error.response?.data?.detail || error.message
      setShowLoadDataConfirm(false)
      setNotification({
        type: 'error',
        message: `Failed to load datasets: ${detail}. Check console for details.`,
      })
      setTimeout(() => setNotification(null), 8000)
    },
  })

  // Clear all data mutation
  const clearAllDataMutation = useMutation({
    mutationFn: () => diseaseTrackingApi.clearAllData(),
    onSuccess: (data) => {
      // Invalidate all related queries to refresh the UI
      queryClient.invalidateQueries({ queryKey: ['patients-summary'] })
      queryClient.invalidateQueries({ queryKey: ['patient-classification'] })
      queryClient.invalidateQueries({ queryKey: ['patient-features'] })
      queryClient.invalidateQueries({ queryKey: ['future-risk'] })
      
      // Clear selected patient
      setSelectedPatientId(null)
      
      setShowClearDataConfirm(false)
      setNotification({
        type: 'success',
        message: `✅ All data cleared successfully! ${data.patients_deleted} patients, ${data.records_deleted} records, ${data.predictions_deleted} predictions deleted. You can now load fresh sample data.`,
      })
      setTimeout(() => setNotification(null), 8000)
    },
    onError: (error: any) => {
      console.error('Clear data error:', error)
      const detail = error.response?.data?.detail || error.message
      setShowClearDataConfirm(false)
      setNotification({
        type: 'error',
        message: `❌ Failed to clear data: ${detail}`,
      })
      setTimeout(() => setNotification(null), 6000)
    },
  })

  // Load sample datasets mutation (200 patients with specific distribution)
  const loadSampleDatasetsMutation = useMutation({
    mutationFn: () => diseaseTrackingApi.loadSampleDatasets(),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['patients-summary'] })
      queryClient.invalidateQueries({ queryKey: ['patient-classification'] })
      queryClient.invalidateQueries({ queryKey: ['patient-features'] })
      queryClient.invalidateQueries({ queryKey: ['future-risk'] })
      setShowLoadSampleDataConfirm(false)
      
      // Check if no new patients were added (all skipped)
      if (data.total_patients === 0 && data.skipped > 0) {
        setNotification({
          type: 'error',
          message: `⚠️ All ${data.skipped} patients already exist in the database! Please click "Clear All Data" button first, then try "Load Sample Data" again.`,
        })
        setTimeout(() => setNotification(null), 15000) // Longer timeout for important message
        return
      }
      
      let message = `✅ Sample data loaded successfully! ${data.total_patients} patients, ${data.total_records} records, ${data.total_predictions} predictions.`
      
      if (data.categories_included) {
        message += ` Categories: ${data.categories_included}.`
      }
      
      if (data.skipped > 0) {
        message += ` (${data.skipped} skipped - already existed)`
      }
      
      if (data.error_count && data.error_count > 0) {
        message += ` ⚠️ WARNING: ${data.error_count} errors occurred during import.`
        console.error('Import errors:', data.errors)
      }
      
      setNotification({
        type: data.error_count && data.error_count > 0 ? 'error' : 'success',
        message,
      })
      setTimeout(() => setNotification(null), 12000)
    },
    onError: (error: any) => {
      console.error('Load sample datasets error:', error)
      const detail = error.response?.data?.detail || error.message
      setShowLoadSampleDataConfirm(false)
      setNotification({
        type: 'error',
        message: `❌ Failed to load sample datasets: ${detail}. Check console for details.`,
      })
      setTimeout(() => setNotification(null), 10000)
    },
  })

  // Select first patient by default
  useEffect(() => {
    if (!selectedPatientId && patientsSummary?.patients && patientsSummary.patients.length > 0) {
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
      {/* Notification */}
      {notification && (
        <div
          className={`fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg ${
            notification.type === 'success'
              ? 'bg-emerald-600 text-white'
              : 'bg-rose-600 text-white'
          }`}
        >
          <div className="flex items-center gap-2">
            {notification.type === 'success' ? (
              <CheckCircleIcon className="h-5 w-5" />
            ) : (
              <ExclamationTriangleIcon className="h-5 w-5" />
            )}
            <span>{notification.message}</span>
            <button
              onClick={() => setNotification(null)}
              className="ml-2 hover:opacity-70"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Disease Tracking Dashboard</h1>
          <p className="text-slate-400 mt-1">
            Real-time monitoring of Alzheimer's and Parkinson's disease indicators
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowAddPatientModal(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            <UserPlusIcon className="h-5 w-5" />
            Add Patient
          </button>
          {selectedPatientId && (
            <button
              onClick={() => setShowAddDataModal(true)}
              className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <DocumentPlusIcon className="h-5 w-5" />
              Add Data
            </button>
          )}
          <button
            onClick={() => setShowClearDataConfirm(true)}
            className="flex items-center gap-2 bg-rose-600 hover:bg-rose-700 text-white px-4 py-2 rounded-lg transition-colors"
            title="Clear all disease tracking data (patients, records, predictions)"
          >
            <TrashIcon className="h-5 w-5" />
            Clear All Data
          </button>
          <button
            onClick={() => setShowLoadSampleDataConfirm(true)}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors"
            title="Load 200 sample patients: 120 Normal, 40 Alzheimer, 40 Parkinson"
          >
            <PlusIcon className="h-5 w-5" />
            Load Sample Data (200)
          </button>
          <button
            onClick={() => setShowLoadDataConfirm(true)}
            className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition-colors"
            title="Load all synthetic and real datasets"
          >
            <PlusIcon className="h-5 w-5" />
            Load All Data
          </button>
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
      </div>

      {/* Error Message */}
      {patientsError && (
        <div className="rounded-2xl border border-rose-800 bg-rose-900/20 p-4">
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 text-rose-400">
              <ExclamationTriangleIcon className="h-5 w-5" />
              <span className="font-semibold">
                Failed to load patients
              </span>
            </div>
            <div className="text-sm text-rose-300">
              {(patientsError as any)?.response?.status === 401 ? (
                <span>Authentication required. Please log in.</span>
              ) : (patientsError as any)?.response?.status === 403 ? (
                <span>Permission denied. You need doctor or admin role.</span>
              ) : (patientsError as any)?.response?.data?.detail ? (
                <span>{(patientsError as any).response.data.detail}</span>
              ) : (
                <span>Please check your connection and try again. Error: {(patientsError as any)?.message}</span>
              )}
            </div>
            <div className="text-xs text-slate-500 mt-2">
              Tip: Make sure the backend is running on port 8001 and you have the required permissions.
            </div>
          </div>
        </div>
      )}

      {/* Help Banner - Show when no patients exist */}
      {!patientsError && patientsSummary && patientsSummary.patients.length === 0 && (
        <div className="bg-blue-900/30 border-2 border-blue-700 rounded-xl p-5">
          <div className="flex items-start gap-4">
            <div className="text-4xl">📊</div>
            <div className="flex-1">
              <h3 className="text-lg font-bold text-blue-200 mb-2">No patients in database</h3>
              <p className="text-slate-300 text-sm mb-3">
                To get started, load sample data into the system:
              </p>
              <div className="space-y-2 text-sm text-slate-300">
                <div className="flex items-start gap-2">
                  <span className="text-indigo-400 font-bold mt-0.5">1.</span>
                  <span>Click <strong className="text-indigo-300">"Load Sample Data (200)"</strong> to load sample patients (183 available in CSV files)</span>
                </div>
                <div className="flex items-start gap-2">
                  <span className="text-purple-400 font-bold mt-0.5">2.</span>
                  <span>Or click <strong className="text-purple-300">"Load All Data"</strong> to load all available datasets</span>
                </div>
              </div>
              <div className="mt-3 p-3 bg-amber-900/20 border border-amber-700/50 rounded-lg">
                <p className="text-amber-200 text-xs">
                  <strong>💡 Tip:</strong> If you've already loaded data and want to refresh, use <strong>"Clear All Data"</strong> first (red button), then load again.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

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

      {/* Patient Classification - تقسیم‌بندی بیماران (نرمال/آلزایمر/پارکینسون) */}
      {patientClassification && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <span>📋</span>
            تقسیم‌بندی بیماران | Patient Classification
          </h2>
          <p className="text-sm text-slate-400 mb-6">
            محدوده سلامت و محدوده بیمار | Feature ranges for Alzheimer's and Parkinson's
          </p>

          {/* Classification Summary */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="rounded-xl border border-emerald-800 bg-emerald-900/30 p-4">
              <div className="text-xs uppercase text-slate-400">نرمال / Normal</div>
              <div className="text-2xl font-bold text-emerald-400">{patientClassification.classification_summary.normal}</div>
            </div>
            <div className="rounded-xl border border-rose-800 bg-rose-900/30 p-4">
              <div className="text-xs uppercase text-slate-400">آلزایمر / Alzheimer</div>
              <div className="text-2xl font-bold text-rose-400">{patientClassification.classification_summary.alzheimer}</div>
            </div>
            <div className="rounded-xl border border-amber-800 bg-amber-900/30 p-4">
              <div className="text-xs uppercase text-slate-400">پارکینسون / Parkinson</div>
              <div className="text-2xl font-bold text-amber-400">{patientClassification.classification_summary.parkinson}</div>
            </div>
            <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
              <div className="text-xs uppercase text-slate-400">نامشخص / Unknown</div>
              <div className="text-2xl font-bold text-slate-400">{patientClassification.classification_summary.unknown}</div>
            </div>
          </div>

          {/* Feature Ranges Table */}
          <div className="mb-6">
            <h3 className="text-base font-semibold text-white mb-3">محدوده ویژگی‌ها | Feature Ranges (Health vs Patient)</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm text-left text-slate-300">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="py-2 px-3 font-medium">ویژگی / Feature</th>
                    <th className="py-2 px-3 font-medium">سالم / Normal</th>
                    <th className="py-2 px-3 font-medium">آلزایمر</th>
                    <th className="py-2 px-3 font-medium">پارکینسون</th>
                  </tr>
                </thead>
                <tbody>
                  {patientClassification.feature_ranges?.cognitive && Object.entries(patientClassification.feature_ranges.cognitive).map(([key, val]: [string, any]) => (
                    <tr key={key} className="border-b border-slate-800">
                      <td className="py-2 px-3">{FEATURE_LABELS[key] || key}</td>
                      <td className="py-2 px-3 text-emerald-400">{val.normal?.min}-{val.normal?.max}</td>
                      <td className="py-2 px-3 text-rose-400">{val.alzheimer?.min}-{val.alzheimer?.max}</td>
                      <td className="py-2 px-3 text-amber-400">{val.parkinson?.min}-{val.parkinson?.max}</td>
                    </tr>
                  ))}
                  {patientClassification.feature_ranges?.biomarkers && Object.entries(patientClassification.feature_ranges.biomarkers).map(([key, val]: [string, any]) => (
                    <tr key={key} className="border-b border-slate-800">
                      <td className="py-2 px-3">{FEATURE_LABELS[key] || key}</td>
                      <td className="py-2 px-3 text-emerald-400">{val.normal?.min}-{val.normal?.max}</td>
                      <td className="py-2 px-3 text-rose-400">{val.alzheimer?.min}-{val.alzheimer?.max}</td>
                      <td className="py-2 px-3 text-amber-400">{val.parkinson?.min}-{val.parkinson?.max}</td>
                    </tr>
                  ))}
                  {patientClassification.feature_ranges?.mri && Object.entries(patientClassification.feature_ranges.mri).map(([key, val]: [string, any]) => (
                    <tr key={key} className="border-b border-slate-800">
                      <td className="py-2 px-3">{FEATURE_LABELS[key] || key}</td>
                      <td className="py-2 px-3 text-emerald-400">{val.normal?.min}-{val.normal?.max}</td>
                      <td className="py-2 px-3 text-rose-400">{val.alzheimer?.min}-{val.alzheimer?.max}</td>
                      <td className="py-2 px-3 text-amber-400">{val.parkinson?.min}-{val.parkinson?.max}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Patient List with Classification */}
          <div>
            <h3 className="text-base font-semibold text-white mb-3">لیست بیماران | Patient List ({patientClassification.total_patients} total)</h3>
            <div className="overflow-x-auto max-h-80 overflow-y-auto">
              <table className="w-full text-sm text-left text-slate-300">
                <thead className="sticky top-0 bg-slate-900 z-10">
                  <tr className="border-b border-slate-700">
                    <th className="py-2 px-3 font-medium">بیمار</th>
                    <th className="py-2 px-3 font-medium">سن</th>
                    <th className="py-2 px-3 font-medium">تشخیص</th>
                    <th className="py-2 px-3 font-medium">ریسک آلزایمر</th>
                    <th className="py-2 px-3 font-medium">ریسک پارکینسون</th>
                    <th className="py-2 px-3 font-medium">MMSE</th>
                    <th className="py-2 px-3 font-medium">Amyloid</th>
                    <th className="py-2 px-3 font-medium">Tau</th>
                    <th className="py-2 px-3 font-medium">Dopamine</th>
                  </tr>
                </thead>
                <tbody>
                  {patientClassification.patients.map((p) => (
                    <tr key={p.patient_id} className="border-b border-slate-800 hover:bg-slate-800/50">
                      <td className="py-2 px-3 font-medium">{p.name}</td>
                      <td className="py-2 px-3">{p.age ?? '-'}</td>
                      <td className="py-2 px-3">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                          p.diagnosis === 'normal' ? 'bg-emerald-900/50 text-emerald-400' :
                          p.diagnosis === 'alzheimer' ? 'bg-rose-900/50 text-rose-400' :
                          p.diagnosis === 'parkinson' ? 'bg-amber-900/50 text-amber-400' :
                          'bg-slate-700 text-slate-400'
                        }`}>
                          {p.diagnosis_fa}
                        </span>
                      </td>
                      <td className="py-2 px-3">{p.alzheimer_risk != null ? (p.alzheimer_risk * 100).toFixed(1) + '%' : '-'}</td>
                      <td className="py-2 px-3">{p.parkinson_risk != null ? (p.parkinson_risk * 100).toFixed(1) + '%' : '-'}</td>
                      <td className="py-2 px-3">{p.features?.mmse_score ?? '-'}</td>
                      <td className="py-2 px-3">{p.features?.amyloid_beta ?? '-'}</td>
                      <td className="py-2 px-3">{p.features?.tau_protein ?? '-'}</td>
                      <td className="py-2 px-3">{p.features?.dopamine_level ?? '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Patient Selection */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-white">Select Patient</h2>
          <div className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Search patients..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-white rounded-lg px-3 py-1.5 text-sm w-48"
            />
          </div>
        </div>
        {patientsSummary && patientsSummary.patients.length === 0 ? (
          <div className="text-center py-8 text-slate-400">
            <p>No patients found. Click "Add Patient" to create a new patient.</p>
          </div>
        ) : (
          <select
            value={selectedPatientId || ''}
            onChange={(e) => setSelectedPatientId(Number(e.target.value))}
            className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2"
          >
            <option value="">Select a patient...</option>
            {patientsSummary?.patients
              .filter((patient) => {
                if (!searchQuery) return true
                const query = searchQuery.toLowerCase()
                return (
                  patient.name.toLowerCase().includes(query) ||
                  patient.patient_id.toString().includes(query)
                )
              })
              .map((patient) => (
                <option key={patient.patient_id} value={patient.patient_id}>
                  {patient.name} - Alzheimer: {(patient.alzheimer_risk * 100).toFixed(1)}%, Parkinson:{' '}
                  {(patient.parkinson_risk * 100).toFixed(1)}%
                </option>
              ))}
          </select>
        )}
      </div>

      {/* Patient Details */}
      {selectedPatientId && !patientFeatures && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="text-center py-8">
            <p className="text-slate-400 mb-4">
              No medical data available for this patient yet.
            </p>
            <button
              onClick={() => setShowAddDataModal(true)}
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg transition-colors"
            >
              Add Medical Data
            </button>
          </div>
        </div>
      )}
      {patientFeatures && selectedPatientId && (
        <>
          {/* 3D Brain Visualization */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <h2 className="text-xl font-semibold text-white mb-4">
              3D Brain Visualization - Disease Impact Map
            </h2>
            <p className="text-sm text-slate-400 mb-4">
              Interactive 3D model showing brain regions affected by Alzheimer's and Parkinson's disease
            </p>
            <BrainVisualization3D
              alzheimerRisk={patientFeatures.latest_prediction?.alzheimer_risk || 0}
              parkinsonRisk={patientFeatures.latest_prediction?.parkinson_risk || 0}
              className="h-[600px] rounded-xl overflow-hidden border border-slate-800"
            />
          </div>

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

            {/* Sidebar with Alerts, Patient List, and Recent Activities */}
            <div className="space-y-6">
              {/* Active Alerts */}
              <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Active Alerts</h3>
                <div className="space-y-3 max-h-64 overflow-y-auto">
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

              {/* Patient List */}
              {patientsSummary && patientsSummary.patients.length > 0 && (
                <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">All Patients</h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {patientsSummary.patients
                      .filter((patient) => {
                        if (!searchQuery) return true
                        const query = searchQuery.toLowerCase()
                        return (
                          patient.name.toLowerCase().includes(query) ||
                          patient.patient_id.toString().includes(query)
                        )
                      })
                      .map((patient) => (
                        <button
                          key={patient.patient_id}
                          onClick={() => setSelectedPatientId(patient.patient_id)}
                          className={`w-full text-left rounded-lg border p-3 transition-colors ${
                            selectedPatientId === patient.patient_id
                              ? 'border-blue-500 bg-blue-900/20'
                              : 'border-slate-700 bg-slate-800/50 hover:bg-slate-800'
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <div className="text-sm font-medium text-white">{patient.name}</div>
                            <div className="flex gap-2">
                              <span
                                className={`text-xs px-2 py-1 rounded ${
                                  patient.alzheimer_risk > 0.66
                                    ? 'bg-rose-500/20 text-rose-400'
                                    : patient.alzheimer_risk > 0.33
                                    ? 'bg-amber-500/20 text-amber-400'
                                    : 'bg-emerald-500/20 text-emerald-400'
                                }`}
                              >
                                A: {(patient.alzheimer_risk * 100).toFixed(0)}%
                              </span>
                              <span
                                className={`text-xs px-2 py-1 rounded ${
                                  patient.parkinson_risk > 0.66
                                    ? 'bg-rose-500/20 text-rose-400'
                                    : patient.parkinson_risk > 0.33
                                    ? 'bg-amber-500/20 text-amber-400'
                                    : 'bg-emerald-500/20 text-emerald-400'
                                }`}
                              >
                                P: {(patient.parkinson_risk * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                        </button>
                      ))}
                    {searchQuery &&
                      patientsSummary.patients.filter((patient) => {
                        const query = searchQuery.toLowerCase()
                        return (
                          patient.name.toLowerCase().includes(query) ||
                          patient.patient_id.toString().includes(query)
                        )
                      }).length === 0 && (
                        <div className="text-center py-4 text-slate-400 text-sm">
                          No patients found matching "{searchQuery}"
                        </div>
                      )}
                  </div>
                </div>
              )}

              {/* Recent Activities */}
              {patientFeatures && (
                <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Recent Data</h3>
                  <div className="space-y-3 text-sm">
                    {patientFeatures.cognitive_features.length > 0 && (
                      <div className="text-slate-300">
                        <span className="text-slate-400">Last Cognitive Assessment:</span>{' '}
                        {new Date(
                          patientFeatures.cognitive_features[
                            patientFeatures.cognitive_features.length - 1
                          ].date
                        ).toLocaleDateString()}
                      </div>
                    )}
                    {patientFeatures.biomarker_features.length > 0 && (
                      <div className="text-slate-300">
                        <span className="text-slate-400">Last Biomarker Test:</span>{' '}
                        {new Date(
                          patientFeatures.biomarker_features[
                            patientFeatures.biomarker_features.length - 1
                          ].date
                        ).toLocaleDateString()}
                      </div>
                    )}
                    {patientFeatures.mri_features.length > 0 && (
                      <div className="text-slate-300">
                        <span className="text-slate-400">Last MRI Scan:</span>{' '}
                        {new Date(
                          patientFeatures.mri_features[patientFeatures.mri_features.length - 1]
                            .date
                        ).toLocaleDateString()}
                      </div>
                    )}
                    {patientFeatures.latest_prediction && (
                      <div className="text-slate-300">
                        <span className="text-slate-400">Last Prediction:</span>{' '}
                        {new Date(patientFeatures.latest_prediction.date || '').toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </div>
              )}
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

      {/* Add Patient Modal */}
      {showAddPatientModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Add New Patient</h2>
              <button
                onClick={() => setShowAddPatientModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            <AddPatientForm
              onSubmit={(data) => {
                createPatientMutation.mutate(data)
              }}
              onCancel={() => setShowAddPatientModal(false)}
              isLoading={createPatientMutation.isPending}
            />
          </div>
        </div>
      )}

      {/* Clear All Data Confirmation Modal */}
      {showClearDataConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-2xl border border-rose-700 p-6 w-full max-w-lg">
            <h2 className="text-2xl font-bold text-white mb-4 flex items-center gap-2">
              <ExclamationTriangleIcon className="h-7 w-7 text-rose-500" />
              Clear All Data?
            </h2>
            <div className="bg-rose-900/30 border border-rose-700/50 rounded-lg p-4 mb-4">
              <p className="text-rose-200 font-semibold mb-2">⚠️ WARNING: This action cannot be undone!</p>
              <p className="text-slate-300 text-sm">
                This will permanently delete:
              </p>
              <ul className="list-disc list-inside mt-2 space-y-1 text-sm text-slate-300">
                <li>All patients</li>
                <li>All medical records</li>
                <li>All predictions</li>
                <li>All disease tracking data</li>
              </ul>
            </div>
            <p className="text-slate-400 text-sm mb-6">
              After clearing, you can load fresh sample data without any conflicts.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowClearDataConfirm(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                disabled={clearAllDataMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={() => clearAllDataMutation.mutate()}
                disabled={clearAllDataMutation.isPending}
                className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                {clearAllDataMutation.isPending ? 'Clearing...' : 'Yes, Clear All Data'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Load Sample Data Confirmation Modal */}
      {showLoadSampleDataConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 w-full max-w-lg">
            <h2 className="text-2xl font-bold text-white mb-4">Load 200 Sample Patients?</h2>
            <p className="text-slate-300 mb-4">
              This will load exactly <strong>200 patients</strong> from CSV files with the following distribution:
            </p>
            <div className="bg-slate-900/60 rounded-lg p-4 mb-4">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between items-center">
                  <span className="text-emerald-400">✓ Normal/Healthy:</span>
                  <span className="font-bold text-white">120 patients</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-rose-400">✓ Alzheimer's Disease:</span>
                  <span className="font-bold text-white">40 patients</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-orange-400">✓ Parkinson's Disease:</span>
                  <span className="font-bold text-white">40 patients</span>
                </div>
                <div className="border-t border-slate-700 pt-2 mt-2">
                  <div className="flex justify-between items-center text-slate-400">
                    <span>Data Source:</span>
                    <span className="text-slate-300">100 Synthetic + 100 Real</span>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-amber-900/30 border border-amber-700/50 rounded-lg p-3 mb-4">
              <p className="text-amber-200 text-xs">
                <strong>⚠️ Important:</strong> If you already have patients in the database, they will be skipped. To load fresh data, please use "Clear All Data" first.
              </p>
            </div>
            <p className="text-xs text-slate-400 mb-6">
              <strong>Note:</strong> This includes all features and detailed information (cognitive scores, biomarkers, MRI data, etc.) for comprehensive analysis and 3D brain visualization.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowLoadSampleDataConfirm(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                disabled={loadSampleDatasetsMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={() => loadSampleDatasetsMutation.mutate()}
                disabled={loadSampleDatasetsMutation.isPending}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                {loadSampleDatasetsMutation.isPending ? 'Loading 200 Patients...' : 'Load Sample Data (200)'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Load All Data Confirmation Modal */}
      {showLoadDataConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 w-full max-w-lg">
            <h2 className="text-2xl font-bold text-white mb-4">Load All Datasets?</h2>
            <p className="text-slate-300 mb-6">
              This will load all synthetic and real data from CSV files into the disease tracking system.
              <br /><br />
              <strong>Note:</strong> This may take a few minutes and will create ~200 patients with their medical records and predictions.
            </p>
            <div className="flex justify-end gap-3">
              <button
                onClick={() => setShowLoadDataConfirm(false)}
                className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
                disabled={loadAllDatasetsMutation.isPending}
              >
                Cancel
              </button>
              <button
                onClick={() => loadAllDatasetsMutation.mutate()}
                disabled={loadAllDatasetsMutation.isPending}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                {loadAllDatasetsMutation.isPending ? 'Loading...' : 'Load All Data'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Medical Data Modal */}
      {showAddDataModal && selectedPatientId && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-slate-800 rounded-2xl border border-slate-700 p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Add Medical Data</h2>
              <button
                onClick={() => setShowAddDataModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>
            <AddMedicalDataForm
              patientId={selectedPatientId}
              onSubmit={(data) => {
                createMedicalRecordMutation.mutate({ patientId: selectedPatientId, recordData: data })
              }}
              onCancel={() => setShowAddDataModal(false)}
              isLoading={createMedicalRecordMutation.isPending}
            />
          </div>
        </div>
      )}
    </div>
  )
}

// Add Patient Form Component
function AddPatientForm({
  onSubmit,
  onCancel,
  isLoading,
}: {
  onSubmit: (data: any) => void
  onCancel: () => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    patient_id: '',
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: 'male' as 'male' | 'female' | 'other',
    email: '',
    phone: '',
    address: '',
    education_years: '',
    medical_history: '',
    family_history: '',
    current_medications: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      ...formData,
      education_years: formData.education_years ? parseInt(formData.education_years) : undefined,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Patient ID *</label>
          <input
            type="text"
            required
            value={formData.patient_id}
            onChange={(e) => setFormData({ ...formData, patient_id: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Date of Birth *</label>
          <input
            type="date"
            required
            value={formData.date_of_birth}
            onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">First Name *</label>
          <input
            type="text"
            required
            value={formData.first_name}
            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Last Name *</label>
          <input
            type="text"
            required
            value={formData.last_name}
            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Gender *</label>
          <select
            required
            value={formData.gender}
            onChange={(e) =>
              setFormData({ ...formData, gender: e.target.value as 'male' | 'female' | 'other' })
            }
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          >
            <option value="male">Male</option>
            <option value="female">Female</option>
            <option value="other">Other</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Email</label>
          <input
            type="email"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Phone</label>
          <input
            type="tel"
            value={formData.phone}
            onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Education Years</label>
          <input
            type="number"
            value={formData.education_years}
            onChange={(e) => setFormData({ ...formData, education_years: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          />
        </div>
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-1">Address</label>
        <textarea
          value={formData.address}
          onChange={(e) => setFormData({ ...formData, address: e.target.value })}
          className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          rows={2}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-1">Medical History</label>
        <textarea
          value={formData.medical_history}
          onChange={(e) => setFormData({ ...formData, medical_history: e.target.value })}
          className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          rows={3}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-1">Family History</label>
        <textarea
          value={formData.family_history}
          onChange={(e) => setFormData({ ...formData, family_history: e.target.value })}
          className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          rows={3}
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-slate-300 mb-1">Current Medications</label>
        <textarea
          value={formData.current_medications}
          onChange={(e) => setFormData({ ...formData, current_medications: e.target.value })}
          className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          rows={2}
        />
      </div>
      <div className="flex justify-end gap-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Creating...' : 'Create Patient'}
        </button>
      </div>
    </form>
  )
}

// Add Medical Data Form Component
function AddMedicalDataForm({
  patientId,
  onSubmit,
  onCancel,
  isLoading,
}: {
  patientId: number
  onSubmit: (data: any) => void
  onCancel: () => void
  isLoading: boolean
}) {
  const [formData, setFormData] = useState({
    visit_date: new Date().toISOString().split('T')[0],
    visit_type: 'Follow-up',
    mmse_score: '',
    moca_score: '',
    memory_score: '',
    attention_score: '',
    executive_function_score: '',
    amyloid_beta: '',
    tau_protein: '',
    dopamine_level: '',
    apoe_e4_status: false,
    hippocampal_volume: '',
    cortical_thickness: '',
    ventricular_volume: '',
    white_matter_hyperintensities: '',
    brain_volume_total: '',
    blood_pressure_systolic: '',
    blood_pressure_diastolic: '',
    temperature: '',
    heart_rate: '',
    respiratory_rate: '',
    oxygen_saturation: '',
    weight: '',
    height: '',
    bmi: '',
    blood_glucose: '',
    cholesterol_total: '',
    symptoms: '',
    clinical_notes: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const data: any = {
      visit_date: new Date(formData.visit_date).toISOString(),
      visit_type: formData.visit_type,
    }
    
    // Only include fields that have values
    if (formData.mmse_score) data.mmse_score = parseFloat(formData.mmse_score)
    if (formData.moca_score) data.moca_score = parseFloat(formData.moca_score)
    if (formData.memory_score) data.memory_score = parseFloat(formData.memory_score)
    if (formData.attention_score) data.attention_score = parseFloat(formData.attention_score)
    if (formData.executive_function_score)
      data.executive_function_score = parseFloat(formData.executive_function_score)
    if (formData.amyloid_beta) data.amyloid_beta = parseFloat(formData.amyloid_beta)
    if (formData.tau_protein) data.tau_protein = parseFloat(formData.tau_protein)
    if (formData.dopamine_level) data.dopamine_level = parseFloat(formData.dopamine_level)
    data.apoe_e4_status = formData.apoe_e4_status
    if (formData.hippocampal_volume) data.hippocampal_volume = parseFloat(formData.hippocampal_volume)
    if (formData.cortical_thickness) data.cortical_thickness = parseFloat(formData.cortical_thickness)
    if (formData.ventricular_volume) data.ventricular_volume = parseFloat(formData.ventricular_volume)
    if (formData.white_matter_hyperintensities)
      data.white_matter_hyperintensities = parseFloat(formData.white_matter_hyperintensities)
    if (formData.brain_volume_total) data.brain_volume_total = parseFloat(formData.brain_volume_total)
    if (formData.blood_pressure_systolic) data.blood_pressure_systolic = parseFloat(formData.blood_pressure_systolic)
    if (formData.blood_pressure_diastolic) data.blood_pressure_diastolic = parseFloat(formData.blood_pressure_diastolic)
    if (formData.temperature) data.temperature = parseFloat(formData.temperature)
    if (formData.heart_rate) data.heart_rate = parseFloat(formData.heart_rate)
    if (formData.respiratory_rate) data.respiratory_rate = parseFloat(formData.respiratory_rate)
    if (formData.oxygen_saturation) data.oxygen_saturation = parseFloat(formData.oxygen_saturation)
    if (formData.weight) data.weight = parseFloat(formData.weight)
    if (formData.height) data.height = parseFloat(formData.height)
    if (formData.bmi) data.bmi = parseFloat(formData.bmi)
    if (formData.blood_glucose) data.blood_glucose = parseFloat(formData.blood_glucose)
    if (formData.cholesterol_total) data.cholesterol_total = parseFloat(formData.cholesterol_total)
    if (formData.symptoms) data.symptoms = formData.symptoms
    if (formData.clinical_notes) data.clinical_notes = formData.clinical_notes

    onSubmit(data)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Visit Date *</label>
          <input
            type="date"
            required
            value={formData.visit_date}
            onChange={(e) => setFormData({ ...formData, visit_date: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Visit Type</label>
          <select
            value={formData.visit_type}
            onChange={(e) => setFormData({ ...formData, visit_type: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
          >
            <option value="Initial">Initial</option>
            <option value="Follow-up">Follow-up</option>
            <option value="Emergency">Emergency</option>
          </select>
        </div>
      </div>

      <div className="border-t border-slate-700 pt-4">
        <h3 className="text-lg font-semibold text-white mb-3">علائم حیاتی و شرایط بالینی</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">فشار خون سیستولیک (mmHg)</label>
            <input
              type="number"
              value={formData.blood_pressure_systolic}
              onChange={(e) => setFormData({ ...formData, blood_pressure_systolic: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
              placeholder="120"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">فشار خون دیاستولیک (mmHg)</label>
            <input
              type="number"
              value={formData.blood_pressure_diastolic}
              onChange={(e) => setFormData({ ...formData, blood_pressure_diastolic: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
              placeholder="80"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">درجه حرارت (°C)</label>
            <input
              type="number"
              step="0.1"
              value={formData.temperature}
              onChange={(e) => setFormData({ ...formData, temperature: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
              placeholder="36.6"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">ضربان قلب (bpm)</label>
            <input
              type="number"
              value={formData.heart_rate}
              onChange={(e) => setFormData({ ...formData, heart_rate: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
              placeholder="72"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">نرخ تنفس (breaths/min)</label>
            <input
              type="number"
              value={formData.respiratory_rate}
              onChange={(e) => setFormData({ ...formData, respiratory_rate: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
              placeholder="16"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">اشباع اکسیژن SpO2 (%)</label>
            <input
              type="number"
              min="0"
              max="100"
              value={formData.oxygen_saturation}
              onChange={(e) => setFormData({ ...formData, oxygen_saturation: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
              placeholder="98"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">وزن (kg)</label>
            <input
              type="number"
              step="0.1"
              value={formData.weight}
              onChange={(e) => setFormData({ ...formData, weight: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">قد (cm)</label>
            <input
              type="number"
              value={formData.height}
              onChange={(e) => setFormData({ ...formData, height: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">شاخص توده بدنی BMI (kg/m²)</label>
            <input
              type="number"
              step="0.1"
              value={formData.bmi}
              onChange={(e) => setFormData({ ...formData, bmi: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">قند خون ناشتا (mg/dL)</label>
            <input
              type="number"
              value={formData.blood_glucose}
              onChange={(e) => setFormData({ ...formData, blood_glucose: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">کلسترول کل (mg/dL)</label>
            <input
              type="number"
              value={formData.cholesterol_total}
              onChange={(e) => setFormData({ ...formData, cholesterol_total: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
        </div>
      </div>

      <div className="border-t border-slate-700 pt-4">
        <h3 className="text-lg font-semibold text-white mb-3">Cognitive Scores</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">MMSE Score (0-30)</label>
            <input
              type="number"
              min="0"
              max="30"
              value={formData.mmse_score}
              onChange={(e) => setFormData({ ...formData, mmse_score: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">MoCA Score (0-30)</label>
            <input
              type="number"
              min="0"
              max="30"
              value={formData.moca_score}
              onChange={(e) => setFormData({ ...formData, moca_score: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Memory Score (0-100)</label>
            <input
              type="number"
              min="0"
              max="100"
              value={formData.memory_score}
              onChange={(e) => setFormData({ ...formData, memory_score: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Attention Score (0-100)</label>
            <input
              type="number"
              min="0"
              max="100"
              value={formData.attention_score}
              onChange={(e) => setFormData({ ...formData, attention_score: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Executive Function Score (0-100)
            </label>
            <input
              type="number"
              min="0"
              max="100"
              value={formData.executive_function_score}
              onChange={(e) => setFormData({ ...formData, executive_function_score: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
        </div>
      </div>

      <div className="border-t border-slate-700 pt-4">
        <h3 className="text-lg font-semibold text-white mb-3">Biomarkers</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Amyloid-Beta (pg/mL)
            </label>
            <input
              type="number"
              value={formData.amyloid_beta}
              onChange={(e) => setFormData({ ...formData, amyloid_beta: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">Tau Protein (pg/mL)</label>
            <input
              type="number"
              value={formData.tau_protein}
              onChange={(e) => setFormData({ ...formData, tau_protein: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Dopamine Level (ng/mL)
            </label>
            <input
              type="number"
              value={formData.dopamine_level}
              onChange={(e) => setFormData({ ...formData, dopamine_level: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">APOE ε4 Status</label>
            <div className="flex items-center gap-2 mt-2">
              <input
                type="checkbox"
                checked={formData.apoe_e4_status}
                onChange={(e) => setFormData({ ...formData, apoe_e4_status: e.target.checked })}
                className="w-4 h-4"
              />
              <span className="text-slate-300">Positive</span>
            </div>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-700 pt-4">
        <h3 className="text-lg font-semibold text-white mb-3">MRI Features</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Hippocampal Volume (mm³)
            </label>
            <input
              type="number"
              value={formData.hippocampal_volume}
              onChange={(e) => setFormData({ ...formData, hippocampal_volume: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Cortical Thickness (mm)
            </label>
            <input
              type="number"
              step="0.1"
              value={formData.cortical_thickness}
              onChange={(e) => setFormData({ ...formData, cortical_thickness: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Ventricular Volume (mm³)
            </label>
            <input
              type="number"
              value={formData.ventricular_volume}
              onChange={(e) => setFormData({ ...formData, ventricular_volume: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              White Matter Hyperintensities
            </label>
            <input
              type="number"
              step="0.1"
              value={formData.white_matter_hyperintensities}
              onChange={(e) =>
                setFormData({ ...formData, white_matter_hyperintensities: e.target.value })
              }
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-1">
              Total Brain Volume (mm³)
            </label>
            <input
              type="number"
              value={formData.brain_volume_total}
              onChange={(e) => setFormData({ ...formData, brain_volume_total: e.target.value })}
              className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            />
          </div>
        </div>
      </div>

      <div className="border-t border-slate-700 pt-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1">Symptoms</label>
          <textarea
            value={formData.symptoms}
            onChange={(e) => setFormData({ ...formData, symptoms: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            rows={3}
          />
        </div>
        <div className="mt-4">
          <label className="block text-sm font-medium text-slate-300 mb-1">Clinical Notes</label>
          <textarea
            value={formData.clinical_notes}
            onChange={(e) => setFormData({ ...formData, clinical_notes: e.target.value })}
            className="w-full bg-slate-700 border border-slate-600 text-white rounded-lg px-3 py-2"
            rows={4}
          />
        </div>
      </div>

      <div className="flex justify-end gap-3 pt-4">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors"
        >
          Cancel
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Saving...' : 'Save Medical Data'}
        </button>
      </div>
    </form>
  )
}

