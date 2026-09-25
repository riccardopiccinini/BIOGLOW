import { useState, useEffect } from "react";
import useSWR from "swr";
import Layout from "../components/Layout";
import { fetcher, formatDate, formatConfidence } from "../lib/utils";
import { supabase } from "../lib/supabase";
import { useRouter } from "next/router";
import { LuCheck, LuX, LuAlertCircle } from "react-icons/lu";

export default function AdminPanel() {
  const router = useRouter();
  const [user, setUser] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);

  // Check auth status
  useEffect(() => {
    const checkUser = async () => {
      const { data: { session } } = await supabase.auth.getSession();
      setUser(session?.user ?? null);
      setLoadingAuth(false);
    };
    checkUser();
  }, []);

  // Fetch only pending observations
  const { data: observations, error, mutate } = useSWR(
    `/observations?verification_status=pending&limit=100`,
    fetcher
  );

  const handleStatusUpdate = async (id, newStatus) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token;

      const response = await fetch(`/observations/${id}`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({ verification_status: newStatus })
      });

      if (!response.ok) throw new Error("Errore durante l'aggiornamento");
      
      // Refresh the list
      mutate();
    } catch (err) {
      alert(`Errore: ${err.message}`);
    }
  };

  if (loadingAuth) return <Layout><div className="flex items-center justify-center min-h-screen">Caricamento...</div></Layout>;
  
  // Redirect to login if not authenticated
  if (!user) {
    router.push("/login");
    return null;
  }

  return (
    <Layout>
      <div className="p-6 max-w-6xl mx-auto">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Pannello di Validazione</h1>
            <p className="text-muted dark:text-gray-400">Revisione scientifica delle osservazioni AI</p>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 px-4 py-2 rounded-full text-sm font-medium border border-blue-100 dark:border-blue-800">
            Modalità Amministratore
          </div>
        </header>

        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-4 rounded-lg mb-6 border border-red-100 dark:border-red-800">
            Errore nel caricamento delle osservazioni.
          </div>
        )}

        {!observations || observations.length === 0 ? (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-md p-12 text-center border border-gray-100 dark:border-gray-700 transition-colors">
            <LuAlertCircle className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Tutto pulito!</h2>
            <p className="text-muted dark:text-gray-400">Non ci sono osservazioni in attesa di validazione.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4">
            {observations.map((obs) => (
              <div 
                key={obs.id} 
                className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-4 flex flex-col sm:flex-row items-center justify-between gap-4 transition-colors hover:shadow-md"
              >
                <div className="flex items-center gap-4 flex-1">
                  <div className="w-16 h-16 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 flex-shrink-0">
                    {obs.method === "image" && obs.media_url ? (
                      <img src={obs.media_url} alt={obs.species} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-muted dark:text-gray-500">
                        🎵
                      </div>
                    )}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="font-bold text-gray-900 dark:text-white">{obs.species}</p>
                      <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
                        {obs.method === "image" ? "Foto" : "Audio"}
                      </span>
                    </div>
                    <p className="text-sm text-muted dark:text-gray-400">
                      {formatDate(obs.date_time)} · Sicurezza: <span className="font-semibold">{formatConfidence(obs.confidence)}</span>
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  <button 
                    onClick={() => handleStatusUpdate(obs.id, "excluded")}
                    className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/40 transition-colors"
                    title="Scarta osservazione"
                  >
                    <LuX className="w-5 h-5" />
                  </button>
                  <button 
                    onClick={() => handleStatusUpdate(obs.id, "confirmed")}
                    className="p-3 rounded-lg bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/40 transition-colors"
                    title="Conferma osservazione"
                  >
                    <LuCheck className="w-5 h-5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Layout>
  );
}
