import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'

function Hello({ name }: { name: string }) {
  return <h1>Hello, {name}!</h1>
}

describe('admin-dashboard smoke', () => {
  it('renders a basic component', () => {
    render(<Hello name="Admin" />)
    expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
      /hello, admin/i,
    )
  })

  it('jest-dom matchers are wired up', () => {
    render(<button aria-label="ping">x</button>)
    expect(screen.getByLabelText(/ping/i)).toBeInTheDocument()
  })
})
