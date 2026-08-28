// src/pages/Home.tsx
// Main landing page: hero, input card, loading state, and results.

import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { InputCard } from '@/components/InputCard'
import { LoadingState } from '@/components/LoadingState'
import { ResultsSection } from '@/components/results/ResultsSection'
import { useAnalysis } from '@/hooks/useAnalysis'

export function Home() {
  const { status, result, error, run, reset } = useAnalysis()
  const location = useLocation()

  useEffect(() => {
    if (location.hash === '#analyze') {
      setTimeout(() => {
        document
          .getElementById('analyze')
          ?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    }
  }, [location])

  return (
    <main className="max-w-6xl mx-auto px-6 py-12">
      {/* Hero */}
      <section className="text-center mb-12">
        <h1 className="text-4xl sm:text-5xl font-display font-bold text-ink-800 tracking-tight mb-4">
          What are your words feeling?
        </h1>
        <p className="text-lg text-ink-700/60 max-w-xl mx-auto">
          Explore the emotions hiding inside your text.
        </p>
      </section>

      {/* Input */}
      <section className="mb-10">
        <InputCard status={status} onSubmit={run} onReset={reset} />
      </section>

      {/* Loading */}
      {status === 'loading' && <LoadingState />}

      {/* Error */}
      {status === 'error' && error && (
        <div className="max-w-2xl mx-auto mb-8 rounded-xl bg-red-50 border border-red-200 px-5 py-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Results */}
      {status === 'success' && result && (
        <section className="mb-16">
          <ResultsSection result={result} />
        </section>
      )}
    </main>
  )
}
