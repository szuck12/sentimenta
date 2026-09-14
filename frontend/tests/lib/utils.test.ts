// frontend/tests/lib/utils.test.ts

import { describe, expect, it } from 'vitest'
import { cn, toWholePercentages } from '@/lib/utils'

describe('cn', () => {
  it('joins class names', () => {
    expect(cn('a', 'b')).toBe('a b')
  })

  it('ignores falsy values', () => {
    expect(cn('a', undefined, null, false, 'c')).toBe('a c')
  })

  it('lets later Tailwind classes win conflicts', () => {
    expect(cn('p-2', 'p-4')).toBe('p-4')
  })

  it('accepts conditional class objects', () => {
    expect(cn('base', { active: true, hidden: false })).toBe('base active')
  })
})

describe('toWholePercentages', () => {
  it('always sums to exactly 100', () => {
    const cases = [
      [0.85, 0.7],
      [0.85, 0.7, 0.4, 0.3, 0.05],
      [1, 1, 1],
      [0.33, 0.33, 0.33],
      [10, 20, 30, 40],
      [0.001, 0.001, 0.001],
      [7],
    ]
    for (const values of cases) {
      const percentages = toWholePercentages(values)
      expect(percentages).toHaveLength(values.length)
      expect(percentages.reduce((sum, value) => sum + value, 0)).toBe(100)
      expect(
        percentages.every((value) => Number.isInteger(value) && value >= 0),
      ).toBe(true)
    }
  })

  it('gives leftovers to the largest remainders', () => {
    expect(toWholePercentages([1, 1, 1])).toEqual([34, 33, 33])
  })

  it('handles an empty list', () => {
    expect(toWholePercentages([])).toEqual([])
  })

  it('handles all-zero input', () => {
    expect(toWholePercentages([0, 0, 0])).toEqual([0, 0, 0])
  })
})
