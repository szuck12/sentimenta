import { motion } from 'framer-motion'
import { cn, toWholePercentages } from '@/lib/utils'
import { Card } from '@/components/ui/Card'

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

function capitalize(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1)
}

interface EmotionMixCardProps {
  emotions: Array<{ label: string; score: number }>
  primaryLabel: string
}

export function EmotionMixCard({
  emotions,
  primaryLabel,
}: EmotionMixCardProps) {
  const percentages = toWholePercentages(emotions.map((e) => e.score))

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card>
        <h3 className="font-display font-semibold text-ink-800 mb-4">
          Emotion Mix
        </h3>

        <div className="flex flex-col gap-2">
          {emotions.map(({ label }, index) => {
            const pct = percentages[index]
            const isPrimary = label === primaryLabel

            return (
              <div
                key={label}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2',
                  isPrimary && 'bg-cream-100',
                )}
              >
                <span className="w-6 text-center shrink-0">
                  {EMOJI_MAP[label] ?? '❓'}
                </span>

                <span className="w-28 text-sm text-ink-700 shrink-0">
                  {capitalize(label)}
                </span>

                <div className="flex-1 h-2 rounded-full bg-cream-200 overflow-hidden">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-coral-400 to-coral-500 transition-all duration-500"
                    style={{ width: `${pct}%` }}
                  />
                </div>

                <span className="w-10 text-right text-xs tabular-nums text-ink-700/70 shrink-0">
                  {pct}%
                </span>
              </div>
            )
          })}
        </div>
      </Card>
    </motion.div>
  )
}
