import React, { createContext, useContext, useMemo, useState } from 'react'

type NoticeType = 'success' | 'error' | 'warning' | 'info'

export type Notice = {
  id: string
  type: NoticeType
  message: string
  duration?: number
  actionLabel?: string
  onAction?: () => void
}

type NotificationContextValue = {
  notices: Notice[]
  remove: (id: string) => void
  success: (message: string, opts?: Partial<Notice>) => void
  error: (message: string, opts?: Partial<Notice>) => void
  warning: (message: string, opts?: Partial<Notice>) => void
  info: (message: string, opts?: Partial<Notice>) => void
}

const NotificationContext = createContext<NotificationContextValue | undefined>(undefined)

function useProvideNotifications(): NotificationContextValue {
  const [notices, setNotices] = useState<Notice[]>([])
  const remove = (id: string) => setNotices((prev) => prev.filter((n) => n.id !== id))
  const push = (type: NoticeType) => (message: string, opts?: Partial<Notice>) => {
    const id = crypto.randomUUID()
    const notice: Notice = {
      id,
      type,
      message,
      duration: 4000,
      ...opts
    }
    setNotices((prev) => [...prev, notice])
    if (notice.duration && notice.duration > 0) {
      setTimeout(() => remove(id), notice.duration)
    }
  }
  return useMemo(
    () => ({
      notices,
      remove,
      success: push('success'),
      error: push('error'),
      warning: push('warning'),
      info: push('info')
    }),
    [notices]
  )
}

export const NotificationProvider: React.FC<React.PropsWithChildren> = ({ children }) => {
  const value = useProvideNotifications()
  return <NotificationContext.Provider value={value}>{children}</NotificationContext.Provider>
}

export function useNotifications(): NotificationContextValue {
  const ctx = useContext(NotificationContext)
  if (!ctx) throw new Error('useNotifications must be used within NotificationProvider')
  return ctx
}

export const NotificationContainer: React.FC = () => {
  const { notices, remove } = useNotifications()
  return (
    <div
      aria-live="polite"
      aria-atomic="true"
      className="fixed z-50 top-4 right-4 space-y-2"
      role="region"
    >
      {notices.map((n) => (
        <div
          key={n.id}
          role="status"
          className={`rounded px-4 py-3 shadow text-sm ${n.type === 'success' ? 'bg-green-600 text-white' : n.type === 'error' ? 'bg-red-600 text-white' : n.type === 'warning' ? 'bg-yellow-500 text-black' : 'bg-blue-600 text-white'}`}
        >
          <div className="flex items-start gap-3">
            <div className="flex-1">{n.message}</div>
            <div className="flex items-center gap-2">
              {n.onAction && n.actionLabel && (
                <button
                  className="underline"
                  onClick={() => {
                    n.onAction?.()
                    remove(n.id)
                  }}
                >
                  {n.actionLabel}
                </button>
              )}
              <button aria-label="Close" onClick={() => remove(n.id)}>
                ×
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}


