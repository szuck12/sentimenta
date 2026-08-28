// src/components/ui/Badge.tsx
// Small pill badge, used for emotion labels and group tags.

import { cva, type VariantProps } from 'class-variance-authority'
import { forwardRef, type HTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

const badgeVariants = cva(
  'inline-flex items-center gap-1 rounded-full '
  + 'px-3 py-1 text-xs font-medium transition-colors',
  {
    variants: {
      variant: {
        positive: 'bg-orange-50 text-orange-700 border border-orange-200',
        negative: 'bg-rose-50 text-rose-700 border border-rose-200',
        cognitive: 'bg-violet-50 text-violet-700 border border-violet-200',
        neutral: 'bg-slate-50 text-slate-600 border border-slate-200',
        default: 'bg-cream-100 text-ink-700 border border-cream-200',
      },
    },
    defaultVariants: { variant: 'default' },
  },
)

export interface BadgeProps
  extends HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export const Badge = forwardRef<HTMLSpanElement, BadgeProps>(
  ({ className, variant, ...props }, ref) => (
    <span
      ref={ref}
      className={cn(badgeVariants({ variant, className }))}
      {...props}
    />
  ),
)
Badge.displayName = 'Badge'
