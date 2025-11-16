import React from 'react'
import { AccessibleButton } from './AccessibleButton'

type Props = {
  targetId?: string
}

export const SkipToContent: React.FC<Props> = ({ targetId = 'main-content' }) => {
  return (
    <a
      href={`#${targetId}`}
      className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 bg-white text-blue-700 px-3 py-2 rounded shadow"
    >
      Skip to content
    </a>
  )
}


