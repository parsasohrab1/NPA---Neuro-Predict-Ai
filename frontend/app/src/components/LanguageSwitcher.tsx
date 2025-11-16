import React from 'react'
import { useLanguage } from '../contexts/LanguageContext'
import { AccessibleButton } from './AccessibleButton'

export const LanguageSwitcher: React.FC = () => {
  const { language, setLanguage } = useLanguage()
  return (
    <div role="group" aria-label="Language">
      <AccessibleButton
        aria-pressed={language.startsWith('en')}
        variant={language.startsWith('en') ? 'primary' : 'secondary'}
        className="mr-2"
        onClick={() => setLanguage('en')}
      >
        English
      </AccessibleButton>
      <AccessibleButton
        aria-pressed={language.startsWith('fa')}
        variant={language.startsWith('fa') ? 'primary' : 'secondary'}
        onClick={() => setLanguage('fa')}
      >
        فارسی
      </AccessibleButton>
    </div>
  )
}


