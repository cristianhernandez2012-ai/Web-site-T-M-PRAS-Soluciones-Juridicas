/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./contacto.html'],
  theme: {
    extend: {
      colors: {
        primary: '#0020E6',
        'background-light': '#f6f6f8',
        'background-dark': '#101622',
      },
      fontFamily: {
        display: ['Public Sans', 'sans-serif'],
      },
      borderRadius: {
        DEFAULT: '0.25rem',
        lg: '0.5rem',
        xl: '0.75rem',
        full: '9999px',
      },
    },
  },
  plugins: [],
};


