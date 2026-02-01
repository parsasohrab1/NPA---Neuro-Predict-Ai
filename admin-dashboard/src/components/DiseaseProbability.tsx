import React, { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { diseaseApi } from '../services/api';
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
  Legend,
  ResponsiveContainer,
} from 'recharts';

const LEVEL_LABELS: Record<string, string> = {
  low: 'Healthy',
  medium: 'At Risk',
  high: 'High Risk / Disease',
};

const COLORS = {
  low: '#10b981',
  medium: '#f59e0b',
  high: '#ef4444',
};

export default function DiseaseProbability() {
  const { data: summaryData, isLoading, error } = useQuery({
    queryKey: ['disease-patients-summary'],
    queryFn: () => diseaseApi.getPatientsSummary().then((res) => res.data),
  });

  const { totals, alzheimerPieData, parkinsonPieData, levelPercentData, topPatientsBarData } =
    useMemo(() => {
      const patients = summaryData?.patients || [];
      const total = patients.length;
      if (total === 0) {
        return {
          totals: { total, avgAlzheimer: 0, avgParkinson: 0 },
          alzheimerPieData: [],
          parkinsonPieData: [],
          levelPercentData: [],
          topPatientsBarData: [],
        };
      }
      const sumAlz = patients.reduce((s: number, p: any) => s + (p.alzheimer_risk ?? 0), 0);
      const sumPark = patients.reduce((s: number, p: any) => s + (p.parkinson_risk ?? 0), 0);
      const avgAlzheimer = (sumAlz / total) * 100;
      const avgParkinson = (sumPark / total) * 100;

      const alzLow = patients.filter((p: any) => p.alzheimer_level === 'low').length;
      const alzMed = patients.filter((p: any) => p.alzheimer_level === 'medium').length;
      const alzHigh = patients.filter((p: any) => p.alzheimer_level === 'high').length;
      const parkLow = patients.filter((p: any) => p.parkinson_level === 'low').length;
      const parkMed = patients.filter((p: any) => p.parkinson_level === 'medium').length;
      const parkHigh = patients.filter((p: any) => p.parkinson_level === 'high').length;

      const alzheimerPieData = [
        { name: LEVEL_LABELS.low, value: alzLow, level: 'low' },
        { name: LEVEL_LABELS.medium, value: alzMed, level: 'medium' },
        { name: LEVEL_LABELS.high, value: alzHigh, level: 'high' },
      ].filter((d) => d.value > 0);

      const parkinsonPieData = [
        { name: LEVEL_LABELS.low, value: parkLow, level: 'low' },
        { name: LEVEL_LABELS.medium, value: parkMed, level: 'medium' },
        { name: LEVEL_LABELS.high, value: parkHigh, level: 'high' },
      ].filter((d) => d.value > 0);

      const levelPercentData = [
        {
          disease: 'Alzheimer',
          Healthy: total ? (alzLow / total) * 100 : 0,
          'At Risk': total ? (alzMed / total) * 100 : 0,
          'High Risk': total ? (alzHigh / total) * 100 : 0,
        },
        {
          disease: 'Parkinson',
          Healthy: total ? (parkLow / total) * 100 : 0,
          'At Risk': total ? (parkMed / total) * 100 : 0,
          'High Risk': total ? (parkHigh / total) * 100 : 0,
        },
      ];

      const topPatientsBarData = [...patients]
        .sort((a: any, b: any) => (b.alzheimer_risk ?? 0) + (b.parkinson_risk ?? 0) - (a.alzheimer_risk ?? 0) - (a.parkinson_risk ?? 0))
        .slice(0, 12)
        .map((p: any) => ({
          name: p.name?.split(' ')[0] || `#${p.patient_id}`,
          Alzheimer: Number((((p.alzheimer_risk ?? 0) * 100).toFixed(1))),
          Parkinson: Number((((p.parkinson_risk ?? 0) * 100).toFixed(1))),
        }));

      return {
        totals: { total, avgAlzheimer, avgParkinson },
        alzheimerPieData,
        parkinsonPieData,
        levelPercentData,
        topPatientsBarData,
      };
    }, [summaryData]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16 text-slate-500">
        Loading...
      </div>
    );
  }
  if (error) {
    return (
      <div className="rounded-2xl border border-rose-200 bg-rose-50 p-6 text-rose-700">
        Error loading data.
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Percentage summary */}
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">📈</span>
          <h2 className="text-lg font-semibold text-slate-800">Disease Probability — Percentages and Summary</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-indigo-50 to-white p-4 text-center">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Total Patients</p>
              <p className="text-3xl font-bold text-indigo-600 mt-1">{totals.total}</p>
            </div>
            <div className="rounded-xl border border-violet-200 bg-gradient-to-br from-violet-50 to-white p-4 text-center">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Avg Alzheimer Probability</p>
              <p className="text-3xl font-bold text-violet-600 mt-1">{totals.avgAlzheimer.toFixed(1)}%</p>
            </div>
            <div className="rounded-xl border border-rose-200 bg-gradient-to-br from-rose-50 to-white p-4 text-center">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Avg Parkinson Probability</p>
              <p className="text-3xl font-bold text-rose-600 mt-1">{totals.avgParkinson.toFixed(1)}%</p>
            </div>
          </div>

          {/* Pie chart: risk level distribution */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
              <h3 className="text-base font-semibold text-slate-800 mb-3 text-center">Alzheimer Risk Level Distribution</h3>
              {alzheimerPieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={alzheimerPieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={2}
                      dataKey="value"
                      nameKey="name"
                      label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                    >
                      {alzheimerPieData.map((entry, index) => (
                        <Cell key={entry.level} fill={COLORS[entry.level as keyof typeof COLORS]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => [`${value}`, 'Count']} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-52 flex items-center justify-center text-slate-500 text-sm">No data available</div>
              )}
            </div>
            <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
              <h3 className="text-base font-semibold text-slate-800 mb-3 text-center">Parkinson Risk Level Distribution</h3>
              {parkinsonPieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={parkinsonPieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={90}
                      paddingAngle={2}
                      dataKey="value"
                      nameKey="name"
                      label={({ name, value, percent }) => `${name}: ${value} (${(percent * 100).toFixed(0)}%)`}
                    >
                      {parkinsonPieData.map((entry, index) => (
                        <Cell key={entry.level} fill={COLORS[entry.level as keyof typeof COLORS]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => [`${value}`, 'Count']} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="h-52 flex items-center justify-center text-slate-500 text-sm">No data available</div>
              )}
            </div>
          </div>

          {/* Bar chart: percentage per level by disease */}
          <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4 mb-6">
            <h3 className="text-base font-semibold text-slate-800 mb-3 text-center">Patient Percentage per Risk Level</h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart
                data={levelPercentData}
                layout="vertical"
                margin={{ top: 8, right: 24, left: 60, bottom: 8 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis type="number" unit="%" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                <YAxis type="category" dataKey="disease" width={56} />
                <Tooltip formatter={(value: number) => [`${value.toFixed(1)}%`, '']} />
                <Legend />
                <Bar dataKey="Healthy" stackId="a" fill="#10b981" name="Healthy" />
                <Bar dataKey="At Risk" stackId="a" fill="#f59e0b" name="At Risk" />
                <Bar dataKey="High Risk" stackId="a" fill="#ef4444" name="High Risk" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Bar chart: disease probability per patient */}
          {topPatientsBarData.length > 0 && (
            <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
              <h3 className="text-base font-semibold text-slate-800 mb-3 text-center">Disease Probability (%) — Sample Patients</h3>
              <ResponsiveContainer width="100%" height={340}>
                <BarChart
                  data={topPatientsBarData}
                  margin={{ top: 8, right: 24, left: 8, bottom: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" angle={-35} textAnchor="end" height={56} interval={0} />
                  <YAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                  <Tooltip formatter={(value: string) => [`${value}%`, '']} />
                  <Legend />
                  <Bar dataKey="Alzheimer" fill="#8b5cf6" name="Alzheimer (%)" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Parkinson" fill="#ec4899" name="Parkinson (%)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
