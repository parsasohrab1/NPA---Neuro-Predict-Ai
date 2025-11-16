import { Navigate, Route, Routes } from 'react-router-dom'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import SystemMonitoring from './pages/SystemMonitoring'
import UsersRoles from './pages/UsersRoles'
import Models from './pages/Models'
import AuditLogs from './pages/AuditLogs'
import Settings from './pages/Settings'

export default function App() {
  return (
    <div className="h-full flex flex-col">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-4 overflow-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/system" replace />} />
            <Route path="/system" element={<SystemMonitoring />} />
            <Route path="/users" element={<UsersRoles />} />
            <Route path="/models" element={<Models />} />
            <Route path="/audit-logs" element={<AuditLogs />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}


