// src/pages/Emotions.tsx
// Reference page displaying all 28 GoEmotions labels with their
// emoji, description, and group classification.

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'
import { Button } from '@/components/ui/Button'
import { fetchEmotions } from '@/lib/api'
import type { EmotionInfo, EmotionsResponse } from '@/lib/types'

const GROUP_COLORS: Record<string, string> = {
  positive: 'positive',
  negative: 'negative',
  cognitive: 'cognitive',
  neutral: 'neutral',
} as const

export function Emotions() {
  const [data, setData] = useState<EmotionsResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchEmotions()
      .then(setData)
      .catch(() => setError('Failed to load emotions. Please try again.'))
  }, [])

  if (error && !data) {
    return (
      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="text-center text-red-600 py-20">
          {error}
        </div>
        <div className="text-center">
          <Button onClick={() => window.location.reload()} variant="secondary">
            Retry
          </Button>
        </div>
      </main>
    )
  }

  if (!data) {
    return (
      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="text-center text-ink-700/40 py-20">
          Loading emotions...
        </div>
      </main>
    )
  }

  const byGroup = (group: string): EmotionInfo[] =>
    data.emotions.filter((e) => e.group === group)

  return (
    <main className="max-w-4xl mx-auto px-6 py-12">
      <section className="mb-8">
        <h1 className="text-3xl sm:text-4xl font-display font-bold text-ink-800 tracking-tight mb-4">
          The 28 Emotions
        </h1>
        <p className="text-ink-700/60 max-w-2xl leading-relaxed">
          GoEmotions recognizes 27 specific emotions plus neutral.
          Sentimenta groups them into broad families for
          visualization, but each label is distinct.
        </p>
      </section>

      {(Object.keys(data.groups) as string[]).map((group) => (
        <section key={group} className="mb-10">
          <h2 className="text-xl font-display font-semibold text-ink-800 mb-4 capitalize">
            {data.groups[group]}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {byGroup(group).map((emotion) => (
              <Card key={emotion.label} className="flex items-start gap-3 p-4">
                <span className="text-2xl shrink-0">{emotion.emoji}</span>
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="font-medium text-sm text-ink-800 capitalize">
                      {emotion.label}
                    </h3>
                    <Badge variant={GROUP_COLORS[group] as 'positive' | 'negative' | 'cognitive' | 'neutral'}>
                      {group}
                    </Badge>
                  </div>
                  <p className="text-xs text-ink-700/50 leading-relaxed">
                    {emotion.description}
                  </p>
                </div>
              </Card>
            ))}
          </div>
        </section>
      ))}

      <section className="text-center mt-8">
        <a
          href="/#analyze"
          className="text-coral-500 hover:text-coral-600 text-sm font-semibold"
        >
          Analyze some text →
        </a>
      </section>
    </main>
  )
}
