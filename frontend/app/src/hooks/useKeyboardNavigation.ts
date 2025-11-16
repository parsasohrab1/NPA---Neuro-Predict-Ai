import { useEffect } from 'react'

export function useKeyboardNavigation() {
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Example: press "g s" to go to settings
      // This is a very lightweight demo; in real apps, use a hotkeys lib.
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        // focus search if present
        const el = document.querySelector<HTMLInputElement>('[data-app-search]')
        el?.focus()
      }
    }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [])
}


