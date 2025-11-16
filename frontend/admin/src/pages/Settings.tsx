import { useEffect, useState } from 'react'
import { apiGet, apiPut } from '../lib/api'

type Policy = {
  id?: number
  name?: string
  description?: string
  min_length: number
  max_length: number
  require_uppercase: boolean
  require_lowercase: boolean
  require_digits: boolean
  require_special_chars: boolean
  special_chars: string
  prevent_reuse_count: number
  expiration_days: number | null
  warning_days: number
  max_failed_attempts: number
  lockout_duration_minutes: number
}

export default function Settings() {
  const [policy, setPolicy] = useState<Policy | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const load = async () => {
    setError(null)
    try {
      const data = await apiGet<Policy>('/admin/settings/security/password-policy')
      setPolicy(data)
    } catch (e) {
      setError(String(e))
    }
  }

  useEffect(() => {
    load()
  }, [])

  const save = async () => {
    if (!policy) return
    setSaving(true)
    setError(null)
    try {
      await apiPut('/admin/settings/security/password-policy', policy)
    } catch (e) {
      setError(String(e))
    } finally {
      setSaving(false)
    }
  }

  if (error) return <div className="text-red-600">Error: {error}</div>
  if (!policy) return <div>Loading...</div>

  return (
    <div className="space-y-4">
      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-3">Password Policy</div>
        <div className="grid grid-cols-2 gap-3">
          <label className="text-sm">
            <span className="block text-gray-600">Min Length</span>
            <input type="number" className="border rounded px-2 py-1 w-full"
              value={policy.min_length}
              onChange={e => setPolicy({...policy, min_length: Number(e.target.value)})}/>
          </label>
          <label className="text-sm">
            <span className="block text-gray-600">Max Length</span>
            <input type="number" className="border rounded px-2 py-1 w-full"
              value={policy.max_length}
              onChange={e => setPolicy({...policy, max_length: Number(e.target.value)})}/>
          </label>

          <label className="text-sm flex items-center gap-2">
            <input type="checkbox" checked={policy.require_uppercase}
              onChange={e => setPolicy({...policy, require_uppercase: e.target.checked})}/>
            Require uppercase
          </label>
          <label className="text-sm flex items-center gap-2">
            <input type="checkbox" checked={policy.require_lowercase}
              onChange={e => setPolicy({...policy, require_lowercase: e.target.checked})}/>
            Require lowercase
          </label>
          <label className="text-sm flex items-center gap-2">
            <input type="checkbox" checked={policy.require_digits}
              onChange={e => setPolicy({...policy, require_digits: e.target.checked})}/>
            Require digits
          </label>
          <label className="text-sm flex items-center gap-2">
            <input type="checkbox" checked={policy.require_special_chars}
              onChange={e => setPolicy({...policy, require_special_chars: e.target.checked})}/>
            Require special chars
          </label>
          <label className="text-sm col-span-2">
            <span className="block text-gray-600">Special chars</span>
            <input className="border rounded px-2 py-1 w-full"
              value={policy.special_chars}
              onChange={e => setPolicy({...policy, special_chars: e.target.value})}/>
          </label>

          <label className="text-sm">
            <span className="block text-gray-600">Prevent reuse (N)</span>
            <input type="number" className="border rounded px-2 py-1 w-full"
              value={policy.prevent_reuse_count}
              onChange={e => setPolicy({...policy, prevent_reuse_count: Number(e.target.value)})}/>
          </label>
          <label className="text-sm">
            <span className="block text-gray-600">Expiration days (empty = none)</span>
            <input className="border rounded px-2 py-1 w-full"
              value={policy.expiration_days ?? ''}
              onChange={e => setPolicy({...policy, expiration_days: e.target.value === '' ? null : Number(e.target.value)})}/>
          </label>
          <label className="text-sm">
            <span className="block text-gray-600">Warning days</span>
            <input type="number" className="border rounded px-2 py-1 w-full"
              value={policy.warning_days}
              onChange={e => setPolicy({...policy, warning_days: Number(e.target.value)})}/>
          </label>
          <label className="text-sm">
            <span className="block text-gray-600">Max failed attempts</span>
            <input type="number" className="border rounded px-2 py-1 w-full"
              value={policy.max_failed_attempts}
              onChange={e => setPolicy({...policy, max_failed_attempts: Number(e.target.value)})}/>
          </label>
          <label className="text-sm">
            <span className="block text-gray-600">Lockout (minutes)</span>
            <input type="number" className="border rounded px-2 py-1 w-full"
              value={policy.lockout_duration_minutes}
              onChange={e => setPolicy({...policy, lockout_duration_minutes: Number(e.target.value)})}/>
          </label>
        </div>
        <div className="mt-3">
          <button onClick={save} disabled={saving} className="px-3 py-1 text-sm bg-blue-600 text-white rounded">
            {saving ? 'Saving...' : 'Save changes'}
          </button>
        </div>
      </div>
    </div>
  )
}


