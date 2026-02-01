import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { dataApi } from '../services/api';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

const TIME_RANGE = '30d';
const CATEGORY_CONFIG = {
  cognitive: {
    title: 'داده‌های شناختی',
    icon: '🧠',
    description: 'نمرات شناختی تولیدشده توسط دیتا جنریتور: MMSE، MoCA، حافظه، توجه، عملکرد اجرایی.',
    color: '#10b981',
  },
  biomarker: {
    title: 'داده‌های بیومارکر',
    icon: '🧪',
    description: 'بیومارکرهای سنتتیک: آمیلوئید بتا، تاو، دوپامین و سایر نشانگرهای زیستی.',
    color: '#06b6d4',
  },
  imaging: {
    title: 'داده‌های MRI',
    icon: '🖼️',
    description: 'داده‌های تصویربرداری MRI سنتتیک: حجم هیپوکامپ، ضخامت قشری، حجم بطنی و غیره.',
    color: '#8b5cf6',
  },
} as const;

type CategoryKey = 'cognitive' | 'biomarker' | 'imaging';

function CategorySection({ category }: { category: CategoryKey }) {
  const config = CATEGORY_CONFIG[category];
  const { data, isLoading, error } = useQuery({
    queryKey: ['data-category', category, TIME_RANGE],
    queryFn: () => dataApi.getCategoryData(category, TIME_RANGE).then((res) => res.data),
  });

  const distribution = data?.distribution || [];
  const timeSeries = data?.time_series || [];
  const metrics = data?.metrics || [];

  if (isLoading) {
    return (
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">{config.icon}</span>
          <h2 className="text-lg font-semibold text-slate-800">{config.title}</h2>
        </div>
        <div className="p-6 text-center text-slate-500">در حال بارگذاری...</div>
      </section>
    );
  }
  if (error) {
    return (
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">{config.icon}</span>
          <h2 className="text-lg font-semibold text-slate-800">{config.title}</h2>
        </div>
        <div className="p-6 text-rose-600 text-sm">خطا در دریافت داده.</div>
      </section>
    );
  }

  return (
    <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <span className="text-xl">{config.icon}</span>
          <h2 className="text-lg font-semibold text-slate-800">{config.title}</h2>
        </div>
        <p className="text-sm text-slate-500 mt-1">{config.description}</p>
      </div>
      <div className="p-6 space-y-6">
        {/* کارت‌های خلاصه متریک‌ها */}
        {metrics.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
            {metrics.slice(0, 5).map((m: any, i: number) => (
              <div
                key={m.metric_name}
                className="rounded-xl border border-slate-200 bg-slate-50/50 p-3 text-center"
              >
                <p className="text-xs font-medium text-slate-500 truncate" title={m.metric_name}>
                  {m.metric_name}
                </p>
                <p className="text-lg font-bold text-slate-800 mt-1">
                  {m.avg_value != null ? Number(m.avg_value).toFixed(2) : '—'}
                </p>
                <p className="text-xs text-slate-400">n={m.count ?? 0}</p>
              </div>
            ))}
          </div>
        )}

        {/* نمودار توزیع */}
        {distribution.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-700 mb-3">توزیع داده</h4>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={distribution} margin={{ top: 8, right: 16, left: 8, bottom: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="range" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill={config.color} name="تعداد" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* نمودار سری زمانی */}
        {timeSeries.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-700 mb-3">روند زمانی (میانگین)</h4>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={timeSeries} margin={{ top: 8, right: 16, left: 8, bottom: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="avg_value" stroke={config.color} name="میانگین" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* جدول متریک‌ها */}
        {metrics.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-700 mb-3">خلاصه متریک‌ها (میانگین / min / max)</h4>
            <div className="rounded-xl border border-slate-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left py-2 px-3 font-medium text-slate-700">ویژگی</th>
                    <th className="text-left py-2 px-3 font-medium text-slate-700">میانگین</th>
                    <th className="text-left py-2 px-3 font-medium text-slate-700">کمینه</th>
                    <th className="text-left py-2 px-3 font-medium text-slate-700">بیشینه</th>
                    <th className="text-left py-2 px-3 font-medium text-slate-700">تعداد</th>
                  </tr>
                </thead>
                <tbody>
                  {metrics.map((m: any) => (
                    <tr key={m.metric_name} className="border-t border-slate-100">
                      <td className="py-2 px-3 font-medium text-slate-800">{m.metric_name}</td>
                      <td className="py-2 px-3">{m.avg_value != null ? Number(m.avg_value).toFixed(2) : '—'}</td>
                      <td className="py-2 px-3">{m.min_value != null ? Number(m.min_value).toFixed(2) : '—'}</td>
                      <td className="py-2 px-3">{m.max_value != null ? Number(m.max_value).toFixed(2) : '—'}</td>
                      <td className="py-2 px-3">{m.count ?? 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {metrics.length === 0 && distribution.length === 0 && timeSeries.length === 0 && (
          <div className="py-8 text-center text-slate-500 text-sm">
            در این بازه زمانی داده‌ای ثبت نشده. می‌توانید از دیتا جنریتور داده سنتتیک بارگذاری کنید.
          </div>
        )}
      </div>
    </section>
  );
}

export default function DataTab() {
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ['data-overview'],
    queryFn: () => dataApi.getOverview().then((res) => res.data),
  });

  return (
    <div className="space-y-6">
      {/* خلاصه کلی */}
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">📊</span>
          <h2 className="text-lg font-semibold text-slate-800">داده‌های دیتاست — سه دسته مولتی‌مودال</h2>
        </div>
        <div className="p-6">
          <p className="text-slate-600 text-sm mb-4">
            داده‌های سنتتیک تولیدشده توسط دیتا جنریتور در سه دسته: <strong>داده‌های MRI</strong>،{' '}
            <strong>داده‌های بیومارکر</strong> و <strong>داده‌های شناختی</strong>. هر دسته با گراف توزیع، روند
            زمانی و جدول متریک‌ها نمایش داده می‌شود.
          </p>
          {!overviewLoading && overview && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <p className="text-xs font-medium text-slate-500 uppercase">کل رکوردها</p>
                <p className="text-2xl font-bold text-slate-800 mt-1">{overview.total_records ?? 0}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <p className="text-xs font-medium text-slate-500 uppercase">تعداد بیماران</p>
                <p className="text-2xl font-bold text-slate-800 mt-1">{overview.total_patients ?? 0}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <p className="text-xs font-medium text-slate-500 uppercase">امتیاز کیفیت داده</p>
                <p className="text-2xl font-bold text-slate-800 mt-1">{overview.data_quality_score ?? 0}</p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* داده‌های شناختی */}
      <CategorySection category="cognitive" />

      {/* داده‌های بیومارکر */}
      <CategorySection category="biomarker" />

      {/* داده‌های MRI */}
      <CategorySection category="imaging" />
    </div>
  );
}
