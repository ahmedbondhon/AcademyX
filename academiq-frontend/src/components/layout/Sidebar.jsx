import { Link, useLocation, useNavigate } from 'react-router-dom'
import useAuthStore from '../../store/authStore'

const navItems = {
  student: [
    { path: '/dashboard',          label: 'Dashboard',      icon: '📊' },
    { path: '/my-progress',        label: 'My CO Progress', icon: '📈' },
    { path: '/my-risk',            label: 'My Risk Score',  icon: '⚠️'  },
  ],
  faculty: [
    { path: '/dashboard',          label: 'Dashboard',      icon: '📊' },
    { path: '/attainment',         label: 'CO Attainment',  icon: '🎯' },
    { path: '/at-risk',            label: 'At-Risk Students',icon: '🔴' },
    { path: '/upload',             label: 'Upload Marks',   icon: '📤' },
  ],
  dean: [
    { path: '/dashboard',          label: 'Dashboard',      icon: '📊' },
    { path: '/all-courses',        label: 'All Courses',    icon: '🏫' },
    { path: '/po-attainment',      label: 'PO Attainment',  icon: '🎓' },
    { path: '/reports',            label: 'Generate Report',icon: '📄' },
  ],
  admin: [
    { path: '/dashboard',          label: 'Dashboard',      icon: '📊' },
  ],
}

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const location         = useLocation()
  const navigate         = useNavigate()
  const items            = navItems[user?.role] || navItems.student

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside className="w-64 min-h-screen bg-brand-800 text-white flex flex-col">

      {/* Logo */}
      <div className="p-6 border-b border-brand-700">
        <h1 className="text-xl font-bold text-white">AcademiQ</h1>
        <p className="text-brand-100 text-xs mt-1">
          OBE Intelligence Platform
        </p>
      </div>

      {/* User info */}
      <div className="p-4 border-b border-brand-700">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-full bg-brand-600 flex items-center
                          justify-center text-sm font-bold">
            {user?.name?.charAt(0) || '?'}
          </div>
          <div>
            <p className="text-sm font-medium text-white truncate w-36">
              {user?.name}
            </p>
            <p className="text-xs text-brand-200 capitalize">{user?.role}</p>
          </div>
        </div>
      </div>

      {/* Nav items */}
      <nav className="flex-1 p-4 space-y-1">
        {items.map((item) => {
          const active = location.pathname === item.path
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg
                          text-sm transition-all duration-150
                          ${active
                            ? 'bg-white text-brand-800 font-semibold'
                            : 'text-brand-100 hover:bg-brand-700'
                          }`}
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="p-4 border-t border-brand-700">
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg
                     text-sm text-brand-200 hover:bg-brand-700 transition-all"
        >
          <span>🚪</span> Logout
        </button>
      </div>
    </aside>
  )
}