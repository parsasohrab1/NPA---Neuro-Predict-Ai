import React from 'react'
import clsx from 'clsx'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'primary' | 'secondary' | 'ghost'
}

const base =
  'inline-flex items-center justify-center rounded px-3 py-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-blue-500'

export const AccessibleButton: React.FC<Props> = ({ variant = 'primary', className, ...props }) => {
  const styles =
    variant === 'primary'
      ? 'bg-blue-600 text-white hover:bg-blue-700'
      : variant === 'secondary'
      ? 'bg-gray-200 text-gray-900 hover:bg-gray-300'
      : 'bg-transparent text-blue-600 hover:bg-blue-50'
  return <button {...props} className={clsx(base, styles, className)} />
}


