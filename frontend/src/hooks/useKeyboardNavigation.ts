import { useEffect, useCallback } from 'react'

export function useKeyboardNavigation() {
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    // Skip to content: Alt + S
    if (e.altKey && e.key === 's') {
      e.preventDefault()
      const mainContent = document.getElementById('main-content')
      if (mainContent) {
        mainContent.focus()
        mainContent.scrollIntoView({ behavior: 'smooth' })
      }
    }

    // Search: Ctrl/Cmd + K
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault()
      const searchInput = document.querySelector<HTMLInputElement>('input[type="search"], input[placeholder*="Search"]')
      if (searchInput) {
        searchInput.focus()
      }
    }

    // Escape to close modals
    if (e.key === 'Escape') {
      const modals = document.querySelectorAll('[role="dialog"]')
      modals.forEach((modal) => {
        if (modal instanceof HTMLElement && modal.style.display !== 'none') {
          const closeButton = modal.querySelector<HTMLButtonElement>('[aria-label*="close" i], [aria-label*="Close"]')
          if (closeButton) {
            closeButton.click()
          }
        }
      })
    }
  }, [])

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [handleKeyDown])
}

