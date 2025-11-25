import { createBrowserRouter } from 'react-router-dom'

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
import TestPage from './pages/TestPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AdminLayout />,
    children: [
      { index: true, element: <SystemOverview /> },
      { path: 'reports', element: <ReportsPage /> },
      { path: 'longitudinal', element: <LongitudinalTrackingPage /> },
      { path: 'disease-tracking', element: <DiseaseTrackingDashboard /> },
      { path: 'users', element: <UsersManagement /> },
      { path: 'roles', element: <RolesPermissions /> },
      { path: 'models', element: <ModelManagement /> },
      { path: 'audit', element: <AuditLogs /> },
      { path: 'settings', element: <SystemSettings /> },
      { path: 'test', element: <TestPage /> },
    ],
  },
])


