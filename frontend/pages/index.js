import { useState, useEffect } from "react";
import useSWR from "swr";
import { useRouter } from "next/router";
import Layout from "../components/Layout";
import FilterBar from "../components/FilterBar";
import StatsCard from "../components/StatsCard";
import ShannonLineChart from "../components/ShannonLineChart";
import SpeciesDistributionChart from "../components/SpeciesDistributionChart";
import MethodDistributionChart from "../components/MethodDistributionChart";
import ObservationList from "../components/ObservationList";
import AlertList from "../components/AlertList";
import StationMap from "../components/StationMap";
import { fetcher, buildFilterParams, ErrorDisplay, LoadingDisplay } from "../lib/utils";

export default function Home() {
  const router = useRouter();
  const [filters, setFilters] = useState({
    station: "",
    method: "",
    startDate: "",
    endDate: "",
  });

  useEffect(() => {
    const { station, method, startDate, endDate } = router.query;
    setFilters({
      station: station ?? "",
      method: method ?? "",
      startDate: startDate ?? "",
      endDate: endDate ?? "",
    });
  }, [router.query]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    const params = buildFilterParams(newFilters);
    router.push(
      {
        pathname: router.pathname,
        query: Object.fromEntries(params),
      },
      undefined,
      { shallow: true }
    );
  };

  const exportToCSV = async () => {
    try {
      const params = buildFilterParams(filters, { limit: "10000" });
      const response = await fetcher(`/observations?${params.toString()}`);
      
      if (!response || !Array.isArray(response)) {
        throw new Error("Nessun dato disponibile per l'esportazione");
      }

      const csvContent = convertToCSV(response);
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      const timestamp = new Date().toISOString().slice(0, 19).replace(/[:]/g, "-");
      link.setAttribute("href", url);
      link.setAttribute("download", `biodiversita_report_${timestamp}.csv`);
      link.style.visibility = "hidden";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error("Export error:", error);
      alert(`Errore durante l'esportazione: ${error.message}`);
    }
  };

  const convertToCSV = (objArray) => {
    if (!objArray || !Array.isArray(objArray) || objArray.length === 0) {
      return "";
    }
    const keys = [...new Set(objArray.flatMap(Object.keys))];
    const header = keys.map(key => `"${key}"`).join(",");
    const rows = objArray.map(obj => {
      return keys.map(key => {
        const value = obj[key];
        if (value === null || value === undefined) return '';
        if (typeof value === 'string') return `"${value.replace(/"/g, '""')}"`;
        if (typeof value === 'object') return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
        return `"${value}"`;
      }).join(",");
    });
    return [header, ...rows].join("\n");
  };

  const { data: stats, error: statsError } = useSWR(
    "/observations/stats",
    fetcher,
    { refreshInterval: 30000 }
  );

  if (statsError) {
    return (
      <Layout>
        <ErrorDisplay
          message="Impossibile recuperare i dati dal server. Verifica che il backend su Render sia attivo."
          onRetry={() => window.location.reload()}
        />
      </Layout>
    );
  }

  if (!stats) {
    return (
      <Layout>
        <LoadingDisplay message="Caricamento dati..." />
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="flex flex-col lg:flex-row gap-6 p-4 lg:p-8 bg-gray-50 dark:bg-gray-900 min-h-screen transition-colors duration-300">

        {/* SIDEBAR: Filtri e Controllo */}
        <aside className="w-full lg:w-80 shrink-0 space-y-6">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 sticky top-8 transition-colors">
            <h2 className="text-xl font-bold text-primary dark:text-blue-400 mb-6 flex items-center gap-2">
              <span className="w-2 h-6 bg-primary dark:bg-blue-500 rounded-full"></span>
              Filtri di Controllo
            </h2>
            <FilterBar
              value={filters}
              onFilterChange={handleFilterChange}
            />
            <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-800 transition-colors">
              <p className="text-xs text-blue-700 dark:text-blue-300 leading-relaxed">
                I filtri aggiornano automaticamente tutti i grafici e le liste della dashboard.
              </p>
            </div>
            
            <div className="mt-4">
              <button
                onClick={exportToCSV}
                className="w-full bg-green-500 text-white px-4 py-2 rounded-lg hover:bg-green-600 transition flex items-center justify-center gap-2"
              >
                <span className="w-4 h-4">📥</span>
                Esporta dati (CSV)
              </button>
            </div>
          </div>
        </aside>

        {/* MAIN CONTENT */}
        <main className="flex-1 space-y-8">

          {/* HEADER */}
          <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-2">
            <div>
              <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white tracking-tight">Monitor Secchia Dashboard</h1>
              <p className="text-muted dark:text-gray-400">Analisi della biodiversità in tempo reale</p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-xs font-bold animate-pulse">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              SISTEMA ATTIVO
            </div>
          </header>

          {/* ZONE 1: Summary Numbers */}
          <section>
            <StatsCard
              totalObservations={stats.total_observations}
              speciesCount={stats.species_count}
              shannonIndex={stats.shannon_index}
            />
          </section>

          {/* ZONE 2: Visual Analysis (Charts) */}
          <section className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            <div className="space-y-6">
              <ShannonLineChart interval="month" filters={filters} />
              <MethodDistributionChart filters={filters} />
            </div>
            <div className="space-y-6">
              <SpeciesDistributionChart filters={filters} />
              <StationMap />
            </div>
          </section>

          {/* ZONE 3: Monitoring (Lists) */}
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <ObservationList filters={filters} />
            </div>
            <div className="lg:col-span-1">
              <AlertList />
            </div>
          </section>

          <footer className="mt-12 py-6 border-t border-gray-200 dark:border-gray-700 text-center text-sm text-muted dark:text-gray-400">
            <p>Dashboard aggiornata in tempo reale · Dati: Supabase → Render → Vercel</p>
          </footer>
        </main>
      </div>
    </Layout>
  );
}
