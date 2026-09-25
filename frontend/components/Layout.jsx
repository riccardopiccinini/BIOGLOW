import { useState, useEffect, useRef } from "react";
import { LuSun, LuMoon } from "react-icons/lu";

export default function Layout({ children }) {
  // Initialize state based on system preference and saved theme (sync to avoid flash)
  const getInitialMode = () => {
    if (typeof window === "undefined") return false; // SSR: default to light
    const saved = localStorage.getItem("theme");
    if (saved) return saved === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  };

  const [darkMode, setDarkMode] = useState(getInitialMode);
  const initializedRef = useRef(false); // To prevent duplicate initialization

  useEffect(() => {
    // Set the initial theme class on documentElement to prevent flash
    if (!initializedRef.current) {
      if (darkMode) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
      initializedRef.current = true;
    }

    // Listen for system theme changes
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e) => {
      // Only update if user hasn't explicitly set a preference (i.e., no localStorage theme)
      if (!localStorage.getItem("theme")) {
        setDarkMode(e.matches);
      }
    };
    mediaQuery.addEventListener("change", handleChange);

    // Update theme class and localStorage when darkMode state changes
    if (darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }

    // Cleanup
    return () => {
      mediaQuery.removeEventListener("change", handleChange);
    };
  }, [darkMode]); // Re-run effect when darkMode changes

  const toggleDarkMode = () => {
    setDarkMode((prevMode) => !prevMode);
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
