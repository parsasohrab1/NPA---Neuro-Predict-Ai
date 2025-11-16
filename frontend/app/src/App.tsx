import { Navigate, Route, Routes } from 'react-router-dom'
import Header from './components/Header'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Patients from './pages/Patients'
import Predict from './pages/Predict'
import Reports from './pages/Reports'
import Longitudinal from './pages/Longitudinal'
import Population from './pages/Population'
import Models from './pages/Models'
import Settings from './pages/Settings'

export default function App() {
  return (
    <div className="h-full flex flex-col">
      <Header />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 p-4 overflow-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/patients" element={<Patients />} />
            <Route path="/predict" element={<Predict />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/longitudinal" element={<Longitudinal />} />
            <Route path="/population" element={<Population />} />
            <Route path="/models" element={<Models />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}


