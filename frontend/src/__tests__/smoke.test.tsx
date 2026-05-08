import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

/**
 * Smoke tests verify the toolchain (TS + Vitest + jsdom + RTL + jest-dom)
 * without depending on full-app wiring (router, query client, axios).
 * They are deliberately tiny so failures here always indicate a broken
 * toolchain — never an app regression.
 */

function Hello({ name }: { name: string }) {
  return <h1>Hello, {name}!</h1>
}

describe('frontend smoke', () => {
  it('renders a basic component', () => {
    render(<Hello name="NeuroPredict" />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      /hello, neuropredict/i,
    )
  })

  it('jest-dom matchers are wired up', () => {
    render(<button disabled>x</button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('environment is jsdom', () => {
    expect(typeof window).toBe('object')
    expect(typeof document).toBe('object')
  })
})
