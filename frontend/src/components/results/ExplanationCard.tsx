import { motion } from 'framer-motion'
import { Info } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Card } from '@/components/ui/Card'

interface ExplanationCardProps {
  summary: string
  signals: Array<{ text: string; weight: number }>
  method: string
}

function methodNote(method: string): string {
  if (method === 'integrated_gradients') {
    return 'These phrases were identified via token attribution'
      + ' (Captum integrated gradients)'
  }
  return 'Showing probability-based evidence only'
}

export function ExplanationCard({
  summary,
  signals,
  method,
}: ExplanationCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card>
        <h3 className="font-display font-semibold text-ink-800 mb-3">
          Why Sentimenta thinks this
        </h3>

        {summary && (
          <p className="text-ink-700/80 leading-relaxed mb-4">
            {summary}
          </p>
        )}

        {signals.length > 0 ? (
          <div className="flex flex-wrap gap-2 mb-3">
            {signals.map((signal) => (
              <span
                key={signal.text}
                className={cn(
                  'inline-block rounded-full px-3 py-1',
                  'bg-peach-200 text-ink-800 text-sm',
                  'shadow-sm shadow-peach-300/40',
                )}
              >
                {signal.text}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-ink-700/50 italic">
            Token-level attribution was unavailable for this
            analysis.
          </p>
        )}

        {signals.length > 0 && (
          <div className="flex items-start gap-1.5 mt-2">
            <Info size={14} className="text-ink-700/40 mt-0.5 shrink-0" />
            <p className="text-xs text-ink-700/50 leading-relaxed">
              {methodNote(method)}
            </p>
          </div>
        )}
      </Card>
    </motion.div>
  )
}
