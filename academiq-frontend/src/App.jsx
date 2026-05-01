import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import ProtectedRoute   from './components/layout/ProtectedRoute'
import useAuthStore     from './store/authStore'

// Auth
import Login            from './pages/Login'

// Faculty
import FacultyDashboard from './pages/faculty/FacultyDashboard'
import COAttainment     from './pages/faculty/COAttainment'
import AtRiskStudents   from './pages/faculty/AtRiskStudents'
import UploadMarksheet  from './pages/faculty/UploadMarksheet'

// Dean
import DeanDashboard    from './pages/dean/DeanDashboard'
import POAttainment     from './pages/dean/POAttainment'
import GenerateReport   from './pages/dean/GenerateReport'

// Student
import StudentDashboard from './pages/student/StudentDashboard'
import MyProgress       from './pages/student/MyProgress'
import MyRiskScore      from './pages/student/MyRiskScore'

function RoleBasedDashboard() {
  const { user } = useAuthStore()
  if (user?.role === 'faculty') return <FacultyDashboard />
  if (user?.role === 'dean')    return <DeanDashboard />
  if (user?.role === 'student') return <StudentDashboard />
  return <FacultyDashboard />
}

function RoleRouter() {
  const { user } = useAuthStore()
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to="/dashboard" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<Login />} />

        {/* Shared dashboard — shows role-based component */}
        <Route path="/dashboard" element={
          <ProtectedRoute allowedRoles={['faculty','dean','student','admin']}>
            <RoleBasedDashboard />
          </ProtectedRoute>
        }/>

        {/* ── Faculty routes ── */}
        <Route path="/attainment" element={
          <ProtectedRoute allowedRoles={['faculty','admin']}>
            <COAttainment />
          </ProtectedRoute>
        }/>
        <Route path="/at-risk" element={
          <ProtectedRoute allowedRoles={['faculty','admin']}>
            <AtRiskStudents />
          </ProtectedRoute>
        }/>
        <Route path="/upload" element={
          <ProtectedRoute allowedRoles={['faculty','admin']}>
            <UploadMarksheet />
          </ProtectedRoute>
        }/>

        {/* ── Dean routes ── */}
        <Route path="/all-courses" element={
          <ProtectedRoute allowedRoles={['dean','admin']}>
            <DeanDashboard />
          </ProtectedRoute>
        }/>
        <Route path="/po-attainment" element={
          <ProtectedRoute allowedRoles={['dean','admin']}>
            <POAttainment />
          </ProtectedRoute>
        }/>
        <Route path="/reports" element={
          <ProtectedRoute allowedRoles={['dean','admin']}>
            <GenerateReport />
          </ProtectedRoute>
        }/>

        {/* ── Student routes ── */}
        <Route path="/my-progress" element={
          <ProtectedRoute allowedRoles={['student']}>
            <MyProgress />
          </ProtectedRoute>
        }/>
        <Route path="/my-risk" element={
          <ProtectedRoute allowedRoles={['student']}>
            <MyRiskScore />
          </ProtectedRoute>
        }/>

        {/* Redirects */}
        <Route path="/"  element={<RoleRouter />} />
        <Route path="*"  element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  )
}