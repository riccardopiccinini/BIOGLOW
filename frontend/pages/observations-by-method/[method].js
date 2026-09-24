import { useState, useEffect } from "react";
import useSWR from "swr";
import { useRouter } from "next/router";
import Layout from "../../components/Layout";
import ObservationList from "../../components/ObservationList";
import StatsCard from "../../components/StatsCard";
import ShannonLineChart from "../../components/ShannonLineChart";
import SpeciesDistributionChart from "../../components/SpeciesDistributionChart";

const fetcher = (url) => fetch(url).then((r) => {
  if (!r.ok) throw new Error("API error");
  return r.json();
});

export default function ObservationsByMethod() {
  const router = useRouter();
  const { method } = router.query;
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [errorStats, setErrorStats] = useState(null);

  // Fetch stats for this method (optional, to show total count)
  useEffect(() => {
    if (!method) return;
    setLoadingStats(true);
    fetcher(`/api/observations/stats?method=${method}`)
      .then((data) => {
        setStats(data);
        setLoadingStats(false);
      })
      .catch((err) => {
        setErrorStats(err.message);
        setLoadingStats(false);
      });
  }, [method]);

  if (loadingStats) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="flex flex-col items-center gap-4">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
            <p className="text-lg text-muted animate-pulse">Caricamento statistiche...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (errorStats) {
    return (
      <Layout>
        <div className="flex items-center justify-center min-h-screen p-4">
          <div className="bg-white p-8 rounded-2xl shadow-xl border border-red-100 text-center max-w-md">
            <div className="text-red-500 text-5xl mb-4">⚠️</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Errore di caricamento</h2>
            <p className="text-muted mb-6">{errorStats}</p>
            <button onClick={() => router.push("/")} className="bg-primary text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-dark transition">Torna alla dashboard</button>
          </div>
        </div>
      </Layout>
    );
  }

  const methodLabel = method === "image" ? "Foto" : method === "audio" ? "Audio" : method;

  return (
    <Layout>
      <div className="p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <h1 className="text-2xl font-extrabold text-gray-900 md:text-3xl">
            Osservazioni per metodo: {methodLabel}
          </h1>
          <a href="/" className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition">
            <span>←</span> Torna alla dashboard
          </a>
        </div>

        {/* Stats card for this method */}
        {stats && (
          <div className="mb-6">
            <StatsCard
              totalObservations={stats.total_observations}
              speciesCount={stats.species_count}
              shannonIndex={stats.shannon_index}
            />
          </div>
        )}

        {/* Observations list */}
        <div className="bg-white rounded-2xl shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4 text-primary">
            Elenco osservazioni ({methodLabel})
          </h2>
          <ObservationList
            filters={{
              station: "",
              method: method || "", // pass the method from URL
              startDate: "",
              endDate: "",
            }}
          />
        </div>

        {/* Optional: Shannon trend for this method */}
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4 text-primary">
            Andamento indice di Shannon ({methodLabel})
          </h2>
          <ShannonLineChart
            interval="month"
            filters={{
              station: "",
              method: method || "",
              startDate: "",
              endDate: "",
            }}
          />
        </div>

        {/* Optional: Species distribution for this method */}
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4 text-primary">
            Distribuzione specie ({methodLabel})
          </h2>
          <SpeciesDistributionChart
            filters={{
              station: "",
              method: method || "",
              startDate: "",
              endDate: "",
            }}
          />
        </div>
      </div>
    </Layout>
  );
}