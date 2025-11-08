import { useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { create } from 'zustand'

type User = {
  id: string
  name: string
  email: string
  role: 'Super Admin' | 'Clinician' | 'Researcher'
  status: 'active' | 'disabled'
  mfaEnabled: boolean
  lastLogin: string
}

type UserState = {
  users: User[]
  addUser: (user: User) => void
}

const useUserStore = create<UserState>((set) => ({
  users: [
    {
      id: '1',
      name: 'Leila Azimi',
      email: 'leila.azimi@neuropredict.ai',
      role: 'Super Admin',
      status: 'active',
      mfaEnabled: true,
      lastLogin: 'Today 08:14',
    },
    {
      id: '2',
      name: 'Dr. Arman Rahimi',
      email: 'arman.rahimi@neuropredict.ai',
      role: 'Clinician',
      status: 'active',
      mfaEnabled: true,
      lastLogin: 'Yesterday 22:48',
    },
  ],
  addUser: (user) =>
    set((state) => ({
      users: [...state.users, user],
    })),
}))

export default function UsersManagement() {
  const { users, addUser } = useUserStore()
  const { register, handleSubmit, reset } = useForm()

  const activeCount = useMemo(() => users.filter((user) => user.status === 'active').length, [users])

  const onSubmit = handleSubmit((values) => {
    addUser({
      id: crypto.randomUUID(),
      name: values.name,
      email: values.email,
      role: values.role,
      status: 'active',
      mfaEnabled: values.mfa === 'on',
      lastLogin: 'Just now',
    })
    reset()
  })

  return (
    <div className="space-y-8">
      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-xs uppercase text-slate-400">Total Users</div>
          <div className="mt-2 text-3xl font-semibold text-white">{users.length}</div>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-xs uppercase text-slate-400">Active</div>
          <div className="mt-2 text-3xl font-semibold text-emerald-400">{activeCount}</div>
        </div>
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-4">
          <div className="text-xs uppercase text-slate-400">MFA Enabled</div>
          <div className="mt-2 text-3xl font-semibold text-sky-400">
            {users.filter((user) => user.mfaEnabled).length}
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-8 lg:grid-cols-[2fr,1fr]">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">User Directory</h2>
            <span className="text-xs text-slate-400">Sample dataset for UX validation</span>
          </div>
          <div className="overflow-hidden rounded-xl border border-slate-800">
            <table className="min-w-full divide-y divide-slate-800 text-sm text-slate-200">
              <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-4 py-3 text-left">Name</th>
                  <th className="px-4 py-3 text-left">Email</th>
                  <th className="px-4 py-3 text-left">Role</th>
                  <th className="px-4 py-3 text-left">Status</th>
                  <th className="px-4 py-3 text-left">MFA</th>
                  <th className="px-4 py-3 text-left">Last login</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-900/50">
                    <td className="px-4 py-3 text-white">{user.name}</td>
                    <td className="px-4 py-3 text-slate-300">{user.email}</td>
                    <td className="px-4 py-3">{user.role}</td>
                    <td className="px-4 py-3">
                      <span
                        className={
                          user.status === 'active'
                            ? 'rounded-full bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300'
                            : 'rounded-full bg-rose-500/20 px-2 py-1 text-xs text-rose-300'
                        }
                      >
                        {user.status}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {user.mfaEnabled ? (
                        <span className="rounded-full bg-sky-500/20 px-2 py-1 text-xs text-sky-300">
                          Enabled
                        </span>
                      ) : (
                        <span className="rounded-full bg-slate-700/40 px-2 py-1 text-xs text-slate-300">
                          Disabled
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-400">{user.lastLogin}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-lg font-semibold text-white">Quick Create User</h2>
          <p className="mt-1 text-xs text-slate-400">
            Form prototype to validate layout; integrate with API in next phase.
          </p>

          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <div>
              <label htmlFor="name" className="block text-xs uppercase text-slate-400">
                Full name
              </label>
              <input
                id="name"
                type="text"
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                placeholder="E.g. Sara Rad"
                {...register('name', { required: true })}
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-xs uppercase text-slate-400">
                Email
              </label>
              <input
                id="email"
                type="email"
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                placeholder="name@example.com"
                {...register('email', { required: true })}
              />
            </div>

            <div>
              <label htmlFor="role" className="block text-xs uppercase text-slate-400">
                Role
              </label>
              <select
                id="role"
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('role', { required: true })}
                defaultValue="Clinician"
              >
                <option value="Super Admin">Super Admin</option>
                <option value="Clinician">Clinician</option>
                <option value="Researcher">Researcher</option>
              </select>
            </div>

            <div className="flex items-center gap-2">
              <input id="mfa" type="checkbox" className="h-4 w-4 rounded border-slate-700" {...register('mfa')} />
              <label htmlFor="mfa" className="text-sm text-slate-300">
                Enforce Multi-Factor Authentication
              </label>
            </div>

            <button
              type="submit"
              className="w-full rounded-lg bg-sky-500 py-2 text-sm font-medium text-slate-950 transition hover:bg-sky-400"
            >
              Add user prototype
            </button>
          </form>
        </div>
      </section>
    </div>
  )
}


