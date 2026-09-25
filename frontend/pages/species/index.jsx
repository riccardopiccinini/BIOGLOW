import { useRouter } from "next/router";
import useSWR from "swr";
import Layout from "../../components/Layout";

const fetcher = (url) => fetch(url).then((r) => r.json());

const SPECIES_CATEGORIES = {
  "Lontra europea": { type: "protetta", label: "Da Proteggere", color: "bg-blue-100 text-blue-800" },
  "Cinghiale": { type: "normale", label: "Normale", color: "bg-gray-100 text-gray-800" },
  "Specie Invasiva X": { type: "pericolosa", label: "Pericolosa", color: "bg-red-100 text-red-800" },
};

export default function SpeciesIndex() {
  const router = useRouter();
  const { data, error } = useSWR("/observations", fetcher);

  if (error) return <Layout><div className="p-8 text-red-500">Errore nel caricamento delle specie</div></Layout>;
  if (!data) return <Layout><div className="p-8">Caricamento...</div></Layout>;

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
            const cat = SPECIES_CATEGORIES[species] || { type: "normale", label: "Normale", color: "bg-gray-100 text-gray-800" };
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
