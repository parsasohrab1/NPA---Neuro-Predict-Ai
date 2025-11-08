import { useForm } from 'react-hook-form'

type SettingsForm = {
  passwordLength: number
  requireMfa: boolean
  ipWhitelist: string
  riskThreshold: number
  alertEmail: string
  backupSchedule: string
}

export default function SystemSettings() {
  const { register, handleSubmit, watch } = useForm<SettingsForm>({
    defaultValues: {
      passwordLength: 12,
      requireMfa: true,
      ipWhitelist: '192.168.1.0/24',
      riskThreshold: 0.72,
      alertEmail: 'alerts@neuropredict.ai',
      backupSchedule: '0 3 * * *',
    },
  })

  const values = watch()

  const onSubmit = handleSubmit((data) => {
    console.log('Prototype submit', data)
    alert('Settings submission is mocked. Integrate API to persist changes.')
  })

  return (
    <form onSubmit={onSubmit} className="space-y-8">
      <header>
        <h2 className="text-xl font-semibold text-white">System Configuration</h2>
        <p className="mt-1 text-sm text-slate-400">
          Form layout built with React Hook Form. Wire it to backend settings service in the implementation phase.
        </p>
      </header>

      <section className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <fieldset className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <legend className="text-sm font-semibold text-white">Security</legend>
          <div className="mt-4 space-y-4 text-sm">
            <label className="flex flex-col gap-1">
              <span className="text-xs uppercase text-slate-400">Minimum password length</span>
              <input
                type="number"
                min={8}
                className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('passwordLength', { valueAsNumber: true })}
              />
            </label>

            <label className="flex items-center gap-2">
              <input type="checkbox" className="h-4 w-4 rounded border-slate-700" {...register('requireMfa')} />
              <span className="text-slate-300">Require MFA for privileged users</span>
            </label>

            <label className="flex flex-col gap-1">
              <span className="text-xs uppercase text-slate-400">Allowed IP ranges (CIDR)</span>
              <input
                type="text"
                className="rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 text-white focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/40"
                {...register('ipWhitelist')}
              />
            </label>
          </div>
        </fieldset>

        <fieldset className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
          <legend className="text-sm font-semibold text-white">Model thresholds</legend>
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
          <legend className="text-sm font-semibold text-white">Backup & retention</legend>
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
                <div>• MFA enforced: {values.requireMfa ? 'Yes' : 'No'}</div>
                <div>• Risk threshold: {(values.riskThreshold * 100).toFixed(0)}%</div>
                <div>• Alerts sent to: {values.alertEmail}</div>
                <div>• Backup cron: {values.backupSchedule}</div>
              </div>
            </div>
          </div>
        </fieldset>
      </section>

      <div className="flex justify-end gap-3">
        <button
          type="button"
          className="rounded-lg border border-slate-700 px-5 py-2 text-sm text-slate-200 hover:border-slate-500 hover:text-slate-100"
        >
          Discard changes
        </button>
        <button
          type="submit"
          className="rounded-lg bg-emerald-500 px-5 py-2 text-sm font-medium text-slate-950 hover:bg-emerald-400"
        >
          Save to staging
        </button>
      </div>
    </form>
  )
}


