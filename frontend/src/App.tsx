import { Routes, Route, Navigate } from 'react-router-dom'
import { ErrorBoundary } from './components/ErrorBoundary'
import SkipToContent from './components/SkipToContent'
import { useKeyboardNavigation } from './hooks/useKeyboardNavigation'
import { useAuthStore } from './services/auth'
import Layout from './components/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PatientsPage from './pages/PatientsPage'
import PatientDetailPage from './pages/PatientDetailPage'
import PredictionPage from './pages/PredictionPage'
import PredictionResultPage from './pages/PredictionResultPage'
import SettingsPage from './pages/SettingsPage'

function App() {
  const { isAuthenticated } = useAuthStore()
  useKeyboardNavigation()

  return (
    <ErrorBoundary>
      <SkipToContent />
      <div id="main-content" tabIndex={-1} className="focus:outline-none">
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          
          {/* Protected routes */}
          <Route
            path="/"
            element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}
          >
            <Route index element={<DashboardPage />} />
            <Route path="patients" element={<PatientsPage />} />
            <Route path="patients/:id" element={<PatientDetailPage />} />
            <Route path="predictions/new" element={<PredictionPage />} />
            <Route path="predictions/:id" element={<PredictionResultPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </ErrorBoundary>
  )
}

export default App

