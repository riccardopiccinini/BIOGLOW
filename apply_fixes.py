import os

layout_content = """import { useState, useEffect, useRef } from "react";
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
    if (!initializedRef.current) {
      if (darkMode) {
        document.documentElement.classList.add("dark");
      } else {
        document.documentElement.classList.remove("dark");
      }
      initializedRef.current = true;
    }

    const checkUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user ?? null);
      setLoadingAuth(false);
    };
    checkUser();

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
"""

obs_content = """import { useRouter } from "next/router";
import useSWR from "swr";
import Layout from "../../components/Layout";
import { LuArrowLeft, LuCircleCheck, LuCircleX, LuClock, LuMusic, LuImage } from "react-icons/lu";
import { fetcher, ErrorDisplay, LoadingDisplay, formatDate, formatConfidence } from "../../lib/utils";
import { VERIFICATION_STATUS, OBSERVATION_METHODS } from "../../lib/constants";
import { supabase } from "../../lib/supabase";

export default function ObservationDetail() {
  const router = useRouter();
  const { id } = router.query;

  const { data: obs, error, mutate } = useSWR(
    id ? `/observations/${id}` : null,
    fetcher
  );

  const updateStatus = async (newStatus) => {
    console.log("DEBUG: Inizio aggiornamento stato per ID:", id, "Nuovo stato:", newStatus);
    try {
      console.log("DEBUG: Richiesta sessione a Supabase...");
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session) {
        console.log("DEBUG: Nessuna sessione trovata. Redirect al login.");
        router.push("/login");
        return;
      }

      console.log("DEBUG: Sessione trovata, invio richiesta PATCH al backend...");
      const response = await fetch(`/observations/${id}`, {
        method: "PATCH",
        headers: { 
          "Content-Type": "application/json",
          "Authorization": `Bearer ${session.access_token}` 
        },
        body: JSON.stringify({ verification_status: newStatus }),
      });

      console.log("DEBUG: Risposta dal backend:", response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.error("DEBUG: Errore API:", errorData);
        throw new Error(errorData.detail || "Errore durante l'aggiornamento");
      }

      console.log("DEBUG: Aggiornamento riuscito. Ricarico dati...");
      await mutate();
    } catch (e) {
      console.error("DEBUG: Eccezione catturata:", e);
      alert(e.message || "Errore durante l'aggiornamento dello stato");
    }
  };

  if (error) return <Layout><ErrorDisplay message={error.message} /></Layout>;
  if (!obs) return <Layout><LoadingDisplay message="Caricamento..." /></Layout>;

  const statusConfig = {
    confirmed: { label: "Confermata", color: "bg-success", icon: <LuCircleCheck /> },
    excluded: { label: "Esclusa", color: "bg-danger", icon: <LuCircleX /> },
    pending: { label: "In attesa", color: "bg-warning", icon: <LuClock /> },
  };

  const methodConfig = OBSERVATION_METHODS[obs.method] || OBSERVATION_METHODS.image;

  return (
    <Layout>
      <button
        onClick={() => router.back()}
        className="flex items-center gap-2 text-muted hover:text-primary transition mb-6"
      >
        <LuArrowLeft /> Torna alla Dashboard
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden border border-gray-100">
          <div className="aspect-video bg-gray-100 flex items-center justify-center relative">
            {obs.method === "image" && obs.media_url ? (
              <img src={obs.media_url} alt={obs.species} className="w-full h-full object-contain" />
            ) : (
              <div className="text-center p-8">
                <div className={`${methodConfig.bgColor} p-6 rounded-full inline-block mb-4`}>
                  {methodConfig.icon === "music" ? (
                    <LuMusic className="w-12 h-12 text-blue-600" />
                  ) : (
                    <LuImage className="w-12 h-12 text-green-600" />
                  )}
                </div>
                <p className="text-gray-500">File Audio</p>
                <audio controls className="mt-4 w-full">
                  <source src={obs.media_url} type="audio/mpeg" />
                  Il tuo browser non supporta l'elemento audio.
                </audio>
              </div>
            )}
          </div>
          <div className="p-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">{obs.species}</h1>
            <p className="text-muted">{formatDate(obs.date_time)}</p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-semibold mb-6 text-primary">Analisi IA</h2>

            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span className="text-muted">Affidabilità (Confidence)</span>
                  <span className="font-bold text-gray-900">{formatConfidence(obs.confidence)}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                  <div
                    className="bg-success h-full transition-all duration-500"
                    style={{ width: `${(obs.confidence ?? 0) * 100}%` }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4">
                <div className="p-4 bg-gray-50 rounded-xl">
                  <span className="block text-xs text-muted mb-1">Stazione</span>
                  <span className="font-medium">{obs.station_id}</span>
                </div>
                <div className="p-4 bg-gray-50 rounded-xl">
                  <span className="block text-xs text-muted mb-1">Metodo</span>
                  <span className="font-medium">{methodConfig.label}</span>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-semibold mb-6 text-primary">Verifica Operatore</h2>
            <p className="text-sm text-muted mb-4">
              Stato attuale:
              <span className={` ml-2 px-2 py-1 rounded text-xs font-bold text-white ${statusConfig[obs.verification_status]?.color || "bg-gray-400"}`}>
                {statusConfig[obs.verification_status]?.label || "Sconosciuto"}
              </span>
            </p>
            <div className="grid grid-cols-3 gap-3">
              {Object.entries(statusConfig).map(([key, config]) => (
                <button
                  key={key}
                  onClick={() => updateStatus(key)}
                  className={`flex flex-col items-center justify-center p-4 rounded-xl border-2 transition-all ${
                    obs.verification_status === key
                    ? `border-${config.color.split('-')[1]} shadow-inner ${config.color} text-white`
                    : "border-gray-100 hover:border-primary text-gray-600 hover:bg-gray-50"
                  }`}
                >
                  <div className="text-2xl mb-1">{config.icon}</div>
                  <span className="text-xs font-medium">{config.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
"""

# Scrittura file
with open("frontend/components/Layout.jsx", "w", encoding="utf-8") as f:
    f.write(layout_content)

with open("frontend/pages/observation/[id].jsx", "w", encoding="utf-8") as f:
    f.write(obs_content)
