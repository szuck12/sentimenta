// frontend/tests/components/ui/Badge.test.tsx

import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Badge } from '@/components/ui/Badge'

describe('Badge', () => {
  it('renders its content', () => {
    render(<Badge>joy</Badge>)
    expect(screen.getByText('joy')).toBeInTheDocument()
  })

  it('applies variant styling', () => {
    render(<Badge variant="negative">anger</Badge>)
    expect(screen.getByText('anger').className).toContain('rose')
  })
})
