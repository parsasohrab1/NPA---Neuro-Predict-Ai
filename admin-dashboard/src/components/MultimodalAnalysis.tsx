import React, { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { monitoringApi, diseaseApi } from '../services/api';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const MODALITY_LABELS: Record<string, string> = {
  MRI: 'تصویربرداری (MRI)',
  Biomarker: 'بیومارکر',
  Cognitive: 'شناختی',
};

const MODALITY_COLORS = ['#8b5cf6', '#06b6d4', '#10b981'];

export default function MultimodalAnalysis() {
  const hours = 24;

  const { data: multimodalData } = useQuery({
    queryKey: ['multimodal-summary', hours],
    queryFn: () => monitoringApi.getMultimodalSummary(hours).then((res) => res.data),
  });

  const { data: modelPerf } = useQuery({
    queryKey: ['model-performance', hours],
    queryFn: () => monitoringApi.getModelPerformance(undefined, hours).then((res) => res.data),
  });

  const { data: patientsSummary } = useQuery({
    queryKey: ['disease-patients-summary'],
    queryFn: () => diseaseApi.getPatientsSummary().then((res) => res.data),
  });

  const modalityPieData = useMemo(() => {
    const w = multimodalData?.modality_weights;
    if (!w) return [];
    return [
      { name: MODALITY_LABELS.MRI, value: Math.round((w.MRI ?? 0.33) * 100), key: 'MRI' },
      { name: MODALITY_LABELS.Biomarker, value: Math.round((w.Biomarker ?? 0.33) * 100), key: 'Biomarker' },
      { name: MODALITY_LABELS.Cognitive, value: Math.round((w.Cognitive ?? 0.34) * 100), key: 'Cognitive' },
    ].filter((d) => d.value > 0);
  }, [multimodalData?.modality_weights]);

  const accuracyBarData = useMemo(() => {
    const acc = multimodalData?.accuracy;
    const list = [];
    if (acc?.alzheimer_confidence_pct != null)
      list.push({ disease: 'آلزایمر', دقت: acc.alzheimer_confidence_pct });
    if (acc?.parkinson_confidence_pct != null)
      list.push({ disease: 'پارکینسون', دقت: acc.parkinson_confidence_pct });
    return list;
  }, [multimodalData?.accuracy]);

  const totalPatients = patientsSummary?.total_patients ?? 0;
  const avgAlzRisk =
    totalPatients > 0 && patientsSummary?.patients?.length
      ? (patientsSummary.patients.reduce((s: number, p: any) => s + (p.alzheimer_risk ?? 0), 0) / totalPatients) * 100
      : null;
  const avgParkRisk =
    totalPatients > 0 && patientsSummary?.patients?.length
      ? (patientsSummary.patients.reduce((s: number, p: any) => s + (p.parkinson_risk ?? 0), 0) / totalPatients) * 100
      : null;

  const alzConfPct = multimodalData?.accuracy?.alzheimer_confidence_pct;
  const parkConfPct = multimodalData?.accuracy?.parkinson_confidence_pct;
  const totalPredictions = multimodalData?.total_predictions ?? 0;

  return (
    <div className="space-y-6">
      {/* معرفی و هدف */}
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">🔬</span>
          <h2 className="text-lg font-semibold text-slate-800">آنالیز داده‌های مولتی‌مودال</h2>
        </div>
        <div className="p-6">
          <p className="text-slate-600 text-sm leading-relaxed">
            این بخش با ترکیب <strong>داده‌های مولتی‌مودال</strong> (تصویربرداری MRI، بیومارکر، شناختی) به پزشک در
            <strong> تصمیم‌گیری پیش‌بینی</strong> و <strong>درصد احتمال ابتلا</strong> به بیماری‌های آلزایمر و پارکینسون
            کمک می‌کند. <strong>درصد دقت و اطمینان مدل</strong> در هر بیماری و سهم هر مودالیتی در پیش‌بینی در زیر
            نمایش داده می‌شود.
          </p>
        </div>
      </section>

      {/* کارت‌های دقت و احتمال */}
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100">
          <h3 className="text-base font-semibold text-slate-800">دقت مدل و احتمال ابتلا</h3>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="rounded-xl border border-violet-200 bg-gradient-to-br from-violet-50 to-white p-4 text-center">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">دقت/اطمینان مدل — آلزایمر</p>
              <p className="text-2xl font-bold text-violet-600 mt-1">
                {alzConfPct != null ? `${alzConfPct}%` : '—'}
              </p>
              <p className="text-xs text-slate-500 mt-1">میانگین اطمینان پیش‌بینی</p>
            </div>
            <div className="rounded-xl border border-rose-200 bg-gradient-to-br from-rose-50 to-white p-4 text-center">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">دقت/اطمینان مدل — پارکینسون</p>
              <p className="text-2xl font-bold text-rose-600 mt-1">
                {parkConfPct != null ? `${parkConfPct}%` : '—'}
              </p>
              <p className="text-xs text-slate-500 mt-1">میانگین اطمینان پیش‌بینی</p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4 text-center">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">تعداد پیش‌بینی‌ها (۲۴h)</p>
              <p className="text-2xl font-bold text-slate-700 mt-1">{totalPredictions}</p>
            </div>
            <div className="rounded-xl border border-indigo-200 bg-indigo-50/50 p-4 text-center">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">میانگین احتمال ابتلا</p>
              <p className="text-lg font-bold text-indigo-600 mt-1">
                آلزایمر: {avgAlzRisk != null ? `${avgAlzRisk.toFixed(1)}%` : '—'}
              </p>
              <p className="text-lg font-bold text-indigo-600">پارکینسون: {avgParkRisk != null ? `${avgParkRisk.toFixed(1)}%` : '—'}</p>
            </div>
          </div>

          {/* نمودار میله‌ای دقت مدل */}
          {accuracyBarData.length > 0 && (
            <div className="mb-6">
              <h4 className="text-sm font-semibold text-slate-700 mb-3">درصد دقت (اطمینان) مدل به تفکیک بیماری</h4>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={accuracyBarData} margin={{ top: 8, right: 24, left: 8, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="disease" />
                  <YAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                  <Tooltip formatter={(value: number) => [`${value}%`, 'دقت']} />
                  <Bar dataKey="دقت" fill="#8b5cf6" name="دقت (%)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </section>

      {/* سهم مودالیتی‌ها */}
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100">
          <h3 className="text-base font-semibold text-slate-800">سهم مودالیتی‌ها در پیش‌بینی (توضیح‌پذیری)</h3>
        </div>
        <div className="p-6">
          <p className="text-slate-500 text-sm mb-4">
            میانگین وزن هر منبع داده در پیش‌بینی‌های اخیر — تصویربرداری (MRI)، بیومارکر و شناختی.
          </p>
          {modalityPieData.length > 0 ? (
            <div className="flex flex-col md:flex-row gap-6 items-center">
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={modalityPieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    nameKey="name"
                    label={({ name, value }) => `${name}: ${value}%`}
                  >
                    {modalityPieData.map((entry, index) => (
                      <Cell key={entry.key} fill={MODALITY_COLORS[index % MODALITY_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => [`${value}%`, 'سهم']} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-2 min-w-[200px]">
                {modalityPieData.map((d, i) => (
                  <div key={d.key} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                    <span className="text-sm font-medium text-slate-700">{d.name}</span>
                    <span
                      className="text-sm font-bold"
                      style={{ color: MODALITY_COLORS[i % MODALITY_COLORS.length] }}
                    >
                      {d.value}%
                    </span>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="py-8 text-center text-slate-500 text-sm">
              داده‌ای برای سهم مودالیتی‌ها در بازه انتخابی موجود نیست. پیش‌بینی‌های دارای attention_scores لازم است.
            </div>
          )}
        </div>
      </section>

      {/* خلاصه برای تصمیم‌گیری پزشک */}
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">📋</span>
          <h3 className="text-base font-semibold text-slate-800">خلاصه برای تصمیم‌گیری</h3>
        </div>
        <div className="p-6">
          <ul className="space-y-2 text-sm text-slate-700">
            <li className="flex items-start gap-2">
              <span className="text-emerald-500 mt-0.5">●</span>
              <span>
                <strong>پیش‌بینی و احتمال ابتلا</strong> بر اساس داده‌های مولتی‌مودال (MRI، بیومارکر، شناختی) محاسبه
                می‌شود.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-500 mt-0.5">●</span>
              <span>
                <strong>درصد دقت (اطمینان مدل)</strong> نشان می‌دهد مدل چقدر در پیش‌بینی هر بیماری اطمینان دارد؛
                عدد بالاتر یعنی اطمینان بیشتر.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-500 mt-0.5">●</span>
              <span>
                <strong>سهم مودالیتی‌ها</strong> نشان می‌دهد کدام منبع (تصویر، بیومارکر، شناختی) در پیش‌بینی‌های
                اخیر بیشتر نقش داشته است.
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-emerald-500 mt-0.5">●</span>
              <span>
                برای تصمیم نهایی، تب‌های <strong>پارکینسون و آلزایمر</strong> و <strong>احتمال بیماری</strong> را برای
                مشاهده تقسیم‌بندی بیماران و درصد احتمال هر بیمار ببینید.
              </span>
            </li>
          </ul>
        </div>
      </section>
    </div>
  );
}
