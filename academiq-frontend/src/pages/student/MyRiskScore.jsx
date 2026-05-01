import { useEffect, useState } from 'react'
import { obeApi } from '../../api/obeApi'
import MainLayout from '../../components/layout/MainLayout'
import toast from 'react-hot-toast'

const riskConfig = {
  high:   { color: 'text-red-600',   bg: 'bg-red-50',   border: 'border-red-200',   badge: 'bg-red-100 text-red-700'    },
  medium: { color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', badge: 'bg-amber-100 text-amber-700' },
  low:    { color: 'text-green-600', bg: 'bg-green-50', border: 'border-green-200', badge: 'bg-green-100 text-green-700' },
}

export default function MyRiskScore() {
  const [risk,    setRisk]    = useState(null)
  const [loading, setLoading] = useState(true)
  const COURSE_ID = 1

  useEffect(() => {
    obeApi.getMyRisk(COURSE_ID)
      .then(res => setRisk(res.data))
      .catch(() => toast.error('Failed to load risk score'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <MainLayout>
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-800"/>
      </div>
    </MainLayout>
  )

  const rc = riskConfig[risk?.risk_level] || riskConfig.low

  return (
    <MainLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">My Risk Score</h1>
        <p className="text-slate-400 text-sm mt-1">
          AI-predicted risk of not attaining Course Outcomes
        </p>
      </div>

      {risk && (
        <div className="space-y-6">
          {/* Main risk card */}
          <div className={`${rc.bg} border ${rc.border} rounded-2xl p-8 text-center`}>
            <p className={`text-6xl font-bold ${rc.color} mb-2`}>
              {risk.risk_pct}%
            </p>
            <span className={`px-4 py-1 rounded-full text-sm font-medium ${rc.badge}`}>
              {risk.risk_level?.toUpperCase()} RISK
            </span>
            <p className="text-slate-500 text-sm mt-4">
              Based on your Week 1–9 performance in CSE301
            </p>
          </div>

          {/* At-risk COs */}
          {risk.at_risk_cos?.length > 0 && (
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
              <h3 className="font-semibold text-red-600 mb-3">
                ⚠️ Course Outcomes Needing Attention
              </h3>
              <div className="flex flex-wrap gap-2">
                {risk.at_risk_cos.map((co, i) => (
                  <span key={i}
                        className="px-3 py-1 bg-red-50 text-red-700 rounded-full
                                   text-sm font-medium border border-red-100">
                    {co}
                  </span>
                ))}
              </div>
              <p className="text-sm text-slate-400 mt-3">
                Contact your faculty advisor for support with these outcomes.
              </p>
            </div>
          )}

          {/* What to do */}
          <div className="bg-blue-50 border border-blue-100 rounded-2xl p-5">
            <h3 className="font-semibold text-blue-800 mb-2">What should I do?</h3>
            <ul className="space-y-2 text-sm text-blue-700">
              <li>→ Attend all remaining classes and submit assignments on time</li>
              <li>→ Visit your faculty advisor during office hours</li>
              <li>→ Form a study group with classmates for at-risk COs</li>
              <li>→ Review lecture materials for the flagged Course Outcomes</li>
            </ul>
          </div>
        </div>
      )}
    </MainLayout>
  )
}