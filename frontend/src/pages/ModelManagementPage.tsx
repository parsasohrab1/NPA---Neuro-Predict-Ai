import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { modelsApi } from '../services/api'

export default function ModelManagementPage() {
  const [selectedModel, setSelectedModel] = useState<string>('')

  // Fetch models from API
  const { data: modelsData } = useQuery({
    queryKey: ['models'],
    queryFn: () => modelsApi.getAll(),
  })

  const { data: performanceData } = useQuery({
    queryKey: ['model-performance', selectedModel],
    queryFn: () => modelsApi.getPerformance(selectedModel),
    enabled: !!selectedModel,
  })

  const models = modelsData?.models || []
  const selectedModelData = models.find((m: any) => m.id === selectedModel) || models[0]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">🤖 Model Management</h1>
        <p className="text-gray-600">Monitor and manage AI models</p>
      </div>

      {/* Model Selection */}
      <div className="card mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold">Active Models</h2>
          <button className="btn btn-primary">
            + Upload New Model
          </button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {models.map((model) => (
            <div
              key={model.id}
              onClick={() => setSelectedModel(model.id)}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-colors ${
                selectedModel === model.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold">{model.name}</h3>
                <span className={`px-2 py-1 text-xs rounded ${
                  model.status === 'active'
                    ? 'bg-green-100 text-green-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {model.status}
                </span>
              </div>
              <p className="text-sm text-gray-600">Version: {model.version}</p>
              <p className="text-sm text-gray-600">Accuracy: {((model.accuracy || 0) * 100).toFixed(1)}%</p>
            </div>
          ))}
        </div>
      </div>

      {/* Model Performance Metrics */}
      {selectedModelData && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="card">
              <p className="text-sm text-gray-600 mb-1">Accuracy</p>
              <p className="text-3xl font-bold text-blue-600">
                {(selectedModelData.accuracy * 100).toFixed(1)}%
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-600 mb-1">Precision</p>
              <p className="text-3xl font-bold text-green-600">
                {(selectedModelData.precision * 100).toFixed(1)}%
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-600 mb-1">Recall</p>
              <p className="text-3xl font-bold text-yellow-600">
                {(selectedModelData.recall * 100).toFixed(1)}%
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-600 mb-1">F1 Score</p>
              <p className="text-3xl font-bold text-purple-600">
                {(selectedModelData.f1Score * 100).toFixed(1)}%
              </p>
            </div>
          </div>

          {/* Model Actions */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Model Actions</h2>
            <div className="flex space-x-3">
              <button className="btn btn-secondary">View ROC Curve</button>
              <button className="btn btn-secondary">View Confusion Matrix</button>
              <button className="btn btn-secondary">Download Model</button>
              <button className="btn btn-danger">Rollback</button>
              <button className="btn btn-danger">Deactivate</button>
            </div>
          </div>

          {/* Drift Monitoring */}
          <div className="card mt-6">
            <h2 className="text-xl font-semibold mb-4">Drift Monitoring</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-blue-50 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-1">Data Drift</p>
                <p className="text-lg font-semibold text-blue-600">Normal</p>
                <p className="text-xs text-gray-500 mt-1">Last checked: 2 hours ago</p>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <p className="text-sm font-medium text-gray-700 mb-1">Concept Drift</p>
                <p className="text-lg font-semibold text-green-600">Normal</p>
                <p className="text-xs text-gray-500 mt-1">Last checked: 2 hours ago</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
