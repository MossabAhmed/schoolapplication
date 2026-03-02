/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './school/templates/**/*.html',
    './templates/registration/**/*.html',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Cairo', 'sans-serif'], // خط Cairo للغة العربية
      },
    },
  },
  plugins: [],
}
