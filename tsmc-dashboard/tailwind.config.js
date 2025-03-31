// tailwind.config.js
module.exports = {
  content: [
    "./templates/**/*.{html,js}",
    "./static/**/*.{html,js}",
  ],
  safelist: [
    "bg-red-200",
    "border",
    "border-red-500",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
