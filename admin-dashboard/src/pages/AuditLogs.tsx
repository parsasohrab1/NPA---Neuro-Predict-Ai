import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { monitoringApi } from '../services/api'

type AuditLogRow = {
  id: number
  timestamp: string
  user_id?: number | null
  action: string
  resource_type?: string | null
  resource_id?: string | number | null
  ip_address?: string | null
  status_code?: number | null
  success?: boolean
  is_high_risk?: boolean
}

export default function AuditLogs() {
  const [hours, setHours] = useState(24)
  const [actionType, setActionType] = useState('')

  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ['audit-logs', hours, actionType],
    queryFn: async () => {
      const res = await monitoringApi.getAuditLogs(
        100,
        actionType || undefined,
        hours
      )
      return res.data as {
        logs: AuditLogRow[]
        high_risk_count: number
        total_count: number
      }
    },
  })

  const logs = data?.logs ?? []

  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-xl font-semibold text-white">Audit & Compliance Logs</h2>
        <p className="mt-1 text-sm text-slate-400">
          Live data from <code className="text-slate-300">GET /api/v1/monitoring/security/audit-logs</code>
        </p>
      </header>

      <section className="flex flex-wrap items-end gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-xs uppercase text-slate-400">Hours</span>
          <select
            value={hours}
            onChange={(e) => setHours(Number(e.target.value))}
            className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white"
          >
            <option value={6}>6</option>
            <option value={24}>24</option>
            <option value={72}>72</option>
            <option value={168}>168</option>
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-xs uppercase text-slate-400">Action type (optional)</span>
          <input
            type="text"
            value={actionType}
            onChange={(e) => setActionType(e.target.value)}
            placeholder="e.g. login"
            className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white"
          />
        </label>
        <button
          type="button"
          onClick={() => refetch()}
          className="rounded-lg bg-sky-500 px-4 py-2 text-sm font-medium text-slate-950 hover:bg-sky-400"
        >
          {isFetching ? 'Refreshing...' : 'Refresh'}
        </button>
        <div className="ml-auto text-sm text-slate-400">
          Total: <span className="text-white">{data?.total_count ?? 0}</span>
          {' · '}
          High risk: <span className="text-amber-400">{data?.high_risk_count ?? 0}</span>
        </div>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        {isLoading ? (
          <p className="text-sm text-slate-400">Loading audit logs...</p>
        ) : error ? (
          <p className="text-sm text-rose-400">
            Failed to load audit logs. Ensure you are authenticated as admin.
          </p>
        ) : logs.length === 0 ? (
          <p className="text-sm text-slate-400">No audit logs in the selected window.</p>
        ) : (
          <table className="min-w-full text-sm text-slate-200">
            <thead className="text-left text-xs uppercase text-slate-400">
              <tr>
                <th className="border-b border-slate-800/70 px-4 py-3">Timestamp</th>
                <th className="border-b border-slate-800/70 px-4 py-3">User</th>
                <th className="border-b border-slate-800/70 px-4 py-3">Action</th>
                <th className="border-b border-slate-800/70 px-4 py-3">Resource</th>
                <th className="border-b border-slate-800/70 px-4 py-3">Outcome</th>
                <th className="border-b border-slate-800/70 px-4 py-3">Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/70">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-slate-900/50">
                  <td className="px-4 py-4 text-slate-300">
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-4 py-4">{log.user_id ?? '—'}</td>
                  <td className="px-4 py-4">{log.action}</td>
                  <td className="px-4 py-4 text-slate-300">
                    {[log.resource_type, log.resource_id].filter(Boolean).join(':') || '—'}
                  </td>
                  <td className="px-4 py-4">
                    <span
                      className={
                        log.success
                          ? 'rounded-full bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300'
                          : 'rounded-full bg-rose-500/20 px-2 py-1 text-xs text-rose-300'
                      }
                    >
                      {log.success ? 'success' : 'failure'}
                      {log.status_code != null ? ` (${log.status_code})` : ''}
                    </span>
                  </td>
                  <td className="px-4 py-4">
                    <span className={log.is_high_risk ? 'text-rose-400' : 'text-sky-400'}>
                      {log.is_high_risk ? 'high' : 'normal'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </div>
  )
}
