import { useEffect, useState } from 'react'
import { apiGet, apiPost, apiPut } from '../lib/api'

type User = {
  id: number
  email: string
  username: string
  full_name: string
  role: 'admin' | 'doctor' | 'radiologist' | 'researcher' | 'nurse' | 'viewer'
  is_active: boolean
  created_at: string
}

const ROLES = ['admin', 'doctor', 'radiologist', 'researcher', 'nurse', 'viewer'] as const

export default function UsersRoles() {
  const [users, setUsers] = useState<User[]>([])
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState<string>('')
  const [isActive, setIsActive] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchUsers = async () => {
    setLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams()
      if (search) params.set('search', search)
      if (roleFilter) params.set('role', roleFilter)
      if (isActive) params.set('is_active', isActive)
      const data = await apiGet<User[]>(`/admin/users?${params.toString()}`)
      setUsers(data)
    } catch (e) {
      setError(String(e))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const [form, setForm] = useState({
    email: '',
    username: '',
    full_name: '',
    password: '',
    role: 'viewer'
  })

  const createUser = async () => {
    setError(null)
    try {
      await apiPost<User>('/admin/users', form)
      setForm({ email: '', username: '', full_name: '', password: '', role: 'viewer' })
      await fetchUsers()
    } catch (e) {
      setError(String(e))
    }
  }

  const toggleActive = async (u: User) => {
    try {
      await apiPut<User>(`/admin/users/${u.id}`, { is_active: !u.is_active })
      await fetchUsers()
    } catch (e) {
      setError(String(e))
    }
  }

  return (
    <div className="space-y-4">
      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-3">Filters</div>
        <div className="flex gap-2">
          <input className="border rounded px-2 py-1 text-sm" placeholder="Search..."
                 value={search} onChange={(e) => setSearch(e.target.value)} />
          <select className="border rounded px-2 py-1 text-sm" value={roleFilter} onChange={(e)=>setRoleFilter(e.target.value)}>
            <option value="">All Roles</option>
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
          <select className="border rounded px-2 py-1 text-sm" value={isActive} onChange={(e)=>setIsActive(e.target.value)}>
            <option value="">Any Status</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
          <button onClick={fetchUsers} className="px-3 py-1 text-sm bg-blue-600 text-white rounded">Apply</button>
        </div>
      </div>

      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-3">Create User</div>
        <div className="grid grid-cols-5 gap-2">
          <input className="border rounded px-2 py-1 text-sm" placeholder="Email" value={form.email} onChange={e=>setForm({...form, email: e.target.value})}/>
          <input className="border rounded px-2 py-1 text-sm" placeholder="Username" value={form.username} onChange={e=>setForm({...form, username: e.target.value})}/>
          <input className="border rounded px-2 py-1 text-sm" placeholder="Full name" value={form.full_name} onChange={e=>setForm({...form, full_name: e.target.value})}/>
          <input className="border rounded px-2 py-1 text-sm" placeholder="Password" type="password" value={form.password} onChange={e=>setForm({...form, password: e.target.value})}/>
          <select className="border rounded px-2 py-1 text-sm" value={form.role} onChange={e=>setForm({...form, role: e.target.value})}>
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>
        <div className="mt-2">
          <button onClick={createUser} className="px-3 py-1 text-sm bg-green-600 text-white rounded">Create</button>
        </div>
      </div>

      <div className="p-4 border rounded bg-white">
        <div className="font-semibold mb-2">Users</div>
        {loading ? <div>Loading...</div> : error ? <div className="text-red-600">{error}</div> : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left border-b">
                <th className="py-2">Name</th>
                <th>Email</th>
                <th>Username</th>
                <th>Role</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map(u => (
                <tr key={u.id} className="border-b">
                  <td className="py-2">{u.full_name}</td>
                  <td>{u.email}</td>
                  <td>{u.username}</td>
                  <td className="capitalize">{u.role}</td>
                  <td>{u.is_active ? 'Active' : 'Inactive'}</td>
                  <td>{new Date(u.created_at).toLocaleDateString()}</td>
                  <td>
                    <button onClick={() => toggleActive(u)} className="px-2 py-1 text-xs border rounded">
                      {u.is_active ? 'Disable' : 'Enable'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}


