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

const RADIUS = 40
const CIRCUMFERENCE = 2 * Math.PI * RADIUS
const STROKE_WIDTH = 6
const SVG_SIZE = (RADIUS + STROKE_WIDTH) * 2

interface PrimaryEmotionCardProps {
  label: string
  percentage: number
  summary: string
  intensity: { score: number; label: string }
}

function getIntensityVariant(
  intensityLabel: string,
): 'positive' | 'negative' | 'neutral' | 'default' {
  if (intensityLabel === 'high') return 'positive'
  if (intensityLabel === 'moderate') return 'default'
  return 'neutral'
}

export function PrimaryEmotionCard({
  label,
  percentage,
  summary,
  intensity,
}: PrimaryEmotionCardProps) {
  const emoji = EMOJI_MAP[label] ?? '❓'
  const pct = percentage
  const offset = CIRCUMFERENCE * (1 - percentage / 100)

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="text-center py-10 px-8">
        <div className="flex flex-col items-center gap-4">
          <div className="relative inline-flex items-center justify-center">
            <svg
              width={SVG_SIZE}
              height={SVG_SIZE}
              className="rotate-[-90deg]"
            >
              <circle
                cx={SVG_SIZE / 2}
                cy={SVG_SIZE / 2}
                r={RADIUS}
                fill="none"
                stroke="currentColor"
                strokeWidth={STROKE_WIDTH}
                className="text-cream-200"
              />
              <circle
                cx={SVG_SIZE / 2}
                cy={SVG_SIZE / 2}
                r={RADIUS}
                fill="none"
                stroke="currentColor"
                strokeWidth={STROKE_WIDTH}
                strokeDasharray={CIRCUMFERENCE}
                strokeDashoffset={offset}
                strokeLinecap="round"
                className="text-coral-500"
                style={{
                  transition: 'stroke-dashoffset 0.8s ease-out',
                }}
              />
            </svg>
            <span
              className="absolute text-4xl"
              aria-hidden="true"
            >
              {emoji}
            </span>
          </div>

          <div className="flex flex-col items-center gap-1">
            <h2
              className={cn(
                'font-display font-bold tracking-wide',
                'text-3xl text-ink-800 uppercase',
              )}
            >
              {label}
            </h2>
            <p className="text-sm text-ink-700/60">
              {pct}% confidence
            </p>
          </div>

          {summary && (
            <p className="text-ink-700/80 max-w-md leading-relaxed">
              {summary}
            </p>
          )}

          <Badge
            variant={getIntensityVariant(intensity.label)}
          >
            {intensity.label} intensity
          </Badge>
        </div>
      </Card>
    </motion.div>
  )
}
