import { useRouter } from "next/router";
import useSWR from "swr";
import Layout from "../../components/Layout";
import ObservationList from "../../components/ObservationList";

const fetcher = (url) => fetch(url).then((r) => r.json());

export default function SpeciesDetail() {
  const router = useRouter();
  const { species } = router.query;

  // Use the general observations endpoint with a species filter if possible, 
  // or filter client-side since the API doesn't have a dedicated species filter.
  const { data: observations, error } = useSWR(
    "/observations?limit=1000", 
    fetcher
  );

  if (!species) return <Layout><div className="p-8">Caricamento specie...</div></Layout>;
  if (error) return <Layout><div className="p-8 text-red-500">Errore nel caricamento dei dati</div></Layout>;
  if (!observations) return <Layout><div className="p-8">Caricamento...</div></Layout>;

  // Filter observations for this specific species
  const filteredObs = observations.filter(obs => obs.species === species);

  return (
    <Layout>
      <div className="flex flex-col gap-8 p-4 lg:p-8 bg-gray-50 min-h-screen">
        <header className="flex items-center gap-4">
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
            <p className="text-muted">Evidenze raccolte: {filteredObs.length} osservazioni</p>
          </div>
        </header>

        <div className="grid grid-cols-1 gap-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
            <h2 className="text-xl font-bold text-primary mb-4">Galleria Prove</h2>
            <ObservationList 
              filters={{ species: species }} // This might need a backend update to support 'species' filter
              data={filteredObs} // Pass filtered data directly to avoid redundant API calls
            />
          </div>
        </div>
      </div>
    </Layout>
  );
}
