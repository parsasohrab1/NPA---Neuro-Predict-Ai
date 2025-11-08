import { useMemo } from 'react'
import { ArrowUpTrayIcon, ArrowPathIcon } from '@heroicons/react/24/outline'

const models = [
  {
    id: 'alzheimers-v2',
    name: 'Alzheimer Risk v2',
    stage: 'Production',
    promotedBy: 'Leila Azimi',
    promotedAt: '2025-10-21',
    metrics: { auc: 0.942, latency: 180, drift: 22 },
  },
  {
    id: 'parkinsons-v1',
    name: 'Parkinson Early Detection',
    stage: 'Staging',
    promotedBy: 'Dr. Arman Rahimi',
    promotedAt: '2025-11-02',
    metrics: { auc: 0.903, latency: 210, drift: 12 },
  },
]

export default function ModelManagement() {
  const activeModels = useMemo(() => models.filter((model) => model.stage === 'Production').length, [])

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

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-xs uppercase text-slate-400">Active production models</div>
          <div className="mt-2 text-3xl font-semibold text-emerald-400">{activeModels}</div>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-xs uppercase text-slate-400">Pending validations</div>
          <div className="mt-2 text-3xl font-semibold text-amber-400">2</div>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-xs uppercase text-slate-400">Drift alerts</div>
          <div className="mt-2 text-3xl font-semibold text-rose-400">1</div>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <table className="min-w-full text-sm text-slate-200">
          <thead className="text-left text-xs uppercase text-slate-400">
            <tr>
              <th className="border-b border-slate-800/70 px-4 py-3">Model</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Stage</th>
              <th className="border-b border-slate-800/70 px-4 py-3">AUC</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Latency (ms)</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Drift %</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Owner</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/70">
            {models.map((model) => (
              <tr key={model.id} className="hover:bg-slate-900/50">
                <td className="px-4 py-4 text-white">{model.name}</td>
                <td className="px-4 py-4">
                  <span
                    className={
                      model.stage === 'Production'
                        ? 'rounded-full bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300'
                        : 'rounded-full bg-amber-500/20 px-2 py-1 text-xs text-amber-300'
                    }
                  >
                    {model.stage}
                  </span>
                </td>
                <td className="px-4 py-4">{model.metrics.auc.toFixed(3)}</td>
                <td className="px-4 py-4">{model.metrics.latency}</td>
                <td className="px-4 py-4">
                  <span
                    className={
                      model.metrics.drift > 30
                        ? 'text-rose-400'
                        : model.metrics.drift > 20
                        ? 'text-amber-400'
                        : 'text-emerald-400'
                    }
                  >
                    {model.metrics.drift}%
                  </span>
                </td>
                <td className="px-4 py-4 text-slate-300">{model.promotedBy}</td>
                <td className="px-4 py-4 text-slate-500">{model.promotedAt}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}


