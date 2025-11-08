const logs = [
  {
    id: 'evt-3012',
    timestamp: '2025-11-07 14:32',
    actor: 'super.admin@neuropredict.ai',
    action: 'MODEL_PROMOTE',
    resource: 'Alzheimer Risk v2',
    outcome: 'success',
    severity: 'high',
  },
  {
    id: 'evt-3013',
    timestamp: '2025-11-07 13:18',
    actor: 'automation@neuropredict.ai',
    action: 'DRIFT_ALERT_CREATE',
    resource: 'Parkinson Early Detection',
    outcome: 'success',
    severity: 'critical',
  },
  {
    id: 'evt-3014',
    timestamp: '2025-11-07 12:50',
    actor: 'support@neuropredict.ai',
    action: 'USER_DISABLE',
    resource: 'user:3241',
    outcome: 'success',
    severity: 'medium',
  },
]

export default function AuditLogs() {
  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-xl font-semibold text-white">Audit & Compliance Logs</h2>
        <p className="mt-1 text-sm text-slate-400">
          Centralized viewer mocking API response. Replace with server pagination & filters in the implementation phase.
        </p>
      </header>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <table className="min-w-full text-sm text-slate-200">
          <thead className="text-left text-xs uppercase text-slate-400">
            <tr>
              <th className="border-b border-slate-800/70 px-4 py-3">Timestamp</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Actor</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Action</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Resource</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Outcome</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Severity</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/70">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-slate-900/50">
                <td className="px-4 py-4 text-slate-300">{log.timestamp}</td>
                <td className="px-4 py-4">{log.actor}</td>
                <td className="px-4 py-4">{log.action}</td>
                <td className="px-4 py-4 text-slate-300">{log.resource}</td>
                <td className="px-4 py-4">
                  <span className="rounded-full bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300">
                    {log.outcome}
                  </span>
                </td>
                <td className="px-4 py-4">
                  <span
                    className={
                      log.severity === 'critical'
                        ? 'text-rose-400'
                        : log.severity === 'high'
                        ? 'text-amber-400'
                        : 'text-sky-400'
                    }
                  >
                    {log.severity}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6 text-sm text-slate-300">
        <h3 className="text-lg font-semibold text-white">Export & Retention Strategy</h3>
        <ul className="mt-3 space-y-2 text-sm">
          <li>• API should support cursor-based pagination and filtering by actor, action, severity, outcome.</li>
          <li>• Export options: CSV for analytics, JSON for compliance snapshots.</li>
          <li>• Log retention configurable per regulation (HIPAA, GDPR) via System Settings.</li>
        </ul>
      </section>
    </div>
  )
}


