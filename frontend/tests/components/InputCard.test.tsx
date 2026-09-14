// frontend/tests/components/InputCard.test.tsx
// Component-level tests for the InputCard form.

import { type ComponentProps } from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { InputCard } from '@/components/InputCard'

function setup(
  overrides: Partial<ComponentProps<typeof InputCard>> = {},
) {
  const props: ComponentProps<typeof InputCard> = {
    status: 'idle',
    onSubmit: vi.fn(),
    onReset: vi.fn(),
    ...overrides,
  }
  render(<InputCard {...props} />)
  return props
}

function textarea(): HTMLTextAreaElement {
  return screen.getByPlaceholderText(
    /read between the lines/i,
  ) as HTMLTextAreaElement
}

describe('InputCard', () => {
  it('renders textarea and button', () => {
    setup()
    expect(textarea()).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: /analyze emotion/i }),
    ).toBeInTheDocument()
  })

  it('shows character count', () => {
    setup()
    expect(screen.getByText(/characters$/)).toBeInTheDocument()
  })

  it('displays example chips', () => {
    setup()
    expect(
      screen.getByRole('button', { name: 'Excitement' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Fear' }),
    ).toBeInTheDocument()
    expect(
      screen.getByRole('button', { name: 'Neutral' }),
    ).toBeInTheDocument()
    expect(
      screen.queryByRole('button', { name: 'Worry' }),
    ).not.toBeInTheDocument()
  })

  it('populates text on example click', async () => {
    setup()
    await userEvent.click(screen.getByRole('button', { name: 'Gratitude' }))
    expect(textarea().value).toContain('Thank you')
  })

  it('fills the excitement example sentence', async () => {
    setup()
    await userEvent.click(screen.getByRole('button', { name: 'Excitement' }))
    expect(textarea().value).toContain('excited')
  })

  it('fills the fear example sentence', async () => {
    setup()
    await userEvent.click(screen.getByRole('button', { name: 'Fear' }))
    expect(textarea().value).toContain('terrified')
  })

  it('disables analyze while the text is empty', () => {
    setup()
    expect(
      screen.getByRole('button', { name: /analyze emotion/i }),
    ).toBeDisabled()
  })

  it('submits the typed text', async () => {
    const props = setup()
    await userEvent.type(textarea(), 'Hello world')
    await userEvent.click(
      screen.getByRole('button', { name: /analyze emotion/i }),
    )
    expect(props.onSubmit).toHaveBeenCalledWith('Hello world')
  })

  it('shows a validation error on empty submit', async () => {
    setup()
    const form = textarea().closest('form') as HTMLFormElement
    fireEvent.submit(form)
    expect(
      await screen.findByText(/please enter some text/i),
    ).toBeInTheDocument()
  })

  it('disables submit and flags over-limit text', () => {
    setup()
    fireEvent.change(textarea(), { target: { value: 'x'.repeat(2001) } })
    expect(
      screen.getByRole('button', { name: /analyze emotion/i }),
    ).toBeDisabled()
  })

  it('clears text and calls onReset', async () => {
    const props = setup()
    await userEvent.type(textarea(), 'Hello')
    await userEvent.click(screen.getByLabelText(/clear text/i))
    expect(textarea().value).toBe('')
    expect(props.onReset).toHaveBeenCalled()
  })

  it('disables example chips while loading', () => {
    setup({ status: 'loading' })
    expect(
      screen.getByRole('button', { name: 'Excitement' }),
    ).toBeDisabled()
    expect(
      screen.getByRole('button', { name: /analysing/i }),
    ).toBeDisabled()
  })

  it('shows start over after success', () => {
    setup({ status: 'success' })
    expect(
      screen.getByRole('button', { name: /start over/i }),
    ).toBeInTheDocument()
  })

  it('shows start over after an error', () => {
    setup({ status: 'error' })
    expect(
      screen.getByRole('button', { name: /start over/i }),
    ).toBeInTheDocument()
  })
})
