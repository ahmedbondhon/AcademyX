import { useEffect, useState } from 'react'
import { obeApi } from '../../api/obeApi'
import MainLayout from '../../components/layout/MainLayout'
import useAuthStore from '../../store/authStore'
import toast from 'react-hot-toast'

const riskColors = {
  high:   { bar: '#ef4444', bg: 'bg-red-50',   text: 'text-red-600',   badge: 'bg-red-100 text-red-700'    },
  medium: { bar: '#f59e0b', bg: 'bg-amber-50',  text: 'text-amber-600', badge: 'bg-amber-100 text-amber-700' },
  low:    { bar: '#10b981', bg: 'bg-green-50',  text: 'text-green-600', badge: 'bg-green-100 text-green-700' },
}

export default function StudentDashboard() {
  const { user }                      = useAuthStore()
  const [breakdown, setBreakdown]     = useState([])
  const [risk,      setRisk]          = useState(null)
  const [loading,   setLoading]       = useState(true)
  const COURSE_ID = 1

  useEffect(() => {
    Promise.all([
      obeApi.getMyBreakdown(COURSE_ID),
      obeApi.getMyRisk(COURSE_ID),
    ]).then(([bRes, rRes]) => {
      setBreakdown(bRes.data.breakdown || [])
      setRisk(rRes.data)
    }).catch(() => toast.error('Failed to load your data'))
    .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <MainLayout>
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10
                        border-b-2 border-brand-800"/>
      </div>
    </MainLayout>
  )

  const rc = riskColors[risk?.risk_level] || riskColors.low

  return (
    <MainLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">
          Welcome, {user?.name} 👋
        </h1>
        <p className="text-slate-400 text-sm mt-1">
          Your learning outcome progress — Spring 2026
        </p>
      </div>

      {/* Risk alert card */}
      {risk && (
        <div className={`${rc.bg} rounded-2xl p-5 mb-6 border
                         border-opacity-20 flex items-center justify-between`}>
          <div>
            <p className={`font-semibold ${rc.text}`}>
              Your AI Risk Assessment
            </p>
            <p className="text-slate-500 text-sm mt-0.5">
              Based on your Week 1–9 performance
            </p>
            {risk.at_risk_cos?.length > 0 && (
              <p className="text-sm text-red-500 mt-1">
                ⚠️ Needs attention: {risk.at_risk_cos.join(', ')}
              </p>
            )}
          </div>
          <div className="text-right">
            <p className={`text-3xl font-bold ${rc.text}`}>
              {risk.risk_pct}%
            </p>
            <span className={`text-xs px-2 py-0.5 rounded-full
                              font-medium ${rc.badge}`}>
              {risk.risk_level} risk
            </span>
          </div>
        </div>
      )}

      {/* CO Progress */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
        <h3 className="font-semibold text-slate-700 mb-4">
          Your CO Progress
        </h3>
        <div className="space-y-4">
          {breakdown.map((co, i) => (
            <div key={i}>
              <div className="flex items-center justify-between mb-1">
                <div>
                  <span className="font-semibold text-brand-700 text-sm">
                    {co.co}
                  </span>
                  <span className="text-slate-400 text-xs ml-2">
                    {co.description}
                  </span>
                </div>
                <div className="text-right">
                  <span className="font-bold text-sm"
                        style={{
                          color: co.percentage >= 60 ? '#10b981' : '#ef4444'
                        }}>
                    {co.percentage}%
                  </span>
                  <span className={`ml-2 text-xs px-1.5 py-0.5 rounded-full
                    ${co.attained
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'
                    }`}>
                    {co.attained ? '✓' : '✗'}
                  </span>
                </div>
              </div>
              {/* Progress bar */}
              <div className="w-full bg-slate-100 rounded-full h-2.5">
                <div
                  className="h-2.5 rounded-full transition-all duration-700"
                  style={{
                    width: `${Math.min(co.percentage, 100)}%`,
                    background: co.percentage >= 60 ? '#10b981' : '#ef4444',
                  }}
                />
              </div>
              <div className="flex justify-between text-xs text-slate-400 mt-0.5">
                <span>{co.obtained}/{co.max_marks} marks</span>
                <span className="text-purple-500">{co.bloom_level}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </MainLayout>
  )
}