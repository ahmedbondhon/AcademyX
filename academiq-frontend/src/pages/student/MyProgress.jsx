import { useEffect, useState } from 'react'
import { obeApi } from '../../api/obeApi'
import MainLayout from '../../components/layout/MainLayout'
import toast from 'react-hot-toast'

export default function MyProgress() {
  const [breakdown, setBreakdown] = useState([])
  const [loading,   setLoading]   = useState(true)
  const COURSE_ID = 1

  useEffect(() => {
    obeApi.getMyBreakdown(COURSE_ID)
      .then(res => setBreakdown(res.data.breakdown || []))
      .catch(() => toast.error('Failed to load your progress'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <MainLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">My CO Progress</h1>
        <p className="text-slate-400 text-sm mt-1">
          Your performance on each Course Outcome — Spring 2026
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-800"/>
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-6">
          {breakdown.map((co, i) => (
            <div key={i}>
              <div className="flex items-center justify-between mb-2">
                <div>
                  <span className="font-bold text-blue-700">{co.co}</span>
                  <span className="text-slate-400 text-sm ml-2">{co.description}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm"
                        style={{ color: co.percentage >= 60 ? '#10b981' : '#ef4444' }}>
                    {co.percentage}%
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium
                    ${co.attained
                      ? 'bg-green-100 text-green-700'
                      : 'bg-red-100 text-red-700'}`}>
                    {co.attained ? '✓ Attained' : '✗ Not Attained'}
                  </span>
                </div>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-3">
                <div
                  className="h-3 rounded-full transition-all duration-700"
                  style={{
                    width: `${Math.min(co.percentage, 100)}%`,
                    background: co.percentage >= 60 ? '#10b981' : '#ef4444',
                  }}
                />
              </div>
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>{co.obtained}/{co.max_marks} marks</span>
                <span className="text-purple-500">{co.bloom_level}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </MainLayout>
  )
}