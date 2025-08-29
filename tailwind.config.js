// tailwind.config.js
module.exports = {
  content: [
    "./templates/**/*.html",     // project templates
    "./**/templates/**/*.html",  // app-level templates
    "./static/src/**/*.{js,jsx,ts,tsx}" // if you use React/JS
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
