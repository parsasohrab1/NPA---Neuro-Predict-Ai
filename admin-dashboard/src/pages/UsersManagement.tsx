import { useMemo, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { usersApi } from '../services/api'

type ApiUser = {
  id: number
  email: string
  username: string
  full_name: string
  role: string
  is_active: boolean
  is_verified?: boolean
  last_login?: string | null
  created_at?: string
}

type CreateForm = {
  full_name: string
  email: string
  username: string
  password: string
  role: string
}

const ROLE_OPTIONS = ['admin', 'doctor', 'radiologist', 'nurse', 'viewer'] as const

export default function UsersManagement() {
  const queryClient = useQueryClient()
  const [actionError, setActionError] = useState('')
  const { register, handleSubmit, reset } = useForm<CreateForm>({
    defaultValues: { role: 'doctor' },
  })

  const { data: users = [], isLoading, error } = useQuery({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const res = await usersApi.getAll(0, 200)
      return (res.data as ApiUser[]) || []
    },
  })

  const createMutation = useMutation({
    mutationFn: (values: CreateForm) =>
      usersApi.create({
        full_name: values.full_name,
        email: values.email,
        username: values.username,
        password: values.password,
        role: values.role,
      }),
    onSuccess: () => {
      setActionError('')
      reset({ role: 'doctor', full_name: '', email: '', username: '', password: '' })
      queryClient.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: (err: unknown) => {
      const ax = err as { response?: { data?: { detail?: string } }; message?: string }
      setActionError(ax.response?.data?.detail || ax.message || 'Failed to create user')
    },
  })

  const toggleActiveMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: number; is_active: boolean }) =>
      usersApi.update(id, { is_active }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-users'] }),
    onError: (err: unknown) => {
      const ax = err as { response?: { data?: { detail?: string } }; message?: string }
      setActionError(ax.response?.data?.detail || ax.message || 'Failed to update user')
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => usersApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-users'] }),
    onError: (err: unknown) => {
      const ax = err as { response?: { data?: { detail?: string } }; message?: string }
      setActionError(ax.response?.data?.detail || ax.message || 'Failed to delete user')
    },
  })

  const activeCount = useMemo(
    () => users.filter((user) => user.is_active).length,
    [users]
  )

  const onSubmit = handleSubmit((values) => {
    setActionError('')
    createMutation.mutate(values)
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
          <div className="text-xs uppercase text-slate-400">Inactive</div>
          <div className="mt-2 text-3xl font-semibold text-sky-400">
            {users.length - activeCount}
          </div>
        </div>
      </section>

      {actionError && (
        <div className="rounded-lg border border-rose-900/50 bg-rose-950/30 px-4 py-3 text-sm text-rose-300">
          {actionError}
        </div>
      )}

      <section className="grid grid-cols-1 gap-8 lg:grid-cols-[2fr,1fr]">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-lg font-semibold text-white">User Directory</h2>
            <span className="text-xs text-slate-400">GET /api/v1/users</span>
          </div>
          {isLoading ? (
            <p className="text-sm text-slate-400">Loading users...</p>
          ) : error ? (
            <p className="text-sm text-rose-400">Failed to load users. Check auth and API.</p>
          ) : (
            <div className="overflow-hidden rounded-xl border border-slate-800">
              <table className="min-w-full divide-y divide-slate-800 text-sm text-slate-200">
                <thead className="bg-slate-900/80 text-xs uppercase text-slate-400">
                  <tr>
                    <th className="px-4 py-3 text-left">Name</th>
                    <th className="px-4 py-3 text-left">Email</th>
                    <th className="px-4 py-3 text-left">Role</th>
                    <th className="px-4 py-3 text-left">Status</th>
                    <th className="px-4 py-3 text-left">Last login</th>
                    <th className="px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/80">
                  {users.map((user) => (
                    <tr key={user.id} className="hover:bg-slate-900/50">
                      <td className="px-4 py-3 text-white">{user.full_name}</td>
                      <td className="px-4 py-3 text-slate-300">{user.email}</td>
                      <td className="px-4 py-3">{user.role}</td>
                      <td className="px-4 py-3">
                        <span
                          className={
                            user.is_active
                              ? 'rounded-full bg-emerald-500/20 px-2 py-1 text-xs text-emerald-300'
                              : 'rounded-full bg-rose-500/20 px-2 py-1 text-xs text-rose-300'
                          }
                        >
                          {user.is_active ? 'active' : 'disabled'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-slate-400">
                        {user.last_login
                          ? new Date(user.last_login).toLocaleString()
                          : '—'}
                      </td>
                      <td className="px-4 py-3 space-x-2">
                        <button
                          type="button"
                          className="text-xs text-sky-400 hover:text-sky-300"
                          onClick={() =>
                            toggleActiveMutation.mutate({
                              id: user.id,
                              is_active: !user.is_active,
                            })
                          }
                        >
                          {user.is_active ? 'Disable' : 'Enable'}
                        </button>
                        <button
                          type="button"
                          className="text-xs text-rose-400 hover:text-rose-300"
                          onClick={() => {
                            if (window.confirm(`Delete user ${user.email}?`)) {
                              deleteMutation.mutate(user.id)
                            }
                          }}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <h2 className="text-lg font-semibold text-white">Create User</h2>
          <p className="mt-1 text-xs text-slate-400">
            POST /api/v1/users — password min 8 characters.
          </p>

          <form className="mt-6 space-y-4" onSubmit={onSubmit}>
            <div>
              <label htmlFor="full_name" className="block text-xs uppercase text-slate-400">
                Full name
              </label>
              <input
                id="full_name"
                type="text"
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('full_name', { required: true })}
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
                {...register('email', { required: true })}
              />
            </div>

            <div>
              <label htmlFor="username" className="block text-xs uppercase text-slate-400">
                Username
              </label>
              <input
                id="username"
                type="text"
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('username', { required: true })}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-xs uppercase text-slate-400">
                Password
              </label>
              <input
                id="password"
                type="password"
                className="mt-1 w-full rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-sm text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('password', { required: true, minLength: 8 })}
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
              >
                {ROLE_OPTIONS.map((r) => (
                  <option key={r} value={r}>{r}</option>
                ))}
              </select>
            </div>

            <button
              type="submit"
              disabled={createMutation.isPending}
              className="w-full rounded-lg bg-sky-500 py-2 text-sm font-medium text-slate-950 transition hover:bg-sky-400 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Add user'}
            </button>
          </form>
        </div>
      </section>
    </div>
  )
}
