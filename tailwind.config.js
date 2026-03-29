/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'pulse': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      colors: {
        'alvo-blue': '#3B82F6',
        'alvo-green': '#10B981',
        'alvo-purple': '#8B5CF6',
        'alvo-yellow': '#F59E0B',
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}