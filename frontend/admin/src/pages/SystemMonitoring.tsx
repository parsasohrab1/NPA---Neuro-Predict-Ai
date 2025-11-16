import { useEffect, useState } from 'react'
import { apiGet } from '../lib/api'

type Overview = {
  health: any
  metrics: Record<string, number>
  counts: { users: number; patients: number; predictions: number }
  recent_alerts: Array<{ id: number; event_type: string; severity: string; timestamp: string; description?: string }>
}

export default function SystemMonitoring() {
  const [data, setData] = useState<Overview | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    apiGet<Overview>('/admin/system/overview')
      .then(setData)
      .catch((e) => setError(String(e)))
  }, [])

  if (error) return <div className="text-red-600">Error: {error}</div>
  if (!data) return <div>Loading...</div>

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 border rounded bg-white">
          <div className="text-sm text-gray-600">Users</div>
          <div className="text-2xl font-semibold">{data.counts.users}</div>
        </div>
        <div className="p-4 border rounded bg-white">
          <div className="text-sm text-gray-600">Patients</div>
          <div className="text-2xl font-semibold">{data.counts.patients}</div>
        </div>
        <div className="p-4 border rounded bg-white">
          <div className="text-sm text-gray-600">Predictions</div>
          <div className="text-2xl font-semibold">{data.counts.predictions}</div>
        </div>
      </div>

      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-2">System Health</div>
        <pre className="text-xs overflow-auto">{JSON.stringify(data.health, null, 2)}</pre>
      </div>

      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-2">Recent Alerts</div>
        <ul className="text-sm space-y-1">
          {data.recent_alerts.map((a) => (
            <li key={a.id} className="flex items-center justify-between">
              <span className="mr-2 inline-flex items-center rounded px-2 py-0.5 text-xs border">
                {a.severity}
              </span>
              <span className="flex-1 px-2">{a.event_type}</span>
              <span className="text-gray-500">{new Date(a.timestamp).toLocaleString()}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}


