import { createBrowserRouter, Navigate } from 'react-router-dom'

import AdminLayout from './layouts/AdminLayout'
import SystemOverview from './pages/SystemOverview'
import UsersManagement from './pages/UsersManagement'
import RolesPermissions from './pages/RolesPermissions'
import ModelManagement from './pages/ModelManagement'
import AuditLogs from './pages/AuditLogs'
import SystemSettings from './pages/SystemSettings'
import ReportsPage from './pages/ReportsPage'
import LongitudinalTrackingPage from './pages/LongitudinalTrackingPage'
import DiseaseTrackingDashboard from './pages/DiseaseTrackingDashboard'
import DataMonitoringPage from './pages/DataMonitoringPage'
import Analysis3DPage from './pages/Analysis3DPage'
import DataFusionReportsPage from './pages/DataFusionReportsPage'
import LoginPage from './pages/LoginPage'
import TestPage from './pages/TestPage'

// Protected Route wrapper (disabled)
// function ProtectedRoute({ children }: { children: React.ReactNode }) {
//   const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
//   
//   if (!token) {
//     return <Navigate to="/login" replace />
//   }
//   
//   return <>{children}</>
// }

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: <AdminLayout />,
    children: [
      { index: true, element: <SystemOverview /> },
      { path: 'reports', element: <ReportsPage /> },
      { path: 'longitudinal', element: <LongitudinalTrackingPage /> },
      { path: 'disease-tracking', element: <DiseaseTrackingDashboard /> },
      { path: 'data-monitoring', element: <DataMonitoringPage /> },
      { path: '3d-analysis', element: <Analysis3DPage /> },
      { path: 'data-fusion', element: <DataFusionReportsPage /> },
      { path: 'users', element: <UsersManagement /> },
      { path: 'roles', element: <RolesPermissions /> },
      { path: 'models', element: <ModelManagement /> },
      { path: 'audit', element: <AuditLogs /> },
      { path: 'settings', element: <SystemSettings /> },
      { path: 'test', element: <TestPage /> },
    ],
  },
])


