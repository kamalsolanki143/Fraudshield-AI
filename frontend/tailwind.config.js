/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#EEF2FF',
          100: '#E0E7FF',
          500: '#6366F1',
          600: '#4F46E5', // NovaShop Indigo Primary
          700: '#4338CA',
          900: '#312E81',
        },
        violet: {
          500: '#8B5CF6',
          600: '#7C3AED',
        },
        dark: {
          bg: '#F3F4F9',
          card: '#FFFFFF',
          border: '#F1F5F9',
          glow: 'rgba(79, 70, 229, 0.15)',
        },
        danger: '#F43F5E',
        success: '#10B981',
        warning: '#F59E0B',
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        heading: ['Plus Jakarta Sans', 'sans-serif'],
        display: ['Plus Jakarta Sans', 'sans-serif'],
      },
      boxShadow: {
        'soft-sm': '0 2px 8px 0 rgba(0, 0, 0, 0.03)',
        'soft-md': '0 4px 20px 0 rgba(0, 0, 0, 0.04)',
        'soft-lg': '0 12px 30px 0 rgba(79, 70, 229, 0.15)',
        'glow-sm': '0 0 15px rgba(79, 70, 229, 0.25)',
      },
      backgroundImage: {
        'novashop-hero': 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 50%, #EC4899 100%)',
        'novashop-promo': 'linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%)',
      },
    },
  },
  plugins: [],
}
