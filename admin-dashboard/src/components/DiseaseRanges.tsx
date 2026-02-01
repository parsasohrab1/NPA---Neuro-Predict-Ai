import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { diseaseApi } from '../services/api';

const RISK_LEVEL_LABELS: Record<string, { label: string; color: string }> = {
  low: { label: 'Healthy', color: 'emerald' },
  medium: { label: 'At Risk', color: 'amber' },
  high: { label: 'High Risk / Disease', color: 'rose' },
};

export default function DiseaseRanges() {
  const { data: rangesData } = useQuery({
    queryKey: ['disease-feature-ranges'],
    queryFn: () => diseaseApi.getFeatureRanges().then((res) => res.data),
  });

  const { data: summaryData, isLoading, error } = useQuery({
    queryKey: ['disease-patients-summary'],
    queryFn: () => diseaseApi.getPatientsSummary().then((res) => res.data),
  });

  const riskRanges = rangesData?.risk_score_ranges;
  const biomarkerRanges = rangesData?.biomarker_ranges;
  const patients = summaryData?.patients || [];
  const totalPatients = summaryData?.total_patients ?? 0;
  const highRiskAlzheimer = summaryData?.high_risk_alzheimer ?? 0;
  const highRiskParkinson = summaryData?.high_risk_parkinson ?? 0;
  const mediumRiskAlzheimer = summaryData?.medium_risk_alzheimer ?? 0;
  const mediumRiskParkinson = summaryData?.medium_risk_parkinson ?? 0;
  const lowRisk = summaryData?.low_risk ?? 0;

  const biomarkerDisplay: { key: string; label: string; unit?: string }[] = [
    { key: 'mmse_score', label: 'MMSE (Cognitive)', unit: '' },
    { key: 'moca_score', label: 'MoCA (Cognitive)', unit: '' },
    { key: 'dopamine_level', label: 'Dopamine (Parkinson)', unit: 'ng/mL' },
    { key: 'tau_protein', label: 'Tau (Alzheimer)', unit: 'pg/mL' },
    { key: 'amyloid_beta', label: 'Amyloid Beta (Alzheimer)', unit: 'pg/mL' },
    { key: 'hippocampal_volume', label: 'Hippocampal Volume (Alzheimer)', unit: 'mm³' },
  ];

  return (
    <div className="space-y-6 max-w-5xl">
      <section className="card">
        <h2 className="section-title">Risk Score Ranges — Alzheimer and Parkinson</h2>
        <p className="text-sm text-slate-400 mb-6">
          Risk score classification (0–1) for healthy, at-risk and high-risk/disease ranges.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {riskRanges?.alzheimer && (
            <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
              <h3 className="text-base font-semibold text-slate-200 mb-3">Alzheimer</h3>
              <div className="space-y-2">
                {['low', 'medium', 'high'].map((level) => {
                  const r = riskRanges.alzheimer[level];
                  if (!r) return null;
                  return (
                    <div
                      key={level}
                      className={`flex items-center justify-between rounded-lg px-3 py-2 border ${
                        level === 'low'
                          ? 'bg-emerald-900/30 border-emerald-600/50 text-emerald-300'
                          : level === 'medium'
                          ? 'bg-amber-900/30 border-amber-600/50 text-amber-300'
                          : 'bg-rose-900/30 border-rose-600/50 text-rose-300'
                      }`}
                    >
                      <span className="font-medium">{(r as any).label_en || r.label}</span>
                      <span className="text-sm">{r.min} – {r.max}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
          {riskRanges?.parkinson && (
            <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-4">
              <h3 className="text-base font-semibold text-slate-200 mb-3">Parkinson</h3>
              <div className="space-y-2">
                {['low', 'medium', 'high'].map((level) => {
                  const r = riskRanges.parkinson[level];
                  if (!r) return null;
                  return (
                    <div
                      key={level}
                      className={`flex items-center justify-between rounded-lg px-3 py-2 border ${
                        level === 'low'
                          ? 'bg-emerald-900/30 border-emerald-600/50 text-emerald-300'
                          : level === 'medium'
                          ? 'bg-amber-900/30 border-amber-600/50 text-amber-300'
                          : 'bg-rose-900/30 border-rose-600/50 text-rose-300'
                      }`}
                    >
                      <span className="font-medium">{(r as any).label_en || r.label}</span>
                      <span className="text-sm">{r.min} – {r.max}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </section>

      {biomarkerRanges && (
        <section className="card">
          <h3 className="section-title">Biomarker Ranges (Normal / Warning / Critical)</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 font-medium text-slate-300">Feature</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-300">Normal</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-300">Warning</th>
                  <th className="text-left py-3 px-4 font-medium text-slate-300">Critical</th>
                </tr>
              </thead>
              <tbody>
                {biomarkerDisplay
                  .filter((b) => biomarkerRanges[b.key])
                  .map((b) => {
                    const ranges = biomarkerRanges[b.key];
                    const normal = Array.isArray(ranges.normal) ? ranges.normal : (ranges.normal as [number, number]);
                    const warning = Array.isArray(ranges.warning) ? ranges.warning : (ranges.warning as [number, number]);
                    const critical = Array.isArray(ranges.critical) ? ranges.critical : (ranges.critical as [number, number]);
                    return (
                      <tr key={b.key} className="border-b border-slate-700/50">
                        <td className="py-3 px-4 font-medium text-slate-200">{b.label}</td>
                        <td className="py-3 px-4 text-emerald-400">
                          {normal[0]} – {normal[1]}
                          {b.unit && ` ${b.unit}`}
                        </td>
                        <td className="py-3 px-4 text-amber-400">
                          {warning[0]} – {warning[1]}
                          {b.unit && ` ${b.unit}`}
                        </td>
                        <td className="py-3 px-4 text-rose-400">
                          {critical[0]} – {critical[1]}
                          {b.unit && ` ${b.unit}`}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </section>
      )}

      <section className="card">
        <h2 className="section-title">Patient Classification</h2>
        {isLoading && <p className="text-slate-400 text-sm">Loading...</p>}
        {error && <p className="text-rose-400 text-sm">Error loading data.</p>}
        {!isLoading && !error && (
          <>
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
              <div className="rounded-xl border border-slate-700 bg-slate-800/50 p-4 text-center">
                <p className="text-xs font-medium text-slate-500 uppercase">Total</p>
                <p className="text-xl font-bold text-slate-100 mt-1">{totalPatients}</p>
              </div>
              <div className="rounded-xl border border-rose-600/50 bg-rose-900/30 p-4 text-center">
                <p className="text-xs font-medium text-rose-300 uppercase">High Risk Alzheimer</p>
                <p className="text-xl font-bold text-rose-400 mt-1">{highRiskAlzheimer}</p>
              </div>
              <div className="rounded-xl border border-rose-600/50 bg-rose-900/30 p-4 text-center">
                <p className="text-xs font-medium text-rose-300 uppercase">High Risk Parkinson</p>
                <p className="text-xl font-bold text-rose-400 mt-1">{highRiskParkinson}</p>
              </div>
              <div className="rounded-xl border border-amber-600/50 bg-amber-900/30 p-4 text-center">
                <p className="text-xs font-medium text-amber-400/80 uppercase">At Risk Alzheimer</p>
                <p className="text-xl font-bold text-amber-400 mt-1">{mediumRiskAlzheimer}</p>
              </div>
              <div className="rounded-xl border border-amber-600/50 bg-amber-900/30 p-4 text-center">
                <p className="text-xs font-medium text-amber-400/80 uppercase">At Risk Parkinson</p>
                <p className="text-xl font-bold text-amber-400 mt-1">{mediumRiskParkinson}</p>
              </div>
              <div className="rounded-xl border border-emerald-600/50 bg-emerald-900/30 p-4 text-center">
                <p className="text-xs font-medium text-emerald-300 uppercase">Healthy</p>
                <p className="text-xl font-bold text-emerald-400 mt-1">{lowRisk}</p>
              </div>
            </div>

            <h3 className="text-sm font-semibold text-slate-300 mb-3">Patient List</h3>
            <div className="rounded-xl border border-slate-700 overflow-hidden">
              <div className="max-h-96 overflow-y-auto">
                <table className="w-full text-sm">
                  <thead className="bg-slate-800 sticky top-0">
                    <tr>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">ID</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Name</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Alzheimer Risk</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Alzheimer Level</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Parkinson Risk</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Parkinson Level</th>
                      <th className="text-left py-3 px-4 font-medium text-slate-300">Last Prediction</th>
                    </tr>
                  </thead>
                  <tbody>
                    {patients.map((p: any) => (
                      <tr key={p.patient_id} className="border-t border-slate-700/50 hover:bg-slate-800/50">
                        <td className="py-3 px-4 font-mono text-slate-400">{p.patient_id}</td>
                        <td className="py-3 px-4 font-medium text-slate-200">{p.name}</td>
                        <td className="py-3 px-4 text-slate-300">{(p.alzheimer_risk ?? 0).toFixed(2)}</td>
                        <td className="py-3 px-4">
                          <span
                            className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                              p.alzheimer_level === 'high'
                                ? 'bg-rose-900/50 text-rose-400'
                                : p.alzheimer_level === 'medium'
                                ? 'bg-amber-900/50 text-amber-400'
                                : 'bg-emerald-900/50 text-emerald-400'
                            }`}
                          >
                            {RISK_LEVEL_LABELS[p.alzheimer_level]?.label ?? p.alzheimer_level}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-300">{(p.parkinson_risk ?? 0).toFixed(2)}</td>
                        <td className="py-3 px-4">
                          <span
                            className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                              p.parkinson_level === 'high'
                                ? 'bg-rose-900/50 text-rose-400'
                                : p.parkinson_level === 'medium'
                                ? 'bg-amber-900/50 text-amber-400'
                                : 'bg-emerald-900/50 text-emerald-400'
                            }`}
                          >
                            {RISK_LEVEL_LABELS[p.parkinson_level]?.label ?? p.parkinson_level}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-slate-500 text-xs">
                          {p.last_prediction_date
                            ? new Date(p.last_prediction_date).toLocaleDateString()
                            : '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
