// frontend/tests/components/results/ResultsSection.test.tsx

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ResultsSection } from '@/components/results/ResultsSection'
import { toWholePercentages } from '@/lib/utils'
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

  it('shows exactly the top five emotions in the mix', () => {
    render(<ResultsSection result={makeAnalyzeResponse()} />)
    for (const label of [
      'Joy',
      'Excitement',
      'Optimism',
      'Curiosity',
      'Neutral',
    ]) {
      expect(screen.getByText(label)).toBeInTheDocument()
    }
    // The sixth-ranked emotion is excluded from the mix.
    expect(screen.queryByText('Anger')).not.toBeInTheDocument()
  })

  it('shares the full-spectrum distribution with the primary and mix', () => {
    const result = makeAnalyzeResponse()
    render(<ResultsSection result={result} />)
    const shares = toWholePercentages(result.all_emotions.map((e) => e.score))
    const joyIndex = result.all_emotions.findIndex((e) => e.label === 'joy')
    const joyPct = shares[joyIndex]
    // The primary emotion's percentage is its share of the distribution.
    expect(screen.getByText(`${joyPct}% confidence`)).toBeInTheDocument()
    // The mix shows the same share for that emotion.
    expect(screen.getByText(`${joyPct}%`)).toBeInTheDocument()
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
