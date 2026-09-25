import { useState, useEffect } from "react";
import useSWR from "swr";
import { useRouter } from "next/router";
import Layout from "../../components/Layout";
import StatsCard from "../../components/StatsCard";
import ShannonLineChart from "../../components/ShannonLineChart";
import ObservationList from "../../components/ObservationList";
import SpeciesDistributionChart from "../../components/SpeciesDistributionChart";
import { fetcher, ErrorDisplay, LoadingDisplay } from "../../lib/utils";

export default function StationDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [stationData, setStationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch station detail
  useEffect(() => {
    if (!id) return;
    setLoading(true);
    setError(null);
    fetch(`/api/stations/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Stazione non trovata");
        return res.json();
      })
      .then((data) => {
        setStationData(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <Layout>
        <LoadingDisplay message="Caricamento dettagli stazione..." />
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <ErrorDisplay
          message="La stazione richiesta non esiste o è stata rimossa."
          onRetry={() => router.push("/")}
        />
      </Layout>
    );
  }

  const { station, stats, species, latest_observations } = stationData;

  return (
    <Layout>
      <div className="p-6">
        {/* Header with back button */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <button
            onClick={() => router.push("/")}
            className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition"
          >
            <span>←</span> Torna alla dashboard
          </button>
          <h1 className="text-2xl font-extrabold text-gray-900 md:text-3xl">
            {station.name}
          </h1>
        </div>

        {/* Station info and stats */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Station details */}
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4 text-primary">Informazioni stazione</h2>
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="w-5 h-5 bg-primary rounded-full"></span>
                <span className="text-sm text-muted">ID</span>
                <p className="font-medium">{station.id}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="w-5 h-5 bg-primary rounded-full"></span>
                <span className="text-sm text-muted">Nome</span>
                <p className="font-medium">{station.name}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="w-5 h-5 bg-primary rounded-full"></span>
                <span className="text-sm text-muted">Coordinate</span>
                <p className="font-medium">
                  {station.lat.toFixed(6)}° N, {station.lon.toFixed(6)}° E
                </p>
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4 text-primary">Statistiche</h2>
            <StatsCard
              totalObservations={stats.total_observations}
              speciesCount={stats.species_count}
              shannonIndex={stats.shannon_index}
            />
          </div>

          {/* Species list */}
          <div className="bg-white rounded-2xl shadow-md p-6">
            <h2 className="text-lg font-semibold mb-4 text-primary">Specie osservate</h2>
            {species.length === 0 ? (
              <p className="text-gray-500 text-center py-4">Nessuna specie registrata</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {species.map((sp) => (
                  <li key={sp.species} className="flex justify-between items-center px-3 py-2 bg-gray-50 rounded">
                    <span className="font-medium">{sp.species}</span>
                    <span className="bg-primary text-white px-3 py-1 rounded text-xs">{sp.count}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Tabs for different views */}
        <div className="mb-6">
          <div className="flex border-b border-gray-200">
            <button
              onClick={() => {}}
              className="px-4 py-3 text-sm font-medium text-gray-500 hover:text-primary border-b-2 border-transparent hover:border-primary"
            >
              Osservazioni recenti
            </button>
            <button
              onClick={() => {}}
              className="px-4 py-3 text-sm font-medium text-gray-500 hover:text-primary border-b-2 border-transparent hover:border-primary"
            >
              Distribuzione specie
            </button>
            <button
              onClick={() => {}}
              className="px-4 py-3 text-sm font-medium text-primary border-b-2 border-primary"
            >
              Andamento Shannon
            </button>
          </div>
        </div>

        {/* Content based on active tab - we'll show all for simplicity */}
        <div className="space-y-8">
          {/* Recent observations */}
          <section>
            <h2 className="text-lg font-semibold mb-4 text-primary">Osservazioni recenti</h2>
            <ObservationList
              filters={{
                station: station.id,
                method: "",
                startDate: "",
                endDate: "",
              }}
            />
          </section>

          {/* Species distribution */}
          <section>
            <h2 className="text-lg font-semibold mb-4 text-primary">Distribuzione specie presso questa stazione</h2>
            <SpeciesDistributionChart
              filters={{
                station: station.id,
                method: "",
                startDate: "",
                endDate: "",
              }}
            />
          </section>

          {/* Shannon trend */}
          <section>
            <h2 className="text-lg font-semibold mb-4 text-primary">Andamento indice di Shannon</h2>
            <ShannonLineChart
              interval="month"
              filters={{
                station: station.id,
                method: "",
                startDate: "",
                endDate: "",
              }}
            />
          </section>
        </div>
      </div>
    </Layout>
  );
}