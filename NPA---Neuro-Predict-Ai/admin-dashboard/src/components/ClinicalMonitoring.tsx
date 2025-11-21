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
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">🏥 Clinical & Longitudinal Monitoring</h2>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-red-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">High Severity Alerts</h3>
            <p className="text-2xl font-bold text-red-600">
              {alerts?.high_severity_count || 0}
            </p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Medium Severity Alerts</h3>
            <p className="text-2xl font-bold text-yellow-600">
              {mediumSeverityAlerts.length}
            </p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Total Alerts</h3>
            <p className="text-2xl font-bold text-blue-600">
              {alerts?.total_alerts || 0}
            </p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Queue Length</h3>
            <p className="text-2xl font-bold text-purple-600">
              {queue?.queue_length || 0}
            </p>
          </div>
        </div>

        {/* Smart Alerts */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">Smart Alerts</h3>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {alerts?.alerts && alerts.alerts.length > 0 ? (
              alerts.alerts.slice(0, 20).map((alert: any, idx: number) => (
                <div
                  key={idx}
                  className={`border-l-4 rounded-lg p-4 ${
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
              <div className="text-center text-gray-500 py-8">No alerts</div>
            )}
          </div>
        </div>

        {/* Prediction Queue */}
        {queue && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Prediction Queue</h3>
            <div className="bg-gray-50 rounded-lg p-4">
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
    </div>
  );
}

