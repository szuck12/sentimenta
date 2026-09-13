// frontend/tests/components/results/PrimaryEmotionCard.test.tsx

import { type ComponentProps } from 'react'
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { PrimaryEmotionCard } from '@/components/results/PrimaryEmotionCard'

function renderCard(
  overrides: Partial<ComponentProps<typeof PrimaryEmotionCard>> = {},
) {
  const props = {
    label: 'joy',
    score: 0.85,
    summary: 'Detected joy.',
    intensity: { score: 0.9, label: 'high' },
    ...overrides,
  }
  return render(<PrimaryEmotionCard {...props} />)
}

describe('PrimaryEmotionCard', () => {
  it('renders label, confidence, and summary', () => {
    renderCard()
    expect(screen.getByText('joy')).toBeInTheDocument()
    expect(screen.getByText('85% confidence')).toBeInTheDocument()
    expect(screen.getByText('Detected joy.')).toBeInTheDocument()
  })

  it('shows the intensity badge', () => {
    renderCard()
    expect(screen.getByText(/high intensity/i)).toBeInTheDocument()
  })

  it('falls back to a placeholder for unknown labels', () => {
    const { container } = renderCard({ label: 'mystery' })
    expect(container.textContent).toContain('❓')
  })

  it('omits the summary when empty', () => {
    renderCard({ summary: '' })
    expect(screen.queryByText('Detected joy.')).not.toBeInTheDocument()
  })
})
