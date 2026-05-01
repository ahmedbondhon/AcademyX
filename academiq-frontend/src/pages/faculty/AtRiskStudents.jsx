import { useEffect, useState } from 'react'
import { obeApi, alertApi } from '../../api/obeApi'
import MainLayout from '../../components/layout/MainLayout'
import RiskTable from '../../components/charts/RiskTable'
import toast from 'react-hot-toast'

export default function AtRiskStudents() {
  const [data,    setData]    = useState({ students: [], high_risk: 0, medium_risk: 0, low_risk: 0 })
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const COURSE_ID = 1

  useEffect(() => {
    obeApi.getCourseRisk(COURSE_ID)
      .then(res => setData(res.data))
      .catch(() => toast.error('Failed to load risk data'))
      .finally(() => setLoading(false))
  }, [])

  const handleSendAlerts = async () => {
    setSending(true)
    try {
      const res = await alertApi.preview(COURSE_ID)
      toast.success(`Alerts ready for ${res.data.high_risk_count + res.data.med_risk_count} students`)
    } catch {
      toast.error('Failed to send alerts')
    } finally {
      setSending(false)
    }
  }

  return (
    <MainLayout>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">At-Risk Students</h1>
          <p className="text-slate-400 text-sm mt-1">
            AI predictions — CSE301 · Week 9 analysis
          </p>
        </div>
        <button
          onClick={handleSendAlerts}
          disabled={sending}
          className="bg-blue-800 text-white px-4 py-2 rounded-xl text-sm
                     font-medium hover:bg-blue-700 disabled:opacity-50 transition-all"
        >
          {sending ? 'Sending...' : '📧 Send Alerts'}
        </button>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-red-50 border border-red-100 rounded-2xl p-4 text-center">
          <p className="text-3xl font-bold text-red-600">{data.high_risk}</p>
          <p className="text-xs text-red-400 mt-1">High Risk</p>
        </div>
        <div className="bg-amber-50 border border-amber-100 rounded-2xl p-4 text-center">
          <p className="text-3xl font-bold text-amber-600">{data.medium_risk}</p>
          <p className="text-xs text-amber-400 mt-1">Medium Risk</p>
        </div>
        <div className="bg-green-50 border border-green-100 rounded-2xl p-4 text-center">
          <p className="text-3xl font-bold text-green-600">{data.low_risk}</p>
          <p className="text-xs text-green-400 mt-1">Low Risk</p>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-48">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-800"/>
        </div>
      ) : (
        <RiskTable data={data.students || []} />
      )}
    </MainLayout>
  )
}