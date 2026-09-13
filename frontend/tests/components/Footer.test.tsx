// frontend/tests/components/Footer.test.tsx

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Footer } from '@/components/Footer'

describe('Footer', () => {
  it('states the privacy guarantee', () => {
    render(<Footer />)
    expect(
      screen.getByText(/nothing is stored/i),
    ).toBeInTheDocument()
  })

  it('credits the underlying technology', () => {
    const { container } = render(<Footer />)
    expect(container.querySelector('footer')?.textContent).toContain(
      'GoEmotions + RoBERTa',
    )
  })
})
