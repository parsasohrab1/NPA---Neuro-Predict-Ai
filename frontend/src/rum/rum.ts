type RUMConfig = {
  sampleRate?: number // 0..1
  sendIntervalMs?: number
}

type RUMEvent = {
  type: string
  value?: number
  meta?: Record<string, any>
  sampled?: boolean
}

const buffer: RUMEvent[] = []
let sampled = false
let initialized = false

function push(ev: RUMEvent) {
  if (!sampled) return
  buffer.push({ ...ev, sampled: true })
}

function postBatch(endpoint: string, events: RUMEvent[]) {
  const body = JSON.stringify({ events })
  navigator.sendBeacon?.(endpoint, body) ||
    fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body,
      keepalive: true,
      credentials: 'include',
    }).catch(() => void 0)
}

function scheduleFlush(interval: number, endpoint: string) {
  setInterval(() => {
    if (!sampled || buffer.length === 0) return;
    const batch = buffer.splice(0, buffer.length)
    postBatch(`${endpoint}/api/v1/rum/events`, batch)
  }, interval)
}

function observePerformance() {
  if (!('PerformanceObserver' in window)) return
  try {
    // LCP
    const poLCP = new PerformanceObserver((list) => {
      const entry = list.getEntries().pop() as any
      if (entry && entry.value) {
        push({ type: 'lcp', value: entry.renderTime || entry.loadTime || entry.startTime, meta: { url: location.pathname } })
      }
    })
    poLCP.observe({ type: 'largest-contentful-paint', buffered: true as any })

    // CLS
    const poCLS = new PerformanceObserver((list) => {
      for (const e of list.getEntries() as any) {
        if (!e.hadRecentInput && e.value) {
          push({ type: 'cls', value: e.value, meta: { url: location.pathname } })
        }
      }
    })
    poCLS.observe({ type: 'layout-shift', buffered: true as any })

    // FCP
    const poFCP = new PerformanceObserver((list) => {
      const entry = list.getEntriesByName('first-contentful-paint')[0]
      if (entry) {
        push({ type: 'fcp', value: entry.startTime, meta: { url: location.pathname } })
      }
    })
    poFCP.observe({ type: 'paint', buffered: true as any })

    // TTFB
    const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined
    if (nav) {
      push({ type: 'ttfb', value: nav.responseStart, meta: { url: location.pathname } })
    }
  } catch {
    // ignore
  }
}

function hookErrors() {
  window.addEventListener('error', (ev) => {
    try {
      const msg = (ev.message || '').toString().slice(0, 200)
      const filename = (ev.filename || '').toString().split('/').pop()
      push({ type: 'js_error', meta: { msg, filename } })
    } catch { /* ignore */ }
  })
  window.addEventListener('unhandledrejection', (ev: PromiseRejectionEvent) => {
    try {
      const reason = (ev.reason && (ev.reason.message || String(ev.reason))) || 'rejection'
      push({ type: 'js_error', meta: { msg: String(reason).slice(0, 200) } })
    } catch { /* ignore */ }
  })
}

export function initRUM(cfg: RuggleConfig = {}) {
  if (initialized) return
  initialized = true
  const rate = cfg?.sampleRate ?? 0.1
  sampled = Math.random() < rate
  if (!sampled) return
  observePerformance()
  hookErrors()
  const interval = cfg?.sendIntervalMs ?? 15000
  const endpoint = `${location.origin}`
  scheduleFlush(interval, endpoint)
}


