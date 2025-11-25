import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { RouterProvider } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { router } from './router'
import { ErrorBoundary } from './ErrorBoundary'
import { autoDevAuth } from './utils/devAuth'
import './index.css'

// Auto-authenticate in development
autoDevAuth()

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

const rootElement = document.getElementById('root')
if (!rootElement) {
  throw new Error('Root element not found')
}

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Toaster position="top-right" />
        <RouterProvider router={router} />
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)

