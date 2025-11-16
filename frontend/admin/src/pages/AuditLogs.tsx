import { useEffect, useState } from 'react'
import { apiGet } from '../lib/api'

type AuditLog = {
  id: number
  user_id: number | null
  action: string
  resource_type?: string | null
  resource_id?: string | null
  ip_address?: string | null
  status_code?: number | null
  success: boolean
  timestamp: string
}

export default function AuditLogs() {
  const [logs, setLogs] = useState<AuditLog[]>([])
  const [action, setAction] = useState('')
  const [userId, setUserId] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchLogs = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({ limit: '100', offset: '0' })
      if (action) params.set('action', action)
      if (userId) params.set('user_id', userId)
      const data = await apiGet<AuditLog[]>(`/admin/audit-logs?${params.toString()}`)
      setLogs(data)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLogs()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className="space-y-4">
      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-2">Filters</div>
        <div className="flex gap-2">
          <input className="border rounded px-2 py-1 text-sm" placeholder="Action contains..." value={action} onChange={e=>setAction(e.target.value)} />
          <input className="border rounded px-2 py-1 text-sm" placeholder="User ID" value={userId} onChange={e=>setUserId(e.target.value)} />
          <button onClick={fetchLogs} className="px-3 py-1 text-sm bg-blue-600 text-white rounded">Apply</button>
        </div>
      </div>

      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-2">Audit Logs</div>
        {loading ? <div>Loading...</div> : error ? <div className="text-red-600">{error}</div> : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2">Time</th>
                <th>User</th>
                <th>Action</th>
                <th>Resource</th>
                <th>IP</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(l => (
                <tr key={l.id} className="border-b">
                  <td className="py-2">{new Date(l.timestamp).toLocaleString()}</td>
                  <td>{l.user_id ?? '-'}</td>
                  <td>{l.action}</td>
                  <td>{l.resource_type ?? '-'} {l.resource_id ?? ''}</td>
                  <td>{l.ip_address ?? '-'}</td>
                  <td>{l.success ? 'OK' : l.status_code ?? 'ERR'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}


