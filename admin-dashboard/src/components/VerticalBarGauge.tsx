interface VerticalBarGaugeProps {
  label: string
  value: number
  min?: number
  max?: number
  status?: 'normal' | 'warning' | 'critical'
}

export default function VerticalBarGauge({
  label,
  value,
  min = 0,
  max = 100,
  status = 'normal',
}: VerticalBarGaugeProps) {
  const normalized = Math.min(max, Math.max(min, value))
  const percent = max > min ? ((normalized - min) / (max - min)) * 100 : 0

  const statusColors = {
    normal: 'bg-emerald-500',
    warning: 'bg-amber-500',
    critical: 'bg-rose-500',
  }

  return (
    <div className="flex flex-col items-center min-w-[56px]">
      <div className="h-28 w-10 border border-slate-600 rounded-lg bg-slate-900 flex flex-col justify-end overflow-hidden">
        <div
          className={`w-full min-h-[4px] transition-all duration-300 ${statusColors[status]}`}
          style={{ height: `${Math.max(percent, 2)}%` }}
        />
      </div>
      <span className="text-xs font-medium text-slate-300 mt-2 text-center leading-tight">{label}</span>
      <span className="text-sm font-mono text-slate-100 mt-1">{value.toFixed(1)}</span>
    </div>
  )
}
