import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import {
  HomeModernIcon,
  UsersIcon,
  ShieldCheckIcon,
  CpuChipIcon,
  ClipboardDocumentListIcon,
  Cog6ToothIcon,
  ArrowTrendingUpIcon,
  HeartIcon,
  ChartBarIcon,
  CubeIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'
import { useEffect } from 'react'

function SkipToContent() {
  return (
    <a
      href="#main-content"
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-slate-800 focus:text-white focus:rounded-lg focus:shadow-lg"
      aria-label="Skip to main content"
    >
      Skip to main content
    </a>
  )
}

function useKeyboardNavigation() {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && e.key.toLowerCase() === 's') {
        e.preventDefault()
        const mainContent = document.getElementById('main-content')
        if (mainContent) {
          ;(mainContent as HTMLElement).focus()
          mainContent.scrollIntoView({ behavior: 'smooth' })
        }
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault()
        const searchInput = document.querySelector<HTMLInputElement>(
          'input[type="search"], input[placeholder*="Search"], input[aria-label*="Search" i]'
        )
        if (searchInput) {
          searchInput.focus()
        }
      }
      if (e.key === 'Escape') {
        const modals = document.querySelectorAll('[role="dialog"]')
        modals.forEach((modal) => {
          const closeButton = modal.querySelector<HTMLButtonElement>(
            '[aria-label*="close" i], [data-close], [aria-label="Close"]'
          )
          if (closeButton) closeButton.click()
        })
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])
}

const navigation = [
  { name: 'System Overview', icon: HomeModernIcon, to: '/' },
  { name: 'Disease Tracking', icon: HeartIcon, to: '/disease-tracking' },
  { name: 'Data Monitoring', icon: ChartBarIcon, to: '/data-monitoring' },
  { name: '3D Analysis', icon: CubeIcon, to: '/3d-analysis' },
  { name: 'Data Fusion Reports', icon: SparklesIcon, to: '/data-fusion', highlight: true },
  { name: 'Reports', icon: ClipboardDocumentListIcon, to: '/reports' },
  { name: 'Longitudinal', icon: ArrowTrendingUpIcon, to: '/longitudinal' },
  { name: 'Users', icon: UsersIcon, to: '/users' },
  { name: 'Roles & Permissions', icon: ShieldCheckIcon, to: '/roles' },
  { name: 'Models', icon: CpuChipIcon, to: '/models' },
  { name: 'Audit Logs', icon: ClipboardDocumentListIcon, to: '/audit' },
  { name: 'System Settings', icon: Cog6ToothIcon, to: '/settings' },
]

export default function AdminLayout() {
  useKeyboardNavigation()
  const navigate = useNavigate()

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    sessionStorage.removeItem('auth_token')
    navigate('/login', { replace: true })
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <SkipToContent />
      <div className="flex min-h-screen">
        <aside
          className="hidden w-72 flex-col border-r border-slate-800 bg-slate-900 p-6 lg:flex"
          role="navigation"
          aria-label="Admin navigation"
        >
          <div className="mb-10 text-sm font-semibold uppercase tracking-widest text-slate-400">
            NeuroPredict-AI
          </div>

          <nav className="space-y-2" aria-label="Primary">
            {navigation.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition focus:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-slate-400 focus-visible:ring-offset-slate-900',
                    item.highlight && !isActive
                      ? 'bg-gradient-to-r from-purple-600/90 to-purple-700/90 text-white hover:from-purple-600 hover:to-purple-700'
                      : isActive
                      ? 'bg-slate-800 text-slate-50'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-slate-50'
                  )
                }
              >
                <item.icon className="h-5 w-5" aria-hidden="true" />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        <div className="flex w-full flex-col">
          <header
            className="flex items-center justify-between border-b border-slate-800 bg-slate-900/70 px-6 py-4 backdrop-blur"
            role="banner"
          >
            <div>
              <h1 className="text-lg font-semibold text-slate-100">
                Admin Control Center
              </h1>
              <p className="text-sm text-slate-400">
                Manage system health, users, models, and compliance
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex flex-col items-end text-xs text-slate-300">
                <span>Admin Dashboard</span>
                <span className="font-medium text-slate-100">
                  {import.meta.env.PROD ? 'Authenticated' : 'Development Mode'}
                </span>
              </div>
              <div className="rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-200">
                Admin
              </div>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium text-slate-200 hover:border-slate-500 hover:text-white"
              >
                Logout
              </button>
            </div>
          </header>

          <main
            id="main-content"
            tabIndex={-1}
            className="flex-1 bg-slate-950/70 p-6 focus:outline-none"
            role="main"
          >
            <div className="mx-auto max-w-7xl">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}


