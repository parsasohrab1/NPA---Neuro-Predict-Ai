import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { BoltIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline'

const trendData = [
  { timestamp: '08:00', cpu: 42, memory: 55, latency: 180 },
  { timestamp: '10:00', cpu: 48, memory: 58, latency: 165 },
  { timestamp: '12:00', cpu: 51, memory: 60, latency: 175 },
  { timestamp: '14:00', cpu: 45, memory: 57, latency: 150 },
  { timestamp: '16:00', cpu: 52, memory: 63, latency: 190 },
]

const alerts = [
  {
    id: 1,
    severity: 'critical',
    title: 'Prediction latency degradation detected',
    description: 'p95 latency increased to 2.4s in the last 15 minutes',
    timestamp: '5 minutes ago',
  },
  {
    id: 2,
    severity: 'warning',
    title: 'Model drift probability trending up',
    description: 'Alzheimer model: population drift alert threshold at 65%',
    timestamp: '23 minutes ago',
  },
]

export default function SystemOverview() {
  return (
    <div className="space-y-6">
      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          { label: 'Active Users', value: '28', change: '+12%', trend: 'up' },
          { label: 'API Requests (24h)', value: '154k', change: '+4%', trend: 'up' },
          { label: 'Prediction Success Rate', value: '99.2%', change: '+0.5%', trend: 'up' },
          { label: 'Critical Alerts', value: '3', change: '-2', trend: 'down' },
        ].map((item) => (
          <div
            key={item.label}
            className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4 shadow-sm"
          >
            <div className="text-xs uppercase tracking-wide text-slate-400">{item.label}</div>
            <div className="mt-2 flex items-end justify-between">
              <div className="text-3xl font-semibold text-white">{item.value}</div>
              <div
                className={item.trend === 'up' ? 'text-emerald-400 text-sm' : 'text-rose-400 text-sm'}
              >
                {item.change}
              </div>
            </div>
          </div>
        ))}
      </section>

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">Platform Health Trends</h2>
            <span className="text-xs uppercase text-slate-400">Last 24 Hours</span>
          </div>
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
              <XAxis dataKey="timestamp" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0f172a',
                  borderColor: '#1e293b',
                  borderRadius: '12px',
                }}
              />
              <Line type="monotone" dataKey="cpu" stroke="#38bdf8" strokeWidth={2} name="CPU %" />
              <Line type="monotone" dataKey="memory" stroke="#22d3ee" strokeWidth={2} name="Memory %" />
              <Line type="monotone" dataKey="latency" stroke="#f472b6" strokeWidth={2} name="Latency (ms)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-4">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center gap-3">
              <BoltIcon className="h-6 w-6 text-amber-400" />
              <div>
                <h2 className="text-lg font-semibold text-white">Automation Feed</h2>
                <p className="text-xs text-slate-400">Recent recovery & maintenance actions</p>
              </div>
            </div>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>• Auto-scaled inference workers to handle peak load.</li>
              <li>• Scheduled drift recalibration job completed successfully.</li>
              <li>• Rotated API gateway certificates (valid until Feb 2026).</li>
            </ul>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center gap-3">
              <ExclamationTriangleIcon className="h-6 w-6 text-rose-400" />
              <div>
                <h2 className="text-lg font-semibold text-white">Active Alerts</h2>
                <p className="text-xs text-slate-400">High priority incidents requiring attention</p>
              </div>
            </div>
            <div className="mt-4 space-y-4">
              {alerts.map((alert) => (
                <div key={alert.id} className="rounded-xl border border-slate-800/70 bg-slate-900/90 p-4">
                  <div className="flex items-center justify-between text-xs uppercase tracking-wide">
                    <span
                      className={alert.severity === 'critical' ? 'text-rose-400' : 'text-amber-400'}
                    >
                      {alert.severity}
                    </span>
                    <span className="text-slate-500">{alert.timestamp}</span>
                  </div>
                  <div className="mt-2 text-sm font-medium text-white">{alert.title}</div>
                  <p className="mt-1 text-xs text-slate-400">{alert.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}


