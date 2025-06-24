// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        'serif': ['"Special Elite"', 'monospace'],
        'mono': ['"Cutive Mono"', 'monospace'],
        'broadway': ['Broadway', 'sans-serif'],
        'brittania': ['"Britannic Bold"', 'sans-serif'],
        'monoton': ['Monoton', 'cursive'],
        'vt323': ['VT323', 'monospace'],
        'didot': ['Didot', 'serif'],
        'work-sans': ['"Work Sans"', 'sans-serif'],
        'handwriting': ['"Homemade Apple"', 'cursive'],
        'typewriter': ['"Special Elite"', 'monospace'],
        'serif-vintage': ['"Cormorant Garamond"', 'serif'],
        'fell': ['"IM Fell English SC"', 'serif'],
        'spectral': ['"Spectral SC"', 'sans-serif'],
        'cormorant': ['"Cormorant"', 'serif'],
        'cinzel': ['"Cinzel"', 'serif'],
        'eb-garamond': ['"EB Garamond"', 'serif'],
        'special-elite': ['"Special Elite"', 'cursive'],
      },
      colors: {
        'lumiere-yellow': '#fdeec5',
        'lumiere-red': '#c83226',
        'lumiere-green': '#1DB954',
        'lumiere-orange': '#FF7A5A',
        'lumiere-console-bg': '#1a1a1a',
        'lumiere-dark-bg': '#0d0d0d',
        'lumiere-loading-text': '#00ff41',
        'lumiere-blue': '#426DF5',
        'lumiere-terminal-bg': '#0a1e0a',
        'lumiere-rec-bg': '#fde8f0',
        'lumiere-detail-bg': '#4a2c40',
        // Wes Anderson Theme for Calibration Page
        'wa-bg': '#F3E9DD', // Muted cream background
        'wa-panel': '#DFD3C3', // Lighter panel color
        'wa-text': '#3A3F5E',  // Deep navy/charcoal text
        'wa-accent': '#E76F51', // A pop of muted orange/red
        'wa-knob-light': '#C0C0C0', // Silver/light gray
        'wa-knob-dark': '#808080', // Darker gray for shadow
        'wa-led-on': '#6D9F93', // Muted teal for "on"
        'wa-led-off': '#D9C6B5', // Off-white/panel color for "off"
        'wa-border': '#6DA5D9', 
        'retro-bg': '#F0EAD6',
        'retro-blue': '#2E3A8A',
        'retro-orange': '#F59E0B',
        'retro-gray': '#D1D5DB',
        'retro-dark-gray': '#4B5563',
        'retro-screen-blue': '#082140',
        'retro-cyan': '#22D3EE',
        'retro-yellow': '#FBBF24',
        'retro-red': '#EF4444',// Muted blue for the outer border
      },
      backgroundImage: {
        'grid-red': 'radial-gradient(var(--tw-gradient-stops))',
        'grid-green': 'linear-gradient(rgba(0,0,0,0.5),rgba(0,0,0,0.5)), radial-gradient(var(--tw-gradient-stops))',
        'noisy-net': "url('https://www.transparenttextures.com/patterns/noisy-net.png')",
        'subtle-zebra': "url('https://www.transparenttextures.com/patterns/subtle-zebra-3d.png')",
      },
      gradientColorStops: theme => ({
        ...theme('colors'),
        'grid-red': '#c83226 1px, transparent 1px',
        'grid-green': '#22c55e 0.5px, transparent 0.5px'
      }),
      backgroundSize: {
        'grid': '16px 16px',
        'grid-sm': '12px 12px'
      }
    },
  },
  plugins: [],
}
