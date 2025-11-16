import { useEffect, useState } from 'react'
import { apiGet, apiPost } from '../lib/api'

type RegistryModel = {
  version: string
  model_path: string
  created_at: string
  metrics?: Record<string, number | string>
  description?: string
  is_active?: boolean
}

export default function Models() {
  const [models, setModels] = useState<RegistryModel[]>([])
  const [current, setCurrent] = useState<RegistryModel | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setError(null)
    try {
      const data = await apiGet<{ models: RegistryModel[]; current_model: RegistryModel | null }>('/admin/models')
      setModels(data.models || [])
      setCurrent(data.current_model || null)
    } catch (e) {
      setError(String(e))
    }
  }

  useEffect(() => {
    load()
  }, [])

  const activate = async (version: string) => {
    try {
      await apiPost('/admin/models/activate', { version })
      await load()
    } catch (e) {
      setError(String(e))
    }
  }

  return (
    <div className="space-y-4">
      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-2">Active Model</div>
        {current ? (
          <div className="text-sm">
            <div><span className="font-medium">Version:</span> {current.version}</div>
            <div><span className="font-medium">Path:</span> {current.model_path}</div>
            <div className="mt-1"><span className="font-medium">Metrics:</span> <pre className="inline">{JSON.stringify(current.metrics || {}, null, 2)}</pre></div>
          </div>
        ) : <div className="text-sm text-gray-600">No active model</div>}
      </div>

      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-2">All Models</div>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left border-b">
              <th className="py-2">Version</th>
              <th>Created</th>
              <th>Active</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {models.map(m => (
              <tr key={m.version} className="border-b">
                <td className="py-2">{m.version}</td>
                <td>{new Date(m.created_at).toLocaleString()}</td>
                <td>{m.is_active ? 'Yes' : 'No'}</td>
                <td>
                  {!m.is_active && (
                    <button onClick={() => activate(m.version)} className="px-2 py-1 text-xs border rounded">Activate</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {error && <div className="text-red-600 mt-2">{error}</div>}
      </div>
    </div>
  )
}


