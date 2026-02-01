import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { monitoringApi } from '../services/api';
import { useWebSocket } from '../hooks/useWebSocket';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export default function SystemHealth() {
  const { data: systemHealth, refetch: refetchHealth } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => monitoringApi.getSystemHealth().then((res) => res.data),
    refetchInterval: 10000,
  });

  const { data: performance } = useQuery({
    queryKey: ['system-performance'],
    queryFn: () => monitoringApi.getSystemPerformance(24).then((res) => res.data),
    refetchInterval: 30000,
  });

  const { data: services } = useQuery({
    queryKey: ['services-status'],
    queryFn: () => monitoringApi.getServicesStatus().then((res) => res.data),
    refetchInterval: 10000,
  });

  // WebSocket for real-time updates
  useWebSocket('system', (message) => {
    if (message.type === 'system_update') {
      refetchHealth();
    }
  });

  const serviceStatus = services?.services || [];

  return (
    <div className="space-y-6">
      <section className="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center gap-2">
          <span className="text-xl">⚙️</span>
          <h2 className="text-lg font-semibold text-slate-800">System Health & DevOps Monitoring</h2>
        </div>
        <div className="p-6">
          {/* Overall Status */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div
              className={`rounded-xl border p-4 ${
                systemHealth?.status === 'healthy'
                  ? 'border-emerald-200 bg-gradient-to-br from-emerald-50 to-white'
                  : systemHealth?.status === 'degraded'
                  ? 'border-amber-200 bg-gradient-to-br from-amber-50 to-white'
                  : 'border-rose-200 bg-gradient-to-br from-rose-50 to-white'
              }`}
            >
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">System Status</p>
              <p
                className={`text-xl font-bold mt-1 ${
                  systemHealth?.status === 'healthy'
                    ? 'text-emerald-600'
                    : systemHealth?.status === 'degraded'
                    ? 'text-amber-600'
                    : 'text-rose-600'
                }`}
              >
                {systemHealth?.status === 'healthy' ? '✓ Healthy' : '⚠ ' + systemHealth?.status}
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-indigo-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Total Patients</p>
              <p className="text-xl font-bold text-indigo-600 mt-1">
                {systemHealth?.metrics?.total_patients || 0}
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-violet-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Predictions/Hour</p>
              <p className="text-xl font-bold text-violet-600 mt-1">
                {performance?.throughput?.predictions_per_hour?.toFixed(1) || 0}
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-gradient-to-br from-amber-50 to-white p-4">
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wide">Error Rate</p>
              <p className="text-xl font-bold text-amber-600 mt-1">
                {performance?.error_rates?.total_error_rate?.toFixed(2) || 0}%
              </p>
            </div>
          </div>

          {/* Service Status */}
          {serviceStatus.length > 0 && (
            <div className="mb-6">
              <h3 className="text-base font-semibold text-slate-800 mb-3">Service Status</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {serviceStatus.map((service: any, idx: number) => (
                  <div
                    key={idx}
                    className={`border-l-4 rounded-xl p-4 ${
                    service.status === 'up'
                      ? 'bg-emerald-50 border-emerald-500'
                      : service.status === 'down'
                      ? 'bg-rose-50 border-rose-500'
                      : 'bg-amber-50 border-amber-500'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-gray-900">{service.name}</h4>
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        service.status === 'up'
                          ? 'bg-green-100 text-green-800'
                          : service.status === 'down'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {service.status.toUpperCase()}
                    </span>
                  </div>
                  {service.response_time_ms && (
                    <p className="text-sm text-gray-600 mt-2">
                      Response: {service.response_time_ms}ms
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Performance Metrics */}
        {performance && (
          <div className="mb-6">
            <h3 className="text-base font-semibold text-slate-800 mb-3">Performance Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Throughput */}
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <h4 className="font-medium text-slate-700 mb-3">Throughput</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Predictions/Hour</span>
                    <div className="flex items-center gap-2">
                      <span className="font-medium">
                        {performance.throughput?.predictions_per_hour?.toFixed(1) || 0}
                      </span>
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          (performance.throughput?.predictions_per_hour || 0) >= 100
                            ? 'bg-green-100 text-green-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        Target: {performance.throughput?.target || 100}
                      </span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">API Requests/Hour</span>
                    <span className="font-medium">
                      {performance.throughput?.api_requests_per_hour?.toFixed(1) || 0}
                    </span>
                  </div>
                </div>
              </div>

              {/* Error Rates */}
              <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
                <h4 className="font-medium text-slate-700 mb-3">Error Rates</h4>
                <div className="space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Total Error Rate</span>
                    <span
                      className={`font-medium ${
                        (performance.error_rates?.total_error_rate || 0) < 1
                          ? 'text-green-600'
                          : (performance.error_rates?.total_error_rate || 0) < 5
                          ? 'text-yellow-600'
                          : 'text-red-600'
                      }`}
                    >
                      {performance.error_rates?.total_error_rate?.toFixed(2) || 0}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Server Errors (5xx)</span>
                    <span className="font-medium text-red-600">
                      {performance.error_rates?.server_error_rate?.toFixed(2) || 0}%
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Client Errors (4xx)</span>
                    <span className="font-medium text-yellow-600">
                      {performance.error_rates?.client_error_rate?.toFixed(2) || 0}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Latency Target */}
        {performance?.latency && (
          <div>
            <h3 className="text-base font-semibold text-slate-800 mb-3">Latency Targets</h3>
            <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4">
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Target Response Time</span>
                  <span className="font-medium">
                    &lt; {performance.latency.target || 200}ms
                  </span>
                </div>
                {performance.latency.avg_response_time_ms && (
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-600">Average Response Time</span>
                    <span
                      className={`font-medium ${
                        (performance.latency.avg_response_time_ms || 0) <
                        (performance.latency.target || 200)
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      {performance.latency.avg_response_time_ms}ms
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
        </div>
      </section>
    </div>
  );
}

