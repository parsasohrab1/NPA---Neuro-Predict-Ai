import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../services/auth'

export default function Layout() {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-primary-900 text-white flex flex-col">
        <div className="p-6">
          <h1 className="text-2xl font-bold">🧠 NeuroPredict-AI</h1>
          <p className="text-primary-200 text-sm mt-1">Neurodegenerative Disease Prediction</p>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          <Link
            to="/"
            className="block px-4 py-3 rounded-lg hover:bg-primary-800 transition-colors"
          >
            📊 Dashboard
          </Link>
          <Link
            to="/patients"
            className="block px-4 py-3 rounded-lg hover:bg-primary-800 transition-colors"
          >
            👥 Patients
          </Link>
          <Link
            to="/predictions/new"
            className="block px-4 py-3 rounded-lg hover:bg-primary-800 transition-colors"
          >
            🔬 New Prediction
          </Link>
        </nav>

        <div className="p-4 border-t border-primary-800">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-10 h-10 bg-primary-700 rounded-full flex items-center justify-center">
              {user?.full_name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">{user?.full_name}</p>
              <p className="text-xs text-primary-300 truncate">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 bg-primary-800 hover:bg-primary-700 rounded-lg text-sm transition-colors"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

