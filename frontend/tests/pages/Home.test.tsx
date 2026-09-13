// frontend/tests/pages/Home.test.tsx

import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { Home } from '@/pages/Home'
import { jsonResponse, makeAnalyzeResponse } from '../fixtures'

afterEach(() => {
  vi.unstubAllGlobals()
})

function renderHome() {
  return render(
    <MemoryRouter>
      <Home />
    </MemoryRouter>,
  )
}

describe('Home', () => {
  it('renders the hero and input card', () => {
    renderHome()
    expect(
      screen.getByRole('heading', {
        name: /what are your words feeling/i,
      }),
    ).toBeInTheDocument()
    expect(
      screen.getByPlaceholderText(/read between the lines/i),
    ).toBeInTheDocument()
  })

  it('runs an analysis and renders the results', async () => {
    vi.stubGlobal('fetch', vi.fn(() => jsonResponse(makeAnalyzeResponse())))
    renderHome()

    await userEvent.type(
      screen.getByPlaceholderText(/read between the lines/i),
      'I love this',
    )
    await userEvent.click(
      screen.getByRole('button', { name: /analyze emotion/i }),
    )

    expect(await screen.findByText('Emotion Mix')).toBeInTheDocument()
  })

  it('surfaces an error from the API', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        jsonResponse(
          { error: { code: 'boom', message: 'Server exploded.' } },
          500,
        ),
      ),
    )
    renderHome()

    await userEvent.type(
      screen.getByPlaceholderText(/read between the lines/i),
      'hi',
    )
    await userEvent.click(
      screen.getByRole('button', { name: /analyze emotion/i }),
    )

    expect(await screen.findByText('Server exploded.')).toBeInTheDocument()
  })
})
