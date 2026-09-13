// frontend/tests/components/results/EmotionMixCard.test.tsx

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { EmotionMixCard } from '@/components/results/EmotionMixCard'

describe('EmotionMixCard', () => {
  it('renders each emotion with its percentage', () => {
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
    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByText('70%')).toBeInTheDocument()
  })
})
