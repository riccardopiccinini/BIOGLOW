/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./pages/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2c3e50",
        secondary: "#3498db",
        success: "#27ae60",
        warning: "#f39c12",
        danger: "#e74c3c",
        muted: "#95a5a6",
      },
    },
  },
  plugins: [],
};
