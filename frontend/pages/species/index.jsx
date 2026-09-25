import { useRouter } from "next/router";
import useSWR from "swr";
import Layout from "../../components/Layout";
import { jsonFetcher, ErrorDisplay, LoadingDisplay } from "../../lib/utils";
import { SPECIES_CATEGORIES } from "../../lib/constants";

export default function SpeciesIndex() {
  const router = useRouter();
  const { data, error } = useSWR("/observations", jsonFetcher);

  if (error) return <Layout><ErrorDisplay message="Errore nel caricamento delle specie" /></Layout>;
  if (!data) return <Layout><LoadingDisplay message="Caricamento dati..." /></Layout>;

  const distinctSpecies = [...new Set(data.map(obs => obs.species))].filter(Boolean);

  return (
    <Layout>
      <div className="flex flex-col gap-8 p-4 lg:p-8 bg-gray-50 min-h-screen">
        <header className="flex items-center gap-4">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-gray-200 rounded-full transition"
          >
            ← Torna alla Dashboard
          </button>
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
            Specie Rilevate
          </h1>
        </header>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {distinctSpecies.map(species => {
            // Determine category from species name
            let category = "normal";
            const speciesRef = window.SPECIES_REF || {};
            if (speciesRef.rare?.includes(species)) category = "rare";
            else if (speciesRef.protected?.includes(species)) category = "protected";
            else if (speciesRef.invasive?.includes(species)) category = "invasive";
            // Filter to show only protected and invasive species (hide rare and normal)
            


            // REMOVED: filter that was hiding normal and rare species
            const cat = SPECIES_CATEGORIES[category] || SPECIES_CATEGORIES.normal;
            return (
              <div
                key={species}
                onClick={() => router.push(`/species/${encodeURIComponent(species)}`)}
                className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 hover:border-primary cursor-pointer transition-all hover:shadow-md group"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold text-gray-900 group-hover:text-primary transition">{species}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${cat.color}`}>
                    {cat.label}
                  </span>
                </div>
                <p className="text-sm text-muted">Clicca per vedere le prove (foto/audio)</p>
              </div>
            );
          })}
        </div>
      </div>
    </Layout>
  );
}
