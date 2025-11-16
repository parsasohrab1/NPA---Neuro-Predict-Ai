import React from 'react'
import { ThemeSwitcher } from '../components/ThemeSwitcher'
import { LanguageSwitcher } from '../components/LanguageSwitcher'
import { AccessibleButton } from '../components/AccessibleButton'
import { useNotifications } from '../contexts/NotificationContext'
import { useKeyboardNavigation } from '../hooks/useKeyboardNavigation'

export const SettingsPage: React.FC = () => {
  const { success } = useNotifications()
  useKeyboardNavigation()

  return (
    <main id="main-content" className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Settings</h1>
      <section>
        <h2 className="text-xl mb-2">Theme</h2>
        <ThemeSwitcher />
      </section>
      <section>
        <h2 className="text-xl mb-2">Language</h2>
        <LanguageSwitcher />
      </section>
      <section>
        <h2 className="text-xl mb-2">Notifications</h2>
        <AccessibleButton onClick={() => success('Saved successfully!')}>Test Success</AccessibleButton>
      </section>
    </main>
  )
}


