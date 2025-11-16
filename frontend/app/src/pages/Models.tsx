import { useEffect, useState } from 'react'
import { apiGet } from '../lib/api'

type RegistryModel = {
  version: string
  model_path: string
  created_at: string
  is_active?: boolean
}

export default function Models() {
  const [models, setModels] = useState<RegistryModel[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      try {
        const data = await apiGet<{ models: RegistryModel[]; current_model: RegistryModel | null }>('/admin/models')
        setModels(data.models || [])
      } catch (e) {
        setError(String(e))
      }
    })()
  }, [])

  return (
    <div className="space-y-4">
      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-2">Models</div>
        {error ? <div className="text-red-600">{error}</div> : (
          <table className="w-full text-sm">
            <thead><tr className="text-left border-b"><th className="py-2">Version</th><th>Created</th><th>Active</th></tr></thead>
            <tbody>
              {models.map(m => (
                <tr key={m.version} className="border-b">
                  <td className="py-2">{m.version}</td>
                  <td>{new Date(m.created_at).toLocaleString()}</td>
                  <td>{m.is_active ? 'Yes' : 'No'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}


