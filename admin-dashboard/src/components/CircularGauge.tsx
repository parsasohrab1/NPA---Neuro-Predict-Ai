import React from 'react'

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
  const rotation = -90 + (percent / 100) * 180 // needle: -90deg (left) to +90deg (right)

  const statusColors = {
    normal: '#22c55e',
    warning: '#f59e0b',
    critical: '#ef4444',
  }
  const needleColor = statusColors[status]

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-32 h-32">
        <svg viewBox="0 0 120 120" className="w-full h-full">
          {/* Background arc */}
          <path
            d="M 10 60 A 50 50 0 0 1 110 60"
            fill="none"
            stroke="#1e293b"
            strokeWidth="8"
            strokeLinecap="round"
          />
          {/* Value arc */}
          <path
            d="M 10 60 A 50 50 0 0 1 110 60"
            fill="none"
            stroke={needleColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={`${(percent / 100) * 157} 157`}
          />
          {/* Needle */}
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
        {/* Digital readout */}
        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-14 bg-white text-black text-center text-sm font-mono font-bold py-0.5 rounded">
          {value.toFixed(1)}
        </div>
      </div>
      <span className="text-xs text-slate-300 mt-1 text-center">{label}</span>
      {unit && <span className="text-[10px] text-slate-500">{unit}</span>}
    </div>
  )
}
