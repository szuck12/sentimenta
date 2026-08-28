// src/components/Footer.tsx
// Simple footer with privacy note and external links.

import { Heart } from 'lucide-react'

export function Footer() {
  return (
    <footer className="border-t border-cream-200/50 mt-auto">
      <div className="max-w-6xl mx-auto px-6 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p className="text-xs text-ink-700/40">
          Your text is analyzed and returned — nothing is stored.
        </p>
        <p className="text-xs text-ink-700/40 flex items-center gap-1">
          Built with <Heart size={12} className="text-rose-300" /> using GoEmotions + RoBERTa
        </p>
      </div>
    </footer>
  )
}
