import { NavLink } from 'react-router-dom'

const linkBase = "px-3 py-2 rounded text-sm"

export default function Sidebar() {
  return (
    <aside className="w-56 border-r bg-gray-50 h-[calc(100vh-3.5rem)] p-3">
      <div className="space-y-1">
        <NavLink to="/system" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>System Monitoring</NavLink>
        <NavLink to="/users" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>Users & Roles</NavLink>
        <NavLink to="/models" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>Models</NavLink>
        <NavLink to="/audit-logs" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>Audit Logs</NavLink>
        <NavLink to="/settings" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>Settings</NavLink>
      </div>
    </aside>
  )
}


