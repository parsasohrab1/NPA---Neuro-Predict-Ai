const roleMatrix = [
  {
    role: 'Super Admin',
    permissions: ['System Monitoring', 'User Management', 'Model Deployment', 'Audit Logs', 'Critical Settings'],
  },
  {
    role: 'Operations',
    permissions: ['System Monitoring', 'Audit Logs'],
  },
  {
    role: 'Data Scientist',
    permissions: ['Model Deployment', 'Drift Analysis'],
  },
  {
    role: 'Support Analyst',
    permissions: ['System Monitoring', 'User Management (view)'],
  },
]

export default function RolesPermissions() {
  return (
    <div className="space-y-6">
      <header>
        <h2 className="text-xl font-semibold text-white">Role Access Control Matrix</h2>
        <p className="mt-1 text-sm text-slate-400">
          Prototype table to guide backend authorization policies. Replace with dynamic data in later phases.
        </p>
      </header>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <table className="min-w-full text-sm text-slate-200">
          <thead className="text-left text-xs uppercase text-slate-400">
            <tr>
              <th className="border-b border-slate-800/70 px-4 py-3">Role</th>
              <th className="border-b border-slate-800/70 px-4 py-3">Permissions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/70">
            {roleMatrix.map((row) => (
              <tr key={row.role} className="hover:bg-slate-900/50">
                <td className="px-4 py-4 text-white">{row.role}</td>
                <td className="px-4 py-4 text-slate-300">
                  <div className="flex flex-wrap gap-2">
                    {row.permissions.map((permission) => (
                      <span
                        key={permission}
                        className="rounded-full bg-slate-800/80 px-3 py-1 text-xs uppercase tracking-wide text-slate-200"
                      >
                        {permission}
                      </span>
                    ))}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
        <h3 className="text-lg font-semibold text-white">Guardrails</h3>
        <p className="mt-2 text-sm text-slate-300">
          Map frontend state management to backend RBAC claims. Super Admin should be the only role with access to
          destructive actions (model promotion, critical settings). All adjustments log to audit trail.
        </p>
      </section>
    </div>
  )
}


