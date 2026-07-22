import { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PatientsPage from './pages/PatientsPage'
import PatientDetailPage from './pages/PatientDetailPage'
import PredictionPage from './pages/PredictionPage'
import PredictionResultPage from './pages/PredictionResultPage'

// Lazy-loaded pages (code splitting) — reduce initial bundle size
const ReportsPage = lazy(() => import('./pages/ReportsPage'))
const LongitudinalPage = lazy(() => import('./pages/LongitudinalPage'))
const PopulationAnalysisPage = lazy(() => import('./pages/PopulationAnalysisPage'))
const ModelManagementPage = lazy(() => import('./pages/ModelManagementPage'))
const SettingsPage = lazy(() => import('./pages/SettingsPage'))

function PageLoader() {
  return (
    <div className="flex items-center justify-center min-h-[200px]">
      <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-primary-600 border-t-transparent" />
      <span className="sr-only">Loading...</span>
    </div>
  )
}

function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Layout />}>
            <Route index element={<DashboardPage />} />
            <Route path="patients" element={<PatientsPage />} />
            <Route path="patients/:id" element={<PatientDetailPage />} />
            <Route path="predictions/new" element={<PredictionPage />} />
            <Route path="predictions/:id" element={<PredictionResultPage />} />
            <Route path="reports" element={<ReportsPage />} />
            <Route path="longitudinal" element={<LongitudinalPage />} />
            <Route path="population" element={<PopulationAnalysisPage />} />
            <Route path="models" element={<ModelManagementPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </Suspense>
  )
}

export default App

