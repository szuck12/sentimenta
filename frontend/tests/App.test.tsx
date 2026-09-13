// frontend/tests/App.test.tsx
// Router navigation across the three pages.

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import App from '@/App'
import { jsonResponse, makeEmotionsResponse } from './fixtures'

afterEach(() => {
  vi.unstubAllGlobals()
})

beforeEach(() => {
  window.history.pushState({}, '', '/')
})

describe('App routing', () => {
  it('renders the home page at the root route', () => {
    render(<App />)
    expect(
      screen.getByRole('heading', {
        name: /what are your words feeling/i,
      }),
    ).toBeInTheDocument()
  })

  it('navigates to How It Works', async () => {
    render(<App />)
    await userEvent.click(
      screen.getByRole('link', { name: 'How It Works' }),
    )
    expect(
      await screen.findByRole('heading', { name: 'How It Works' }),
    ).toBeInTheDocument()
  })

  it('navigates to Emotions and loads the taxonomy', async () => {
    vi.stubGlobal('fetch', vi.fn(() => jsonResponse(makeEmotionsResponse())))
    render(<App />)
    await userEvent.click(screen.getByRole('link', { name: 'Emotions' }))
    expect(await screen.findByText('joy')).toBeInTheDocument()
  })
})
