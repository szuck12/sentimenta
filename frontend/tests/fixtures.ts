// frontend/tests/fixtures.ts
// Shared deterministic API payloads for component and page tests.

import type { AnalyzeResponse, EmotionsResponse } from '@/lib/types'

export function makeAnalyzeResponse(
  overrides: Partial<AnalyzeResponse> = {},
): AnalyzeResponse {
  const base: AnalyzeResponse = {
    primary_emotion: { label: 'joy', score: 0.85 },
    emotions: [
      { label: 'joy', score: 0.85 },
      { label: 'excitement', score: 0.7 },
    ],
    all_emotions: [
      { label: 'joy', score: 0.85 },
      { label: 'excitement', score: 0.7 },
      { label: 'optimism', score: 0.4 },
      { label: 'curiosity', score: 0.3 },
      { label: 'neutral', score: 0.05 },
      { label: 'anger', score: 0.02 },
    ],
    intensity: { score: 0.9, label: 'high' },
    profile: {
      positive: 2.0,
      negative: 0.2,
      cognitive: 0.1,
      neutral: 0.05,
      shares: {
        positive: 0.85,
        negative: 0.08,
        cognitive: 0.04,
        neutral: 0.03,
      },
    },
    explanation: {
      summary: 'Sentimenta detected joy (85% confidence).',
      signals: [{ text: 'love', weight: 1.0 }],
      method: 'integrated_gradients',
      target_label: 'joy',
      target_percentage: 54,
    },
    sentences: [
      {
        index: 0,
        text: 'I love this.',
        primary_emotion: { label: 'joy', score: 0.85 },
        emotions: [],
      },
      {
        index: 1,
        text: 'It is wonderful.',
        primary_emotion: { label: 'joy', score: 0.6 },
        emotions: [],
      },
    ],
    metadata: {
      model_id: 'test-model',
      char_count: 20,
      word_count: 4,
      sentence_count: 2,
      threshold: 0.3,
      attribution_used: true,
      truncated_tokens: false,
      latency_ms: { inference: 10, explanation: 5, total: 15 },
    },
  }
  return { ...base, ...overrides }
}

export function makeEmotionsResponse(): EmotionsResponse {
  return {
    count: 3,
    groups: {
      positive: 'Positive & affiliative',
      negative: 'Negative & heavy',
      cognitive: 'Cognitive & ambiguous',
      neutral: 'Neutral',
    },
    emotions: [
      {
        label: 'joy',
        emoji: '😊',
        group: 'positive',
        description: 'Happiness and delight.',
      },
      {
        label: 'anger',
        emoji: '😠',
        group: 'negative',
        description: 'Strong displeasure.',
      },
      {
        label: 'neutral',
        emoji: '😐',
        group: 'neutral',
        description: 'No strong signal.',
      },
    ],
  }
}

export function jsonResponse(body: unknown, status = 200) {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  })
}
