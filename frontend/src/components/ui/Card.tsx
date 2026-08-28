// src/components/ui/Card.tsx
// Simple rounded card with subtle shadow, used by all result sections.

import { forwardRef, type HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

export const Card = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(
        'rounded-2xl bg-white/80 backdrop-blur-sm border border-cream-200 '
        + 'shadow-sm p-6',
        className,
      )}
      {...props}
    />
  ),
)
Card.displayName = 'Card'
