// frontend/tests/components/Header.test.tsx

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { Header } from '@/components/Header'

function renderHeader(initialPath = '/') {
  return render(
    <MemoryRouter initialEntries={[initialPath]}>
      <Header />
    </MemoryRouter>,
  )
}

describe('Header', () => {
  it('renders the brand and navigation links', () => {
    renderHeader()
    expect(screen.getByText(/Sentimenta/)).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'How It Works' }),
    ).toBeInTheDocument()
  })

  it('highlights the active route', () => {
    renderHeader('/emotions')
    expect(
      screen.getByRole('link', { name: 'Emotions' }).className,
    ).toContain('text-coral-600')
  })

  it('opens the mobile menu', async () => {
    renderHeader()
    await userEvent.click(
      screen.getByLabelText(/toggle navigation menu/i),
    )
    expect(
      screen.getAllByRole('link', { name: 'Emotions' }).length,
    ).toBeGreaterThan(1)
  })
})
