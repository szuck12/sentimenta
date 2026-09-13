// frontend/tests/components/ui/Card.test.tsx

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Card } from '@/components/ui/Card'

describe('Card', () => {
  it('renders children and merges class names', () => {
    render(
      <Card data-testid="card" className="custom">
        Body
      </Card>,
    )
    const card = screen.getByTestId('card')
    expect(card).toHaveTextContent('Body')
    expect(card.className).toContain('custom')
    expect(card.className).toContain('rounded-2xl')
  })
})
