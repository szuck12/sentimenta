// frontend/tests/components/results/ExplanationCard.test.tsx

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ExplanationCard } from '@/components/results/ExplanationCard'

describe('ExplanationCard', () => {
  it('renders signals with the attribution note', () => {
    render(
      <ExplanationCard
        summary="Why joy."
        signals={[{ text: 'love', weight: 1 }]}
        method="integrated_gradients"
      />,
    )
    expect(screen.getByText('Why joy.')).toBeInTheDocument()
    expect(screen.getByText('love')).toBeInTheDocument()
    expect(screen.getByText(/token attribution/i)).toBeInTheDocument()
  })

  it('shows the fallback message when there are no signals', () => {
    render(
      <ExplanationCard
        summary="Only probabilities."
        signals={[]}
        method="probabilities"
      />,
    )
    expect(
      screen.getByText(/unavailable for this analysis/i),
    ).toBeInTheDocument()
  })

  it('describes probability-based evidence when signals exist', () => {
    render(
      <ExplanationCard
        summary="s"
        signals={[{ text: 'love', weight: 1 }]}
        method="probabilities"
      />,
    )
    expect(
      screen.getByText(/probability-based evidence/i),
    ).toBeInTheDocument()
  })
})
