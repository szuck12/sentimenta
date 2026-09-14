// src/lib/types.ts
// Shared TypeScript types mirroring the Sentimenta backend API contract.

export interface EmotionScore {
  label: string
  score: number
}

/**
 * An emotion paired with its whole-number share of the derived
 * distribution across all detected emotions. The shares across the full
 * 28-emotion spectrum always sum to exactly 100.
 */
export interface EmotionPercentage {
  label: string
  percentage: number
}

export interface Intensity {
  score: number
  label: 'low' | 'moderate' | 'high'
}

export interface EvidenceSignal {
  text: string
  weight: number
}

export interface Explanation {
  summary: string
  signals: EvidenceSignal[]
  method: 'integrated_gradients' | 'probabilities'
  target_label: string
}

export interface ProfileShares {
  positive: number
  negative: number
  cognitive: number
  neutral: number
}

export interface AnalyzeResponse {
  primary_emotion: EmotionScore
  emotions: EmotionScore[]
  all_emotions: EmotionScore[]
  intensity: Intensity
  profile: {
    positive: number
    negative: number
    cognitive: number
    neutral: number
    shares: ProfileShares
  }
  explanation: Explanation
  sentences: SentenceAnalysis[]
  metadata: {
    model_id: string
    char_count: number
    word_count: number
    sentence_count: number
    threshold: number
    attribution_used: boolean
    truncated_tokens: boolean
    latency_ms: Record<string, number>
  }
}

export interface SentenceAnalysis {
  index: number
  text: string
  primary_emotion: EmotionScore
  emotions: EmotionScore[]
}

export interface EmotionInfo {
  label: string
  emoji: string
  group: 'positive' | 'negative' | 'cognitive' | 'neutral'
  description: string
}

export interface EmotionsResponse {
  count: number
  groups: Record<string, string>
  emotions: EmotionInfo[]
}

export interface ApiError {
  error: {
    code: string
    message: string
  }
}

export const EMOTION_COLORS: Record<string, string> = {
  positive: '#F97D4D',
  negative: '#F47B82',
  cognitive: '#A78BFA',
  neutral: '#C5B9A8',
}

export const GROUP_LABELS: Record<string, string> = {
  positive: 'Positive & affiliative',
  negative: 'Negative & heavy',
  cognitive: 'Cognitive & ambiguous',
  neutral: 'Neutral',
}
