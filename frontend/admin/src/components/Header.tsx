import { Link } from 'react-router-dom'

export default function Header() {
  return (
    <header className="h-14 border-b bg-white flex items-center px-4 justify-between">
      <div className="font-semibold">NeuroPredict-AI Admin</div>
      <nav className="flex gap-4 text-sm">
        <Link to="/system" className="hover:underline">System</Link>
        <Link to="/users" className="hover:underline">Users</Link>
        <Link to="/models" className="hover:underline">Models</Link>
        <Link to="/audit-logs" className="hover:underline">Audit Logs</Link>
        <Link to="/settings" className="hover:underline">Settings</Link>
      </nav>
    </header>
  )
}


