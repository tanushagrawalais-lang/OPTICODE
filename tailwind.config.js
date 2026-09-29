/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        /* Komorebi Glass — Light Mode */
        primary:           '#984726',
        'primary-container': '#f08c65',
        'on-primary':      '#ffffff',
        secondary:         '#6f5a4e',
        'secondary-container': '#f7dacb',
        surface:           '#fcf9f6',
        'on-surface':      '#1b1c1a',
        'on-surface-variant': '#55433c',
        outline:           '#88726b',
        'outline-variant': '#dbc1b8',
        background:        '#fcf9f6',

        /* Luminescent Peach Glass — Dark Mode extras */
        'surface-dark':    '#0f131c',
        'surface-glass-dark': 'rgba(10, 14, 23, 0.65)',

        /* Shared Accent */
        peach: {
          300: '#ffc2a6',
          400: '#f08c65',
          500: '#e07248',
          600: '#c7582e',
        },
      },
      fontFamily: {
        sans:    ['Plus Jakarta Sans', 'sans-serif'],
        mono:    ['JetBrains Mono', 'monospace'],
        display: ["'Century Gothic'", 'CenturyGothic', 'AppleGothic', 'sans-serif'],
      },
      backdropBlur: {
        xs: '4px',
        '2xl': '24px',
        '3xl': '40px',
      },
      boxShadow: {
        glass:     '0 8px 32px -4px rgba(220,160,130,0.12), 0 2px 8px -2px rgba(45,38,34,0.03)',
        'glass-hover': '0 16px 48px rgba(0,0,0,0.07)',
        'glass-dark':  '0 20px 50px rgba(0,0,0,0.5)',
        card:          '0 1px 3px rgba(0,0,0,0.04)',
      },
    },
  },
  plugins: [],
};
