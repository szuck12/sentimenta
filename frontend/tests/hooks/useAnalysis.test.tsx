// frontend/tests/hooks/useAnalysis.test.tsx
// Lifecycle of the analysis hook: idle -> loading -> success/error,
// plus reset behaviour.

import { act, renderHook, waitFor } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { useAnalysis } from '@/hooks/useAnalysis'
import { jsonResponse, makeAnalyzeResponse } from '../fixtures'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('useAnalysis', () => {
  it('starts idle', () => {
    const { result } = renderHook(() => useAnalysis())
    expect(result.current.status).toBe('idle')
    expect(result.current.result).toBeNull()
    expect(result.current.error).toBeNull()
  })

  it('moves idle -> loading -> success', async () => {
    vi.stubGlobal('fetch', vi.fn(() => jsonResponse(makeAnalyzeResponse())))
    const { result } = renderHook(() => useAnalysis())

    act(() => {
      void result.current.run('hello')
    })
    expect(result.current.status).toBe('loading')

    await waitFor(() => expect(result.current.status).toBe('success'))
    expect(result.current.result?.primary_emotion.label).toBe('joy')
  })

  it('records the error message on failure', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        jsonResponse(
          { error: { code: 'boom', message: 'Nope.' } },
          500,
        ),
      ),
    )
    const { result } = renderHook(() => useAnalysis())

    await act(async () => {
      await result.current.run('hello')
    })

    expect(result.current.status).toBe('error')
    expect(result.current.error).toBe('Nope.')
  })

  it('reset clears result and error', async () => {
    vi.stubGlobal('fetch', vi.fn(() => jsonResponse(makeAnalyzeResponse())))
    const { result } = renderHook(() => useAnalysis())

    await act(async () => {
      await result.current.run('hello')
    })
    expect(result.current.status).toBe('success')

    act(() => {
      result.current.reset()
    })
    expect(result.current.status).toBe('idle')
    expect(result.current.result).toBeNull()
    expect(result.current.error).toBeNull()
  })
})
