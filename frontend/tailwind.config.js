/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: {
          50:  '#FFFDF7',
          100: '#FDF8F0',
          200: '#FAF1E3',
          300: '#F5E6D0',
        },
        coral: {
          300: '#FDBA94',
          400: '#FB9A66',
          500: '#F97D4D',
          600: '#F0613C',
        },
        peach: {
          200: '#FED7B6',
          300: '#FEC396',
          400: '#FDAA73',
        },
        rose: {
          100: '#FDE2E4',
          200: '#FBC8CA',
          300: '#F8A0A4',
          400: '#F47B82',
        },
        lavender: {
          100: '#EDE9FE',
          200: '#DDD6FE',
          300: '#C4B5FD',
          400: '#A78BFA',
        },
        sand: {
          300: '#E0D6C8',
          400: '#C5B9A8',
          500: '#A89882',
        },
        ink: {
          700: '#3D3229',
          800: '#2C251D',
          900: '#1F1A14',
        },
      },
      fontFamily: {
        display: [
          '"Segoe UI Variable Display"',
          '"Segoe UI"',
          'system-ui',
          'sans-serif',
        ],
        sans: [
          '"Segoe UI Variable Text"',
          '"Segoe UI"',
          'system-ui',
          '-apple-system',
          'sans-serif',
        ],
        mono: [
          'ui-monospace',
          '"Cascadia Code"',
          'Consolas',
          'monospace',
        ],
      },
      keyframes: {
        'fade-in-up': {
          '0%': { opacity: '0', transform: 'translateY(12px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.4s ease-out forwards',
        'pulse-soft': 'pulse-soft 2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
