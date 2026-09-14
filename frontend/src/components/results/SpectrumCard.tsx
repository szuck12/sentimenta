import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import { cn } from '@/lib/utils'
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

interface SpectrumCardProps {
  emotions: Array<{ label: string; score: number }>
}

export function SpectrumCard({ emotions }: SpectrumCardProps) {
  const [expanded, setExpanded] = useState(false)

  const sorted = [...emotions].sort(
    (a, b) => b.score - a.score,
  )

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-display font-semibold text-ink-800">
            Full Spectrum
          </h3>
          <button
            type="button"
            onClick={() => setExpanded((prev) => !prev)}
            className={cn(
              'inline-flex items-center gap-1 text-sm',
              'text-coral-500 hover:text-coral-600',
              'transition-colors font-medium',
            )}
          >
            {expanded ? 'Hide' : 'Show full spectrum'}
            <ChevronDown
              size={16}
              className={cn(
                'transition-transform duration-300',
                expanded && 'rotate-180',
              )}
            />
          </button>
        </div>

        <AnimatePresence initial={false}>
          {expanded && (
            <motion.div
              key="spectrum-body"
              initial={{ height: 0, opacity: 0 }}
              animate={{ height: 'auto', opacity: 1 }}
              exit={{ height: 0, opacity: 0 }}
              transition={{ duration: 0.3, ease: 'easeInOut' }}
              className="overflow-hidden"
            >
              <div className="flex flex-col gap-1.5">
                {sorted.map(({ label, score }) => {
                  const pct = Math.round(score * 100)

                  return (
                    <div
                      key={label}
                      className="flex items-center gap-3 py-1"
                    >
                      <span className="w-5 text-center shrink-0 text-xs">
                        {EMOJI_MAP[label] ?? '❓'}
                      </span>

                      <span className="w-24 text-xs text-ink-700 shrink-0">
                        {capitalize(label)}
                      </span>

                      <div className="flex-1 h-1.5 rounded-full bg-cream-200 overflow-hidden">
                        <div
                          className={cn(
                            'h-full rounded-full transition-all duration-500',
                            'bg-coral-400',
                          )}
                          style={{ width: `${pct}%` }}
                        />
                      </div>

                      <span className="w-9 text-right text-xs tabular-nums text-ink-700/60 shrink-0">
                        {pct}%
                      </span>
                    </div>
                  )
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  )
}
