import { useEffect, useState } from 'react'
import { obeApi } from '../../api/obeApi'
import MainLayout from '../../components/layout/MainLayout'
import COAttainmentBar from '../../components/charts/COAttainmentBar'
import toast from 'react-hot-toast'

export default function COAttainment() {
  const [coData,  setCoData]  = useState([])
  const [loading, setLoading] = useState(true)
  const COURSE_ID = 1

  useEffect(() => {
    obeApi.getCOAttainment(COURSE_ID)
      .then(res => setCoData(res.data.results || []))
      .catch(() => toast.error('Failed to load CO attainment'))
      .finally(() => setLoading(false))
  }, [])

  return (
    <MainLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">CO Attainment</h1>
        <p className="text-slate-400 text-sm mt-1">
          Course Outcome attainment levels — CSE301 Spring 2026
        </p>
      </div>
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-800"/>
        </div>
      ) : (
        <div className="space-y-6">
          <COAttainmentBar data={coData} />
          <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-5">
            <h3 className="font-semibold text-slate-700 mb-4">CO Detail</h3>
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
                  <tr key={i} className="border-t border-slate-50 hover:bg-slate-50">
                    <td className="px-4 py-3 font-bold text-blue-700">{co.co}</td>
                    <td className="px-4 py-3 text-slate-600 max-w-xs truncate">
                      {co.description}
                    </td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full text-xs">
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
                          : 'bg-red-100 text-red-700'}`}>
                        {co.threshold_met ? 'MET' : 'NOT MET'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </MainLayout>
  )
}