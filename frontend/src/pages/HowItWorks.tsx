// src/pages/HowItWorks.tsx
// Explanatory page covering the GoEmotions model, multi-label
// classification, explainability, and limitations.

import { Link } from 'react-router-dom'
import { Card } from '@/components/ui/Card'

const STEPS = [
  {
    num: '1',
    title: 'You enter text',
    body: 'Type or paste anything from a few words to several paragraphs into the analysis box.',
  },
  {
    num: '2',
    title: 'The model reads it',
    body: "Sentimenta uses RoBERTa, a transformer model trained specifically on GoEmotions — Google's dataset of 58,000 Reddit comments annotated across 27 emotion categories plus neutral.",
  },
  {
    num: '3',
    title: 'Multi-label scoring',
    body: 'Unlike a simple sentiment classifier, GoEmotions produces a probability for each of the 28 emotions independently. Multiple emotions can score highly at the same time — because real text often expresses several feelings at once.',
  },
  {
    num: '4',
    title: 'Attribution & explanation',
    body: 'When available, token-level attribution (Captum integrated gradients) identifies which words contributed most strongly to the primary emotion, giving you evidence for why Sentimenta read the text the way it did.',
  },
] as const

export function HowItWorks() {
  return (
    <main className="max-w-4xl mx-auto px-6 py-12">
      <section className="mb-12">
        <h1 className="text-3xl sm:text-4xl font-display font-bold text-ink-800 tracking-tight mb-4">
          How It Works
        </h1>
        <p className="text-ink-700/60 max-w-2xl leading-relaxed">
          Sentimenta is an explainable emotion-analysis application
          powered by Google's GoEmotions dataset and the RoBERTa
          transformer architecture.
        </p>
      </section>

      <div className="space-y-6 mb-12">
        {STEPS.map(({ num, title, body }) => (
          <Card key={num} className="flex gap-5 items-start">
            <span className="shrink-0 w-10 h-10 rounded-full bg-coral-500 text-white flex items-center justify-center font-display font-bold text-sm">
              {num}
            </span>
            <div>
              <h2 className="font-display font-semibold text-ink-800 mb-1">
                {title}
              </h2>
              <p className="text-sm text-ink-700/60 leading-relaxed">
                {body}
              </p>
            </div>
          </Card>
        ))}
      </div>

      <section className="mb-12">
        <h2 className="text-2xl font-display font-bold text-ink-800 mb-4">
          Important Limitations
        </h2>
        <Card className="bg-cream-100/60 border-cream-200/50 space-y-3">
          <p className="text-sm text-ink-700/70 leading-relaxed">
            The GoEmotions dataset is based on Reddit comments and
            carries the biases inherent in that source. Not all emotions
            translate equally across cultures, demographics, or contexts.
          </p>
          <p className="text-sm text-ink-700/70 leading-relaxed">
            The model reports an overall F1 around 0.45 under its
            published 0.5 threshold, with substantial variation across
            individual emotions. <strong className="text-ink-700">
            Confidence scores are not certainty scores.</strong>
          </p>
          <p className="text-sm text-ink-700/70 leading-relaxed">
            Intensity, emotional profile, and groupings are
            Sentimenta-derived presentation metrics, not outputs of
            the GoEmotions model.
          </p>
        </Card>
      </section>

      <section className="text-center">
        <Link
          to="/"
          className="text-coral-500 hover:text-coral-600 text-sm font-semibold"
        >
          Try it yourself →
        </Link>
      </section>
    </main>
  )
}
