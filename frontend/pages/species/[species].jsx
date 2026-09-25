import { useRouter } from "next/router";
import useSWR from "swr";
import Layout from "../../components/Layout";
import ObservationList from "../../components/ObservationList";
import { jsonFetcher, ErrorDisplay, LoadingDisplay } from "../../lib/utils";

export default function SpeciesDetail() {
  const router = useRouter();
  const { species } = router.query;

  const { data: observations, error } = useSWR(
    "/observations?limit=1000",
    jsonFetcher
  );

  if (!species) return <Layout><LoadingDisplay message="Caricamento dati..." /></Layout>;
  if (error) return <Layout><ErrorDisplay message="Errore nel caricamento dei dati" /></Layout>;
  if (!observations) return <Layout><LoadingDisplay message="Caricamento dati..." /></Layout>;

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
              filters={{ species: species }}
              data={filteredObs}
            />
          </div>
        </div>
      </div>
    </Layout>
  );
}