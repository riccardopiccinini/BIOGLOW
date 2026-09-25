import React, { useState, useEffect } from "react";
import useSWR from "swr";
import { useRouter } from "next/router";
import Layout from "../../components/Layout";
import ObservationList from "../../components/ObservationList";
import FilterBar from "../../components/FilterBar";
import { jsonFetcher, ErrorDisplay, LoadingDisplay } from "../../lib/utils";

export default function SpeciesDetail() {
  const router = useRouter();
  const { species } = router.query;
  const [filters, setFilters] = useState({
    station: "",
    method: "",
    startDate: "",
    endDate: "",
  });

  // Sync filters with query params on mount and on route change
  useEffect(() => {
    const { station, method, startDate, endDate } = router.query;
    setFilters(prev => ({
      ...prev,
      station: station ?? "",
      method: method ?? "",
      startDate: startDate ?? "",
      endDate: endDate ?? "",
    }));
  }, [router.query]);

  // Update URL when filters change (shallow push to preserve state)
  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    const params = {
      species: species, // Always include the species filter
      ...newFilters
    };
    // Remove empty params to keep URL clean
    const filteredParams = Object.fromEntries(
      Object.entries(params).filter(([_, value]) => value !== "")
    );
    router.push(
      {
        pathname: router.pathname,
        query: filteredParams,
      },
      undefined,
      { shallow: true }
    );
  };

  const { data: allObservations, error } = useSWR(
    "/observations?limit=1000",
    jsonFetcher
  );

  if (!species) return <Layout><LoadingDisplay message="Caricamento dati..." /></Layout>;
  if (error) return <Layout><ErrorDisplay message="Errore nel caricamento dei dati" /></Layout>;
  if (!allObservations) return <Layout><LoadingDisplay message="Caricamento dati..." /></Layout>;

  // Filter observations by species first (since we're on a species page)
  const speciesObservations = allObservations.filter(obs => obs.species === species);

  return (
    <Layout>
      <div className="flex flex-col gap-8 p-4 lg:p-8 bg-gray-50 min-h-screen">
        <header className="flex flex-col gap-4">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-gray-200 rounded-full transition"
          >
            ← Torna alle Specie
          </button>
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
              {species}
            </h1>
            <p className="text-muted">Evidenze raccolte: {speciesObservations.length} osservazioni</p>
          </div>
        </header>

        <div className="grid grid-cols-1 gap-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
            <h2 className="text-xl font-bold text-primary mb-4">Galleria Prove</h2>
            <ObservationList
              filters={{ species: species, ...filters }}
              data={speciesObservations}
            />
          </div>
        </div>

        {/* Advanced Filters Section */}
        <div className="mt-6">
          <FilterBar
            value={filters}
            onFilterChange={handleFilterChange}
          />
        </div>
      </div>
    </Layout>
  );
}
