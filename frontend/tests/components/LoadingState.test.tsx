// frontend/tests/components/LoadingState.test.tsx

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { LoadingState } from '@/components/LoadingState'

describe('LoadingState', () => {
  it('shows the first loading message', () => {
    render(<LoadingState />)
    expect(
      screen.getByText('Reading between the lines...'),
    ).toBeInTheDocument()
  })

  it('renders three animated dots', () => {
    const { container } = render(<LoadingState />)
    expect(
      container.querySelectorAll('.animate-pulse-soft'),
    ).toHaveLength(3)
  })
})
