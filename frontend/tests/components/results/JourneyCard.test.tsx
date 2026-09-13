// frontend/tests/components/results/JourneyCard.test.tsx

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { JourneyCard } from '@/components/results/JourneyCard'

const sentences = [
  {
    text: 'I was nervous.',
    primary_emotion: { label: 'nervousness', score: 0.8 },
  },
  {
    text: 'Then I felt relieved.',
    primary_emotion: { label: 'relief', score: 0.7 },
  },
]

describe('JourneyCard', () => {
  it('renders nothing for a single sentence', () => {
    const { container } = render(
      <JourneyCard sentences={[sentences[0]]} />,
    )
    expect(container).toBeEmptyDOMElement()
  })

  it('renders each sentence with its emotion badge', () => {
    render(<JourneyCard sentences={sentences} />)
    expect(screen.getByText('I was nervous.')).toBeInTheDocument()
    expect(screen.getByText(/nervousness \(80%\)/)).toBeInTheDocument()
    expect(screen.getByText(/relief \(70%\)/)).toBeInTheDocument()
  })

  it('truncates very long sentences', () => {
    const long = 'w'.repeat(120) + '.'
    render(
      <JourneyCard
        sentences={[
          {
            text: long,
            primary_emotion: { label: 'joy', score: 0.5 },
          },
          sentences[1],
        ]}
      />,
    )
    expect(screen.getByText(/…/)).toBeInTheDocument()
  })
})
