// src/lib/api.ts
// Typed fetch wrapper for the Sentimenta backend.

import type { AnalyzeResponse, EmotionsResponse, ApiError } from './types'

const BASE = ''

async function request<T>(path: string, body?: unknown): Promise<T> {
  const init: RequestInit = body
    ? {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }
    : {}

  const res = await fetch(`${BASE}${path}`, init)
  const json = await res.json()

  if (!res.ok) {
    const err = json as ApiError
    throw new Error(err.error?.message ?? 'An unexpected error occurred.')
  }
  return json as T
}

export async function analyze(
  text: string,
  includeSentences = false,
): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>('/api/analyze', {
    text,
    include_sentences: includeSentences,
  })
}

export async function analyzeSentences(
  text: string,
): Promise<AnalyzeResponse> {
  return request<AnalyzeResponse>('/api/analyze', {
    text,
    include_sentences: true,
  })
}

export async function fetchEmotions(): Promise<EmotionsResponse> {
  return request<EmotionsResponse>('/api/emotions')
}
