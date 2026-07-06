module.exports = {
  presets: [require('frappe-ui/src/utils/tailwind.config')],
  darkMode: 'class',
  content: [
    './index.html',
    './src/**/*.{vue,js,ts,jsx,tsx}',
    './node_modules/frappe-ui/src/components/**/*.{vue,js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // Brand navy scale (anchored at #05102a). Static hex for utility
        // classes; CSS vars in design/tokens.css drive runtime theming.
        brand: {
          DEFAULT: '#05102a',
          50: '#eef1f6',
          100: '#d8dfeb',
          200: '#b1bfd6',
          300: '#8499bd',
          400: '#5470a0',
          500: '#345086',
          600: '#25406f',
          700: '#1c3158',
          800: '#15233f',
          900: '#0c1730',
          950: '#05102a',
        },
      },
      borderRadius: {
        card: 'var(--radius-card)',
        control: 'var(--radius-control)',
      },
      boxShadow: {
        card: 'var(--shadow-sm)',
        'card-hover': 'var(--shadow-md)',
      },
    },
  },
  plugins: [],
}
