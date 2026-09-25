import { useState, useEffect } from "react";
import { LuSun, LuMoon } from "react-icons/lu";

export default function Layout({ children }) {
  const [darkMode, setDarkMode] = useState(false);

  useEffect(() => {
    // Check system preference or saved setting
    const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches || localStorage.getItem("theme") === "dark";
    setDarkMode(isDark);
    if (isDark) {
      document.documentElement.classList.add("dark");
    }
  }, []);

  const toggleDarkMode = () => {
    const newMode = !darkMode;
    setDarkMode(newMode);
    if (newMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100 transition-colors duration-300">
      <header className="p-4 flex justify-end">
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:ring-2 ring-primary transition-all"
          aria-label="Toggle Dark Mode"
        >
          {darkMode ? <LuSun className="w-5 h-5" /> : <LuMoon className="w-5 h-5" />}
        </button>
      </header>
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
