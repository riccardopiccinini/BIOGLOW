import { useState, useEffect, useRef } from "react";
import { LuSun, LuMoon, LuLogOut, LuUser, LuLogIn } from "react-icons/lu";
import { useRouter } from "next/router";
import Link from "next/link";
import { supabase } from "../lib/supabase";

export default function Layout({ children }) {
  const [darkMode, setDarkMode] = useState(false);
  const [user, setUser] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);
  const router = useRouter();
  const initializedRef = useRef(false);

  const getInitialMode = () => {
    if (typeof window === "undefined") return false;
    const saved = localStorage.getItem("theme");
    if (saved) return saved === "dark";
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  };

  useEffect(() => {
    // Theme Init
    if (!initializedRef.current) {
      if (darkMode) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
      initializedRef.current = true;
    }

    // Auth Init
    const checkUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user ?? null);
      setLoadingAuth(false);
    };
    checkUser();

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e) => {
      if (!localStorage.getItem("theme")) {
        setDarkMode(e.matches);
      }
    };
    mediaQuery.addEventListener("change", handleChange);

    if (darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }

    return () => {
      mediaQuery.removeEventListener("change", handleChange);
      subscription.unsubscribe();
    };
  }, [darkMode]);

  const toggleDarkMode = () => {
    setDarkMode((prevMode) => !prevMode);
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100 transition-colors duration-300">
      <header className="p-4 flex justify-end items-center gap-4">
        {user && (
          <div className="flex items-center gap-2 text-sm font-medium text-muted dark:text-gray-400">
            <LuUser className="w-4 h-4" />
            <span>Biologo</span>
            <button 
              onClick={handleLogout}
              className="ml-2 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
              title="Logout"
            >
              <LuLogOut className="w-4 h-4" />
            </button>
          </div>
        )}
        {!user && !loadingAuth && (
          <Link href="/login" className="flex items-center gap-2 text-sm font-medium text-primary hover:text-primary-dark transition-colors px-3 py-1 rounded-lg hover:bg-primary/10">
            <LuLogIn className="w-4 h-4" />
            <span>Accedi</span>
          </Link>
        )}
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
