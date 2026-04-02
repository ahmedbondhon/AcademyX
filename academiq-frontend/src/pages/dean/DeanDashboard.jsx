import { useEffect, useState } from 'react'
import { obeApi, reportApi } from '../../api/obeApi'
import MainLayout from '../../components/layout/MainLayout'
import StatCard from '../../components/common/StatCard'
import toast from 'react-hot-toast'

export default function DeanDashboard() {
  const [courses, setCourses] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    obeApi.getAllCourses()
      .then(res => setCourses(res.data || []))
      .catch(() => toast.error('Failed to load courses'))
      .finally(() => setLoading(false))
  }, [])

  const handleDownloadReport = async (courseId, courseCode) => {
    const toastId = toast.loading('Generating PDF report...')
    try {
      const res  = await reportApi.downloadOBEReport(courseId)
      const url  = URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href  = url
      link.download = `OBE_Report_${courseCode}.pdf`
      link.click()
      toast.success('Report downloaded!', { id: toastId })
    } catch {
      toast.error('Failed to generate report', { id: toastId })
    }
  }

  const totalStudents = courses.reduce((a, c) => a + (c.student_count || 0), 0)
  const avgAttainment = courses.length
    ? (courses.reduce((a, c) => a + c.avg_attainment, 0) / courses.length).toFixed(1)
    : 0
  const critical = courses.filter(c => c.health === 'Critical').length

  if (loading) return (
    <MainLayout>
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10
                        border-b-2 border-brand-800"/>
      </div>
    </MainLayout>
  )

  return (
    <MainLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Dean Dashboard</h1>
        <p className="text-slate-400 text-sm mt-1">
          University-wide OBE performance overview
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total Courses"   value={courses.length}    icon="🏫" color="blue"   />
        <StatCard label="Total Students"  value={totalStudents}     icon="👥" color="purple" />
        <StatCard label="Avg Attainment"  value={`${avgAttainment}%`} icon="📊" color="green"  />
        <StatCard label="Critical Courses" value={critical}         icon="⚠️"  color="red"    />
      </div>

      {/* Courses table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
        <div className="p-5 border-b border-slate-100">
          <h3 className="font-semibold text-slate-700">All Courses</h3>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 text-xs text-slate-400 uppercase">
              <th className="px-4 py-3 text-left">Course</th>
              <th className="px-4 py-3 text-left">Semester</th>
              <th className="px-4 py-3 text-center">Students</th>
              <th className="px-4 py-3 text-center">COs Met</th>
              <th className="px-4 py-3 text-center">Avg Attainment</th>
              <th className="px-4 py-3 text-center">Health</th>
              <th className="px-4 py-3 text-center">Report</th>
            </tr>
          </thead>
          <tbody>
            {courses.map((c, i) => {
              const healthStyle = {
                Good:     'bg-green-100 text-green-700',
                Warning:  'bg-amber-100 text-amber-700',
                Critical: 'bg-red-100 text-red-700',
              }[c.health] || ''
              return (
                <tr key={i}
                    className="border-t border-slate-50 hover:bg-slate-50">
                  <td className="px-4 py-3">
                    <p className="font-semibold text-brand-700">
                      {c.course_code}
                    </p>
                    <p className="text-xs text-slate-400">{c.course_name}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-500">{c.semester}</td>
                  <td className="px-4 py-3 text-center">{c.student_count}</td>
                  <td className="px-4 py-3 text-center">
                    {c.cos_met}/{c.total_cos}
                  </td>
                  <td className="px-4 py-3 text-center font-semibold"
                      style={{
                        color: c.avg_attainment >= 60 ? '#10b981' : '#ef4444'
                      }}>
                    {c.avg_attainment}%
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-0.5 rounded-full text-xs
                                      font-medium ${healthStyle}`}>
                      {c.health}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() =>
                        handleDownloadReport(c.course_id, c.course_code)
                      }
                      className="bg-brand-800 text-white px-3 py-1.5 rounded-lg
                                 text-xs font-medium hover:bg-brand-700 transition"
                    >
                      📄 PDF
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </MainLayout>
  )
}