/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Palette NerdWallet EXACTE (extraite du site)
        'nw-green': {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        'nw-navy': {
          DEFAULT: '#003366',
          light: '#0055a4',
          dark: '#002244',
        },
        'nw-gray': {
          50: '#f8f9fa',
          100: '#f1f3f5',
          200: '#e9ecef',
          300: '#dee2e6',
          400: '#ced4da',
          500: '#adb5bd',
          600: '#6c757d',
          700: '#495057',
          800: '#343a40',
          900: '#212529',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'nw-card': '0 2px 8px rgba(0, 51, 102, 0.08)',
        'nw-card-hover': '0 8px 24px rgba(0, 51, 102, 0.12)',
        'nw-button': '0 4px 12px rgba(0, 179, 89, 0.25)',
      },
    },
  },
  plugins: [],
}
