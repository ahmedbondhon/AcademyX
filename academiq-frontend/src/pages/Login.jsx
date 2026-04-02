import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { authApi } from '../api/obeApi'
import useAuthStore from '../store/authStore'
import toast from 'react-hot-toast'
import { Toaster } from 'react-hot-toast'

export default function Login() {
  const [form, setForm]     = useState({ email: '', password: '' })
  const [loading, setLoading] = useState(false)
  const { login }           = useAuthStore()
  const navigate            = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await authApi.login(form)
      const { access_token, ...user } = res.data
      login(user, access_token)
      toast.success(`Welcome back, ${user.name}!`)
      navigate('/dashboard')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-800 to-brand-900
                    flex items-center justify-center p-4">
      <Toaster position="top-right" />
      <div className="bg-white rounded-3xl shadow-2xl w-full max-w-md p-8">

        {/* Logo */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-brand-800 rounded-2xl flex items-center
                          justify-center mx-auto mb-4">
            <span className="text-white text-2xl font-bold">A</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-800">AcademiQ</h1>
          <p className="text-slate-400 text-sm mt-1">
            OBE Intelligence Platform
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-600 block mb-1">
              Email
            </label>
            <input
              type="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="you@diu.edu.bd"
              required
              className="w-full px-4 py-3 rounded-xl border border-slate-200
                         focus:outline-none focus:ring-2 focus:ring-brand-500
                         text-slate-700 text-sm"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-slate-600 block mb-1">
              Password
            </label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="••••••••"
              required
              className="w-full px-4 py-3 rounded-xl border border-slate-200
                         focus:outline-none focus:ring-2 focus:ring-brand-500
                         text-slate-700 text-sm"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-brand-800 text-white py-3 rounded-xl
                       font-semibold text-sm hover:bg-brand-700
                       disabled:opacity-60 transition-all"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Demo credentials */}
        <div className="mt-6 p-4 bg-slate-50 rounded-xl">
          <p className="text-xs font-semibold text-slate-500 mb-2">
            Demo Credentials:
          </p>
          <div className="space-y-1 text-xs text-slate-500">
            <p>Faculty → faculty@diu.edu.bd / test1234</p>
            <p>Dean &nbsp; → dean@diu.edu.bd / test1234</p>
            <p>Student → alice@diu.edu.bd / test1234</p>
          </div>
        </div>
      </div>
    </div>
  )
}