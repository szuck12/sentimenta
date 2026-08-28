// src/components/InputCard.tsx
// The primary input interface: textarea, character counter, example
// chips, clear/reset, validation messages, and the Analyze button.

import { useCallback, useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { X, Sparkles, RotateCcw } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { Card } from '@/components/ui/Card'
import type { AnalysisStatus } from '@/hooks/useAnalysis'

const MAX_CHARS = 2000

const schema = z.object({
  text: z
    .string()
    .min(1, 'Please enter some text to analyse.')
    .max(MAX_CHARS, `Text must be ${MAX_CHARS} characters or fewer.`),
})

type FormValues = z.infer<typeof schema>

const EXAMPLES = [
  { text: "I finally got the job I've been hoping for!", label: 'Excitement' },
  { text: "I'm worried about what tomorrow will bring.", label: 'Worry' },
  { text: "I can't believe they did that.", label: 'Surprise' },
  { text: "Thank you so much for helping me.", label: 'Gratitude' },
  { text: "I don't really know how I feel about this.", label: 'Confusion' },
  { text: "The weather is 72 degrees today.", label: 'Neutral' },
] as const

interface Props {
  status: AnalysisStatus
  onSubmit: (text: string) => void
  onReset: () => void
}

export function InputCard({ status, onSubmit, onReset }: Props) {
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { text: '' },
  })

  const text = watch('text')
  const loading = status === 'loading'
  const hasResult = status === 'success' || status === 'error'

  const handleExample = useCallback(
    (text: string) => {
      setValue('text', text, { shouldValidate: true })
    },
    [setValue],
  )

  const handleClear = useCallback(() => {
    setValue('text', '', { shouldValidate: false })
    onReset()
  }, [setValue, onReset])

  const charPct = Math.min((text.length / MAX_CHARS) * 100, 100)
  const nearLimit = text.length > MAX_CHARS * 0.9
  const overLimit = text.length > MAX_CHARS

  return (
    <Card id="analyze" className="max-w-2xl mx-auto">
      <form noValidate onSubmit={handleSubmit((d) => onSubmit(d.text))}>
        <label
          htmlFor="analysis-input"
          className="block text-sm font-medium text-ink-700/70 mb-2"
        >
          Enter your text
        </label>

        <div className="relative">
          <textarea
            id="analysis-input"
            rows={6}
            placeholder="Write something and we'll read between the lines..."
            className={[
              'w-full resize-none rounded-xl border border-cream-300 bg-cream-50',
              'p-4 pr-10 text-base text-ink-800 placeholder:text-ink-700/30',
              'focus:outline-none focus:ring-2 focus:ring-coral-400 focus:border-transparent',
              'transition-shadow',
              errors.text ? 'border-red-300 focus:ring-red-300' : '',
            ].join(' ')}
            {...register('text')}
            disabled={loading}
            maxLength={MAX_CHARS + 100}
          />

          {text.length > 0 && !loading && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute top-3 right-3 p-1.5 rounded-full text-ink-700/40 hover:text-ink-700 hover:bg-cream-200 transition-colors"
              aria-label="Clear text"
            >
              <X size={16} />
            </button>
          )}
        </div>

        {/* Char counter + validation */}
        <div className="flex items-center justify-between mt-2 px-1">
          <div>
            {errors.text && (
              <p className="text-xs text-red-500">{errors.text.message}</p>
            )}
          </div>
          <p
            className={[
              'text-xs tabular-nums',
              overLimit ? 'text-red-500 font-medium' : nearLimit ? 'text-amber-600' : 'text-ink-700/40',
            ].join(' ')}
          >
            {text.length.toLocaleString()} / {MAX_CHARS.toLocaleString()} characters
          </p>
        </div>

        {/* Examples */}
        <div className="mt-4 flex flex-wrap gap-2">
          {EXAMPLES.map(({ text: ex, label }) => (
            <button
              key={label}
              type="button"
              onClick={() => handleExample(ex)}
              disabled={loading}
              className={[
                'px-3 py-1.5 rounded-full text-xs font-medium',
                'border border-cream-300 bg-cream-100 text-ink-700/70',
                'hover:bg-cream-200 hover:text-ink-700 transition-colors',
                'disabled:opacity-40',
              ].join(' ')}
            >
              {label}
            </button>
          ))}
        </div>

        {/* Action row */}
        <div className="mt-6 flex items-center gap-3">
          <Button
            type="submit"
            disabled={loading || text.trim().length === 0 || overLimit}
          >
            {loading ? (
              <>
                <span className="animate-spin inline-block h-4 w-4 border-2 border-white/30 border-t-white rounded-full" />
                Analysing...
              </>
            ) : (
              <>
                <Sparkles size={16} />
                Analyse Emotion
              </>
            )}
          </Button>

          {hasResult && (
            <Button
              type="button"
              variant="ghost"
              onClick={handleClear}
            >
              <RotateCcw size={14} />
              Start over
            </Button>
          )}
        </div>
      </form>
    </Card>
  )
}
