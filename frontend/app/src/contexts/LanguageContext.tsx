import React, { createContext, useContext, useEffect, useState } from 'react'
import i18n from '../i18n/config'

type LanguageContextValue = {
  language: string
  isRTL: boolean
  setLanguage: (lng: string) => void
}

const LanguageContext = createContext<LanguageContextValue | undefined>(undefined)

function computeIsRTL(lng: string): boolean {
  return ['fa', 'ar', 'he', 'ur'].includes(lng)
}

export const LanguageProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const [language, setLanguageState] = useState<string>(() => i18n.language || 'en')
  const [isRTL, setIsRTL] = useState<boolean>(() => computeIsRTL(language))

  const setLanguage = (lng: string) => {
    setLanguageState(lng)
    void i18n.changeLanguage(lng)
  }

  useEffect(() => {
    const dir = isRTL ? 'rtl' : 'ltr'
    const lang = language || 'en'
    const html = document.documentElement
    html.setAttribute('dir', dir)
    html.setAttribute('lang', lang)
  }, [language, isRTL])

  useEffect(() => {
    setIsRTL(computeIsRTL(language))
  }, [language])

  return (
    <LanguageContext.Provider value={{ language, isRTL, setLanguage }}>
      {children}
    </LanguageContext.Provider>
  )
}

export function useLanguage(): LanguageContextValue {
  const ctx = useContext(LanguageContext)
  if (!ctx) throw new Error('useLanguage must be used within LanguageProvider')
  return ctx
}


