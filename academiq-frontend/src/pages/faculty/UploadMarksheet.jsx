import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { uploadApi, obeApi } from '../../api/obeApi'
import MainLayout from '../../components/layout/MainLayout'
import toast from 'react-hot-toast'

export default function UploadMarksheet() {
  const [file,     setFile]     = useState(null)
  const [preview,  setPreview]  = useState(null)
  const [loading,  setLoading]  = useState(false)
  const COURSE_ID = 1

  const onDrop = useCallback((accepted) => {
    if (accepted.length > 0) {
      setFile(accepted[0])
      setPreview(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv':                                               ['.csv'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel':                               ['.xls'],
    },
    maxFiles: 1,
  })

  const handlePreview = async () => {
    if (!file) return
    setLoading(true)
    try {
      const res = await uploadApi.uploadMarksheet(file, false)
      setPreview(res.data)
      toast.success('File validated successfully')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Validation failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!file) return
    setLoading(true)
    try {
      const res = await uploadApi.uploadMarksheet(file, true)
      toast.success(
        `Saved! ${res.data.saved?.inserted} new + ${res.data.saved?.updated} updated`
      )
      setFile(null)
      setPreview(null)
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  const handleDownloadTemplate = async () => {
    try {
      const res  = await uploadApi.downloadTemplate(COURSE_ID)
      const url  = URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href  = url
      link.download = `marks_template_course_${COURSE_ID}.xlsx`
      link.click()
      toast.success('Template downloaded!')
    } catch {
      toast.error('Download failed')
    }
  }

  return (
    <MainLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-800">Upload Marksheet</h1>
        <p className="text-slate-400 text-sm mt-1">
          Upload CSV or Excel files to import student marks
        </p>
      </div>

      {/* Download template */}
      <div className="bg-blue-50 border border-blue-100 rounded-2xl p-5 mb-6
                      flex items-center justify-between">
        <div>
          <p className="font-semibold text-blue-800">
            Need the template?
          </p>
          <p className="text-sm text-blue-600 mt-0.5">
            Download the pre-filled Excel template, add marks, and upload back
          </p>
        </div>
        <button
          onClick={handleDownloadTemplate}
          className="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm
                     font-medium hover:bg-blue-700 transition-all"
        >
          Download Template
        </button>
      </div>

      {/* Dropzone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-12 text-center
                    cursor-pointer transition-all mb-6
                    ${isDragActive
                      ? 'border-brand-500 bg-blue-50'
                      : 'border-slate-200 hover:border-brand-400 bg-white'
                    }`}
      >
        <input {...getInputProps()} />
        <div className="text-4xl mb-3">📤</div>
        {file ? (
          <div>
            <p className="font-semibold text-slate-700">{file.name}</p>
            <p className="text-sm text-slate-400 mt-1">
              {(file.size / 1024).toFixed(1)} KB
            </p>
          </div>
        ) : (
          <div>
            <p className="font-semibold text-slate-600">
              {isDragActive ? 'Drop it here!' : 'Drag & drop your marksheet'}
            </p>
            <p className="text-sm text-slate-400 mt-1">
              Supports .csv, .xlsx, .xls
            </p>
          </div>
        )}
      </div>

      {/* Action buttons */}
      {file && (
        <div className="flex gap-3 mb-6">
          <button
            onClick={handlePreview}
            disabled={loading}
            className="px-5 py-2.5 bg-slate-100 text-slate-700 rounded-xl
                       text-sm font-medium hover:bg-slate-200 transition-all
                       disabled:opacity-50"
          >
            {loading ? 'Validating...' : 'Validate & Preview'}
          </button>
          {preview?.valid && (
            <button
              onClick={handleSave}
              disabled={loading}
              className="px-5 py-2.5 bg-brand-800 text-white rounded-xl
                         text-sm font-medium hover:bg-brand-700 transition-all
                         disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save to Database'}
            </button>
          )}
        </div>
      )}

      {/* Preview results */}
      {preview && (
        <div className="bg-white rounded-2xl border border-slate-100 p-5">
          <h3 className="font-semibold text-slate-700 mb-3">
            Validation Results
          </h3>
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="bg-slate-50 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-slate-700">
                {preview.summary?.total_rows}
              </p>
              <p className="text-xs text-slate-400">Total Rows</p>
            </div>
            <div className="bg-green-50 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-green-600">
                {preview.summary?.valid_rows}
              </p>
              <p className="text-xs text-slate-400">Valid</p>
            </div>
            <div className="bg-red-50 rounded-xl p-3 text-center">
              <p className="text-2xl font-bold text-red-600">
                {preview.summary?.error_rows}
              </p>
              <p className="text-xs text-slate-400">Errors</p>
            </div>
          </div>
          {preview.errors?.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-red-600">Errors found:</p>
              {preview.errors.map((err, i) => (
                <div key={i}
                     className="bg-red-50 text-red-600 text-xs px-3 py-2
                                rounded-lg">
                  Row {err.row}: {err.errors.join(', ')}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </MainLayout>
  )
}