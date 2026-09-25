import { useRouter } from "next/router";
import Layout from "../../components/Layout";
import ObservationList from "../../components/ObservationList";
import { getMethodLabel, OBSERVATION_METHODS } from "../../lib/utils";

export default function MethodDetail() {
  const router = useRouter();
  const { method } = router.query;

  if (!method) return <Layout><div className="p-8">Caricamento dati...</div></Layout>;

  const methodLabel = getMethodLabel(method);
  const methodConfig = OBSERVATION_METHODS[method] || OBSERVATION_METHODS.image;

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
              Rilevazioni: {methodLabel}
            </h1>
            <p className="text-muted">Elenco completo di tutte le osservazioni registrate tramite {methodLabel.toLowerCase()}</p>
          </div>
        </header>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
          <ObservationList
            filters={{ method: method }}
          />
        </div>
      </div>
    </Layout>
  );
}