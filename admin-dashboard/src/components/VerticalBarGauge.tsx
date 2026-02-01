import React from 'react'

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
    <div className="flex flex-col items-center">
      <div className="h-24 w-8 border border-slate-600 rounded bg-slate-900 flex flex-col justify-end overflow-hidden">
        <div
          className={`w-full transition-all duration-300 ${statusColors[status]}`}
          style={{ height: `${percent}%` }}
        />
      </div>
      <span className="text-[10px] text-slate-300 mt-1 text-center leading-tight">{label}</span>
      <span className="text-xs font-mono text-white">{value.toFixed(1)}</span>
    </div>
  )
}
