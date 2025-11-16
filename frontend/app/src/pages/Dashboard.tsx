import { useEffect, useState } from 'react'
import { apiGet } from '../lib/api'

type Metrics = { metrics: Record<string, number> }
type SecurityLog = { id: number; event_type: string; severity: string; timestamp: string }

export default function Dashboard() {
  const [metrics, setMetrics] = useState<Metrics['metrics']>({})
  const [alerts, setAlerts] = useState<SecurityLog[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      try {
        const m = await apiGet<{ metrics: Record<string, number> }>('/monitoring/metrics')
        setMetrics(m.metrics || {})
      } catch (e) {
        setError(String(e))
      }
      try {
        const logs = await apiGet<SecurityLog[]>('/security/logs?limit=10&offset=0')
        setAlerts(logs.filter(l => ['warning','error','critical'].includes(l.severity)))
      } catch {
        /* ignore if unauthorized for non-admins */
      }
    })()
  }, [])

  return (
    <div className="space-y-4">
      {error && <div className="text-red-600">{error}</div>}

      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 border rounded bg-white">
          <div className="text-sm text-gray-600">CPU Usage</div>
          <div className="text-2xl font-semibold">{metrics.cpu_usage_percent ?? '-'}%</div>
        </div>
        <div className="p-4 border rounded bg-white">
          <div className="text-sm text-gray-600">Memory Usage</div>
          <div className="text-2xl font-semibold">{metrics.memory_usage_percent ?? '-'}%</div>
        </div>
        <div className="p-4 border rounded bg-white">
          <div className="text-sm text-gray-600">Disk Usage</div>
          <div className="text-2xl font-semibold">{metrics.disk_usage_percent ?? '-'}%</div>
        </div>
      </div>

      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-2">System Metrics</div>
        <pre className="text-xs overflow-auto">{JSON.stringify(metrics, null, 2)}</pre>
      </div>

      {alerts.length > 0 && (
        <div className="p-4 border rounded bg-white">
          <div className="font-semibold mb-2">Urgent Alerts</div>
          <ul className="text-sm space-y-1">
            {alerts.map(a => (
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
      )}
    </div>
  )
}


