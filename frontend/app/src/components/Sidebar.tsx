import { NavLink } from 'react-router-dom'

const linkBase = "px-3 py-2 rounded text-sm"

export default function Sidebar() {
  return (
    <aside className="w-56 border-r bg-gray-50 h-[calc(100vh-3.5rem)] p-3">
      <div className="space-y-1">
        <NavLink to="/dashboard" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>داشبورد کلی</NavLink>
        <NavLink to="/patients" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>مدیریت بیماران</NavLink>
        <NavLink to="/predict" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>تحلیل و پیش‌بینی</NavLink>
        <NavLink to="/reports" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>گزارش‌ها</NavLink>
        <NavLink to="/longitudinal" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>ردیابی طولی</NavLink>
        <NavLink to="/population" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>تحلیل جمعیت</NavLink>
        <NavLink to="/models" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>مدیریت مدل‌ها</NavLink>
        <NavLink to="/settings" className={({isActive}) => `${linkBase} ${isActive ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'}`}>تنظیمات سیستم</NavLink>
      </div>
    </aside>
  )
}


