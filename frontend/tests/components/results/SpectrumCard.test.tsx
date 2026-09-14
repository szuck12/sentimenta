// frontend/tests/components/results/SpectrumCard.test.tsx

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it } from 'vitest'
import { SpectrumCard } from '@/components/results/SpectrumCard'
import { toWholePercentages } from '@/lib/utils'

const emotions = [
  { label: 'joy', percentage: 85 },
  { label: 'anger', percentage: 20 },
]

const labels = ['joy', 'excitement', 'optimism', 'curiosity', 'neutral', 'anger']
const scores = [0.85, 0.7, 0.4, 0.3, 0.05, 0.02]
const fullShares = toWholePercentages(scores).map((percentage, index) => ({
  label: labels[index],
  percentage,
}))

describe('SpectrumCard', () => {
  it('hides the spectrum until expanded', () => {
    render(<SpectrumCard emotions={emotions} />)
    expect(screen.queryByText('Joy')).not.toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /show full spectrum/i }),
    ).toBeInTheDocument()
  })

  it('reveals every emotion when expanded', async () => {
    render(<SpectrumCard emotions={emotions} />)
    await userEvent.click(
      screen.getByRole('button', { name: /show full spectrum/i }),
    )
    expect(await screen.findByText('Joy')).toBeInTheDocument()
    expect(screen.getByText('Anger')).toBeInTheDocument()
    expect(screen.getByText('85%')).toBeInTheDocument()
  })

  it('renders every bar in the same coral colour', async () => {
    render(<SpectrumCard emotions={emotions} />)
    await userEvent.click(
      screen.getByRole('button', { name: /show full spectrum/i }),
    )
    await screen.findByText('Joy')
    const coral = document.querySelectorAll('.bg-coral-400')
    expect(coral.length).toBe(2)
    expect(document.querySelectorAll('.bg-cream-300').length).toBe(0)
  })

  it('renders a full distribution that sums to 100%', async () => {
    render(<SpectrumCard emotions={fullShares} />)
    await userEvent.click(
      screen.getByRole('button', { name: /show full spectrum/i }),
    )
    await screen.findByText('Joy')
    const percentages = screen
      .getAllByText(/^\d+%$/)
      .map((el) => Number((el.textContent ?? '').replace('%', '')))
    expect(percentages).toHaveLength(labels.length)
    expect(percentages.reduce((sum, value) => sum + value, 0)).toBe(100)
  })
})
