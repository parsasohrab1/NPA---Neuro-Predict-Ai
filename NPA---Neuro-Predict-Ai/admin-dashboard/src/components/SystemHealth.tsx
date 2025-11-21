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
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">⚙️ System Health & DevOps Monitoring</h2>

        {/* Overall Status */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div
            className={`rounded-lg p-4 ${
              systemHealth?.status === 'healthy'
                ? 'bg-green-50'
                : systemHealth?.status === 'degraded'
                ? 'bg-yellow-50'
                : 'bg-red-50'
            }`}
          >
            <h3 className="text-sm font-medium text-gray-600">System Status</h3>
            <p
              className={`text-2xl font-bold ${
                systemHealth?.status === 'healthy'
                  ? 'text-green-600'
                  : systemHealth?.status === 'degraded'
                  ? 'text-yellow-600'
                  : 'text-red-600'
              }`}
            >
              {systemHealth?.status === 'healthy' ? '✓ Healthy' : '⚠ ' + systemHealth?.status}
            </p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Total Patients</h3>
            <p className="text-2xl font-bold text-blue-600">
              {systemHealth?.metrics?.total_patients || 0}
            </p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Predictions/Hour</h3>
            <p className="text-2xl font-bold text-purple-600">
              {performance?.throughput?.predictions_per_hour?.toFixed(1) || 0}
            </p>
          </div>
          <div className="bg-orange-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Error Rate</h3>
            <p className="text-2xl font-bold text-orange-600">
              {performance?.error_rates?.total_error_rate?.toFixed(2) || 0}%
            </p>
          </div>
        </div>

        {/* Service Status */}
        {serviceStatus.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Service Status</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {serviceStatus.map((service: any, idx: number) => (
                <div
                  key={idx}
                  className={`border-l-4 rounded-lg p-4 ${
                    service.status === 'up'
                      ? 'bg-green-50 border-green-500'
                      : service.status === 'down'
                      ? 'bg-red-50 border-red-500'
                      : 'bg-yellow-50 border-yellow-500'
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
            <h3 className="text-lg font-semibold mb-3">Performance Metrics</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Throughput */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium mb-3">Throughput</h4>
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
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium mb-3">Error Rates</h4>
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
            <h3 className="text-lg font-semibold mb-3">Latency Targets</h3>
            <div className="bg-gray-50 rounded-lg p-4">
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
    </div>
  );
}

