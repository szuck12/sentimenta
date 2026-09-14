// src/lib/utils.ts
// Shared class-name utility used by all UI components.

import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs))
}

/**
 * Convert raw scores into whole-number percentages that always sum to 100.
 *
 * Uses the largest-remainder (Hamilton) method: every value is scaled to
 * its exact share, floored, and the leftover points are handed to the
 * values with the largest fractional parts. This avoids the naive
 * rounding problem where the displayed percentages sum to 99 or 101.
 *
 * Returns an array of integers with the same length as `values`.
 */
export function toWholePercentages(values: number[]): number[] {
  if (values.length === 0) return []

  const total = values.reduce((sum, value) => sum + value, 0)
  if (total <= 0) return values.map(() => 0)

  const exact = values.map((value) => (value / total) * 100)
  const result = exact.map((value) => Math.floor(value))
  const used = result.reduce((sum, value) => sum + value, 0)

  const byRemainder = exact
    .map((value, index) => ({ index, remainder: value - Math.floor(value) }))
    .sort((a, b) => b.remainder - a.remainder)

  for (let i = 0; i < 100 - used; i += 1) {
    result[byRemainder[i].index] += 1
  }

  return result
}
