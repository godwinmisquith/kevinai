/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'kevin-bg': '#1a1a2e',
        'kevin-surface': '#16213e',
        'kevin-primary': '#0f3460',
        'kevin-accent': '#e94560',
        'kevin-text': '#eaeaea',
        'kevin-muted': '#8b8b8b',
      },
    },
  },
  plugins: [],
}
