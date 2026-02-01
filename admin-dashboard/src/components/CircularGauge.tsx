interface CircularGaugeProps {
  label: string
  value: number
  min?: number
  max?: number
  unit?: string
  status?: 'normal' | 'warning' | 'critical'
}

export default function CircularGauge({
  label,
  value,
  min = 0,
  max = 100,
  unit = '',
  status = 'normal',
}: CircularGaugeProps) {
  const normalized = Math.min(max, Math.max(min, value))
  const percent = max > min ? ((normalized - min) / (max - min)) * 100 : 0
  const rotation = -90 + (percent / 100) * 180

  const statusColors = {
    normal: '#22c55e',
    warning: '#f59e0b',
    critical: '#ef4444',
  }
  const needleColor = statusColors[status]

  return (
    <div className="flex flex-col items-center p-4 rounded-xl bg-slate-900/50 border border-slate-700/80 min-w-[140px]">
      <div className="relative w-28 h-28 flex-shrink-0">
        <svg viewBox="0 0 120 120" className="w-full h-full">
          <path
            d="M 10 60 A 50 50 0 0 1 110 60"
            fill="none"
            stroke="#334155"
            strokeWidth="8"
            strokeLinecap="round"
          />
          <path
            d="M 10 60 A 50 50 0 0 1 110 60"
            fill="none"
            stroke={needleColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${(percent / 100) * 157} 157`}
          />
          <line
            x1="60"
            y1="60"
            x2="60"
            y2="20"
            stroke={needleColor}
            strokeWidth="2"
            strokeLinecap="round"
            transform={`rotate(${rotation} 60 60)`}
          />
        </svg>
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-12 bg-slate-800 text-slate-100 text-center text-sm font-semibold py-1 rounded border border-slate-600">
          {value.toFixed(1)}
        </div>
      </div>
      <span className="text-sm font-medium text-slate-200 mt-2 text-center">{label}</span>
      {unit && <span className="text-xs text-slate-500 mt-0.5">{unit}</span>}
    </div>
  )
}
