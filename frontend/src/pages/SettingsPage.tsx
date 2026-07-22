import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { usersApi } from '../services/api'
import { useAuthStore } from '../services/auth'

const PREFS_KEY = 'neuropredict-local-preferences'

type LocalPrefs = {
  minPasswordLength: boolean
  requireCaseMix: boolean
  enable2fa: boolean
  sessionTimeoutMinutes: number
  riskThresholdLow: number
  riskThresholdMedium: number
  confidenceThreshold: number
}

const defaultPrefs: LocalPrefs = {
  minPasswordLength: true,
  requireCaseMix: true,
  enable2fa: false,
  sessionTimeoutMinutes: 30,
  riskThresholdLow: 0.3,
  riskThresholdMedium: 0.7,
  confidenceThreshold: 0.75,
}

function loadPrefs(): LocalPrefs {
  try {
    const raw = localStorage.getItem(PREFS_KEY)
    if (!raw) return { ...defaultPrefs }
    return { ...defaultPrefs, ...JSON.parse(raw) }
  } catch {
    return { ...defaultPrefs }
  }
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'users' | 'security' | 'model' | 'logs'>('users')
  const [prefs, setPrefs] = useState<LocalPrefs>(loadPrefs)
  const [saveMessage, setSaveMessage] = useState('')
  const { user } = useAuthStore()

  useEffect(() => {
    setPrefs(loadPrefs())
  }, [])

  const { data: users = [] } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.getAll(),
    enabled: user?.role === 'admin' && activeTab === 'users',
  })

  const updatePref = <K extends keyof LocalPrefs>(key: K, value: LocalPrefs[K]) => {
    setPrefs((p) => ({ ...p, [key]: value }))
    setSaveMessage('')
  }

  const saveLocalPrefs = () => {
    localStorage.setItem(PREFS_KEY, JSON.stringify(prefs))
    setSaveMessage('Saved to this browser only (local preferences — not synced to server).')
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">⚙️ System Settings</h1>
        <p className="text-gray-600">
          Manage system configuration and users.{' '}
          <span className="text-amber-700 font-medium">
            Security and model toggles are local preferences only unless a server API is available.
          </span>
        </p>
      </div>

      {/* Tabs */}
      <div className="card mb-6">
        <div className="flex space-x-4 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-4 py-2 border-b-2 transition-colors ${
              activeTab === 'users'
                ? 'border-primary-500 text-primary-600 font-medium'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            👥 User Management
          </button>
          <button
            onClick={() => setActiveTab('security')}
            className={`px-4 py-2 border-b-2 transition-colors ${
              activeTab === 'security'
                ? 'border-primary-500 text-primary-600 font-medium'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            🔐 Security Settings
          </button>
          <button
            onClick={() => setActiveTab('model')}
            className={`px-4 py-2 border-b-2 transition-colors ${
              activeTab === 'model'
                ? 'border-primary-500 text-primary-600 font-medium'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            🤖 Model Configuration
          </button>
          <button
            onClick={() => setActiveTab('logs')}
            className={`px-4 py-2 border-b-2 transition-colors ${
              activeTab === 'logs'
                ? 'border-primary-500 text-primary-600 font-medium'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            📋 System Logs
          </button>
        </div>
      </div>

      {/* Tab Content */}
      <div className="card">
        {activeTab === 'users' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">User Management</h2>
            </div>
            {user?.role !== 'admin' ? (
              <p className="text-sm text-gray-600">Admin role required to list users.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">Email</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">Role</th>
                      <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u: { id: number; full_name?: string; name?: string; email: string; role: string; is_active?: boolean; status?: string }) => (
                      <tr key={u.id} className="border-b border-gray-100">
                        <td className="py-3 px-4">{u.full_name || u.name}</td>
                        <td className="py-3 px-4">{u.email}</td>
                        <td className="py-3 px-4">
                          <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                            {u.role}
                          </span>
                        </td>
                        <td className="py-3 px-4">
                          <span className={`px-2 py-1 text-xs rounded ${
                            (u.is_active ?? u.status === 'active')
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {u.is_active != null ? (u.is_active ? 'active' : 'inactive') : (u.status || 'unknown')}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'security' && (
          <div>
            <h2 className="text-xl font-semibold mb-2">Security Settings</h2>
            <p className="text-sm text-amber-700 mb-4">
              Local preferences only — these toggles are stored in your browser (localStorage), not on the server.
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password Policy
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="mr-2"
                      checked={prefs.minPasswordLength}
                      onChange={(e) => updatePref('minPasswordLength', e.target.checked)}
                    />
                    <span>Minimum 8 characters</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="mr-2"
                      checked={prefs.requireCaseMix}
                      onChange={(e) => updatePref('requireCaseMix', e.target.checked)}
                    />
                    <span>Require uppercase and lowercase</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      className="mr-2"
                      checked={prefs.enable2fa}
                      onChange={(e) => updatePref('enable2fa', e.target.checked)}
                    />
                    <span>Prefer 2FA (Two-Factor Authentication)</span>
                  </label>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Session Timeout (minutes)
                </label>
                <input
                  type="number"
                  value={prefs.sessionTimeoutMinutes}
                  onChange={(e) => updatePref('sessionTimeoutMinutes', Number(e.target.value))}
                  className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              {saveMessage && <p className="text-sm text-green-700">{saveMessage}</p>}
              <button type="button" className="btn btn-primary" onClick={saveLocalPrefs}>
                Save local preferences
              </button>
            </div>
          </div>
        )}

        {activeTab === 'model' && (
          <div>
            <h2 className="text-xl font-semibold mb-2">Model Configuration</h2>
            <p className="text-sm text-amber-700 mb-4">
              Local preferences only — not persisted to the model registry API.
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Risk Threshold (Low)
                </label>
                <input
                  type="number"
                  value={prefs.riskThresholdLow}
                  onChange={(e) => updatePref('riskThresholdLow', Number(e.target.value))}
                  step="0.1"
                  min="0"
                  max="1"
                  className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Risk Threshold (Medium)
                </label>
                <input
                  type="number"
                  value={prefs.riskThresholdMedium}
                  onChange={(e) => updatePref('riskThresholdMedium', Number(e.target.value))}
                  step="0.1"
                  min="0"
                  max="1"
                  className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Confidence Threshold
                </label>
                <input
                  type="number"
                  value={prefs.confidenceThreshold}
                  onChange={(e) => updatePref('confidenceThreshold', Number(e.target.value))}
                  step="0.05"
                  min="0"
                  max="1"
                  className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              {saveMessage && <p className="text-sm text-green-700">{saveMessage}</p>}
              <button type="button" className="btn btn-primary" onClick={saveLocalPrefs}>
                Save local preferences
              </button>
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">System Logs</h2>
            <p className="text-sm text-gray-600">
              Live system logs are available in the Admin Dashboard under Audit Logs.
              This clinician UI does not embed a log stream.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
