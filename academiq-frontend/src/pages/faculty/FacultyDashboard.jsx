import { useEffect, useState } from 'react'
import { obeApi } from '../../api/obeApi'
import MainLayout from '../../components/layout/MainLayout'
import COAttainmentBar from '../../components/charts/COAttainmentBar'
import RiskTable from '../../components/charts/RiskTable'
import StatCard from '../../components/common/StatCard'
import toast from 'react-hot-toast'

export default function FacultyDashboard() {
  const [summary,    setSummary]    = useState(null)
  const [coData,     setCoData]     = useState([])
  const [riskData,   setRiskData]   = useState([])
  const [loading,    setLoading]    = useState(true)
  const COURSE_ID = 1

  useEffect(() => {
    const load = async () => {
      try {
        const [sumRes, coRes, riskRes] = await Promise.all([
          obeApi.getCourseSummary(COURSE_ID),
          obeApi.getCOAttainment(COURSE_ID),
          obeApi.getCourseRisk(COURSE_ID),
        ])
        setSummary(sumRes.data)
        setCoData(coRes.data.results || [])
        setRiskData(riskRes.data.students || [])
      } catch (err) {
        toast.error('Failed to load dashboard data')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) return (
    <MainLayout>
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10
                        border-b-2 border-brand-800"/>
      </div>
    </MainLayout>
  )

  const healthColor = {
    Good:     'green',
    Warning:  'amber',
    Critical: 'red',
  }[summary?.health] || 'blue'

  return (
    <MainLayout>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">
          Faculty Dashboard
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          {summary?.course_code} — {summary?.course_name} · {summary?.semester}
        </p>
      </div>

      {/* Stat cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          label="Students"
          value={summary?.student_count}
          icon="👥"
          color="blue"
        />
        <StatCard
          label="COs Met"
          value={`${summary?.cos_met} / ${summary?.total_cos}`}
          icon="🎯"
          color="green"
        />
        <StatCard
          label="Avg Attainment"
          value={`${summary?.avg_attainment}%`}
          icon="📊"
          color="purple"
        />
        <StatCard
          label="Course Health"
          value={summary?.health}
          icon="❤️"
          color={healthColor}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <COAttainmentBar data={coData} />
        <RiskTable data={riskData} />
      </div>

      {/* CO detail table */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
        <h3 className="font-semibold text-slate-700 mb-4">
          CO Breakdown Detail
        </h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-slate-50 text-xs text-slate-400 uppercase">
              <th className="px-4 py-2 text-left">CO</th>
              <th className="px-4 py-2 text-left">Description</th>
              <th className="px-4 py-2 text-left">Bloom Level</th>
              <th className="px-4 py-2 text-center">Students Passed</th>
              <th className="px-4 py-2 text-center">Attainment</th>
              <th className="px-4 py-2 text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {coData.map((co, i) => (
              <tr key={i}
                  className="border-t border-slate-50 hover:bg-slate-50">
                <td className="px-4 py-3 font-bold text-brand-700">
                  {co.co}
                </td>
                <td className="px-4 py-3 text-slate-600 max-w-xs truncate">
                  {co.description}
                </td>
                <td className="px-4 py-3">
                  <span className="px-2 py-0.5 bg-purple-100 text-purple-700
                                   rounded-full text-xs">
                    {co.bloom_level}
                  </span>
                </td>
                <td className="px-4 py-3 text-center text-slate-600">
                  {co.passing_students}/{co.total_students}
                </td>
                <td className="px-4 py-3 text-center font-semibold"
                    style={{ color: co.attainment_pct >= 60 ? '#10b981' : '#ef4444' }}>
                  {co.attainment_pct}%
                </td>
                <td className="px-4 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium
                    ${co.threshold_met
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                    }`}>
                    {co.threshold_met ? 'MET' : 'NOT MET'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </MainLayout>
  )
}