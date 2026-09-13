// frontend/tests/components/results/ResultsSection.test.tsx

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ResultsSection } from '@/components/results/ResultsSection'
import { makeAnalyzeResponse } from '../../fixtures'

describe('ResultsSection', () => {
  it('composes every result card', () => {
    render(<ResultsSection result={makeAnalyzeResponse()} />)
    expect(screen.getByText('Emotion Mix')).toBeInTheDocument()
    expect(
      screen.getByText('Why Sentimenta thinks this'),
    ).toBeInTheDocument()
    expect(screen.getByText('Emotional Journey')).toBeInTheDocument()
    expect(screen.getByText('Full Spectrum')).toBeInTheDocument()
    expect(
      screen.getByText(/results are estimates/i),
    ).toBeInTheDocument()
  })

  it('omits the journey card for single-sentence results', () => {
    const result = makeAnalyzeResponse({
      sentences: [
        {
          index: 0,
          text: 'One sentence only.',
          primary_emotion: { label: 'neutral', score: 0.9 },
          emotions: [],
        },
      ],
    })
    render(<ResultsSection result={result} />)
    expect(
      screen.queryByText('Emotional Journey'),
    ).not.toBeInTheDocument()
  })
})
