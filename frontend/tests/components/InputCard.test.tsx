// frontend/tests/components/InputCard.test.tsx
// Component-level tests for the InputCard form.

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { InputCard } from '@/components/InputCard'

describe('InputCard', () => {
  const defaultProps = {
    status: 'idle' as const,
    onSubmit: vi.fn(),
    onReset: vi.fn(),
  }

  it('renders textarea and button', () => {
    render(<InputCard {...defaultProps} />)
    expect(screen.getByPlaceholderText(/read between the lines/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /analyze emotion/i })).toBeInTheDocument()
  })

  it('shows character count', () => {
    render(<InputCard {...defaultProps} />)
    expect(screen.getByText(/characters$/)).toBeInTheDocument()
  })

  it('displays example chips', () => {
    render(<InputCard {...defaultProps} />)
    expect(screen.getByRole('button', { name: 'Excitement' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Neutral' })).toBeInTheDocument()
  })

  it('populates text on example click', async () => {
    const user = userEvent.setup()
    render(<InputCard {...defaultProps} />)
    await user.click(screen.getByRole('button', { name: 'Gratitude' }))
    const textarea = screen.getByPlaceholderText(/read between the lines/i) as HTMLTextAreaElement
    expect(textarea.value).toContain('Thank you')
  })

  it('disables button when loading', () => {
    render(<InputCard {...defaultProps} status="loading" />)
    expect(screen.getByRole('button', { name: /analysing/i })).toBeDisabled()
  })

  it('shows start over button after success', () => {
    render(<InputCard {...defaultProps} status="success" />)
    expect(screen.getByRole('button', { name: /start over/i })).toBeInTheDocument()
  })
})
