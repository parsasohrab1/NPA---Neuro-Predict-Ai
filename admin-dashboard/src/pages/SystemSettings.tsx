import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminSettingsApi } from '../services/api'

const LOCAL_SETTINGS_KEY = 'admin-dashboard-local-settings'

type SettingsForm = {
  passwordLength: number
  requireMfa: boolean
  ipWhitelist: string
  riskThreshold: number
  alertEmail: string
  backupSchedule: string
}

type PasswordPolicy = {
  min_length?: number
  require_uppercase?: boolean
  require_lowercase?: boolean
  require_digits?: boolean
  require_special_chars?: boolean
  max_failed_attempts?: number
  lockout_duration_minutes?: number
}

function loadLocalExtras(): Partial<SettingsForm> {
  try {
    const raw = localStorage.getItem(LOCAL_SETTINGS_KEY)
    return raw ? JSON.parse(raw) : {}
  } catch {
    return {}
  }
}

export default function SystemSettings() {
  const queryClient = useQueryClient()
  const [message, setMessage] = useState<{ type: 'ok' | 'err' | 'info'; text: string } | null>(null)

  const { data: policy, isLoading, error: policyError } = useQuery({
    queryKey: ['password-policy'],
    queryFn: async () => {
      const res = await adminSettingsApi.getPasswordPolicy()
      return res.data as PasswordPolicy
    },
    retry: false,
  })

  const { register, handleSubmit, watch, reset } = useForm<SettingsForm>({
    defaultValues: {
      passwordLength: 12,
      requireMfa: true,
      ipWhitelist: '192.168.1.0/24',
      riskThreshold: 0.72,
      alertEmail: 'alerts@neuropredict.ai',
      backupSchedule: '0 3 * * *',
      ...loadLocalExtras(),
    },
  })

  useEffect(() => {
    if (policy) {
      const local = loadLocalExtras()
      reset({
        passwordLength: policy.min_length ?? 12,
        requireMfa: local.requireMfa ?? true,
        ipWhitelist: local.ipWhitelist ?? '192.168.1.0/24',
        riskThreshold: local.riskThreshold ?? 0.72,
        alertEmail: local.alertEmail ?? 'alerts@neuropredict.ai',
        backupSchedule: local.backupSchedule ?? '0 3 * * *',
      })
    }
  }, [policy, reset])

  const values = watch()

  const savePolicyMutation = useMutation({
    mutationFn: (min_length: number) =>
      adminSettingsApi.updatePasswordPolicy({ min_length }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['password-policy'] })
    },
  })

  const onSubmit = handleSubmit(async (data) => {
    setMessage(null)

    // Persist non-API fields locally (honest local/dev preferences)
    localStorage.setItem(
      LOCAL_SETTINGS_KEY,
      JSON.stringify({
        requireMfa: data.requireMfa,
        ipWhitelist: data.ipWhitelist,
        riskThreshold: data.riskThreshold,
        alertEmail: data.alertEmail,
        backupSchedule: data.backupSchedule,
      })
    )

    if (policyError || !policy) {
      setMessage({
        type: 'info',
        text: 'Local preferences saved in this browser. Password policy API unavailable — server settings were not updated.',
      })
      return
    }

    try {
      await savePolicyMutation.mutateAsync(data.passwordLength)
      setMessage({
        type: 'ok',
        text: 'Password min length saved to server. Other fields are local preferences only.',
      })
    } catch (err: unknown) {
      const ax = err as { response?: { data?: { detail?: string } }; message?: string }
      setMessage({
        type: 'err',
        text:
          ax.response?.data?.detail ||
          ax.message ||
          'Server save failed. Local preferences were still stored in this browser.',
      })
    }
  })

  return (
    <form onSubmit={onSubmit} className="space-y-8">
      <header>
        <h2 className="text-xl font-semibold text-white">System Configuration</h2>
        <p className="mt-1 text-sm text-slate-400">
          Password length loads/saves via{' '}
          <code className="text-slate-300">/api/v1/admin/settings/security/password-policy</code>.
          MFA, IP whitelist, risk threshold, alerts, and backup schedule are{' '}
          <strong className="text-amber-300">local/dev preferences only</strong>.
        </p>
      </header>

      {isLoading && (
        <p className="text-sm text-slate-400">Loading password policy from server...</p>
      )}
      {policyError && (
        <p className="text-sm text-amber-400">
          Could not load server password policy — form is local/dev only.
        </p>
      )}

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <fieldset className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <legend className="text-sm font-semibold text-white">Security</legend>
          <div className="mt-4 space-y-4 text-sm">
            <label className="flex flex-col gap-1">
              <span className="text-xs uppercase text-slate-400">
                Minimum password length (server)
              </span>
              <input
                type="number"
                min={8}
                className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('passwordLength', { valueAsNumber: true })}
              />
            </label>

            <label className="flex items-center gap-2">
              <input type="checkbox" className="h-4 w-4 rounded border-slate-700" {...register('requireMfa')} />
              <span className="text-slate-300">Require MFA for privileged users (local only)</span>
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-xs uppercase text-slate-400">Allowed IP ranges — local only</span>
              <input
                type="text"
                className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('ipWhitelist')}
              />
            </label>
          </div>
        </fieldset>

        <fieldset className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <legend className="text-sm font-semibold text-white">Model thresholds (local)</legend>
          <div className="mt-4 space-y-4 text-sm">
            <label className="flex flex-col gap-1">
              <span className="text-xs uppercase text-slate-400">High risk threshold</span>
              <input
                type="number"
                step={0.01}
                min={0}
                max={1}
                className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('riskThreshold', { valueAsNumber: true })}
              />
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-xs uppercase text-slate-400">Alert escalation email</span>
              <input
                type="email"
                className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('alertEmail')}
              />
            </label>
          </div>
        </fieldset>

        <fieldset className="lg:col-span-2 rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <legend className="text-sm font-semibold text-white">Backup & retention (local)</legend>
          <div className="mt-4 grid grid-cols-1 gap-6 md:grid-cols-2 text-sm">
            <label className="flex flex-col gap-1">
              <span className="text-xs uppercase text-slate-400">Backup cron schedule</span>
              <input
                type="text"
                className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('backupSchedule')}
              />
            </label>

            <div className="rounded-xl border border-slate-800/70 bg-slate-900/60 p-4 text-xs text-slate-400">
              <strong className="text-slate-200">Preview</strong>
              <div className="mt-2 space-y-1">
                <div>• Minimum password length: {values.passwordLength}</div>
                <div>• MFA enforced (local): {values.requireMfa ? 'Yes' : 'No'}</div>
                <div>• Risk threshold: {(values.riskThreshold * 100).toFixed(0)}%</div>
                <div>• Alerts sent to: {values.alertEmail}</div>
                <div>• Backup cron: {values.backupSchedule}</div>
              </div>
            </div>
          </div>
        </fieldset>
      </section>

      {message && (
        <p
          className={
            message.type === 'ok'
              ? 'text-sm text-emerald-400'
              : message.type === 'err'
              ? 'text-sm text-rose-400'
              : 'text-sm text-amber-400'
          }
        >
          {message.text}
        </p>
      )}

      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={() => {
            const local = loadLocalExtras()
            reset({
              passwordLength: policy?.min_length ?? 12,
              requireMfa: local.requireMfa ?? true,
              ipWhitelist: local.ipWhitelist ?? '192.168.1.0/24',
              riskThreshold: local.riskThreshold ?? 0.72,
              alertEmail: local.alertEmail ?? 'alerts@neuropredict.ai',
              backupSchedule: local.backupSchedule ?? '0 3 * * *',
            })
            setMessage(null)
          }}
          className="rounded-lg border border-slate-700 px-5 py-2 text-sm text-slate-200 hover:border-slate-500 hover:text-slate-100"
        >
          Discard changes
        </button>
        <button
          type="submit"
          disabled={savePolicyMutation.isPending}
          className="rounded-lg bg-emerald-500 px-5 py-2 text-sm font-medium text-slate-950 hover:bg-emerald-400 disabled:opacity-50"
        >
          {savePolicyMutation.isPending ? 'Saving...' : 'Save settings'}
        </button>
      </div>
    </form>
  )
}
