import { Routes, Route, NavLink } from 'react-router-dom'
import { Home } from 'lucide-react'
import { useLang } from './i18n'
import type { Lang } from './i18n/types'
import Dashboard from './pages/Dashboard'
import Trends from './pages/Trends'
import Listings from './pages/Listings'
import Alerts from './pages/Alerts'

const LANGS: { code: Lang; label: string }[] = [
  { code: 'cs', label: 'CZ' },
  { code: 'en', label: 'EN' },
  { code: 'ua', label: 'UA' },
]

export default function App() {
  const { lang, setLang, t } = useLang()

  const navItems = [
    { to: '/', label: t.nav.dashboard },
    { to: '/trends', label: t.nav.trends },
    { to: '/listings', label: t.nav.listings },
    { to: '/alerts', label: t.nav.alerts },
  ]

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 flex items-center justify-between">
          <div className="flex items-center gap-2 py-4">
            <div className="w-7 h-7 bg-gray-900 rounded-md flex items-center justify-center flex-shrink-0">
              <Home size={13} className="text-white" />
            </div>
            <span className="text-sm font-semibold text-gray-900 tracking-tight">DBRealtor</span>
          </div>

          <nav className="flex items-end h-full">
            {navItems.map(({ to, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  `px-4 py-4 text-sm font-medium border-b-2 transition-colors ${
                    isActive
                      ? 'border-gray-900 text-gray-900'
                      : 'border-transparent text-gray-500 hover:text-gray-800 hover:border-gray-300'
                  }`
                }
              >
                {label}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-3">
            {/* Language switcher */}
            <div className="flex items-center gap-0.5">
              {LANGS.map(({ code, label }) => (
                <button
                  key={code}
                  onClick={() => setLang(code)}
                  className={`px-2 py-1 rounded text-xs font-semibold transition-colors ${
                    lang === code
                      ? 'bg-gray-900 text-white'
                      : 'text-gray-400 hover:text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
              <span className="text-xs font-bold text-white select-none">VB</span>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/trends" element={<Trends />} />
          <Route path="/listings" element={<Listings />} />
          <Route path="/alerts" element={<Alerts />} />
        </Routes>
      </main>
    </div>
  )
}
