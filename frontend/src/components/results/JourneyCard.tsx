import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/Card'
import { Badge } from '@/components/ui/Badge'

const EMOJI_MAP: Record<string, string> = {
  admiration: '👏', amusement: '😄', anger: '😠',
  annoyance: '😒', approval: '👍', caring: '🤗',
  confusion: '🤔', curiosity: '🧐', desire: '✨',
  disappointment: '😞', disapproval: '👎',
  disgust: '🤢', embarrassment: '😳',
  excitement: '🤩', fear: '😨', gratitude: '🙏',
  grief: '💔', joy: '😊', love: '❤️',
  nervousness: '😬', optimism: '🌤️', pride: '🏆',
  realization: '💡', relief: '😌', remorse: '😔',
  sadness: '😢', surprise: '😲', neutral: '😐',
}

const POSITIVE_LABELS = [
  'admiration', 'amusement', 'approval', 'caring',
  'desire', 'excitement', 'gratitude', 'joy', 'love',
  'optimism', 'pride', 'relief',
]
const NEGATIVE_LABELS = [
  'anger', 'annoyance', 'disappointment', 'disapproval',
  'disgust', 'embarrassment', 'fear', 'grief',
  'nervousness', 'remorse', 'sadness',
]
const COGNITIVE_LABELS = [
  'confusion', 'curiosity', 'realization', 'surprise',
]

function lineColor(label: string): string {
  if (POSITIVE_LABELS.includes(label)) return 'bg-coral-400'
  if (NEGATIVE_LABELS.includes(label)) return 'bg-rose-400'
  if (COGNITIVE_LABELS.includes(label)) return 'bg-lavender-400'
  return 'bg-sand-400'
}

function badgeVariant(
  label: string,
): 'positive' | 'negative' | 'cognitive' | 'neutral' {
  if (POSITIVE_LABELS.includes(label)) return 'positive'
  if (NEGATIVE_LABELS.includes(label)) return 'negative'
  if (COGNITIVE_LABELS.includes(label)) return 'cognitive'
  return 'neutral'
}

function truncate(s: string, max: number): string {
  if (s.length <= max) return s
  return s.slice(0, max).trimEnd() + '…'
}

interface JourneyCardProps {
  sentences: Array<{
    text: string
    primary_emotion: { label: string; score: number }
  }>
}

export function JourneyCard({ sentences }: JourneyCardProps) {
  if (sentences.length <= 1) return null

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card>
        <h3 className="font-display font-semibold text-ink-800 mb-4">
          Emotional Journey
        </h3>

        <div className="relative flex flex-col gap-0">
          {sentences.map((item, i) => {
            const { label, score } = item.primary_emotion
            const pct = Math.round(score * 100)
            const isLast = i === sentences.length - 1

            return (
              <div key={i} className="flex gap-3">
                <div className="relative flex flex-col items-center shrink-0">
                  <div
                    className={cn(
                      'w-2 h-2 rounded-full mt-1.5 z-10',
                      lineColor(label),
                    )}
                  />
                  {!isLast && (
                    <div
                      className={cn(
                        'w-0.5 flex-1 rounded-full',
                        lineColor(
                          sentences[i + 1]?.primary_emotion
                            .label ?? '',
                        ),
                      )}
                    />
                  )}
                </div>

                <div
                  className={cn(
                    'pb-4',
                    isLast && 'pb-0',
                  )}
                >
                  <p className="text-sm text-ink-700/80 mb-1">
                    {truncate(item.text, 80)}
                  </p>
                  <Badge
                    variant={badgeVariant(label)}
                  >
                    {EMOJI_MAP[label] ?? '❓'}{' '}
                    {label} ({pct}%)
                  </Badge>
                </div>
              </div>
            )
          })}
        </div>
      </Card>
    </motion.div>
  )
}
