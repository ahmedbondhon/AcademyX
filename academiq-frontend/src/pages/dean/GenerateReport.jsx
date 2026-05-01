import { useState } from 'react'
import { reportApi } from '../../api/obeApi'
import MainLayout from '../../components/layout/MainLayout'
import toast from 'react-hot-toast'

export default function GenerateReport() {
  const [generating, setGenerating] = useState(false)

  const handleDownload = async () => {
    const toastId = toast.loading('Generating PDF report...')
    setGenerating(true)
    try {
      const res  = await reportApi.downloadOBEReport(1)
      const url  = URL.createObjectURL(
        new Blob([res.data], { type: 'application/pdf' })
      )
      const link = document.createElement('a')
      link.href  = url
      link.download = 'OBE_Report_CSE301_Spring2026.pdf'
      link.click()
      URL.revokeObjectURL(url)
      toast.success('Report downloaded!', { id: toastId })
    } catch {
      toast.error('Failed to generate report', { id: toastId })
    } finally {
      setGenerating(false)
    }
  }

  return (
    <MainLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Generate Report</h1>
        <p className="text-slate-400 text-sm mt-1">
          Download accreditation-ready OBE PDF reports
        </p>
      </div>

      <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-8">
        <div className="text-center max-w-md mx-auto">
          <div className="text-6xl mb-4">📄</div>
          <h2 className="text-xl font-bold text-slate-800 mb-2">
            OBE Attainment Report
          </h2>
          <p className="text-slate-400 text-sm mb-2">
            CSE301 — Data Structures & Algorithms
          </p>
          <p className="text-slate-400 text-sm mb-8">
            Spring 2026 · Includes CO/PO attainment, student counts,
            and accreditation summary
          </p>
          <button
            onClick={handleDownload}
            disabled={generating}
            className="bg-blue-800 text-white px-8 py-3 rounded-xl
                       font-semibold hover:bg-blue-700 disabled:opacity-50
                       transition-all w-full"
          >
            {generating ? 'Generating...' : '⬇️ Download PDF Report'}
          </button>
          <p className="text-xs text-slate-300 mt-3">
            Generated in under 60 seconds
          </p>
        </div>
      </div>
    </MainLayout>
  )
}