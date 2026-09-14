// frontend/tests/components/results/EmotionMixCard.test.tsx

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { EmotionMixCard } from '@/components/results/EmotionMixCard'

function percentages(): number[] {
  return screen
    .getAllByText(/^\d+%$/)
    .map((el) => Number((el.textContent ?? '').replace('%', '')))
}

describe('EmotionMixCard', () => {
  it('renders each emotion with its given share', () => {
    render(
      <EmotionMixCard
        emotions={[
          { label: 'joy', percentage: 55 },
          { label: 'excitement', percentage: 45 },
        ]}
        primaryLabel="joy"
      />,
    )
    expect(screen.getByText('Joy')).toBeInTheDocument()
    expect(screen.getByText('Excitement')).toBeInTheDocument()
    expect(screen.getByText('55%')).toBeInTheDocument()
    expect(screen.getByText('45%')).toBeInTheDocument()
  })

  it('shows the provided shares verbatim (the mix need not sum to 100)', () => {
    render(
      <EmotionMixCard
        emotions={[
          { label: 'joy', percentage: 37 },
          { label: 'excitement', percentage: 30 },
          { label: 'optimism', percentage: 17 },
          { label: 'curiosity', percentage: 13 },
          { label: 'neutral', percentage: 2 },
        ]}
        primaryLabel="joy"
      />,
    )
    // 37 + 30 + 17 + 13 + 2 = 99: the top five of a 100% distribution.
    expect(percentages()).toEqual([37, 30, 17, 13, 2])
  })
})
