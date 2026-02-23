/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Playfair Display', 'serif'],
        body: ['Manrope', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        background: '#050505',
        foreground: '#FAFAFA',
        card: {
          DEFAULT: '#0A0A0A',
          foreground: '#FAFAFA',
        },
        primary: {
          DEFAULT: '#D9381E',
          foreground: '#FFFFFF',
        },
        secondary: {
          DEFAULT: '#C5A059',
          foreground: '#000000',
        },
        accent: {
          DEFAULT: '#06B6D4',
          foreground: '#000000',
        },
        muted: {
          DEFAULT: '#1A1A1A',
          foreground: '#A1A1AA',
        },
        border: '#27272A',
        input: '#27272A',
        ring: '#D9381E',
      },
      borderRadius: {
        lg: '0.5rem',
        md: 'calc(0.5rem - 2px)',
        sm: 'calc(0.5rem - 4px)',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};