import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute from './components/layout/ProtectedRoute'
import Login              from './pages/Login'
import FacultyDashboard   from './pages/faculty/FacultyDashboard'
import UploadMarksheet    from './pages/faculty/UploadMarksheet'
import DeanDashboard      from './pages/dean/DeanDashboard'
import StudentDashboard   from './pages/student/StudentDashboard'
import useAuthStore       from './store/authStore'

function RoleRouter() {
  const { user } = useAuthStore()
  const roleHome = {
    faculty: '/dashboard',
    dean:    '/dashboard',
    student: '/dashboard',
    admin:   '/dashboard',
  }
  return <Navigate to={roleHome[user?.role] || '/login'} replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />

        {/* Faculty routes */}
        <Route path="/dashboard" element={
          <ProtectedRoute allowedRoles={['faculty', 'dean', 'student', 'admin']}>
            <RoleBasedDashboard />
          </ProtectedRoute>
        }/>

        <Route path="/upload" element={
          <ProtectedRoute allowedRoles={['faculty', 'admin']}>
            <UploadMarksheet />
          </ProtectedRoute>
        }/>

        <Route path="/all-courses" element={
          <ProtectedRoute allowedRoles={['dean', 'admin']}>
            <DeanDashboard />
          </ProtectedRoute>
        }/>

        <Route path="/" element={<RoleRouter />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

function RoleBasedDashboard() {
  const { user } = useAuthStore()
  if (user?.role === 'faculty') return <FacultyDashboard />
  if (user?.role === 'dean')    return <DeanDashboard />
  if (user?.role === 'student') return <StudentDashboard />
  return <FacultyDashboard />
}