// src/components/ui/Button.tsx
// CVA-based button component following shadcn/ui conventions.

import { cva, type VariantProps } from 'class-variance-authority'
import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { cn } from '@/lib/utils'

const variants = cva(
  'inline-flex items-center justify-center gap-2 rounded-full '
  + 'px-6 py-3 text-sm font-semibold transition-colors '
  + 'disabled:pointer-events-none disabled:opacity-40 '
  + 'focus-visible:outline-none focus-visible:ring-2 '
  + 'focus-visible:ring-coral-400 focus-visible:ring-offset-2 '
  + 'focus-visible:ring-offset-cream-50',
  {
    variants: {
      variant: {
        primary:
          'bg-coral-500 text-white hover:bg-coral-600 '
          + 'active:bg-coral-600 shadow-sm',
        secondary:
          'bg-cream-200 text-ink-700 hover:bg-cream-300 '
          + 'active:bg-cream-300',
        ghost:
          'bg-transparent text-ink-700 hover:bg-cream-200',
      },
      size: {
        sm: 'h-9 px-4 text-xs',
        md: 'h-11 px-5 text-sm',
        lg: 'h-12 px-7 text-base',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  },
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof variants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button
      ref={ref}
      className={cn(variants({ variant, size, className }))}
      {...props}
    />
  ),
)
Button.displayName = 'Button'
