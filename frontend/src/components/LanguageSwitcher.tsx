import React from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import { GlobeAltIcon } from '@heroicons/react/24/outline'

export default function LanguageSwitcher() {
  const { language, setLanguage } = useLanguage()

  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'fa' : 'en')
  }

  return (
    <button
      onClick={toggleLanguage}
      className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      aria-label={`Switch to ${language === 'en' ? 'Persian' : 'English'}`}
      aria-pressed={language === 'fa'}
    >
      <GlobeAltIcon className="h-5 w-5" />
      <span className="font-medium">{language === 'en' ? 'EN' : 'FA'}</span>
    </button>
  )
}

