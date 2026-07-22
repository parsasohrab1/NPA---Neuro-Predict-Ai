import { Navigate, Outlet, useLocation } from 'react-router-dom'

function getAuthToken(): string | null {
  return localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
}

/**
 * Protects AdminLayout children — redirects to /login when no token.
 */
export default function ProtectedRoute() {
  const location = useLocation()
  const token = getAuthToken()

  if (!token) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return <Outlet />
}
