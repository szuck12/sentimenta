// frontend/tests/lib/utils.test.ts

import { describe, expect, it } from 'vitest'
import { cn } from '@/lib/utils'

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
