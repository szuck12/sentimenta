// src/components/Header.tsx
// Sticky top navigation with blur backdrop, desktop nav links,
// and a mobile-friendly hamburger menu.

import { useState, type MouseEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Menu, X } from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV_LINKS = [
  { to: '/#analyze', label: 'Analyze' },
  { to: '/how-it-works', label: 'How It Works' },
  { to: '/emotions', label: 'Emotions' },
] as const

export function Header() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()

  const isActive = (href: string) => {
    if (href.startsWith('/#')) {
      return location.pathname === '/' && location.hash === href.slice(1)
    }
    return location.pathname === href
  }

  const handleClick = (e: MouseEvent<HTMLAnchorElement>, href: string) => {
    if (href.startsWith('/#') && location.pathname === '/') {
      e.preventDefault()
      const el = document.getElementById(href.slice(2))
      el?.scrollIntoView({ behavior: 'smooth' })
      setMobileOpen(false)
    } else {
      setMobileOpen(false)
    }
  }

  return (
    <header className="sticky top-0 z-50 bg-cream-50/70 backdrop-blur-md border-b border-cream-200/50">
      <nav className="max-w-6xl mx-auto flex items-center justify-between h-16 px-6">
        <Link
          to="/"
          className="text-xl font-display font-bold text-ink-800 tracking-tight"
        >
          ✨ Sentimenta
        </Link>

        {/* Desktop nav */}
        <ul className="hidden md:flex items-center gap-8">
          {NAV_LINKS.map(({ to, label }) => (
            <li key={to}>
              <Link
                to={to}
                onClick={(e) => handleClick(e, to)}
                className={cn(
                  'text-sm font-medium transition-colors',
                  isActive(to)
                    ? 'text-coral-600'
                    : 'text-ink-700/70 hover:text-ink-700',
                )}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>

        {/* Mobile toggle */}
        <button
          className="md:hidden p-2 text-ink-700"
          onClick={() => setMobileOpen(!mobileOpen)}
          aria-label="Toggle navigation menu"
        >
          {mobileOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </nav>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden bg-white/95 backdrop-blur-sm border-b border-cream-200">
          <ul className="flex flex-col px-6 py-4 gap-3">
            {NAV_LINKS.map(({ to, label }) => (
              <li key={to}>
                <Link
                  to={to}
                  onClick={(e) => handleClick(e, to)}
                  className={cn(
                    'block py-2 text-sm font-medium',
                    isActive(to) ? 'text-coral-600' : 'text-ink-700',
                  )}
                >
                  {label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </header>
  )
}
