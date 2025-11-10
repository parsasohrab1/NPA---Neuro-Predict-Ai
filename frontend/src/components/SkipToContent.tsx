import React from 'react'
import { useTranslation } from 'react-i18next'

export default function SkipToContent() {
  const { t } = useTranslation()

  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary-600 focus:text-white focus:rounded-lg focus:shadow-lg"
      aria-label={t('accessibility.skipToContent')}
    >
      {t('accessibility.skipToContent')}
    </a>
  )
}

