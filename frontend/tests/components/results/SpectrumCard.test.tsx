// frontend/tests/components/results/SpectrumCard.test.tsx

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { SpectrumCard } from '@/components/results/SpectrumCard'

const emotions = [
  { label: 'joy', score: 0.85 },
  { label: 'anger', score: 0.2 },
]

describe('SpectrumCard', () => {
  it('hides the spectrum until expanded', () => {
    render(<SpectrumCard emotions={emotions} threshold={0.3} />)
    expect(screen.queryByText('Joy')).not.toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /show full spectrum/i }),
    ).toBeInTheDocument()
  })

  it('reveals every emotion when expanded', async () => {
    render(<SpectrumCard emotions={emotions} threshold={0.3} />)
    await userEvent.click(
      screen.getByRole('button', { name: /show full spectrum/i }),
    )
    expect(await screen.findByText('Joy')).toBeInTheDocument()
    expect(screen.getByText('Anger')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
  })
})
