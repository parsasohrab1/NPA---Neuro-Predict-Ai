import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore, isMfaRequiredError } from '../services/auth'

export default function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [mfaCode, setMfaCode] = useState('')
  const [mfaToken, setMfaToken] = useState<string | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const { login, loginWithMfa } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (mfaToken) {
        await loginWithMfa(mfaToken, mfaCode)
      } else {
        await login(username, password)
      }
      navigate('/')
    } catch (err: unknown) {
      if (isMfaRequiredError(err)) {
        setMfaToken(err.mfa_token)
        setError('')
      } else {
        const ax = err as { response?: { data?: { detail?: string } }; message?: string }
        setError(ax.response?.data?.detail || ax.message || 'Login failed. Please check your credentials.')
      }
    } finally {
      setLoading(false)
    }
  }

  const handleBackToCredentials = () => {
    setMfaToken(null)
    setMfaCode('')
    setError('')
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-900 mb-2">🧠 NeuroPredict-AI</h1>
          <p className="text-gray-600">Advanced Neurodegenerative Disease Prediction</p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            {mfaToken ? 'Multi-Factor Authentication' : 'Sign In'}
          </h2>

          {error && (
            <div className="mb-4 p-3 bg-danger-50 border border-danger-200 text-danger-700 rounded-lg text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {!mfaToken ? (
              <>
                <div>
                  <label className="label">Username</label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    className="input"
                    required
                    autoComplete="username"
                  />
                </div>

                <div>
                  <label className="label">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="input"
                    required
                    autoComplete="current-password"
                  />
                </div>
              </>
            ) : (
              <div>
                <p className="text-sm text-gray-600 mb-3">
                  Enter the verification code from your authenticator app.
                </p>
                <label className="label">MFA Code</label>
                <input
                  type="text"
                  inputMode="numeric"
                  pattern="[0-9]*"
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value)}
                  className="input"
                  required
                  autoComplete="one-time-code"
                  autoFocus
                  placeholder="6-digit code"
                />
                <button
                  type="button"
                  onClick={handleBackToCredentials}
                  className="mt-2 text-sm text-primary-600 hover:text-primary-700"
                >
                  ← Back to username / password
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading
                ? (mfaToken ? 'Verifying...' : 'Signing in...')
                : (mfaToken ? 'Verify MFA' : 'Sign In')}
            </button>
          </form>

          {!mfaToken && (
            <div className="mt-6 text-center text-sm text-gray-600">
              <p>Demo Credentials:</p>
              <p className="mt-1">Username: <code className="bg-gray-100 px-2 py-1 rounded">admin</code></p>
              <p>Password: <code className="bg-gray-100 px-2 py-1 rounded">admin123</code></p>
            </div>
          )}
        </div>

        <p className="text-center text-sm text-gray-600 mt-6">
          © 2024 NeuroPredict-AI. HIPAA & GDPR Compliant.
        </p>
      </div>
    </div>
  )
}
