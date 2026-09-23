import { useState } from "react";
import useSWR from "swr";
import Layout from "../components/Layout";
import FilterBar from "../components/FilterBar";
import StatsCard from "../components/StatsCard";
import ShannonLineChart from "../components/ShannonLineChart";
import SpeciesDistributionChart from "../components/SpeciesDistributionChart";
import ObservationList from "../components/ObservationList";
import AlertList from "../components/AlertList";

const fetcher = (url) => fetch(url).then((r) => r.json());

export default function Home() {
  // Stato filtri
  const [filters, setFilters] = useState({
    station: "",
    method: "",
    startDate: "",
    endDate: "",
  });

  // Fetch statistiche base (non dipende dai filtri)
  const { data: stats, error: statsError } = useSWR(
    "/observations/stats",
    fetcher,
    { refreshInterval: 30000 } // refresh ogni 30 secondi
  );

  if (statsError) {
    return (
      <Layout>
        <div className="text-center py-12 text-red-500">
          <h2 className="text-xl font-semibold">Errore nel caricamento delle statistiche</h2>
          <p className="text-muted mt-2">Impossibile connettersi al backend. Verifica che il server sia attivo.</p>
        </div>
      </Layout>
    );
  }

  if (!stats) {
    return (
      <Layout>
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">Caricamento dashboard…</p>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      {/* Header */}
      <header className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-bold text-primary">Monitor Secchia Dashboard</h1>
        <p className="text-muted mt-1">Visualizzazione dei dati di biodiversità osservata</p>
      </header>

      {/* Filtri */}
      <FilterBar onFilterChange={setFilters} initialFilters={filters} />

      {/* Riepilogo generale */}
      <StatsCard
        totalObservations={stats.total_observations}
        speciesCount={stats.species_count}
        shannonIndex={stats.shannon_index}
      />

      {/* Griglia principale: grafici a sinistra, liste a destra */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Colonna sinistra (2/3) - Grafici */}
        <div className="lg:col-span-2 space-y-6">
          <ShannonLineChart interval="month" />
          <SpeciesDistributionChart filters={filters} />
        </div>

        {/* Colonna destra (1/3) - Liste */}
        <div className="space-y-6">
          <ObservationList filters={filters} />
          <AlertList />
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-10 text-center text-sm text-muted border-t border-gray-200 pt-6">
        <p>Dashboard aggiornata in tempo reale</p>
        <p className="mt-1">Dati: Supabase → Render (Backend) → Vercel (Frontend)</p>
      </footer>
    </Layout>
  );
}