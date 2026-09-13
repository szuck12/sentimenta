// frontend/tests/lib/api.test.ts
// The typed fetch wrapper: request shaping and error surfaces.

import { afterEach, describe, expect, it, vi } from 'vitest'
import { analyze, analyzeSentences, fetchEmotions } from '@/lib/api'
import { jsonResponse, makeAnalyzeResponse, makeEmotionsResponse } from '../fixtures'

type FetchArgs = [url: string, init?: RequestInit]

afterEach(() => {
  vi.unstubAllGlobals()
})

function stubFetch() {
  const mock = vi.fn<(...args: FetchArgs) => Promise<unknown>>()
  vi.stubGlobal('fetch', mock)
  return mock
}

describe('api client', () => {
  it('POSTs analyze with the expected body', async () => {
    const mock = stubFetch()
    mock.mockResolvedValue(jsonResponse(makeAnalyzeResponse()))

    const result = await analyze('hello')

    expect(result.primary_emotion.label).toBe('joy')
    const [url, init] = mock.mock.calls[0]
    expect(url).toBe('/api/analyze')
    expect(init?.method).toBe('POST')
    expect(JSON.parse(String(init?.body))).toEqual({
      text: 'hello',
      include_sentences: false,
    })
  })

  it('requests sentences when includeSentences is true', async () => {
    const mock = stubFetch()
    mock.mockResolvedValue(jsonResponse(makeAnalyzeResponse()))

    await analyzeSentences('hello')

    const [, init] = mock.mock.calls[0]
    expect(JSON.parse(String(init?.body))).toEqual({
      text: 'hello',
      include_sentences: true,
    })
  })

  it('GETs the emotion taxonomy', async () => {
    const mock = stubFetch()
    mock.mockResolvedValue(jsonResponse(makeEmotionsResponse()))

    const result = await fetchEmotions()

    expect(result.count).toBe(3)
    expect(mock).toHaveBeenCalledWith('/api/emotions', {})
  })

  it('surfaces the server error message', async () => {
    const mock = stubFetch()
    mock.mockResolvedValue(
      jsonResponse(
        { error: { code: 'text_too_long', message: 'Too long.' } },
        422,
      ),
    )

    await expect(analyze('x')).rejects.toThrow('Too long.')
  })

  it('propagates network failures', async () => {
    const mock = stubFetch()
    mock.mockRejectedValue(new TypeError('Failed to fetch'))

    await expect(analyze('x')).rejects.toThrow('Failed to fetch')
  })
})
