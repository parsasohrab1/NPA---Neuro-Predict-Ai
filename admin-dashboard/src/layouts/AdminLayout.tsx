import { NavLink, Outlet } from 'react-router-dom'
import {
  HomeModernIcon,
  UsersIcon,
  ShieldCheckIcon,
  CpuChipIcon,
  ClipboardDocumentListIcon,
  Cog6ToothIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline'
import clsx from 'clsx'

const navigation = [
  { name: 'System Overview', icon: HomeModernIcon, to: '/' },
  { name: 'Reports', icon: ClipboardDocumentListIcon, to: '/reports' },
  { name: 'Longitudinal', icon: ArrowTrendingUpIcon, to: '/longitudinal' },
  { name: 'Users', icon: UsersIcon, to: '/users' },
  { name: 'Roles & Permissions', icon: ShieldCheckIcon, to: '/roles' },
  { name: 'Models', icon: CpuChipIcon, to: '/models' },
  { name: 'Audit Logs', icon: ClipboardDocumentListIcon, to: '/audit' },
  { name: 'System Settings', icon: Cog6ToothIcon, to: '/settings' },
]

export default function AdminLayout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="flex min-h-screen">
        <aside className="hidden w-72 flex-col border-r border-slate-800 bg-slate-900 p-6 lg:flex">
          <div className="mb-10 text-sm font-semibold uppercase tracking-widest text-slate-400">
            NeuroPredict-AI
          </div>

          <nav className="space-y-2">
            {navigation.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  clsx(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition',
                    isActive
                      ? 'bg-slate-800 text-slate-50'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-slate-50'
                  )
                }
              >
                <item.icon className="h-5 w-5" aria-hidden />
                <span>{item.name}</span>
              </NavLink>
            ))}
          </nav>
        </aside>

        <div className="flex w-full flex-col">
          <header className="flex items-center justify-between border-b border-slate-800 bg-slate-900/70 px-6 py-4 backdrop-blur">
            <div>
              <h1 className="text-lg font-semibold text-slate-100">
                Admin Control Center
              </h1>
              <p className="text-sm text-slate-400">
                Manage system health, users, models, and compliance
              </p>
            </div>
            <div className="flex items-center gap-2">
              <div className="flex flex-col items-end text-xs text-slate-300">
                <span>Logged in as</span>
                <span className="font-medium text-slate-100">super.admin@neuropredict.ai</span>
              </div>
              <div className="rounded-full bg-slate-800 px-3 py-1 text-xs font-semibold text-slate-200">
                Super Admin
              </div>
            </div>
          </header>

          <main className="flex-1 bg-slate-950/70 p-6">
            <div className="mx-auto max-w-7xl">
              <Outlet />
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}


