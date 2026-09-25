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

  // Sync filters with query params on mount and on route change
  useEffect(() => {
    const { station, method, startDate, endDate } = router.query;
    setFilters({
      station: station ?? "",
      method: method ?? "",
      startDate: startDate ?? "",
      endDate: endDate ?? "",
    });
  }, [router.query]);

  // Update URL when filters change (shallow push to preserve state)
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
      <div className="flex flex-col lg:flex-row gap-6 p-4 lg:p-8 bg-gray-50 min-h-screen">

        {/* SIDEBAR: Filtri e Controllo */}
        <aside className="w-full lg:w-80 shrink-0 space-y-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 sticky top-8">
            <h2 className="text-xl font-bold text-primary mb-6 flex items-center gap-2">
              <span className="w-2 h-6 bg-primary rounded-full"></span>
              Filtri di Controllo
            </h2>
            <FilterBar
              value={filters}
              onFilterChange={handleFilterChange}
            />
            <div className="mt-6 p-4 bg-blue-50 rounded-xl border border-blue-100">
              <p className="text-xs text-blue-700 leading-relaxed">
                I filtri aggiornano automaticamente tutti i grafici e le liste della dashboard.
              </p>
            </div>
          </div>
        </aside>

        {/* MAIN CONTENT */}
        <main className="flex-1 space-y-8">

          {/* HEADER */}
          <header className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-2">
            <div>
              <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Monitor Secchia Dashboard</h1>
              <p className="text-muted">Analisi della biodiversità in tempo reale</p>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-100 text-green-700 rounded-full text-xs font-bold animate-pulse">
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

          <footer className="mt-12 py-6 border-t border-gray-200 text-center text-sm text-muted">
            <p>Dashboard aggiornata in tempo reale · Dati: Supabase → Render → Vercel</p>
          </footer>
        </main>
      </div>
    </Layout>
  );
}