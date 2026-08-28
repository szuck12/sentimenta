// src/components/LoadingState.tsx
// Animated loading messages displayed during inference.

import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

const MESSAGES = [
  'Reading between the lines...',
  'Finding emotional signals...',
  'Building your emotional profile...',
  'Interpreting emotional language...',
] as const

export function LoadingState() {
  const [idx, setIdx] = useState(0)

  useEffect(() => {
    const interval = setInterval(
      () => setIdx((i) => (i + 1) % MESSAGES.length),
      2200,
    )
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="max-w-2xl mx-auto py-12 flex flex-col items-center gap-4">
      <div className="flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-2 h-2 rounded-full bg-coral-400 animate-pulse-soft"
            style={{ animationDelay: `${i * 0.2}s` }}
          />
        ))}
      </div>
      <AnimatePresence mode="wait">
        <motion.p
          key={idx}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.3 }}
          className="text-sm text-ink-700/50 font-medium"
        >
          {MESSAGES[idx]}
        </motion.p>
      </AnimatePresence>
    </div>
  )
}
