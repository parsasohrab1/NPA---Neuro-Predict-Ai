import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { usersApi } from '../services/api'
import { useAuthStore } from '../services/auth'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'users' | 'security' | 'model' | 'logs'>('users')
  const { user } = useAuthStore()

  // Fetch users from API (Admin only)
  const { data: users = [] } = useQuery({
    queryKey: ['users'],
    queryFn: () => usersApi.getAll(),
    enabled: user?.role === 'admin' && activeTab === 'users',
  })

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">⚙️ System Settings</h1>
        <p className="text-gray-600">Manage system configuration and users</p>
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
              <button className="btn btn-primary">+ Add User</button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Name</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Email</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Role</th>
                    <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                    <th className="text-right py-3 px-4 font-semibold text-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user) => (
                    <tr key={user.id} className="border-b border-gray-100">
                      <td className="py-3 px-4">{user.name}</td>
                      <td className="py-3 px-4">{user.email}</td>
                      <td className="py-3 px-4">
                        <span className="px-2 py-1 text-xs rounded bg-blue-100 text-blue-800">
                          {user.role}
                        </span>
                      </td>
                      <td className="py-3 px-4">
                        <span className={`px-2 py-1 text-xs rounded ${
                          user.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {user.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right">
                        <button className="text-primary-600 hover:text-primary-800 mr-3">Edit</button>
                        <button className="text-red-600 hover:text-red-800">Delete</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'security' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Security Settings</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password Policy
                </label>
                <div className="space-y-2">
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span>Minimum 8 characters</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" defaultChecked />
                    <span>Require uppercase and lowercase</span>
                  </label>
                  <label className="flex items-center">
                    <input type="checkbox" className="mr-2" />
                    <span>Enable 2FA (Two-Factor Authentication)</span>
                  </label>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Session Timeout (minutes)
                </label>
                <input
                  type="number"
                  defaultValue={30}
                  className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <button className="btn btn-primary">Save Security Settings</button>
            </div>
          </div>
        )}

        {activeTab === 'model' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">Model Configuration</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Risk Threshold (Low)
                </label>
                <input
                  type="number"
                  defaultValue={0.3}
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
                  defaultValue={0.7}
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
                  defaultValue={0.75}
                  step="0.05"
                  min="0"
                  max="1"
                  className="w-full max-w-xs px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>
              <button className="btn btn-primary">Save Model Settings</button>
            </div>
          </div>
        )}

        {activeTab === 'logs' && (
          <div>
            <h2 className="text-xl font-semibold mb-4">System Logs</h2>
            <div className="space-y-2">
              <div className="p-3 bg-gray-50 rounded border border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">[2024-11-15 10:30:25] INFO: User logged in</span>
                  <span className="text-xs text-gray-500">System</span>
                </div>
              </div>
              <div className="p-3 bg-gray-50 rounded border border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700">[2024-11-15 10:28:10] INFO: Prediction created</span>
                  <span className="text-xs text-gray-500">User: admin</span>
                </div>
              </div>
              <div className="p-3 bg-yellow-50 rounded border border-yellow-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-yellow-800">[2024-11-15 10:25:00] WARNING: High risk case detected</span>
                  <span className="text-xs text-yellow-600">System</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
