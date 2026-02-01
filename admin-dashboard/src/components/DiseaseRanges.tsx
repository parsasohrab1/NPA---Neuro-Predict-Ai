import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { diseaseApi } from '../services/api';

const RISK_LEVEL_LABELS: Record<string, { fa: string; en: string; color: string }> = {
  low: { fa: 'سلامت', en: 'Healthy', color: 'emerald' },
  medium: { fa: 'هشدار', en: 'At Risk', color: 'amber' },
  high: { fa: 'پرریسک/بیمار', en: 'High Risk / Disease', color: 'rose' },
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
    { key: 'mmse_score', label: 'MMSE (شناختی)', unit: '' },
    { key: 'moca_score', label: 'MoCA (شناختی)', unit: '' },
    { key: 'dopamine_level', label: 'دوپامین (پارکینسون)', unit: 'ng/mL' },
    { key: 'tau_protein', label: 'تاو (آلزایمر)', unit: 'pg/mL' },
    { key: 'amyloid_beta', label: 'آمیلوئید بتا (آلزایمر)', unit: 'pg/mL' },
    { key: 'hippocampal_volume', label: 'حجم هیپوکامپ (آلزایمر)', unit: 'mm³' },
  ];

  return (
    <div className="space-y-6">
      {/* Risk score ranges: Alzheimer & Parkinson */}
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">📋</span>
          <h2 className="text-lg font-semibold text-slate-800">
            محدوده امتیاز ریسک — آلزایمر و پارکینسون
          </h2>
        </div>
        <div className="p-6">
          <p className="text-sm text-slate-500 mb-4">
            تقسیم‌بندی امتیاز ریسک (۰ تا ۱) برای تعیین محدوده سلامت، هشدار و پرریسک/بیمار.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {riskRanges?.alzheimer && (
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <h3 className="text-base font-semibold text-slate-800 mb-3">
                  آلزایمر (Alzheimer)
                </h3>
                <div className="space-y-2">
                  {['low', 'medium', 'high'].map((level) => {
                    const r = riskRanges.alzheimer[level];
                    const labels = RISK_LEVEL_LABELS[level];
                    if (!r) return null;
                    return (
                      <div
                        key={level}
                        className={`flex items-center justify-between rounded-lg px-3 py-2 border ${
                          level === 'low'
                            ? 'bg-emerald-50 border-emerald-200'
                            : level === 'medium'
                            ? 'bg-amber-50 border-amber-200'
                            : 'bg-rose-50 border-rose-200'
                        }`}
                      >
                        <span className="font-medium text-slate-700">{r.label}</span>
                        <span className="text-sm text-slate-600">
                          {r.min} – {r.max}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            {riskRanges?.parkinson && (
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <h3 className="text-base font-semibold text-slate-800 mb-3">
                  پارکینسون (Parkinson)
                </h3>
                <div className="space-y-2">
                  {['low', 'medium', 'high'].map((level) => {
                    const r = riskRanges.parkinson[level];
                    if (!r) return null;
                    return (
                      <div
                        key={level}
                        className={`flex items-center justify-between rounded-lg px-3 py-2 border ${
                          level === 'low'
                            ? 'bg-emerald-50 border-emerald-200'
                            : level === 'medium'
                            ? 'bg-amber-50 border-amber-200'
                            : 'bg-rose-50 border-rose-200'
                        }`}
                      >
                        <span className="font-medium text-slate-700">{r.label}</span>
                        <span className="text-sm text-slate-600">
                          {r.min} – {r.max}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Biomarker ranges (healthy vs at-risk vs disease) */}
      {biomarkerRanges && (
        <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-100">
            <h3 className="text-base font-semibold text-slate-800">
              محدوده بیومارکرها (سلامت / هشدار / بحرانی)
            </h3>
          </div>
          <div className="p-6 overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200">
                  <th className="text-left py-2 px-3 font-medium text-slate-700">ویژگی</th>
                  <th className="text-left py-2 px-3 font-medium text-slate-700">سلامت (normal)</th>
                  <th className="text-left py-2 px-3 font-medium text-slate-700">هشدار (warning)</th>
                  <th className="text-left py-2 px-3 font-medium text-slate-700">بحرانی (critical)</th>
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
                      <tr key={b.key} className="border-b border-slate-100">
                        <td className="py-2 px-3 font-medium text-slate-700">{b.label}</td>
                        <td className="py-2 px-3 text-emerald-700">
                          {normal[0]} – {normal[1]}
                          {b.unit && ` ${b.unit}`}
                        </td>
                        <td className="py-2 px-3 text-amber-700">
                          {warning[0]} – {warning[1]}
                          {b.unit && ` ${b.unit}`}
                        </td>
                        <td className="py-2 px-3 text-rose-700">
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

      {/* Patient classification summary */}
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">👥</span>
          <h2 className="text-lg font-semibold text-slate-800">
            تقسیم‌بندی بیماران موجود در دیتابیس
          </h2>
        </div>
        <div className="p-6">
          {isLoading && (
            <p className="text-slate-500 text-sm">در حال بارگذاری...</p>
          )}
          {error && (
            <p className="text-rose-600 text-sm">خطا در دریافت داده‌ها.</p>
          )}
          {!isLoading && !error && (
            <>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-3 text-center">
                  <p className="text-xs font-medium text-slate-500 uppercase">کل بیماران</p>
                  <p className="text-xl font-bold text-slate-800 mt-1">{totalPatients}</p>
                </div>
                <div className="rounded-xl border border-rose-200 bg-rose-50/80 p-3 text-center">
                  <p className="text-xs font-medium text-slate-500 uppercase">پرریسک آلزایمر</p>
                  <p className="text-xl font-bold text-rose-600 mt-1">{highRiskAlzheimer}</p>
                </div>
                <div className="rounded-xl border border-rose-200 bg-rose-50/80 p-3 text-center">
                  <p className="text-xs font-medium text-slate-500 uppercase">پرریسک پارکینسون</p>
                  <p className="text-xl font-bold text-rose-600 mt-1">{highRiskParkinson}</p>
                </div>
                <div className="rounded-xl border border-amber-200 bg-amber-50/80 p-3 text-center">
                  <p className="text-xs font-medium text-slate-500 uppercase">هشدار آلزایمر</p>
                  <p className="text-xl font-bold text-amber-600 mt-1">{mediumRiskAlzheimer}</p>
                </div>
                <div className="rounded-xl border border-amber-200 bg-amber-50/80 p-3 text-center">
                  <p className="text-xs font-medium text-slate-500 uppercase">هشدار پارکینسون</p>
                  <p className="text-xl font-bold text-amber-600 mt-1">{mediumRiskParkinson}</p>
                </div>
                <div className="rounded-xl border border-emerald-200 bg-emerald-50/80 p-3 text-center">
                  <p className="text-xs font-medium text-slate-500 uppercase">سلامت (کم‌ریسک)</p>
                  <p className="text-xl font-bold text-emerald-600 mt-1">{lowRisk}</p>
                </div>
              </div>

              <h3 className="text-base font-semibold text-slate-800 mb-3">لیست بیماران و سطح ریسک</h3>
              <div className="rounded-xl border border-slate-200 overflow-hidden">
                <div className="max-h-96 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 sticky top-0">
                      <tr>
                        <th className="text-left py-3 px-4 font-medium text-slate-700">شناسه</th>
                        <th className="text-left py-3 px-4 font-medium text-slate-700">نام</th>
                        <th className="text-left py-3 px-4 font-medium text-slate-700">ریسک آلزایمر</th>
                        <th className="text-left py-3 px-4 font-medium text-slate-700">سطح آلزایمر</th>
                        <th className="text-left py-3 px-4 font-medium text-slate-700">ریسک پارکینسون</th>
                        <th className="text-left py-3 px-4 font-medium text-slate-700">سطح پارکینسون</th>
                        <th className="text-left py-3 px-4 font-medium text-slate-700">آخرین پیش‌بینی</th>
                      </tr>
                    </thead>
                    <tbody>
                      {patients.map((p: any) => (
                        <tr key={p.patient_id} className="border-t border-slate-100 hover:bg-slate-50/50">
                          <td className="py-2 px-4 font-mono text-slate-600">{p.patient_id}</td>
                          <td className="py-2 px-4 font-medium text-slate-800">{p.name}</td>
                          <td className="py-2 px-4">{(p.alzheimer_risk ?? 0).toFixed(2)}</td>
                          <td className="py-2 px-4">
                            <span
                              className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                                p.alzheimer_level === 'high'
                                  ? 'bg-rose-100 text-rose-800'
                                  : p.alzheimer_level === 'medium'
                                  ? 'bg-amber-100 text-amber-800'
                                  : 'bg-emerald-100 text-emerald-800'
                              }`}
                            >
                              {RISK_LEVEL_LABELS[p.alzheimer_level]?.fa ?? p.alzheimer_level}
                            </span>
                          </td>
                          <td className="py-2 px-4">{(p.parkinson_risk ?? 0).toFixed(2)}</td>
                          <td className="py-2 px-4">
                            <span
                              className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                                p.parkinson_level === 'high'
                                  ? 'bg-rose-100 text-rose-800'
                                  : p.parkinson_level === 'medium'
                                  ? 'bg-amber-100 text-amber-800'
                                  : 'bg-emerald-100 text-emerald-800'
                              }`}
                            >
                              {RISK_LEVEL_LABELS[p.parkinson_level]?.fa ?? p.parkinson_level}
                            </span>
                          </td>
                          <td className="py-2 px-4 text-slate-500 text-xs">
                            {p.last_prediction_date
                              ? new Date(p.last_prediction_date).toLocaleDateString('fa-IR')
                              : '—'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {patients.length === 0 && (
                  <div className="py-8 text-center text-slate-500 text-sm">
                    هیچ بیماری در دیتابیس یافت نشد.
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </section>
    </div>
  );
}
