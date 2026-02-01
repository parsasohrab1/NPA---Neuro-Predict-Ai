import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import diseaseTrackingApi from '../services/diseaseTracking'
import {
  ChevronDownIcon,
  ChevronRightIcon,
  HeartIcon,
  BeakerIcon,
  CpuChipIcon,
  UserCircleIcon,
} from '@heroicons/react/24/outline'

function MetricCard({
  label,
  value,
  unit,
  status,
  subtitle,
}: {
  label: string
  value: number | string
  unit?: string
  status?: 'normal' | 'warning' | 'critical'
  subtitle?: string
}) {
  const statusBg =
    status === 'critical'
      ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
      : status === 'warning'
      ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
      : 'bg-slate-800/50 border-slate-700/50 text-slate-200'

  return (
    <div
      className={`rounded-lg border p-3 ${statusBg}`}
      title={subtitle}
    >
      <div className="text-xs text-slate-400 truncate">{label}</div>
      <div className="text-lg font-semibold mt-0.5">
        {typeof value === 'number' ? value.toFixed(1) : value}
        {unit && <span className="text-sm font-normal text-slate-400 ml-1">{unit}</span>}
      </div>
    </div>
  )
}

function CollapsibleSection({
  title,
  icon: Icon,
  open: defaultOpen,
  children,
}: {
  title: string
  icon: React.ComponentType<{ className?: string }>
  open?: boolean
  children: React.ReactNode
}) {
  const [open, setOpen] = useState(defaultOpen ?? false)

  return (
    <div className="rounded-xl border border-slate-700/60 bg-slate-900/40 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-3 text-left hover:bg-slate-800/40 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Icon className="h-5 w-5 text-slate-400" />
          <span className="font-medium text-slate-200">{title}</span>
        </div>
        {open ? (
          <ChevronDownIcon className="h-5 w-5 text-slate-400" />
        ) : (
          <ChevronRightIcon className="h-5 w-5 text-slate-400" />
        )}
      </button>
      {open && <div className="px-4 pb-4 pt-1 border-t border-slate-700/40">{children}</div>}
    </div>
  )
}

export default function GaugeDisplayTab() {
  const [selectedPatientId, setSelectedPatientId] = useState<string>('')
  const { data: summary, isError, error } = useQuery({
    queryKey: ['patients-summary'],
    queryFn: () => diseaseTrackingApi.getAllPatientsSummary(),
    retry: 1,
  })

  const patients = summary?.patients || []
  const pid = selectedPatientId ? parseInt(selectedPatientId, 10) : (patients[0]?.patient_id ?? null)
  const { data: features } = useQuery({
    queryKey: ['patient-features', pid],
    queryFn: () => diseaseTrackingApi.getPatientFeatures(pid!, 365),
    enabled: pid != null,
  })

  const samplePatient = selectedPatientId
    ? patients.find((p: any) => String(p.patient_id) === selectedPatientId) || patients[0]
    : patients[0]
  const alzRisk = (samplePatient?.alzheimer_risk ?? 0) * 100
  const parkRisk = (samplePatient?.parkinson_risk ?? 0) * 100

  const lv = features?.latest_values || {}
  const getStatus = (val: number, low: number, high: number): 'normal' | 'warning' | 'critical' => {
    if (val < low * 0.9 || val > high * 1.1) return 'critical'
    if (val < low || val > high) return 'warning'
    return 'normal'
  }

  if (isError) {
    return (
      <div className="rounded-xl border border-amber-500/50 bg-amber-500/10 p-6 max-w-xl">
        <p className="font-semibold text-amber-200">API Error</p>
        <p className="text-sm text-slate-300 mt-2">
          {(error as Error)?.message || 'Check backend (port 8001)'}
        </p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl space-y-5">
      {/* Patient selector */}
      <div className="flex items-center gap-3">
        <UserCircleIcon className="h-5 w-5 text-slate-500" />
        <select
          value={selectedPatientId}
          onChange={(e) => setSelectedPatientId(e.target.value)}
          className="bg-slate-800 border border-slate-600 text-slate-100 text-sm px-3 py-2 rounded-lg w-64 focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500"
        >
          <option value="">
            {patients.length === 0 ? 'No patients' : 'Select patient'}
          </option>
          {patients.slice(0, 50).map((p: any) => (
            <option key={p.patient_id} value={p.patient_id}>
              {p.name || `Patient #${p.patient_id}`}
            </option>
          ))}
        </select>
        {patients.length === 0 && (
          <span className="text-sm text-slate-500">Load sample data to get started</span>
        )}
      </div>

      {/* Primary metrics - Risk levels (always visible) */}
      <div>
        <h2 className="text-sm font-medium text-slate-400 mb-3">Risk Level</h2>
        <div className="grid grid-cols-2 gap-4">
          <div
            className={`rounded-xl border-2 p-5 ${
              alzRisk > 66
                ? 'border-rose-500/60 bg-rose-500/10'
                : alzRisk > 33
                ? 'border-amber-500/50 bg-amber-500/10'
                : 'border-emerald-500/40 bg-emerald-500/10'
            }`}
          >
            <div className="text-sm text-slate-400 mb-1">Alzheimer Risk</div>
            <div
              className={`text-3xl font-bold ${
                alzRisk > 66 ? 'text-rose-400' : alzRisk > 33 ? 'text-amber-400' : 'text-emerald-400'
              }`}
            >
              {alzRisk.toFixed(0)}%
            </div>
            <div className="text-xs text-slate-500 mt-1">
              {alzRisk > 66 ? 'High' : alzRisk > 33 ? 'Medium' : 'Normal'}
            </div>
          </div>
          <div
            className={`rounded-xl border-2 p-5 ${
              parkRisk > 66
                ? 'border-rose-500/60 bg-rose-500/10'
                : parkRisk > 33
                ? 'border-amber-500/50 bg-amber-500/10'
                : 'border-emerald-500/40 bg-emerald-500/10'
            }`}
          >
            <div className="text-sm text-slate-400 mb-1">Parkinson Risk</div>
            <div
              className={`text-3xl font-bold ${
                parkRisk > 66 ? 'text-rose-400' : parkRisk > 33 ? 'text-amber-400' : 'text-emerald-400'
              }`}
            >
              {parkRisk.toFixed(0)}%
            </div>
            <div className="text-xs text-slate-500 mt-1">
              {parkRisk > 66 ? 'High' : parkRisk > 33 ? 'Medium' : 'Normal'}
            </div>
          </div>
        </div>
      </div>

      {/* Collapsible sections */}
      <CollapsibleSection title="Vital Signs" icon={HeartIcon} defaultOpen>
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mt-2">
          <MetricCard
            label="Temperature"
            value={lv.temperature ?? 37}
            unit="°C"
            status={getStatus(lv.temperature ?? 37, 36, 37.5)}
          />
          <MetricCard
            label="Heart Rate"
            value={lv.heart_rate ?? 72}
            unit="bpm"
            status={getStatus(lv.heart_rate ?? 72, 60, 100)}
          />
          <MetricCard
            label="Blood Pressure"
            value={`${lv.blood_pressure_systolic ?? 120}/${lv.blood_pressure_diastolic ?? 80}`}
            unit="mmHg"
            status={getStatus(lv.blood_pressure_systolic ?? 120, 90, 140)}
          />
          <MetricCard
            label="Oxygen"
            value={lv.oxygen_saturation ?? 98}
            unit="%"
            status={getStatus(lv.oxygen_saturation ?? 98, 95, 100)}
          />
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Biomarkers" icon={BeakerIcon}>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mt-2">
          <MetricCard
            label="Amyloid-Beta"
            value={lv.amyloid_beta ?? 600}
            unit="pg/mL"
            status={getStatus(lv.amyloid_beta ?? 600, 400, 1000)}
          />
          <MetricCard
            label="Tau Protein"
            value={lv.tau_protein ?? 200}
            unit="pg/mL"
            status={getStatus(lv.tau_protein ?? 200, 40, 360)}
          />
          <MetricCard
            label="Dopamine"
            value={lv.dopamine_level ?? 100}
            unit="ng/mL"
            status={getStatus(lv.dopamine_level ?? 100, 80, 160)}
          />
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Cognitive & MRI" icon={CpuChipIcon}>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
          <MetricCard
            label="MMSE"
            value={lv.mmse_score ?? 28}
            status={getStatus(lv.mmse_score ?? 28, 24, 30)}
          />
          <MetricCard
            label="MoCA"
            value={lv.moca_score ?? 26}
            status={getStatus(lv.moca_score ?? 26, 22, 30)}
          />
          <MetricCard
            label="Memory"
            value={lv.memory_score ?? 85}
            unit="%"
            status={getStatus(lv.memory_score ?? 85, 60, 100)}
          />
          <MetricCard
            label="Hippocampal"
            value={((lv.hippocampal_volume ?? 3800) / 1000).toFixed(1)}
            unit="cm³"
            status={getStatus((lv.hippocampal_volume ?? 3800) / 1000, 3.4, 4.6)}
          />
        </div>
      </CollapsibleSection>
    </div>
  )
}
