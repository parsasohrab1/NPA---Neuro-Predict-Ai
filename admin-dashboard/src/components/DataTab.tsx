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
    title: 'Cognitive Data',
    icon: '🧠',
    description: 'Cognitive scores from data generator: MMSE, MoCA, memory, attention, executive function.',
    color: '#10b981',
  },
  biomarker: {
    title: 'Biomarker Data',
    icon: '🧪',
    description: 'Synthetic biomarkers: amyloid beta, tau, dopamine and other biological markers.',
    color: '#06b6d4',
  },
  imaging: {
    title: 'MRI Data',
    icon: '🖼️',
    description: 'Synthetic MRI imaging data: hippocampal volume, cortical thickness, ventricular volume, etc.',
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
        <div className="p-6 text-center text-slate-500">Loading...</div>
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
        <div className="p-6 text-rose-600 text-sm">Error loading data.</div>
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
        {/* Metric summary cards */}
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

        {/* Distribution chart */}
        {distribution.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-700 mb-3">Data Distribution</h4>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={distribution} margin={{ top: 8, right: 16, left: 8, bottom: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="range" tick={{ fontSize: 12 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill={config.color} name="Count" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Time series chart */}
        {timeSeries.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-700 mb-3">Time Series (Average)</h4>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={timeSeries} margin={{ top: 8, right: 16, left: 8, bottom: 24 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="avg_value" stroke={config.color} name="Average" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Metrics table */}
        {metrics.length > 0 && (
          <div>
            <h4 className="text-sm font-semibold text-slate-700 mb-3">Metrics Summary (avg / min / max)</h4>
            <div className="rounded-xl border border-slate-200 overflow-hidden">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left py-2 px-3 font-medium text-slate-700">Feature</th>
                    <th className="text-left py-2 px-3 font-medium text-slate-700">Average</th>
                    <th className="text-left py-2 px-3 font-medium text-slate-700">Min</th>
                    <th className="text-left py-2 px-3 font-medium text-slate-700">Max</th>
                    <th className="text-left py-2 px-3 font-medium text-slate-700">Count</th>
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
            No data recorded in this time range. You can load synthetic data from the data generator.
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
      {/* Overview summary */}
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">📊</span>
          <h2 className="text-lg font-semibold text-slate-800">Dataset — Three Multimodal Categories</h2>
        </div>
        <div className="p-6">
          <p className="text-slate-600 text-sm mb-4">
            Synthetic data from the data generator in three categories: <strong>MRI data</strong>,{' '}
            <strong>biomarker data</strong>, and <strong>cognitive data</strong>. Each category shows distribution chart, time series and metrics table.
          </p>
          {!overviewLoading && overview && (
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <p className="text-xs font-medium text-slate-500 uppercase">Total Records</p>
                <p className="text-2xl font-bold text-slate-800 mt-1">{overview.total_records ?? 0}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <p className="text-xs font-medium text-slate-500 uppercase">Total Patients</p>
                <p className="text-2xl font-bold text-slate-800 mt-1">{overview.total_patients ?? 0}</p>
              </div>
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <p className="text-xs font-medium text-slate-500 uppercase">Data Quality Score</p>
                <p className="text-2xl font-bold text-slate-800 mt-1">{overview.data_quality_score ?? 0}</p>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Cognitive data */}
      <CategorySection category="cognitive" />

      {/* Biomarker data */}
      <CategorySection category="biomarker" />

      {/* MRI data */}
      <CategorySection category="imaging" />
    </div>
  );
}
