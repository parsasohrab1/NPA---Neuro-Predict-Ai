import { Link } from 'react-router-dom'

export default function Header() {
  return (
    <header className="h-14 border-b bg-white flex items-center px-4 justify-between">
      <div className="font-semibold">NeuroPredict-AI</div>
      <nav className="flex gap-4 text-sm">
        <Link to="/dashboard" className="hover:underline">Dashboard</Link>
        <Link to="/patients" className="hover:underline">Patients</Link>
        <Link to="/predict" className="hover:underline">Analysis</Link>
        <Link to="/reports" className="hover:underline">Reports</Link>
        <Link to="/longitudinal" className="hover:underline">Longitudinal</Link>
        <Link to="/population" className="hover:underline">Population</Link>
        <Link to="/models" className="hover:underline">Models</Link>
        <Link to="/settings" className="hover:underline">Settings</Link>
      </nav>
    </header>
  )
}


