# UI Design Guidelines

Sentimenta's frontend follows a warm, approachable aesthetic built with
Tailwind CSS 3 and custom design tokens. This document serves as the
reference for all UI components, patterns, and conventions.

---

## 1. Color Palette

### Backgrounds

The application uses a warm cream gradient as its base:

| Token | Hex | Usage |
|-------|-----|-------|
| `cream-50` | `#FFFDF7` | Page background, header backdrop |
| `cream-100` | `#FDF6EC` | Card hover states, input backgrounds |
| `cream-200` | `#F5E6D0` | Borders, chart backgrounds, subtle fills |
| `cream-300` | `#E8D5B8` | Below-threshold bar fills, secondary borders |

### Accent

| Token | Hex | Usage |
|-------|-----|-------|
| `coral-400` | `#F97D4D` | Above-threshold bar fills, focus rings, primary actions |
| `coral-500` | `#E86B35` | Primary button background, ring stroke in primary emotion card |
| `coral-600` | `#D15A28` | Primary button hover/active |

### Emotion Group Colors

| Group | Token | Hex | Badge variant |
|-------|-------|-----|---------------|
| Positive | `orange-*` | `#F97D4D` range | `positive` |
| Negative | `rose-*` | `#F47B82` range | `negative` |
| Cognitive | `violet-*` | `#A78BFA` range | `cognitive` |
| Neutral | `slate-*` | `#C5B9A8` range | `neutral` |

These colors are defined in `lib/types.ts` as `EMOTION_COLORS`:

```typescript
export const EMOTION_COLORS: Record<string, string> = {
  positive: '#F97D4D',
  negative: '#F47B82',
  cognitive: '#A78BFA',
  neutral: '#C5B9A8',
}
```

### Text

| Token | Hex | Usage |
|-------|-----|-------|
| `ink-800` | `#3D3229` | Headings, primary text, labels |
| `ink-700` | `#5A4D40` | Body text (often at reduced opacity) |

Text opacity is used extensively:
- `text-ink-700/70` — secondary text, nav links
- `text-ink-700/50` — placeholder text, small notes
- `text-ink-700/40` — footer, very subtle text
- `text-ink-700/30` — textarea placeholder

---

## 2. Typography

Sentimenta uses the system font stack:

```css
font-family: 'Segoe UI Variable', 'system-ui', -apple-system, sans-serif;
```

### Font Weights and Sizes

| Class | Usage |
|-------|-------|
| `font-display font-bold text-4xl sm:text-5xl` | Hero heading on Home page |
| `font-display font-bold text-3xl sm:text-4xl` | Page titles (How It Works, Emotions) |
| `font-display font-semibold text-lg` | Section headings within cards |
| `font-display font-semibold text-ink-800` | Card titles ("Emotion Mix", "Full Spectrum") |
| `font-medium text-sm` | Navigation links, button labels, form labels |
| `text-sm text-ink-700/60` | Body text in How It Works steps |
| `text-xs text-ink-700/50` | Disclaimer notes, method attribution, footer |

The `font-display` class applies the display font variant (slightly
tighter tracking, bolder weight) for headings and brand text.

---

## 3. Spacing and Layout

### Page Structure

- **Max width**: `max-w-6xl` (1152px) for the main content area.
- **Max width (narrow)**: `max-w-2xl` (672px) for the input card and
  results section.
- **Max width (medium)**: `max-w-4xl` (896px) for How It Works and
  Emotions pages.
- **Horizontal padding**: `px-6` (24px) on all page containers.
- **Vertical padding**: `py-12` (48px) on page containers.

### Vertical Rhythm

- Sections are separated by `space-y-6` (24px) or `mb-10`/`mb-12`
  (40px/48px).
- Card internal padding: `p-6` (24px).
- Card group spacing: `space-y-6` (24px) between cards.

### Responsive Breakpoints

- **Mobile first**: Base styles target mobile.
- **`sm` (640px)**: Larger heading sizes, grid columns on Emotions page.
- **`md` (768px)**: Desktop nav replaces hamburger menu.
- **`lg` (1024px)**: 3-column grid on Emotions page.

---

## 4. Card Style

All cards use the same base style (defined in `components/ui/Card.tsx`):

```
rounded-2xl bg-white/80 backdrop-blur-sm border border-cream-200 shadow-sm p-6
```

- **Rounded corners**: `rounded-2xl` (16px) — generous, friendly feel.
- **Background**: `bg-white/80` with `backdrop-blur-sm` — subtle glass
  effect over the cream page background.
- **Border**: `1px solid cream-200` — barely visible, defines edges.
- **Shadow**: `shadow-sm` — soft depth without heaviness.

### Card Variants

- **Default**: Standard white/translucent card.
- **Input card**: Same base, wrapped in a `max-w-2xl mx-auto` container
  and given the `id="analyze"` for hash-link scrolling.
- **Disclaimer card**: `bg-cream-100/60 border-cream-200/50` — slightly
  more transparent, sits at the bottom of results.

---

## 5. Button Variants

Defined via CVA in `components/ui/Button.tsx`:

| Variant | Classes | Usage |
|---------|---------|-------|
| `primary` | `bg-coral-500 text-white hover:bg-coral-600 shadow-sm` | Main "Analyze Emotion" action |
| `secondary` | `bg-cream-200 text-ink-700 hover:bg-cream-300` | Alternative actions |
| `ghost` | `bg-transparent text-ink-700 hover:bg-cream-200` | "Start over" button |

Sizes: `sm` (h-9), `md` (h-11), `lg` (h-12). Default is `md`.

All buttons:
- Use `rounded-full` — fully rounded pill shape.
- Include `focus-visible:ring-2 focus-visible:ring-coral-400` for
  keyboard accessibility.
- Include `disabled:pointer-events-none disabled:opacity-40` for
  disabled states.
- Contain a `gap-2` between icon and label.

---

## 6. Badge Variants

Defined via CVA in `components/ui/Badge.tsx`:

| Variant | Background | Text | Border | Usage |
|---------|-----------|------|--------|-------|
| `positive` | `bg-orange-50` | `text-orange-700` | `border-orange-200` | Positive emotion labels, journey badges |
| `negative` | `bg-rose-50` | `text-rose-700` | `border-rose-200` | Negative emotion labels, journey badges |
| `cognitive` | `bg-violet-50` | `text-violet-700` | `border-violet-200` | Cognitive emotion labels, journey badges |
| `neutral` | `bg-slate-50` | `text-slate-600` | `border-slate-200` | Neutral emotion labels |
| `default` | `bg-cream-100` | `text-ink-700` | `border-cream-200` | General use |

Badge shape: `rounded-full px-3 py-1 text-xs font-medium`.

---

## 7. Animations

### framer-motion

Sentimenta uses framer-motion 11 for all animations:

**Results container** (`ResultsSection.tsx`):
```typescript
const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.1 } },
}
const item = {
  hidden: { opacity: 0, y: 12 },
  show: { opacity: 1, y: 0 },
}
```

Cards stagger in with 100ms delay between each. Individual cards
animate from `opacity: 0, y: 12` to `opacity: 1, y: 0`.

**Individual cards** (PrimaryEmotionCard, EmotionMixCard, etc.):
```typescript
initial={{ opacity: 0, y: 12 }}
animate={{ opacity: 1, y: 0 }}
transition={{ duration: 0.4 }}
```

**SpectrumCard collapse/expand**:
```typescript
initial={{ height: 0, opacity: 0 }}
animate={{ height: 'auto', opacity: 1 }}
exit={{ height: 0, opacity: 0 }}
transition={{ duration: 0.3, ease: 'easeInOut' }}
```

**LoadingState messages**: `AnimatePresence` with `mode="wait"` for
crossfade between cycling messages. Text animates from `y: 8` to `y: 0`.

### CSS Animations

- **Loading dots**: `animate-pulse-soft` with staggered `animationDelay`
  (0s, 0.2s, 0.4s).
- **Spinner on Analyze button**: `animate-spin` on a CSS border spinner.
- **Primary emotion ring**: `transition: stroke-dashoffset 0.8s ease-out`
  for the SVG ring animation.
- **Bar widths**: `transition-all duration-500` for smooth bar growth.
- **Chevron rotation**: `transition-transform duration-300` with
  `rotate-180` when expanded.

---

## 8. Loading State

`LoadingState.tsx` displays:

1. **Three animated dots**: Coral-colored circles with `animate-pulse-soft`
   and staggered delays.
2. **Cycling messages**: Four messages rotate every 2.2 seconds with a
   fade-in/fade-out animation:
   - "Reading between the lines..."
   - "Finding emotional signals..."
   - "Building your emotional profile..."
   - "Interpreting emotional language..."

The loading state renders between the InputCard and the results section
when `status === 'loading'`.

---

## 9. Responsive Design

### Mobile (default)

- Single column layout.
- Hamburger menu in the header (`md:hidden`).
- Input card at `max-w-2xl mx-auto`.
- Results stack vertically.

### Tablet (`md` / 768px)

- Desktop nav replaces hamburger (`hidden md:flex`).
- Emotions page uses 2-column grid.

### Desktop (`lg` / 1024px)

- Emotions page uses 3-column grid (`lg:grid-cols-3`).
- Full nav visible.

### Header Behavior

The header is `sticky top-0 z-50` with `bg-cream-50/70 backdrop-blur-md`.
It remains visible during scroll with a subtle blur backdrop. The mobile
menu is an absolutely-positioned dropdown that appears below the header.

---

## 10. Bar Charts

### EmotionMixCard

Horizontal bars for detected emotions (above threshold):

- **Bar height**: `h-2` (8px).
- **Background**: `bg-cream-200` (track).
- **Fill**: `bg-gradient-to-r from-coral-400 to-coral-500` (gradient).
- **Width**: Inline `style={{ width: ${pct}% }}` based on score.
- **Labels**: Emoji (w-6), capitalized name (w-28), percentage (w-10).

The primary emotion row gets `bg-cream-100` background highlight.

### SpectrumCard

Horizontal bars for all 28 emotions:

- **Bar height**: `h-1.5` (6px) — thinner than EmotionMixCard.
- **Above threshold**: `bg-coral-400` (solid coral).
- **Below threshold**: `bg-cream-300` (muted cream).
- **Labels**: Emoji (w-5), capitalized name (w-24), percentage (w-9).
- **Collapse/expand**: Controlled by a toggle button with ChevronDown
  icon that rotates 180° when expanded.

---

## 11. Accessibility

### Focus Management

- All interactive elements have `focus-visible:ring-2 focus-visible:ring-coral-400`.
- The ring offset uses `focus-visible:ring-offset-2 focus-visible:ring-offset-cream-50`.
- Textarea uses `focus:outline-none focus:ring-2 focus:ring-coral-400 focus:border-transparent`.

### Semantic HTML

- `<header>`, `<main>`, `<footer>`, `<nav>`, `<section>` elements.
- `<label htmlFor="analysis-input">` for the textarea.
- Heading hierarchy: `<h1>` for page titles, `<h2>` for sections,
  `<h3>` for card titles.

### ARIA Attributes

- `aria-label="Toggle navigation menu"` on hamburger button.
- `aria-label="Clear text"` on clear button.
- `aria-hidden="true"` on decorative emoji in PrimaryEmotionCard.
- `role="button"` is implicit on `<button>` elements.

### Disabled States

- Textarea and buttons disabled during loading (`disabled={loading}`).
- Example chips disabled during loading.
- Submit button disabled when text is empty or over limit.
- Disabled styling: `disabled:pointer-events-none disabled:opacity-40`.

### Color Contrast

- `text-ink-800` (#3D3229) on cream backgrounds provides strong
  contrast.
- Reduced-opacity text (`/50`, `/40`) is used only for supplementary
  information, never for critical content.

---

## 12. The Disclaimer Note Pattern

Every results section ends with a disclaimer card:

```tsx
<Card className="bg-cream-100/60 border-cream-200/50">
  <div className="flex items-start gap-2">
    <AlertCircle size={16} className="text-ink-700/40 mt-0.5 shrink-0" />
    <p className="text-xs text-ink-700/50 leading-relaxed">
      Sentimenta provides an AI-generated interpretation
      of emotional language. Results are estimates and
      may not reflect the writer's actual feelings.
    </p>
  </div>
</Card>
```

This pattern:
- Uses a slightly transparent card variant.
- Includes an `AlertCircle` icon from lucide-react.
- Small text (`text-xs`) at reduced opacity (`/50`).
- Wraps with `leading-relaxed` for comfortable reading.
- Sits at the bottom of the results stack as the last animated item.

---

## 13. Component File Naming

| Convention | Example |
|------------|---------|
| Page components | `pages/Home.tsx`, `pages/HowItWorks.tsx`, `pages/Emotions.tsx` |
| Feature components | `components/InputCard.tsx`, `components/LoadingState.tsx` |
| Result sub-components | `components/results/PrimaryEmotionCard.tsx` |
| UI primitives | `components/ui/Button.tsx`, `components/ui/Badge.tsx`, `components/ui/Card.tsx` |
| Hooks | `hooks/useAnalysis.ts` |
| Utilities | `lib/api.ts`, `lib/types.ts`, `lib/utils.ts` |

Every component file starts with a comment header:

```typescript
// src/components/MyComponent.tsx
// Brief description of the component's purpose.
```
