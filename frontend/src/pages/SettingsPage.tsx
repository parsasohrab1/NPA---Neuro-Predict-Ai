import React from 'react'
import { useTranslation } from 'react-i18next'
import { useTheme } from '../contexts/ThemeContext'
import { useLanguage } from '../contexts/LanguageContext'
import ThemeSwitcher from '../components/ThemeSwitcher'
import LanguageSwitcher from '../components/LanguageSwitcher'
import { Cog6ToothIcon } from '@heroicons/react/24/outline'

export default function SettingsPage() {
  const { t } = useTranslation()
  const { theme, actualTheme } = useTheme()
  const { language, isRTL } = useLanguage()

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Cog6ToothIcon className="h-8 w-8 text-primary-600" />
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{t('nav.settings')}</h1>
        </div>
        <p className="text-gray-600 dark:text-gray-400">Customize your experience</p>
      </div>

      <div className="space-y-6">
        {/* Appearance Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Appearance</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Theme
              </label>
              <ThemeSwitcher />
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Current theme: <span className="font-medium">{theme}</span> ({actualTheme})
              </p>
            </div>
          </div>
        </section>

        {/* Language Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Language</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Interface Language
              </label>
              <LanguageSwitcher />
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Current language: <span className="font-medium">{language.toUpperCase()}</span>
                {isRTL && ' (RTL)'}
              </p>
            </div>
          </div>
        </section>

        {/* Accessibility Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Accessibility</h2>
          <div className="space-y-4">
            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Keyboard Shortcuts</h3>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">Alt</kbd> +{' '}
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">S</kbd> - Skip to main content
                </li>
                <li>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">Ctrl</kbd> /{' '}
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">Cmd</kbd> +{' '}
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">K</kbd> - Focus search
                </li>
                <li>
                  <kbd className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded">Esc</kbd> - Close modals
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* About Section */}
        <section className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">About</h2>
          <div className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
            <p>
              <strong className="text-gray-900 dark:text-white">NeuroPredict-AI</strong> v1.0.0
            </p>
            <p>AI-Powered Neurodegenerative Disease Prediction System</p>
            <p className="mt-4">
              <a
                href="/docs/USER_GUIDE.md"
                className="text-primary-600 dark:text-primary-400 hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                User Guide
              </a>
              {' • '}
              <a
                href="/docs/DEVELOPER_GUIDE.md"
                className="text-primary-600 dark:text-primary-400 hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                Developer Guide
              </a>
            </p>
          </div>
        </section>
      </div>
    </div>
  )
}

