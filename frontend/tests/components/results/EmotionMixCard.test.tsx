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
  it('renders each emotion with a normalized percentage', () => {
    render(
      <EmotionMixCard
        emotions={[
          { label: 'joy', score: 0.85 },
          { label: 'excitement', score: 0.7 },
        ]}
        primaryLabel="joy"
      />,
    )
    expect(screen.getByText('Joy')).toBeInTheDocument()
    expect(screen.getByText('Excitement')).toBeInTheDocument()
    // 85 / (85 + 70) and 70 / (85 + 70), rounded to whole numbers.
    expect(screen.getByText('55%')).toBeInTheDocument()
    expect(screen.getByText('45%')).toBeInTheDocument()
  })

  it('always sums to 100%', () => {
    render(
      <EmotionMixCard
        emotions={[
          { label: 'joy', score: 0.85 },
          { label: 'excitement', score: 0.7 },
          { label: 'optimism', score: 0.4 },
          { label: 'curiosity', score: 0.3 },
          { label: 'neutral', score: 0.05 },
        ]}
        primaryLabel="joy"
      />,
    )
    expect(percentages().reduce((sum, value) => sum + value, 0)).toBe(100)
  })
})
