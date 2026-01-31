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
  PieChart,
  Pie,
  Cell,
} from 'recharts';

export default function AIMLHealth() {
  const { data: mlHealth, refetch } = useQuery({
    queryKey: ['ml-health'],
    queryFn: () => monitoringApi.getMLHealth(24).then((res) => res.data),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: featureImportance } = useQuery({
    queryKey: ['feature-importance'],
    queryFn: () => monitoringApi.getFeatureImportance(20, 24).then((res) => res.data),
    refetchInterval: 60000,
  });

  const { data: modelPerformance } = useQuery({
    queryKey: ['model-performance'],
    queryFn: () => monitoringApi.getModelPerformance(undefined, 24).then((res) => res.data),
    refetchInterval: 30000,
  });

  // WebSocket for real-time updates
  useWebSocket('ai_ml', (message) => {
    if (message.type === 'ai_ml_update') {
      refetch();
    }
  });

  const confidenceData = mlHealth?.confidence_distribution
    ? [
        {
          name: 'High Confidence (≥0.8)',
          value: mlHealth.confidence_distribution.high_confidence,
        },
        {
          name: 'Medium Confidence (0.5-0.8)',
          value: mlHealth.confidence_distribution.medium_confidence,
        },
        {
          name: 'Low Confidence (<0.5)',
          value: mlHealth.confidence_distribution.low_confidence,
        },
      ]
    : [];

  const COLORS = ['#10b981', '#f59e0b', '#ef4444'];

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">🤖 AI/ML Health Monitoring</h2>
        
        {/* Overall Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Status</h3>
            <p className="text-2xl font-bold text-blue-600">
              {mlHealth?.status === 'healthy' ? '✓ Healthy' : '⚠ Warning'}
            </p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Total Predictions</h3>
            <p className="text-2xl font-bold text-green-600">
              {mlHealth?.total_predictions || 0}
            </p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-600">Avg Confidence</h3>
            <p className="text-2xl font-bold text-purple-600">
              {mlHealth?.confidence_distribution?.avg_confidence
                ? (mlHealth.confidence_distribution.avg_confidence * 100).toFixed(1) + '%'
                : 'N/A'}
            </p>
          </div>
        </div>

        {/* Data Drift Indicators */}
        {mlHealth?.data_drift && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Data Drift Indicators</h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Overall Status</span>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    mlHealth.data_drift.overall_status === 'normal'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {mlHealth.data_drift.overall_status}
                </span>
              </div>
              {mlHealth.data_drift.indicators && mlHealth.data_drift.indicators.length > 0 && (
                <div className="mt-4 space-y-2">
                  {mlHealth.data_drift.indicators.slice(0, 5).map((indicator: any, idx: number) => (
                    <div key={idx} className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">{indicator.feature}</span>
                      <span
                        className={`px-2 py-1 rounded ${
                          indicator.status === 'normal'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-yellow-100 text-yellow-700'
                        }`}
                      >
                        {indicator.status}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Performance Metrics */}
        {modelPerformance && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Model Performance</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium mb-2">Alzheimer's Disease</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>High Risk Rate:</span>
                    <span className="font-medium">
                      {modelPerformance.metrics?.alzheimer?.high_risk_rate || 0}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Avg Confidence:</span>
                    <span className="font-medium">
                      {modelPerformance.metrics?.alzheimer?.avg_confidence
                        ? (modelPerformance.metrics.alzheimer.avg_confidence * 100).toFixed(1) + '%'
                        : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium mb-2">Parkinson's Disease</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span>High Risk Rate:</span>
                    <span className="font-medium">
                      {modelPerformance.metrics?.parkinson?.high_risk_rate || 0}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Avg Confidence:</span>
                    <span className="font-medium">
                      {modelPerformance.metrics?.parkinson?.avg_confidence
                        ? (modelPerformance.metrics.parkinson.avg_confidence * 100).toFixed(1) + '%'
                        : 'N/A'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Confidence Distribution */}
        {confidenceData.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-semibold mb-3">Confidence Score Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={confidenceData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {confidenceData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Feature Importance */}
        {featureImportance?.features && featureImportance.features.length > 0 && (
          <div>
            <h3 className="text-lg font-semibold mb-3">Feature Importance (Explainability)</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={featureImportance.features.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="feature"
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  interval={0}
                />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="avg_importance" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}

