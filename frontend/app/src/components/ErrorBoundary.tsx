import React from 'react'

type Props = {
  fallback?: React.ReactNode
}

type State = {
  hasError: boolean
}

export class ErrorBoundary extends React.Component<React.PropsWithChildren<Props>, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(): State {
    return { hasError: true }
  }

  componentDidCatch(error: unknown, info: unknown) {
    // In a real app, report to monitoring service
    console.error('ErrorBoundary caught error', error, info)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? <div role="alert">Something went wrong.</div>
    }
    return this.props.children
  }
}


