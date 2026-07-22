import { Navigate, Outlet } from 'react-router-dom'
import { useAuthStore } from '../services/auth'

/**
 * Redirects unauthenticated users to /login.
 * Use as a route element wrapping protected layout/children.
 */
export default function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
