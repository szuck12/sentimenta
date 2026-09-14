// frontend/tests/pages/Emotions.test.tsx

import { render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Emotions } from '@/pages/Emotions'
import { jsonResponse, makeEmotionsResponse } from '../fixtures'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('Emotions', () => {
  it('shows a loading state until data arrives', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(<Emotions />)
    expect(screen.getByText(/loading emotions/i)).toBeInTheDocument()
  })

  it('renders the taxonomy grouped by family', async () => {
    vi.stubGlobal('fetch', vi.fn(() => jsonResponse(makeEmotionsResponse())))
    render(<Emotions />)
    expect(await screen.findByText('joy')).toBeInTheDocument()
    expect(screen.getByText(/Positive & affiliative/)).toBeInTheDocument()
    expect(screen.getByText(/Negative & heavy/)).toBeInTheDocument()
  })

  it('shows an error message when the fetch fails', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => jsonResponse({}, 500)),
    )
    render(<Emotions />)
    expect(
      await screen.findByText(/failed to load emotions/i),
    ).toBeInTheDocument()
  })

  it('shows a retry button after error', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() => jsonResponse({}, 500)),
    )
    render(<Emotions />)
    await screen.findByText(/failed to load emotions/i)
    expect(
      screen.getByRole('button', { name: /retry/i }),
    ).toBeInTheDocument()
  })
})
