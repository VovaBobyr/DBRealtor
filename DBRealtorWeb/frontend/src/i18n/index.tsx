import { createContext, useContext, useState } from 'react'
import type { Lang, Translations } from './types'
import { cs } from './cs'
import { en } from './en'
import { ua } from './ua'

const STORAGE_KEY = 'dbrealtor_lang'

const translations: Record<Lang, Translations> = { cs, en, ua }

function getInitialLang(): Lang {
  const stored = localStorage.getItem(STORAGE_KEY)
  if (stored === 'cs' || stored === 'en' || stored === 'ua') return stored
  return 'cs'
}

interface LangContextValue {
  lang: Lang
  setLang: (l: Lang) => void
  t: Translations
}

const LangContext = createContext<LangContextValue>({
  lang: 'cs',
  setLang: () => {},
  t: cs,
})

export function LangProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>(getInitialLang)

  function setLang(l: Lang) {
    setLangState(l)
    localStorage.setItem(STORAGE_KEY, l)
  }

  return (
    <LangContext.Provider value={{ lang, setLang, t: translations[lang] }}>
      {children}
    </LangContext.Provider>
  )
}

export function useLang() {
  return useContext(LangContext)
}
