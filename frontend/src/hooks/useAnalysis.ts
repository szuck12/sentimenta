// src/hooks/useAnalysis.ts
// React hook managing the full analysis lifecycle: idle → loading →
// success or error, with built-in abort on reset.

import { useCallback, useRef, useState } from 'react'
import { analyze } from '@/lib/api'
import type { AnalyzeResponse } from '@/lib/types'

export type AnalysisStatus = 'idle' | 'loading' | 'success' | 'error'

export function useAnalysis() {
  const [status, setStatus] = useState<AnalysisStatus>('idle')
  const [result, setResult] = useState<AnalyzeResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const abortRef = useRef<AbortController | null>(null)

  const run = useCallback(async (text: string) => {
    abortRef.current?.abort()
    const controller = new AbortController()
    abortRef.current = controller

    setStatus('loading')
    setError(null)
    setResult(null)

    try {
      const data = await analyze(text)
      if (!controller.signal.aborted) {
        setResult(data)
        setStatus('success')
      }
    } catch (err: unknown) {
      if (!controller.signal.aborted) {
        setError(
          err instanceof Error
            ? err.message
            : 'Something went wrong while analyzing your text.',
        )
        setStatus('error')
      }
    }
  }, [])

  const reset = useCallback(() => {
    abortRef.current?.abort()
    setStatus('idle')
    setResult(null)
    setError(null)
  }, [])

  return { status, result, error, run, reset }
}
