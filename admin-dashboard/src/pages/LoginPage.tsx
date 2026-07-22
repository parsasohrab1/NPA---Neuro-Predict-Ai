import { useState, FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { LockClosedIcon, UserIcon, ExclamationCircleIcon } from '@heroicons/react/24/outline'
import axios from '../config/api'

export default function LoginPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('admin@neuropredict.ai')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // OAuth2 password flow uses "username"; map demo email to admin username
      const formData = new URLSearchParams()
      const username =
        email === 'admin@neuropredict.ai' ? 'admin' : email
      formData.append('username', username)
      formData.append('password', password)

      const response = await axios.post('/api/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })

      if (response.data.access_token) {
        // Save token
        localStorage.setItem('auth_token', response.data.access_token)
        
        // Redirect to dashboard
        navigate('/')
      } else {
        setError('Login failed: No token received')
      }
    } catch (err: any) {
      console.error('Login error:', err)
      
      if (err.response?.status === 401) {
        setError('Invalid email or password. Try the default: admin@neuropredict.ai / admin123')
      } else if (err.response?.status === 404) {
        setError('User not found. You may need to create an admin user first.')
      } else {
        setError(err.response?.data?.detail || err.message || 'Login failed. Check console for details.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 px-4">
      <div className="max-w-md w-full space-y-8">
        {/* Logo/Header */}
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="rounded-full bg-sky-500/10 p-6">
              <LockClosedIcon className="h-12 w-12 text-sky-400" />
            </div>
          </div>
          <h2 className="text-3xl font-bold text-white">
            NeuroPredict AI
          </h2>
          <p className="mt-2 text-sm text-slate-400">
            Admin Dashboard - Sign in to continue
          </p>
        </div>

        {/* Login Form */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm p-8 shadow-xl">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {/* Error Message */}
            {error && (
              <div className="rounded-lg border border-rose-900/50 bg-rose-950/30 p-4">
                <div className="flex items-start gap-3">
                  <ExclamationCircleIcon className="h-5 w-5 text-rose-400 flex-shrink-0 mt-0.5" />
                  <div className="text-sm text-rose-300">{error}</div>
                </div>
              </div>
            )}

            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-slate-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <UserIcon className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-700 rounded-lg bg-slate-950/60 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                  placeholder="admin@neuropredict.ai"
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-slate-300 mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <LockClosedIcon className="h-5 w-5 text-slate-500" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-700 rounded-lg bg-slate-950/60 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg text-sm font-medium text-white bg-sky-600 hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-sky-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="h-4 w-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <span>Signing in...</span>
                </div>
              ) : (
                'Sign in'
              )}
            </button>
          </form>

          {/* Help Text */}
          <div className="mt-6 text-center">
            <div className="text-xs text-slate-500">
              Default credentials:
            </div>
            <div className="mt-1 text-xs text-slate-400 font-mono">
              admin@neuropredict.ai / admin123
            </div>
          </div>
        </div>

        {/* Footer Info */}
        <div className="text-center text-xs text-slate-500">
          <p>Having trouble logging in?</p>
          <p className="mt-1">
            Check the console (F12) for detailed error messages.
          </p>
        </div>
      </div>
    </div>
  )
}

