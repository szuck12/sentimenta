// frontend/tests/pages/HowItWorks.test.tsx

import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { HowItWorks } from '@/pages/HowItWorks'

function renderPage() {
  return render(
    <MemoryRouter>
      <HowItWorks />
    </MemoryRouter>,
  )
}

describe('HowItWorks', () => {
  it('renders the heading and all four steps', () => {
    renderPage()
    expect(
      screen.getByRole('heading', { name: 'How It Works' }),
    ).toBeInTheDocument()
    for (const title of [
      'You enter text',
      'The model reads it',
      'Multi-label scoring',
      'Attribution & explanation',
    ]) {
      expect(screen.getByText(title)).toBeInTheDocument()
    }
  })

  it('states the model limitations', () => {
    renderPage()
    expect(
      screen.getAllByText(/Reddit comments/).length,
    ).toBeGreaterThan(0)
    expect(screen.getAllByText(/not certainty scores/i).length).toBeGreaterThan(
      0,
    )
  })
})
