import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import { Card } from '@/components/ui/Card'
import { PrimaryEmotionCard } from './PrimaryEmotionCard'
import { EmotionMixCard } from './EmotionMixCard'
import { ExplanationCard } from './ExplanationCard'
import { SpectrumCard } from './SpectrumCard'
import { JourneyCard } from './JourneyCard'
import type { AnalyzeResponse } from '@/lib/types'

interface ResultsSectionProps {
  result: AnalyzeResponse
}

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 },
  },
}

const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
}

export function ResultsSection({ result }: ResultsSectionProps) {
  const {
    primary_emotion,
    all_emotions,
    intensity,
    explanation,
    sentences,
  } = result

  const topEmotions = all_emotions.slice(0, 5)

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="space-y-6 max-w-2xl mx-auto"
    >
      <motion.div variants={item}>
        <PrimaryEmotionCard
          label={primary_emotion.label}
          score={primary_emotion.score}
          summary={explanation.summary}
          intensity={intensity}
        />
      </motion.div>

      <motion.div variants={item}>
        <EmotionMixCard
          emotions={topEmotions}
          primaryLabel={primary_emotion.label}
        />
      </motion.div>

      <motion.div variants={item}>
        <ExplanationCard
          summary={explanation.summary}
          signals={explanation.signals}
          method={explanation.method}
        />
      </motion.div>

      {sentences.length > 1 && (
        <motion.div variants={item}>
          <JourneyCard sentences={sentences} />
        </motion.div>
      )}

      <motion.div variants={item}>
        <SpectrumCard emotions={all_emotions} />
      </motion.div>

      <motion.div variants={item}>
        <Card className="bg-cream-100/60 border-cream-200/50">
          <div className="flex items-start gap-2">
            <AlertCircle
              size={16}
              className="text-ink-700/40 mt-0.5 shrink-0"
            />
            <p className="text-xs text-ink-700/50 leading-relaxed">
              Sentimenta provides an AI-generated interpretation
              of emotional language. Results are estimates and
              may not reflect the writer's actual feelings.
            </p>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  )
}
