import React from 'react'
import { useTheme } from '../contexts/ThemeContext'
import { AccessibleButton } from './AccessibleButton'

export const ThemeSwitcher: React.FC = () => {
  const { theme, setTheme } = useTheme()
  return (
    <div role="group" aria-label="Theme">
      <AccessibleButton
        aria-pressed={theme === 'light'}
        variant={theme === 'light' ? 'primary' : 'secondary'}
        className="mr-2"
        onClick={() => setTheme('light')}
      >
        Light
      </AccessibleButton>
      <AccessibleButton
        aria-pressed={theme === 'dark'}
        variant={theme === 'dark' ? 'primary' : 'secondary'}
        className="mr-2"
        onClick={() => setTheme('dark')}
      >
        Dark
      </AccessibleButton>
      <AccessibleButton
        aria-pressed={theme === 'system'}
        variant={theme === 'system' ? 'primary' : 'secondary'}
        onClick={() => setTheme('system')}
      >
        System
      </AccessibleButton>
    </div>
  )
}


