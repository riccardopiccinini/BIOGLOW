import { useRouter } from "next/router";
import useSWR from "swr";
import Layout from "../../components/Layout";
import StatsCard from "../../components/StatsCard";
import ShannonLineChart from "../../components/ShannonLineChart";
import SpeciesDistributionChart from "../../components/SpeciesDistributionChart";
import ObservationList from "../../components/ObservationList";

const fetcher = (url) => fetch(url).then((r) => r.json());

export default function StationDetail() {
  const router = useRouter();
  const { id } = router.query;

  const { data: stats, error } = useSWR(
    id ? `/observations/stats?station_id=${id}` : null,
    fetcher
  );

  if (!id) return <Layout><div className="p-8">Caricamento dati...ti...</div></Layout>;
  if (error) return <Layout><div className="p-8 text-red-500">Errore nel caricamento dei dati della stazione</div></Layout>;
  if (!stats) return <Layout><div className="p-8">Caricamento dati...</div></Layout>;

  const filters = { station: id, method: "", startDate: "", endDate: "" };

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
          <div>
            <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">
              Stazione: {id}
            </h1>
            <p className="text-muted">Dettaglio monitoraggio biodiversità locale</p>
          </div>
        </header>

        <StatsCard
          totalObservations={stats.total_observations}
          speciesCount={stats.species_count}
          shannonIndex={stats.shannon_index}
        />

        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <ShannonLineChart interval="month" filters={filters} />
          <SpeciesDistributionChart filters={filters} />
        </div>

        <ObservationList filters={filters} />
      </div>
    </Layout>
  );
}
