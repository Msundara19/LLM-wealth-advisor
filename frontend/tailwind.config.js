/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        'ww-navy': '#1a365d',
        'ww-navy-dark': '#0f2744',
        'ww-gold': '#d4a437',
        'ww-gold-light': '#e8c468',
        'ww-orange': '#e67e22',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
