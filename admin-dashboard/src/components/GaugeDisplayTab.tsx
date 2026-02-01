import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import diseaseTrackingApi from '../services/diseaseTracking'
import CircularGauge from './CircularGauge'
import VerticalBarGauge from './VerticalBarGauge'

export default function GaugeDisplayTab() {
  const [selectedPatientId, setSelectedPatientId] = useState<string>('')
  const { data: summary } = useQuery({
    queryKey: ['patients-summary'],
    queryFn: () => diseaseTrackingApi.getAllPatientsSummary(),
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
  const latestPred = samplePatient
    ? {
        alzheimer_risk: (samplePatient.alzheimer_risk ?? 0) * 100,
        parkinson_risk: (samplePatient.parkinson_risk ?? 0) * 100,
      }
    : null

  const lv = features?.latest_values || {}
  const getStatus = (val: number, low: number, high: number): 'normal' | 'warning' | 'critical' => {
    if (val < low * 0.9 || val > high * 1.1) return 'critical'
    if (val < low || val > high) return 'warning'
    return 'normal'
  }

  return (
    <div className="space-y-6">
      {/* Parameter selection (turbine-style) */}
      <div className="flex gap-4 mb-4 items-center">
        <div>
          <label className="text-xs text-slate-400 block mb-1">Patient</label>
          <select
            value={selectedPatientId}
            onChange={(e) => setSelectedPatientId(e.target.value)}
            className="bg-slate-800 border border-slate-600 text-white text-sm px-3 py-1.5 rounded focus:ring-1 focus:ring-lime-500"
          >
            <option value="">All (Sample)</option>
            {patients.slice(0, 20).map((p: any) => (
              <option key={p.patient_id} value={p.patient_id}>{p.name || `#${p.patient_id}`}</option>
            ))}
          </select>
        </div>
      </div>
      {/* Vital Signs — Turbine-style column layout */}
      <div>
        <h3 className="text-slate-300 text-xs font-semibold uppercase mb-3">Vital Signs (°C / bpm / mmHg)</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
          <CircularGauge label="Am Temp" value={lv.temperature ?? 37} min={35} max={40} unit="°C" status={getStatus(lv.temperature ?? 37, 36, 37.5)} />
          <CircularGauge label="In Temp" value={36.5} min={35} max={40} unit="°C" status="normal" />
          <CircularGauge label="Out Temp" value={36.8} min={35} max={40} unit="°C" status="normal" />
          <CircularGauge label="Heart Rate" value={lv.heart_rate ?? 72} min={50} max={120} unit="bpm" status={getStatus(lv.heart_rate ?? 72, 60, 100)} />
          <CircularGauge label="BP Systolic" value={lv.blood_pressure_systolic ?? 120} min={80} max={180} unit="mmHg" status={getStatus(lv.blood_pressure_systolic ?? 120, 90, 140)} />
          <CircularGauge label="BP Diastolic" value={lv.blood_pressure_diastolic ?? 80} min={50} max={120} unit="mmHg" status={getStatus(lv.blood_pressure_diastolic ?? 80, 60, 90)} />
        </div>
      </div>

      {/* Biomarkers — pg/mL / ng/mL */}
      <div>
        <h3 className="text-slate-300 text-xs font-semibold uppercase mb-3">Biomarkers (pg/mL / ng/mL)</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <CircularGauge label="Amyloid-Beta" value={lv.amyloid_beta ?? 600} min={100} max={1000} unit="pg/mL" status={getStatus(lv.amyloid_beta ?? 600, 400, 1000)} />
          <CircularGauge label="Tau Protein" value={lv.tau_protein ?? 200} min={40} max={900} unit="pg/mL" status={getStatus(lv.tau_protein ?? 200, 40, 360)} />
          <CircularGauge label="Dopamine" value={lv.dopamine_level ?? 100} min={0} max={160} unit="ng/mL" status={getStatus(lv.dopamine_level ?? 100, 80, 160)} />
          <CircularGauge label="Oxygen Sat" value={lv.oxygen_saturation ?? 98} min={85} max={100} unit="%" status={getStatus(lv.oxygen_saturation ?? 98, 95, 100)} />
        </div>
      </div>

      {/* Cognitive & Risk */}
      <div>
        <h3 className="text-slate-300 text-xs font-semibold uppercase mb-3">Cognitive & Risk (%)</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <CircularGauge label="MMSE" value={lv.mmse_score ?? 28} min={0} max={30} unit="" status={getStatus(lv.mmse_score ?? 28, 24, 30)} />
          <CircularGauge label="MoCA" value={lv.moca_score ?? 26} min={0} max={30} unit="" status={getStatus(lv.moca_score ?? 26, 22, 30)} />
          {latestPred && (
            <>
              <CircularGauge
                label="Alzheimer Risk"
                value={latestPred.alzheimer_risk}
                min={0}
                max={100}
                unit="%"
                status={latestPred.alzheimer_risk > 66 ? 'critical' : latestPred.alzheimer_risk > 33 ? 'warning' : 'normal'}
              />
              <CircularGauge
                label="Parkinson Risk"
                value={latestPred.parkinson_risk}
                min={0}
                max={100}
                unit="%"
                status={latestPred.parkinson_risk > 66 ? 'critical' : latestPred.parkinson_risk > 33 ? 'warning' : 'normal'}
              />
            </>
          )}
        </div>
      </div>

      {/* Vertical bar section — TEMP / Viscosity style */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-slate-300 text-xs font-semibold uppercase mb-3">TEMP — Cognitive Scores</h3>
          <div className="flex gap-4 justify-around py-4 px-4 rounded bg-slate-900/50 border border-slate-700">
            <VerticalBarGauge label="Memory" value={lv.memory_score ?? 85} min={0} max={100} status={getStatus(lv.memory_score ?? 85, 60, 100)} />
            <VerticalBarGauge label="Attention" value={lv.attention_score ?? 78} min={0} max={100} status={getStatus(lv.attention_score ?? 78, 60, 100)} />
            <VerticalBarGauge label="Executive" value={lv.executive_function_score ?? 72} min={0} max={100} status={getStatus(lv.executive_function_score ?? 72, 60, 100)} />
            <VerticalBarGauge label="MMSE" value={lv.mmse_score ?? 28} min={0} max={30} status="normal" />
            <VerticalBarGauge label="MoCA" value={lv.moca_score ?? 26} min={0} max={30} status="normal" />
          </div>
        </div>
        <div>
          <h3 className="text-slate-300 text-xs font-semibold uppercase mb-3">MRI Features</h3>
          <div className="flex gap-4 justify-around py-4 px-4 rounded bg-slate-900/50 border border-slate-700">
            <VerticalBarGauge label="Hippocampal" value={(lv.hippocampal_volume ?? 3800) / 1000} min={1.5} max={4.6} status={getStatus((lv.hippocampal_volume ?? 3800) / 1000, 3.4, 4.6)} />
            <VerticalBarGauge label="Cortical" value={lv.cortical_thickness ?? 2.8} min={1.5} max={3.2} status="normal" />
            <VerticalBarGauge label="Brain Vol" value={(lv.brain_volume_total ?? 1200000) / 1000} min={800} max={1400} status="normal" />
            <VerticalBarGauge label="Ventricular" value={(lv.ventricular_volume ?? 35000) / 1000} min={20} max={70} status="normal" />
          </div>
        </div>
      </div>
    </div>
  )
}
