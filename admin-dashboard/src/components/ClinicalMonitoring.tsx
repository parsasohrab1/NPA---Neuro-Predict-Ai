import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { monitoringApi } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function ClinicalMonitoring() {
  const { data: alerts, refetch: refetchAlerts } = useQuery({
    queryKey: ['smart-alerts'],
    queryFn: () => monitoringApi.getSmartAlerts().then((res) => res.data),
    refetchInterval: 30000,
  });

  const { data: queue } = useQuery({
    queryKey: ['prediction-queue'],
    queryFn: () => monitoringApi.getPredictionQueue().then((res) => res.data),
    refetchInterval: 10000,
  });

  // WebSocket for real-time updates
  useWebSocket('clinical', (message) => {
    if (message.type === 'clinical_update' || message.type === 'alert') {
      refetchAlerts();
    }
  });

  const highSeverityAlerts = alerts?.alerts?.filter(
    (a: any) => a.severity === 'high'
  ) || [];
  const mediumSeverityAlerts = alerts?.alerts?.filter(
    (a: any) => a.severity === 'medium'
  ) || [];

  return (
    <div className="space-y-6">
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">🏥</span>
          <h2 className="text-lg font-semibold text-slate-800">Clinical & Longitudinal Monitoring</h2>
        </div>
        <div className="p-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="rounded-xl border border-rose-200 bg-gradient-to-br from-rose-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">High Severity Alerts</p>
              <p className="text-xl font-bold text-rose-600 mt-1">
                {alerts?.high_severity_count || 0}
              </p>
            </div>
            <div className="rounded-xl border border-amber-200 bg-gradient-to-br from-amber-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Medium Severity</p>
              <p className="text-xl font-bold text-amber-600 mt-1">
                {mediumSeverityAlerts.length}
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-indigo-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Total Alerts</p>
              <p className="text-xl font-bold text-indigo-600 mt-1">
                {alerts?.total_alerts || 0}
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-violet-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Queue Length</p>
              <p className="text-xl font-bold text-violet-600 mt-1">
                {queue?.queue_length || 0}
              </p>
            </div>
          </div>

          {/* Smart Alerts */}
          <div className="mb-6">
            <h3 className="text-base font-semibold text-slate-800 mb-3">Smart Alerts</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {alerts?.alerts && alerts.alerts.length > 0 ? (
                alerts.alerts.slice(0, 20).map((alert: any, idx: number) => (
                  <div
                    key={idx}
                    className={`border-l-4 rounded-xl p-4 ${
                    alert.severity === 'high'
                      ? 'bg-red-50 border-red-500'
                      : alert.severity === 'medium'
                      ? 'bg-yellow-50 border-yellow-500'
                      : 'bg-blue-50 border-blue-500'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className={`px-2 py-1 rounded text-xs font-medium ${
                            alert.severity === 'high'
                              ? 'bg-red-100 text-red-800'
                              : 'bg-yellow-100 text-yellow-800'
                          }`}
                        >
                          {alert.severity.toUpperCase()}
                        </span>
                        <span className="text-xs text-gray-500">{alert.type}</span>
                      </div>
                      <p className="font-medium text-gray-900">{alert.patient_name}</p>
                      <p className="text-sm text-gray-600 mt-1">{alert.message}</p>
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(alert.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center text-slate-500 py-8">No alerts</div>
            )}
          </div>
        </div>

        {/* Prediction Queue */}
        {queue && (
          <div>
            <h3 className="text-base font-semibold text-slate-800 mb-3">Prediction Queue</h3>
            <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
              <div className="flex items-center justify-between mb-4">
                <span className="text-sm font-medium">Queue Length</span>
                <span className="text-2xl font-bold text-purple-600">
                  {queue.queue_length}
                </span>
              </div>
              {queue.recent_predictions && queue.recent_predictions.length > 0 && (
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {queue.recent_predictions.map((pred: any, idx: number) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between text-sm bg-white rounded p-2"
                    >
                      <span className="text-gray-600">Prediction #{pred.id}</span>
                      <span className="text-gray-500">
                        {new Date(pred.created_at).toLocaleTimeString()}
                      </span>
                      <span
                        className={`px-2 py-1 rounded text-xs ${
                          pred.status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {pred.status}
                      </span>
                    </div>
                  ))}
              </div>
            )}
            </div>
          </div>
        )}
        </div>
      </section>
    </div>
  );
}

