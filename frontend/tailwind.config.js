/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'var(--primary-50)',
          100: 'var(--primary-100)',
          200: 'var(--primary-200)',
          300: 'var(--primary-300)',
          400: 'var(--primary-400)',
          500: 'var(--primary-500)',
          600: 'var(--primary-600)',
          700: 'var(--primary-700)',
          800: 'var(--primary-800)',
          900: 'var(--primary-900)',
        },
        ink: 'var(--ink)',
        muted: 'var(--muted)',
        paper: 'var(--paper)',
        'paper-strong': 'var(--paper-strong)',
        dark: 'var(--dark)',
        pink: 'var(--pink)',
        peach: 'var(--peach)',
        mint: 'var(--mint)',
        blue: 'var(--blue)',
        lilac: 'var(--lilac)',
        yellow: 'var(--yellow)',
      },
      borderRadius: {
        'xl': 'var(--radius-sm)',
        '2xl': 'var(--radius)',
        '3xl': 'var(--radius-lg)',
      },
      boxShadow: {
        'glass': 'var(--shadow)',
        'glass-sm': 'var(--shadow-sm)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'rise': 'rise 0.25s ease',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        rise: {
          'from': { opacity: '0', transform: 'translateY(8px)' },
          'to': { opacity: '1', transform: 'none' },
        },
      },
    },
  },
  plugins: [],
}
