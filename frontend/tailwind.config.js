/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neonPurple: '#B026FF',
        electricBlue: '#0FF0FC',
      },
      backgroundImage: {
        'deep-space': "url('https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?q=80&w=2070&auto=format&fit=crop')",
      }
    },
  },
  plugins: [],
}
