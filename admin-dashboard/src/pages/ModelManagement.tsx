import { useMemo, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowUpTrayIcon, ArrowPathIcon, CheckCircleIcon, XCircleIcon } from '@heroicons/react/24/outline'
import axios from '../config/api'

interface Model {
  version: string
  model_path: string
  created_at: string
  metrics: {
    training?: {
      best_val_loss?: number
      epochs_trained?: number
    }
    test?: {
      alzheimer?: {
        accuracy?: number
        sensitivity?: number
        specificity?: number
        auc_roc?: number
      }
      parkinson?: {
        accuracy?: number
        sensitivity?: number
        specificity?: number
        auc_roc?: number
      }
    }
  }
  description?: string
  is_active?: boolean
}

interface ModelsResponse {
  models: Model[]
  current_model: Model | null
}

export default function ModelManagement() {
  const [selectedVersion, setSelectedVersion] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Fetch models from API
  const { data: modelsData, isLoading, error } = useQuery<ModelsResponse>({
    queryKey: ['admin', 'models'],
    queryFn: async () => {
      const response = await axios.get('/api/v1/admin/models')
      return response.data
    },
    refetchInterval: 30000, // Refetch every 30 seconds
  })

  // Activate model mutation
  const activateModelMutation = useMutation({
    mutationFn: async (version: string) => {
      const response = await axios.post('/api/v1/admin/models/activate', { version })
      return response.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin', 'models'] })
    },
  })

  const models = modelsData?.models || []
  const currentModel = modelsData?.current_model
  const activeModels = useMemo(
    () => models.filter((model) => model.is_active).length,
    [models]
  )
  const pendingValidations = useMemo(
    () => models.filter((model) => !model.is_active && model.metrics?.test).length,
    [models]
  )

  const handleActivateModel = (version: string) => {
    if (confirm(`Are you sure you want to activate model version ${version}?`)) {
      activateModelMutation.mutate(version)
    }
  }

  return (
    <div className="space-y-6">
      <header className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Model Lifecycle Management</h2>
          <p className="text-sm text-slate-400">
            Monitor performance, manage rollout, and keep audit trace of AI deployments.
          </p>
        </div>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:border-sky-400 hover:text-sky-300">
            <ArrowPathIcon className="h-4 w-4" />
            Run validation
          </button>
          <button className="flex items-center gap-2 rounded-lg bg-sky-500 px-3 py-2 text-sm font-medium text-slate-950 hover:bg-sky-400">
            <ArrowUpTrayIcon className="h-4 w-4" />
            Upload model
          </button>
        </div>
      </header>

      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <div className="text-slate-400">Loading models...</div>
        </div>
      )}

      {error && (
        <div className="rounded-2xl border border-rose-800 bg-rose-900/20 p-6">
          <div className="flex items-center gap-3">
            <XCircleIcon className="h-6 w-6 text-rose-400" />
            <div>
              <h3 className="text-lg font-semibold text-rose-300">Error loading models</h3>
              <p className="text-sm text-rose-400/80">
                {(error as Error).message || 'Failed to load models from API'}
              </p>
            </div>
          </div>
        </div>
      )}

      {!isLoading && !error && (
        <>
          <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="text-xs uppercase text-slate-400">Active production models</div>
              <div className="mt-2 text-3xl font-semibold text-emerald-400">{activeModels}</div>
              {currentModel && (
                <div className="mt-1 text-xs text-slate-500">Current: {currentModel.version}</div>
              )}
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="text-xs uppercase text-slate-400">Pending validations</div>
              <div className="mt-2 text-3xl font-semibold text-amber-400">{pendingValidations}</div>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
              <div className="text-xs uppercase text-slate-400">Total models</div>
              <div className="mt-2 text-3xl font-semibold text-sky-400">{models.length}</div>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            {models.length === 0 ? (
              <div className="py-12 text-center">
                <p className="text-slate-400">No models found. Train a model first.</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm text-slate-200">
                  <thead className="text-left text-xs uppercase text-slate-400">
                    <tr>
                      <th className="border-b border-slate-800/70 px-4 py-3">Version</th>
                      <th className="border-b border-slate-800/70 px-4 py-3">Status</th>
                      <th className="border-b border-slate-800/70 px-4 py-3">Alzheimer AUC</th>
                      <th className="border-b border-slate-800/70 px-4 py-3">Parkinson AUC</th>
                      <th className="border-b border-slate-800/70 px-4 py-3">Alzheimer Accuracy</th>
                      <th className="border-b border-slate-800/70 px-4 py-3">Parkinson Accuracy</th>
                      <th className="border-b border-slate-800/70 px-4 py-3">Created</th>
                      <th className="border-b border-slate-800/70 px-4 py-3">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/70">
                    {models.map((model) => {
                      const alzheimerMetrics = model.metrics?.test?.alzheimer
                      const parkinsonMetrics = model.metrics?.test?.parkinson
                      const isActive = model.is_active || currentModel?.version === model.version

                      return (
                        <tr
                          key={model.version}
                          className={`hover:bg-slate-900/50 ${isActive ? 'bg-emerald-900/10' : ''}`}
                        >
                          <td className="px-4 py-4">
                            <div className="text-white font-medium">{model.version}</div>
                            {model.description && (
                              <div className="text-xs text-slate-500 mt-1">{model.description}</div>
                            )}
                          </td>
                          <td className="px-4 py-4">
                            <span
                              className={
                                isActive
                                  ? 'flex items-center gap-1 rounded-full bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300'
                                  : 'flex items-center gap-1 rounded-full bg-amber-500/20 px-2 py-1 text-xs text-amber-300'
                              }
                            >
                              {isActive ? (
                                <>
                                  <CheckCircleIcon className="h-3 w-3" />
                                  Active
                                </>
                              ) : (
                                'Inactive'
                              )}
                            </span>
                          </td>
                          <td className="px-4 py-4">
                            {alzheimerMetrics?.auc_roc !== undefined ? (
                              <span className="text-emerald-400">
                                {(alzheimerMetrics.auc_roc * 100).toFixed(1)}%
                              </span>
                            ) : (
                              <span className="text-slate-500">N/A</span>
                            )}
                          </td>
                          <td className="px-4 py-4">
                            {parkinsonMetrics?.auc_roc !== undefined ? (
                              <span className="text-emerald-400">
                                {(parkinsonMetrics.auc_roc * 100).toFixed(1)}%
                              </span>
                            ) : (
                              <span className="text-slate-500">N/A</span>
                            )}
                          </td>
                          <td className="px-4 py-4">
                            {alzheimerMetrics?.accuracy !== undefined ? (
                              <span>{(alzheimerMetrics.accuracy * 100).toFixed(1)}%</span>
                            ) : (
                              <span className="text-slate-500">N/A</span>
                            )}
                          </td>
                          <td className="px-4 py-4">
                            {parkinsonMetrics?.accuracy !== undefined ? (
                              <span>{(parkinsonMetrics.accuracy * 100).toFixed(1)}%</span>
                            ) : (
                              <span className="text-slate-500">N/A</span>
                            )}
                          </td>
                          <td className="px-4 py-4 text-slate-500">
                            {new Date(model.created_at).toLocaleDateString()}
                          </td>
                          <td className="px-4 py-4">
                            {!isActive && (
                              <button
                                onClick={() => handleActivateModel(model.version)}
                                disabled={activateModelMutation.isPending}
                                className="rounded-lg bg-sky-500 px-3 py-1 text-xs font-medium text-slate-950 hover:bg-sky-400 disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                {activateModelMutation.isPending ? 'Activating...' : 'Activate'}
                              </button>
                            )}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </div>
  )
}


