import { useEffect, useState } from 'react'
import { obeApi } from '../../api/obeApi'
import MainLayout from '../../components/layout/MainLayout'
import toast from 'react-hot-toast'

export default function POAttainment() {
  const [poData,  setPoData]  = useState([])
  const [loading, setLoading] = useState(true)
  const PROGRAM_ID = 1

  useEffect(() => {
    obeApi.getPOAttainment(PROGRAM_ID)
      .then(res => setPoData(res.data.results || []))
      .catch(() => toast.error('Failed to load PO attainment'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <MainLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">PO Attainment</h1>
        <p className="text-slate-400 text-sm mt-1">
          Program Outcome attainment — BSc CSE
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-800"/>
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
          <div className="space-y-5">
            {poData.map((po, i) => (
              <div key={i}>
                <div className="flex items-center justify-between mb-2">
                  <div>
                    <span className="font-bold text-blue-700">{po.po}</span>
                    <span className="text-slate-500 text-sm ml-2">{po.description}</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-bold"
                          style={{ color: po.attainment_pct >= 60 ? '#10b981' : '#ef4444' }}>
                      {po.attainment_pct}%
                    </span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-medium
                      ${po.threshold_met
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700'}`}>
                      {po.threshold_met ? 'MET' : 'NOT MET'}
                    </span>
                  </div>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-3">
                  <div
                    className="h-3 rounded-full transition-all duration-700"
                    style={{
                      width: `${Math.min(po.attainment_pct, 100)}%`,
                      background: po.attainment_pct >= 60 ? '#10b981' : '#ef4444',
                    }}
                  />
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  {po.level_label}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </MainLayout>
  )
}