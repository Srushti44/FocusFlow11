/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./extension/**/*.{html,js,ts}"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        neo: {
          bg: '#F4F0E8',         // Warm off-white
          ink: '#151515',        // Ink black
          blue: '#2455FF',       // Electric blue
          lime: '#D7FF38',       // Acid lime
          coral: '#FF5E5B',      // Alert / Attention
          amber: '#FFA400',      // Warning / Review
          card: '#FFFFFF',
          muted: '#E6E1D5',
          darkBg: '#121212',
          darkCard: '#1E1E1E',
          darkBorder: '#333333',
        }
      },
      boxShadow: {
        'brutal-sm': '2px 2px 0px #151515',
        'brutal': '4px 4px 0px #151515',
        'brutal-lg': '6px 6px 0px #151515',
        'brutal-xl': '8px 8px 0px #151515',
        'brutal-blue': '4px 4px 0px #2455FF',
        'brutal-lime': '4px 4px 0px #D7FF38',
        'brutal-dark': '4px 4px 0px #F4F0E8',
      },
      fontFamily: {
        sans: ['Space Grotesk', 'Inter', 'system-ui', 'sans-serif'],
        display: ['Space Grotesk', 'Impact', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
        dyslexic: ['OpenDyslexic', 'Comic Sans MS', 'sans-serif'],
        lexend: ['Lexend', 'sans-serif'],
        atkinson: ['Atkinson Hyperlegible', 'sans-serif'],
        serif: ['Georgia', 'Charter', 'serif']
      },
      borderWidth: {
        '3': '3px',
      }
    },
  },
  plugins: [],
}
